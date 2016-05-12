"""Predicts the Her2 score from a histogram of pixel intensities."""

# Python imports.
import os
import sys

# 3rd party imports.
import numpy as np
import scipy.ndimage
from sklearn.linear_model import ElasticNet

# User imports.
import Utilities.merge_dictionaries
import Utilities.partition_dataset

# Globals.
modelChoices = {  # The choices of models available to use.
    "ElasticNet": {"Model": ElasticNet, "Stratified": True}
}


def main(arguments):
    """

    Assumes 8 bit greyscale or color images.

    :param arguments:   The Her2 histogram prediction arguments in JSON format.
    :type arguments:    JSON object

    """

    # Process the parameters.
    dirImages = arguments["ImageLocation"]
    if not os.path.isdir(dirImages):
        print("Image location {0:s} is not a directory.".format(dirImages))
        sys.exit()
    fileGroundTruth = arguments["GroundTruth"]
    backgroundThreshold = arguments["BackgroundThreshold"]  # The lowest pixel value that makes up the background.
    isPredictingHer2 = arguments["TargetHer2"]  # Whether we are attempting to predict Her2 or cell staining percentage.
    foldsToUse = arguments["CVFolds"]  # The number of CV folds to use.
    dirResults = arguments["ResultsLocation"]  # Directory to save the results in.
    if not os.path.exists(dirResults):
        # The results directory doesn't exist, so try and create it.
        try:
            os.makedirs(dirResults)
        except Exception as err:
            print("Error creating results directory: {0:s}".format(err))
            sys.exit()
    modelToUse = arguments["ModelToUse"]  # The type of model to train.
    modelParams = arguments["ModelParameters"]

    # Extract the ground truth values.
    caseNumbers = []
    her2Scores = []
    stainingPercent = []
    with open(fileGroundTruth, 'r') as fidGroundTruth:
        fidGroundTruth.readline()  # Strip off the header.
        for line in fidGroundTruth:
            chunks = (line.strip()).split('\t')
            caseNumbers.append(int(chunks[0]))
            her2Scores.append(int(chunks[1]))
            stainingPercent.append(float(chunks[2]))
    groundTruth = np.array([caseNumbers, her2Scores, stainingPercent])

    # Determine the mask for removing the background pixel colors.
    backgroundMask = np.array([(False if i >= backgroundThreshold else True) for i in range(256)])

    # Initalise the matrix that will hold the histogram data.
    # There will be one row per image and one column for each of the non-background pixel values, one
    # for the case number, one for the Her2 score and one for the percentage of stained cells).
    dataMatrix = np.empty((len(os.listdir(dirImages)), (backgroundMask.sum() + 3)))

    # Generate the matrix of histogram feature vectors.
    for ind, i in enumerate(os.listdir(dirImages)):
        # Read in the file.
        filePath = "{0:s}/{1:s}".format(dirImages, i)
        image = scipy.ndimage.imread(filePath)

        # Generate the histogram. One bin per color value.
        histogram = scipy.ndimage.histogram(image, 0, 255, 256)

        # Strip out the background color.
        histogram = histogram[backgroundMask]

        # Convert histogram to relative values. This will remove issues with image sizes being different.
        histogram = histogram / histogram.sum()

        # Determine the number case identifier for the image.
        caseID = int(i.split('_')[0])

        # Create the feature vector.
        caseGroundTruth = groundTruth[:, groundTruth[0, :] == caseID]  # The ground truth values for this image.
        dataMatrix[ind, 0] = caseID
        dataMatrix[ind, 1] = caseGroundTruth[1]
        dataMatrix[ind, 2] = caseGroundTruth[2]
        dataMatrix[ind, 3:] = histogram

    # Determine the target vector and the subset of the dataset used for training.
    trainingDataMatrix = dataMatrix[:, 3:]
    targetVector = dataMatrix[:, 1] if isPredictingHer2 else dataMatrix[:, 2]

    # Determine all combinations of the model parameters. The parameters to be considered are stored as a dictionary,
    # with the value for each dictionary entry being a list of the values to use when training the model.
    # The goal is therefore to convert a dictionary of lists into a list of dictionaries, where each dictionary
    # contains the same keys as the original dictionary, but has a single value associated with each key (instead of
    # a list).
    # For example, modelParams = {"lambda": [1, 2, 3, 4], "alpha": [0.001, 0.01, 0.1]} would become:
    #   [{"lambda": 1, "alpha": 0.001}, {"lambda": 1, "alpha": 0.01}, {"lambda": 1, "alpha": 0.1},
    #    {"lambda": 2, "alpha": 0.001}, {"lambda": 2, "alpha": 0.01}, {"lambda": 2, "alpha": 0.1},
    #    {"lambda": 3, "alpha": 0.001}, {"lambda": 3, "alpha": 0.01}, {"lambda": 3, "alpha": 0.1},
    #    {"lambda": 4, "alpha": 0.001}, {"lambda": 4, "alpha": 0.01}, {"lambda": 4, "alpha": 0.1}]
    paramList = []
    for i in modelParams:
        if paramList:
            # The parameter list already has some dictionaries in it. Therefore, create every combination of the
            # dictionaries in the list with the dictionaries made from the values in the modelParams[i] list.
            paramList = [Utilities.merge_dictionaries.main(k, {i: j}) for j in modelParams[i] for k in paramList]
        else:
            # If this is the first parameter, then take this entry of the modelParams dict and split it into a list
            # containing one dict for each list element.
            paramList = [{i: j} for j in modelParams[i]]

    # Perform the model training.
    if foldsToUse < 2:
        # Train on the entire dataset and predict on the test observations.
        for params in paramList:
            print(params)
            # Create the model.
            model = modelChoices[modelToUse]["Model"](**params)

            # Train the model.
            model.fit(trainingDataMatrix, targetVector)
    else:
        # Train using cross validation. With two folds this is equivalent to hold out testing.
        pass