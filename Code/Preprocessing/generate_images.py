"""Code to process the full WSI image pyramid into usable images."""

# Python imports.
import json
import os

# 3rd party imports.
from matplotlib import pyplot as plt
import numpy as np
import openslide
import PIL.Image
import PIL.ImageOps

# User imports.
from . import create_image_mask


def main(arguments):
    """

    :param arguments:   The preprocessing arguments in JSON format.
    :type arguments:    JSON object

    """

    # Parse parameters and set up result directories.
    dirInputImages = arguments["RawImageLocation"]
    dirOutputImages = arguments["CleanedImageLocation"]
    dirColorImages = dirOutputImages + "/Color"
    dirColorThumbnails = dirColorImages + "/Thumbnails"
    try:
        os.makedirs(dirColorThumbnails)
    except FileExistsError:
        # Directory already exists.
        pass
    dirColorCrops = dirColorImages + "/CroppedImages"
    try:
        os.makedirs(dirColorCrops)
    except FileExistsError:
        # Directory already exists.
        pass
    dirGreyImages = dirOutputImages + "/Greyscale"
    dirGreyThumbnails = dirGreyImages + "/Thumbnails"
    try:
        os.makedirs(dirGreyThumbnails)
    except FileExistsError:
        # Directory already exists.
        pass
    dirGreyCrops = dirGreyImages + "/CroppedImages"
    try:
        os.makedirs(dirGreyCrops)
    except FileExistsError:
        # Directory already exists.
        pass
    dirGreyInvertedCrops = dirGreyImages + "/InvertedCroppedImages"
    try:
        os.makedirs(dirGreyInvertedCrops)
    except FileExistsError:
        # Directory already exists.
        pass
    fileCropParameters = arguments["CropParameters"]  # The location containing the parameters for cropping each image.
    rawCropLevel = arguments["RawCropLevel"]  # The resolution level at which you want to perform the cropping.

    # Load crop parameters.
    fidCropParams = open(fileCropParameters, 'r')
    cropParameters = json.load(fidCropParams)
    fidCropParams.close()

    # Process images.
    for i in os.listdir(dirInputImages):
        # Determine the file being processed, and where to save the processed images.
        nameOfFile = i.split('.')[0].lower()  # Strip off the file extension.
        fileRawImage = "{0:s}/{1:s}".format(dirInputImages, i)  # Location of the raw WSI.
        fileColorThumbnail = "{0:s}/{1:s}.png".format(dirColorThumbnails, nameOfFile)  # Loc to save the color thumbnail.
        fileGreyThumbnail = "{0:s}/{1:s}.png".format(dirGreyThumbnails, nameOfFile)  # Loc to save the greyscale thumbnail.

        # Display status message.
        print("Now processing image {0:s}".format(nameOfFile))

        # Generate a thumbnail of the file. The thumbnail returned by get_thumbnail is RGB.
        slide = openslide.OpenSlide(fileRawImage)
        thumbnailColor = slide.get_thumbnail((1000, 1000))
        thumbnailColor.save(fileColorThumbnail)
        thumbnailGrey = thumbnailColor.convert(mode='L')
        thumbnailGrey.save(fileGreyThumbnail)

        if nameOfFile in cropParameters:
            # If the file is an IHC slide, then generate a cropped thumbnail of it. The cropping is based
            # on visual inspection.
            fileColorCrop = "{0:s}/{1:s}_crop.png".format(dirColorCrops, nameOfFile)  # Loc to save color crop.
            fileGreyCrop = "{0:s}/{1:s}_crop.png".format(dirGreyCrops, nameOfFile)  # Loc to save greyscale crop.
            fileGreyCropInverse = "{0:s}/{1:s}_inverted_crop.png".format(
                dirGreyInvertedCrops, nameOfFile)  # Loc to save inverted color greyscale crop.
            cropParams = cropParameters[nameOfFile]  # Locations defining the cropped area.
            fullSlideDimensions = slide.level_dimensions[0]  # Dimensions of the level 0 image.
            desiredSlideDimensions = slide.level_dimensions[rawCropLevel]  # Dimensions of the desired level image.

            # Determine the pixel in the full size level 0 image where the crop should start.
            fullCropStart = (cropParams["CropCoordinates"]["Start"]["X"] * fullSlideDimensions[0],
                             cropParams["CropCoordinates"]["Start"]["Y"] * fullSlideDimensions[1])
            fullCropStart = [int(i) for i in fullCropStart]

            # Determine the pixel in the desired level image where the crop should start and end.
            desiredCropStart = (cropParams["CropCoordinates"]["Start"]["X"] * desiredSlideDimensions[0],
                                cropParams["CropCoordinates"]["Start"]["Y"] * desiredSlideDimensions[1])
            desiredCropEnd = (cropParams["CropCoordinates"]["End"]["X"] * desiredSlideDimensions[0],
                              cropParams["CropCoordinates"]["End"]["Y"] * desiredSlideDimensions[1])

            # Determine the dimensions of the crop in the desired level image.
            cropDimensions = (desiredCropEnd[0] - desiredCropStart[0], desiredCropEnd[1] - desiredCropStart[1])
            cropDimensions = [int(i) for i in cropDimensions]

            # Generate the crop.
            # The starting location of the crop is relative to the level 0 image, while the dimension of the crop
            # is relative to the desired level image.
            # The read_region function returns a non-premultiplied image (only in the Python API).
            rawCropColor = slide.read_region(fullCropStart, rawCropLevel, cropDimensions)  # Cropped image.
            rawColorImageArray = np.array(rawCropColor)
            rawCropGrey = rawCropColor.convert(mode='L')  # Create the greyscale image.
            rawGreyImageArray = np.array(rawCropGrey)

            # Visualise the crop compared to the original thumbnail.
            if cropParams["Visualise"]:
                fig = plt.figure()
                axes = fig.add_subplot(1, 2, 1)
                axes.set_title("Input Image")
                plt.imshow(np.array(thumbnailGrey), cmap="Greys_r")
                axes = fig.add_subplot(1, 2, 2)
                axes.set_title("Cropped Image")
                plt.imshow(rawGreyImageArray, cmap='Greys_r')
                plt.show()

            # Create the mask needed to clean up the image. Do this by identifying the regions in the original image
            # that contain pixels of interest, and creating a boolean mask to apply to the raw images.
            mask = create_image_mask.main(
                rawGreyImageArray, backgroundThreshold=cropParams["BackgroundThreshold"],
                maxFilterSize=cropParams["MaxFilter"], objectsToUse=cropParams["ObjectsToKeep"],
                visualise=cropParams["Visualise"])

            # Create the cleaned images.
            rawColorImageArray[:, :, -1] *= mask  # Set alpha to invisible to hide the background.
            rawGreyImageArray *= mask
            rawGreyImageArray[rawGreyImageArray == 0] = 255  # Set all pixels that aren't of interest to white.

            # Process the cleaned images to remove all rows and columns containing only background pixels.
            # This will shrink the final size of the image.
            backgroundRows = np.all(mask == False, axis=1)
            backgroundCols = np.all(mask == False, axis=0)
            rawColorImageArray = rawColorImageArray[~backgroundRows, :][:, ~backgroundCols]
            rawGreyImageArray = rawGreyImageArray[~backgroundRows, :][:, ~backgroundCols]

            # Save the images.
            cleanCropColor = PIL.Image.fromarray(rawColorImageArray)
            cleanCropColor.save(fileColorCrop)
            cleanCropGrey = PIL.Image.fromarray(rawGreyImageArray)
            cleanCropGrey = cleanCropGrey.convert(mode='L')
            cleanCropGrey.save(fileGreyCrop)
            cleanCropGreyInverse = PIL.ImageOps.invert(cleanCropGrey)
            cleanCropGreyInverse.save(fileGreyCropInverse)
