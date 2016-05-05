"""Predicts the Her2 score from a histogram of pixel intensities."""

# Python imports.
import os
import sys


def main(arguments):
    """

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