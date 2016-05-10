"""Test the partition of datasets.

To run this unittest run the command "python -m unittest Test.test_partition_dataset" from the Code directory.

"""

# Python imports.
import unittest

# 3rd party imports.
import numpy as np

# User imports.
import Utilities.partition_dataset


class CompletionTest(unittest.TestCase):
    """Test whether the permuting successfully completes."""

    def test_simple(self):
        for i in range(2, 11):
            dataset = np.empty((100 * i, 100 * i))
            targetArray = np.random.randint(i, size=100 * i)
            dataset[:, -1] = targetArray
            targetClasses = np.unique(targetArray)


            for j in range(2, 11):
                partition = Utilities.partition_dataset.main(dataset, -1, numPartitions=j, isStratified=False)
                self.assertEqual(np.unique(partition).tolist(), list(range(j)))
                partition = Utilities.partition_dataset.main(dataset, -1, numPartitions=j, isStratified=True)
                self.assertEqual(np.unique(partition).tolist(), list(range(j)))

                # Ensure that the difference in the number of examples in each partition is within the
                # expected bounds, i.e. that the partition with the most examples has no more than K examples more
                # than the partition with the least, where K is the number of classes.
                examplesInEachPartition = []
                for k in range(j):
                    examplesInEachPartition.append(sum(partition == k))
                self.assertTrue((max(examplesInEachPartition) - min(examplesInEachPartition)) <= targetClasses.shape[0])

                # Ensure that the number of examples of each class in the original Y array is the same
                # as the sum of the number in each partition.
                for k in targetClasses:
                    numObservationsOfClass = sum(targetArray == k)
                    partitionsClassIn = np.unique(partition[targetArray == k])
                    numInEachPartition = {i: sum(partition[targetArray == k] == i) for i in partitionsClassIn}
                    totalExamplesPartitioned = sum([numInEachPartition[i] for i in numInEachPartition])
                    self.assertEqual(numObservationsOfClass, totalExamplesPartitioned)