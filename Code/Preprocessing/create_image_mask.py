"""Function to generate a mask that selects only those pixels in regions of interest."""

# 3rd party imports.
from matplotlib import pyplot as plt
import numpy as np
import scipy.ndimage
import skimage.morphology


def main(imageArray, backgroundThreshold=255, maxFilterSize=5, objectsToUse=(1,), visualise=False):
    """Select pixels in regions of interest of a greyscale image.

    This function assumes that the image is dark regions of interest on a light background. In order
    to use it with a light on dark image, simply invert the image before calling.


    visualise is used to check on the developing mask so that you can choose which chunks you should use

    object 0 is always the backgournd, so unless you want that in it do not put 0 in objectsToUse
    objects to use is done by size, so 1 means keep the biggest object, 2 the 2nd biggest etc.

    returns a image mask with True values for the pixels in regions of interest and False values everywhere else

    """

    # First convert the greyscale image to a binary image by thresholding the image based on pixel value.
    # This will convert the image to white pixels on a black background.
    binaryImageArray = imageArray < backgroundThreshold

    # Next, run a max filter over the image to perform a dilation and 'grow' the white regions of non-background
    # pixels. This is not needed, but will make the segmenter have an easier time locating large regions of interest.
    # If the regions of interest have few 'holes' in them, then a small max filter can be used. For images where the
    # regions have large 'holes' a larger filter is needed.
    dilatedImageArray = scipy.ndimage.maximum_filter(binaryImageArray, size=maxFilterSize, mode="constant", cval=0)

    # Label all 'objects' in the image in order to segment it. The labeled image is the same size as the input image,
    # but each pixel belonging to an object is numbered with the numeric value given to that object.
    # Use a full 8 neighbour neighbourhood to determine whether pixels belong to the same object.
    labeledObjectArray = skimage.morphology.label(dilatedImageArray, background=0, connectivity=None)

    # Next get the actual integers used to label the objects, and the number of pixels in the corresponding object.
    labels, labelCounts = np.unique(labeledObjectArray, return_counts=True)

    # Determine the ordering of objects in terms of the number of pixels in them. Use descending order.
    objectsSortedByPixels = labels[labelCounts.argsort()[::-1]]

    # Create the mask used to select only the regions of interest.
    mask = np.zeros(imageArray.shape, dtype="bool")
    for i in objectsToUse:
        mask += labeledObjectArray == objectsSortedByPixels[i]

        if visualise:
            # Visualise the mask as it develops.
            fig = plt.figure()
            axes = fig.add_subplot(1, 2, 1)
            axes.set_title("Input Image")
            plt.imshow(imageArray, cmap="Greys_r")
            axes = fig.add_subplot(1, 2, 2)
            axes.set_title("Mask For Object {0:d}".format(i))
            plt.imshow(labeledObjectArray == objectsSortedByPixels[i], cmap='Greys_r')
            plt.show()

    # Remove the portions of the mask that are only present due to the dilation.
    mask &= binaryImageArray

    # View the final image containing only the selected regions of interest.
    if visualise:
        finalImage = imageArray * mask
        finalImage[finalImage == 0] = 255
        fig = plt.figure()
        axes = fig.add_subplot(1, 3, 1)
        axes.set_title("Input Image")
        plt.imshow(imageArray, cmap="Greys_r")
        axes = fig.add_subplot(1, 3, 2)
        axes.set_title("Final Mask")
        plt.imshow(mask, cmap='Greys_r')
        axes = fig.add_subplot(1, 3, 3)
        axes.set_title("Final Image")
        plt.imshow(finalImage, cmap='Greys_r')
        plt.show()

    return mask
