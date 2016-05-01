"""Code to process the full WSI image pyramid into usable images."""

# Python imports.
import os

# 3rd party imports.
import openslide

# Globals.
RAW_CROP_LEVEL = 4  # The resolution level at which you want to perform the cropping (lower = greater resolution).
RAW_CROP_START_LOCS = {
    # Fractional coordinates for the cropping of the raw WSI files, and the direction (left or right hand side) from
    # which the coordinates should be calculated.
    # Assume you have an entry of "#_her2" : [(X1, Y1), (X2, Y2)], and that the total dimensions (width, height) of
    # the layer 0 (highest resolution) image in the WSI pyramid for image #_her2 is 1000x1000. The cropped area will
    # then be between (X1*1000, Y1*1000) and (X2*1000, Y2*1000).
    # All cropping is actually done in the specified level, so if the RAW_CROP_LEVEL == L and level L has dimensions
    # 200x200 (so is a 5x downsample of the layer 0 image), then the created image will go from
    # (X1*200, Y1*200) to (X2*200, Y2*200).

    "1_her2": [(0.0, 0.0), (1.0, 1.0)],  # The crop is the same as the full image.
    "4_her2": [(0.5, 0.0), (1.0, 1.0)],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    #"6_her2": [(0.5, 0.0), (1.0, 1.0)],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    "6_her2": [(0.8, 0.0), (1.0, 1.0)],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    #"9_her2": [(0.5, 0.0), (1.0, 1.0)],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    "9_her2": [(0.7, 0.0), (1.0, 1.0)],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    #"11_her2": [(0.5, 0.0), (1.0, 1.0)],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    "11_her2": [(0.8, 0.0), (1.0, 1.0)],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    #"12_her2": [(0.5, 0.0), (1.0, 1.0)],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    "12_her2": [(0.8, 0.0), (1.0, 1.0)],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    #"13_her2": [(0.5, 0.0), (1.0, 1.0)],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    "13_her2": [(0.8, 0.0), (1.0, 1.0)],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    #"14_her2": [(0.5, 0.0), (1.0, 1.0)],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    "14_her2": [(0.8, 0.0), (1.0, 1.0)],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    "15_her2": [(0.5, 0.0), (1.0, 1.0)],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    #"16_her2": [(0.5, 0.0), (1.0, 1.0)],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    "16_her2": [(0.8, 0.0), (1.0, 1.0)],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    #"18_her2": [(0.0, 0.0), (0.5, 1.0)],  # Start in the top left corner and end in the middle of the bottom edge (remove the RHS).
    "18_her2": [(0.0, 0.0), (0.3, 1.0)],  # Start in the top left corner and end in the middle of the bottom edge (remove the RHS).
    "19_her2": [(0.0, 0.0), (0.4, 1.0)],
    "22_her2": [(0.0, 0.0), (0.6, 1.0)],
    "24_her2": [(0.5, 0.0), (1.0, 1.0)],
    "25_her2": [(0.0, 0.0), (0.4, 1.0)],
    "26_her2": [(0.0, 0.0), (0.9, 1.0)],
    "27_her2": [(0.0, 0.0), (0.4, 1.0)],
    "29_her2": [(0.0, 0.0), (0.4, 1.0)],
    "30_her2": [(0.0, 0.0), (0.4, 1.0)],
    "32_her2": [(0.0, 0.0), (0.5, 1.0)],
    "33_her2": [(0.0, 0.0), (0.5, 1.0)],
    "34_her2": [(0.5, 0.0), (1.0, 1.0)],
    "35_her2": [(0.3, 0.0), (1.0, 1.0)],
    "36_her2": [(0.0, 0.0), (0.5, 1.0)],
    "38_her2": [(0.0, 0.0), (0.5, 1.0)],
    "39_her2": [(0.5, 0.0), (1.0, 1.0)],
    "40_her2": [(0.0, 0.0), (0.5, 1.0)],
    "46_her2": [(0.0, 0.0), (0.7, 1.0)],
    "47_her2": [(0.5, 0.0), (1.0, 1.0)],
    "48_her2": [(0.5, 0.0), (1.0, 1.0)],
    "49_her2": [(0.0, 0.0), (0.5, 1.0)],
    "50_her2": [(0.4, 0.0), (1.0, 1.0)],
    "52_her2": [(0.5, 0.0), (1.0, 1.0)],
    "55_her2": [(0.5, 0.0), (1.0, 1.0)],
    "57_her2": [(0.4, 0.0), (1.0, 1.0)],
    "58_her2": [(0.4, 0.0), (1.0, 1.0)],
    "61_her2": [(0.4, 0.0), (1.0, 1.0)],
    "63_her2": [(0.0, 0.0), (0.5, 1.0)],
    "65_her2": [(0.0, 0.0), (1.0, 1.0)],
    "66_her2": [(0.5, 0.0), (1.0, 1.0)],
    "67_her2": [(0.5, 0.0), (1.0, 1.0)],
    "68_her2": [(0.0, 0.0), (0.8, 1.0)],
    "70_her2": [(0.0, 0.0), (0.5, 1.0)],
    "73_her2": [(0.0, 0.0), (0.6, 1.0)],
    "74_her2": [(0.5, 0.0), (1.0, 1.0)],
    "79_her2": [(0.5, 0.0), (1.0, 1.0)],
    "82_her2": [(0.5, 0.0), (1.0, 1.0)],
    "83_her2": [(0.0, 0.0), (0.5, 1.0)],
    "84_her2": [(0.5, 0.0), (1.0, 1.0)],
    "86_her2": [(0.5, 0.0), (1.0, 1.0)],
    "87_her2": [(0.0, 0.0), (0.5, 1.0)],
    "88_her2": [(0.0, 0.0), (0.5, 1.0)]
}


def main(arguments):
    """

    :param arguments:   The preprocessing arguments in JSON format.
    :type arguments:    JSON object

    """

    dirInputImages = arguments["Preprocessing"]["RawImageLocation"]
    dirOutputImages = arguments["Preprocessing"]["RawThumbnailImageLocation"]
    dirColorImages = dirOutputImages + "/Color"
    try:
        os.makedirs(dirColorImages)
    except FileExistsError:
        # Directory already exists.
        pass
    dirGreyImages = dirOutputImages + "/Greyscale"
    try:
        os.makedirs(dirGreyImages)
    except FileExistsError:
        # Directory already exists.
        pass

    for i in os.listdir(dirInputImages):
        # Determine the file being processed, and where to save the processed images.
        nameOfFile = i.split('.')[0].lower()  # Strip off the file extension.
        fileRawImage = "{0:s}/{1:s}".format(dirInputImages, i)  # Location of the raw WSI.
        fileColorThumbnail = "{0:s}/{1:s}.png".format(dirColorImages, nameOfFile)  # Loc to save the color thumbnail.
        fileGreyThumbnail = "{0:s}/{1:s}.png".format(dirGreyImages, nameOfFile)  # Loc to save the greyscale thumbnail.

        # Display status message.
        print("Now processing image {0:s}".format(nameOfFile))

        # Generate a thumbnail of the file. The thumbnail returned by get_thumbnail is RGB.
        slide = openslide.OpenSlide(fileRawImage)
        thumbnailColor = slide.get_thumbnail((1000, 1000))
        thumbnailColor.save(fileColorThumbnail)
        thumbnailGrey = thumbnailColor.convert(mode='L')
        thumbnailGrey.save(fileGreyThumbnail)

        if nameOfFile in RAW_CROP_START_LOCS:
            # If the file is an IHC slide, then generate a cropped thumbnail of it. The cropping is based
            # on visual inspection.
            fileColorCrop = "{0:s}/{1:s}_crop.png".format(dirColorImages, nameOfFile)  # Loc to save color crop.
            fileGreyCrop = "{0:s}/{1:s}_crop.png".format(dirGreyImages, nameOfFile)  # Loc to save greyscale crop.
            cropParams = RAW_CROP_START_LOCS[nameOfFile]  # Locations defining the cropped area.
            fullSlideDimensions = slide.level_dimensions[0]  # Dimensions of the level 0 image.
            desiredSlideDimensions = slide.level_dimensions[RAW_CROP_LEVEL]  # Dimensions of the desired level image.

            # Determine crop start location and dimensions.
            # The starting location of the crop is relative to the level 0 image, while the dimension of the crop
            # is relative to the desired level image.
            fullCropStart = (cropParams[0][0] * fullSlideDimensions[0], cropParams[0][1] * fullSlideDimensions[1])
            fullCropStart = [int(i) for i in fullCropStart]  # Location where the crop would start in the level 0 image.
            desiredCropStart = (cropParams[0][0] * desiredSlideDimensions[0],  # Start loc in the desired level image.
                                cropParams[0][1] * desiredSlideDimensions[1])
            desiredCropEnd = (cropParams[1][0] * desiredSlideDimensions[0],  # End loc in the desired level image.
                              cropParams[1][1] * desiredSlideDimensions[1])
            cropDimensions = (desiredCropEnd[0] - desiredCropStart[0], desiredCropEnd[1] - desiredCropStart[1])
            cropDimensions = [int(i) for i in cropDimensions]  # Dimension of the crop in the desired level image.

            # Generate the crop. The read_region function returns a non-premultiplied image (only in the Python API),
            # so as we don't really care about the background to use we can just discard the alpha channel as needed.
            rawCropColor = slide.read_region(fullCropStart, RAW_CROP_LEVEL, cropDimensions)  # Cropped image.
            rawCropColor.save(fileColorCrop)
            rawCropGrey = rawCropColor.convert(mode='L')
            rawCropGrey.save(fileGreyCrop)