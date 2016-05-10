"""Test the permuting of images.

To run this unittest run the command "python -m unittest Test.test_image_permutation" from the Code directory.

"""

# Python imports.
import unittest

# 3rd party imports.
import numpy as np

# User imports.
import Test.permutation_config
import Utilities.image_permutation


class CompletionTest(unittest.TestCase):
    """Test whether the permuting successfully completes."""

    def test_no_permute(self):
        print("Test")
        for i in Test.permutation_config.completionNoPermute:
            runParams = Test.permutation_config.completionNoPermute[i]
            image = Utilities.image_permutation.main(
                runParams["ImageLocation"], maxRotation=runParams["MaxRotation"], maxShear=runParams["MaxShear"],
                maxTranslation=runParams["MaxTranslation"], maxScale=runParams["MaxScale"],
                scaleUpProb=runParams["ScaleUpProb"],jointScale=runParams["JointScale"],
                inversionProb=runParams["InversionProb"])

