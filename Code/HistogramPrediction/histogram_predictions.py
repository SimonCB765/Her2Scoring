"""Predicts the Her2 score from a histogram of pixel intensities."""

# Python imports.
import os
import sys

# 3rd party imports.
import numpy as np
import scipy.ndimage


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
    backgroundColor = arguments["BackgroundColor"]

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

    # Determine the mask for removing the background pixel color.
    backgroundMask = np.array([(False if i == backgroundColor else True) for i in range(256)])

    # Initalise the matrix that will hold the histogram data.
    # There will be one row per image and 258 columns (one for each of the non-background pixel values plus one
    # for the case number, one for the Her2 score and one for the percentage of stained cells).
    dataMatrix = np.empty((len(os.listdir(dirImages)), 258))

    # Generate the matrix of histogram feature vectors.
    for ind, i in enumerate(os.listdir(dirImages)):
        # Read in the file.
        filePath = "{0:s}/{1:s}".format(dirImages, i)
        image = scipy.ndimage.imread(filePath)

        # Generate the histogram. One bin per color value.
        histogram = scipy.ndimage.histogram(image, 0, 255, 256)

        # Strip out the background color.
        histogram = histogram[backgroundMask]

        # Convert histogram to relative values.
        histogram = histogram / histogram.sum()

        # Determine the number case identifier for the image.
        caseID = int(i.split('_')[0])

        # Create the feature vector.
        caseGroundTruth = groundTruth[:, groundTruth[0, :] == caseID]  # The ground truth values for this image.
        featureVector = np.empty(258)
        featureVector[0] = caseID
        featureVector[1] = caseGroundTruth[1]
        featureVector[2] = caseGroundTruth[2]
        featureVector[3:] = histogram

        # Add the feature vector to the data matrix.
        dataMatrix[ind, :] = featureVector