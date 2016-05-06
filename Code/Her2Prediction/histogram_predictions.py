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
    with open(fileGroundTruth, 'r') as fidGroundTruth:
        fidGroundTruth.readline()  # Strip off the header.
        for line in fidGroundTruth:
            chunks = (line.strip()).split('\t')
            caseNumbers.append(chunks[0])
            her2Scores.append(int(chunks[1]))

    print(caseNumbers)
    print(her2Scores)

    # Go through each image, generate the histogram of all pixels intensities from 0-255 and then remove
    # the intensity from the background. This is your feature vector.

    # Determine the mask for removing the background pixel color.
    backgroundMask = np.array([(False if i == backgroundColor else True) for i in range(256)])

    for i in os.listdir(dirImages):
        # Read in the file.
        filePath = "{0:s}/{1:s}".format(dirImages, i)
        image = scipy.ndimage.imread(filePath)

        # Generate the histogram. One bin per color value.
        histogram = scipy.ndimage.histogram(image, 0, 255, 256)

        # Strip out the background color.
        histogram = histogram[backgroundMask]
