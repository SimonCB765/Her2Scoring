"""Partition a dataset."""

# Python imports.
import numbers
import random
import sys

# 3rd party imports.
import numpy as np


def main(dataset, target, numPartitions=1, isStratified=False):
    """Partition a dataset into CV folds.

    :param dataset:
    :type dataset:
    :param targetIndex:
    :type targetIndex:
    :param numPartitions:
    :type numPartitions:
    :param isStratified:
    :type isStratified:
    :return :               A 1 dimensional array containing the partition to which each example in the dataset belongs.
                                Each entry records the partition (from 0..numPartitions-1) that the example
                                belongs to.
    :rtype :                numpy array

    """

    # Perform the partitioning.
    if isStratified:
        # Used stratified partitioning.

        # Determine the target vector.
        if isinstance(target, numbers.Integral):
            # If the target provided is an integer, then treat it as the index of the column containing the targets.
            target = dataset[:, target]

        # Create the array to hold the partition.
        partition = np.empty(dataset.shape[0])
        partition.fill(np.nan)

        # Determine the different classes in the dataset.
        differentClasses = np.unique(target)

        # Perform the partitioning.
        for i in differentClasses:
            # Determine the indices of the examples in this class.
            classExampleIndices = np.nonzero(target == i)[0]

            # Partition the examples in this class.
            for i in range(numPartitions):
                # For each class, assign a roughly equal subset of the examples to each partition.
                indicesInThisPartition = classExampleIndices[i::numPartitions]
                partition[indicesInThisPartition] = i
    else:
        # Do not stratify the partitions.
        # Create random partitions where each partition has an (almost) equal number of examples.

        # Create the array to hold the partition.
        partition = np.empty(dataset.shape[0])
        partition.fill(np.nan)

        # Create a permuted list of the indices of the examples in the dataset.
        exampleIndices = np.random.permutation(dataset.shape[0])

        if numPartitions < 2:
            # If no partitioning is requested, then stick every example in the same partition.
            partition.fill(0)
        else:
            # Partition the dataset.
            for i in range(numPartitions):
                # For each partition, select a roughly equal subset of the examples.
                # These examples will then belong to partition i.
                indicesInThisPartition = exampleIndices[i::numPartitions]
                partition[indicesInThisPartition] = i

    return partition