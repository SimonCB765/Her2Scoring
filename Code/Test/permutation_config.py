"""Config file for the image permutation unit tests."""

# Python imports.
import os


# Determine the directory containing the test images.
dirConfigFile = os.path.dirname(os.path.realpath(__file__))  # Get the directory containing this config file.
dirPermutation = "PermutationTestImages"  # Name of he directory containing the test images.
dirImages = os.path.join(dirConfigFile, dirPermutation)

completionNoPermute = {
    "Test1": {
        "ImageLocation": os.path.join(dirImages, "Test1.png"), "MaxRotation": 0, "MaxShear": (0,),
        "MaxTranslation": (0,), "MaxScale": (0,), "ScaleUpProb": (0.5,), "JointScale": True, "InversionProb": (0.0,)
    },
    "Test2": {
        "ImageLocation": os.path.join(dirImages, "Test2.png"), "MaxRotation": 0, "MaxShear": (0,),
        "MaxTranslation": (0,), "MaxScale": (0,), "ScaleUpProb": (0.5,), "JointScale": True,  "InversionProb": (0.0,)
    }
}