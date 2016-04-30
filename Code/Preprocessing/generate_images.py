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
    # Assume you have an entry of "#_her2" : [(X, Y), D], and that the total dimensions (width, height) of the layer
    # 0 (highest resolution) image in the WSI pyramid for image #_her2 is 1000x1000. The direction of the crop is
    # determined by the value of D, which in turn dictates whether (X, Y) is used to calculate the start or end
    # position of the crop.
    # If D == 0, then 1000*X is taken to be the X coordinate (in the level 0 image) of the start point of the crop,
    # and 1000*Y the Y coordinate of the start point. The crop will therefore go from (1000*X, 1000*Y) to the
    # bottom right hand corner (1000, 1000) of the image.
    # If D == 1, then 1000*X is taken to be the X coordinate (in the level 0 image) of the end point of the crop,
    # and 1000*Y the Y coordinate of the end point. The crop with therefore go from the top left hand corner (0, 0)
    # of the image to (1000*X, 1000*Y).
    # All cropping is actually done in the specified level, so if the RAW_CROP_LEVEL == L and level L has dimensions
    # 200x200 (so is a 5x downsample of the layer 0 image), then the created image when D == 0 will go from
    # (200*X, 200*Y) to (200, 200) (and from (0, 0) to (200*X, 200*Y) when D == 1).

    "1_her2": [(0, 0), 0],  # The crop is the same as the full image as there is no control to remove from the image.
    "4_her2": [(0.5, 0), 0],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    #"6_her2": [(0.5, 0), 0],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    "6_her2": [(0.8, 0), 0],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    #"9_her2": [(0.5, 0), 0],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    "9_her2": [(0.7, 0), 0],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    #"11_her2": [(0.5, 0), 0],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    "11_her2": [(0.8, 0), 0],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    #"12_her2": [(0.5, 0), 0],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    "12_her2": [(0.8, 0), 0],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    #"13_her2": [(0.5, 0), 0],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    "13_her2": [(0.8, 0), 0],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    #"14_her2": [(0.5, 0), 0],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    "14_her2": [(0.8, 0), 0],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    "15_her2": [(0.5, 0), 0],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    #"16_her2": [(0.5, 0), 0],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    "16_her2": [(0.8, 0), 0],  # Start in the middle of the top edge; end in the bottom right corner (remove the LHS).
    #"18_her2": [(0.5, 1), 1],  # Start in the top left corner and end in the middle of the bottom edge (remove the RHS).
    "18_her2": [(0.3, 1), 1],  # Start in the top left corner and end in the middle of the bottom edge (remove the RHS).
    "19_her2": [(0.4, 0), 0],
    "22_her2": [(0.6, 1), 1],
    "24_her2": [(0.5, 0), 0],
    "25_her2": [(0.4, 1), 1],
    "26_her2": [(0.9, 1), 1],
    "27_her2": [(0.4, 1), 1],
    "29_her2": [(0.4, 1), 1],
    "30_her2": [(0.4, 1), 1],
    "32_her2": [(0.5, 1), 1],
    "33_her2": [(0.5, 1), 1],
    "34_her2": [(0.5, 0), 0],
    "35_her2": [(0.3, 0), 0],
    "36_her2": [(0.5, 1), 1],
    "38_her2": [(0.5, 1), 1],
    "39_her2": [(0.5, 0), 0],
    "40_her2": [(0.5, 1), 1],
    "46_her2": [(0.7, 1), 1],
    "47_her2": [(0.5, 0), 0],
    "48_her2": [(0.5, 0), 0],
    "49_her2": [(0.5, 1), 1],
    "50_her2": [(0.4, 0), 0],
    "52_her2": [(0.5, 0), 0],
    "55_her2": [(0.5, 0), 0],
    "57_her2": [(0.4, 0), 0],
    "58_her2": [(0.4, 0), 0],
    "61_her2": [(0.4, 0), 0],
    "63_her2": [(0.5, 1), 1],
    "65_her2": [(0, 0), 0],
    "66_her2": [(0.5, 0), 0],
    "67_her2": [(0.5, 0), 0],
    "68_her2": [(0.8, 1), 1],
    "70_her2": [(0.5, 1), 1],
    "73_her2": [(0.6, 1), 1],
    "74_her2": [(0.5, 0), 0],
    "79_her2": [(0.5, 0), 0],
    "82_her2": [(0.5, 0), 0],
    "83_her2": [(0.5, 1), 1],
    "84_her2": [(0.5, 0), 0],
    "86_her2": [(0.5, 0), 0],
    "87_her2": [(0.5, 1), 1],
    "88_her2": [(0.5, 1), 1]
}


def main(arguments):
    """

    :param arguments:   The preprocessing arguments in JSON format.
    :type arguments:    JSON object

    """

    dirInputImages = arguments["Preprocessing"]["RawImageLocation"]
    dirOutputImages = arguments["Preprocessing"]["RawThumbnailImageLocation"]

    for i in os.listdir(dirInputImages):
        nameOfFile = i.split('.')[0].lower()  # Strip off the file extension.
        fileRawImage = "{0:s}/{1:s}".format(dirInputImages, i)
        fileThumbnail = "{0:s}/{1:s}.png".format(dirOutputImages, nameOfFile)

        # Generate a thumbnail of the file.
        slide = openslide.OpenSlide(fileRawImage)
        thumbnail = slide.get_thumbnail((1000, 1000))
        thumbnail.save(fileThumbnail)

        print(nameOfFile)

        if nameOfFile in RAW_CROP_START_LOCS:
            # If the file is an IHC slide, then generate a cropped thumbnail of it. The cropping is based
            # on visual inspection.

            # Cropping arguments are the (x, y) in the level 0 slide, the level you want the crop from and the
            # (width, height) in the DESIRED LEVEL.
            fileThumbnailCrop = "{0:s}/{1:s}_crop.png".format(dirOutputImages, nameOfFile)
            cropParams = RAW_CROP_START_LOCS[nameOfFile]
            fullSlideDimensions = slide.level_dimensions[0]
            desiredSlideDimensions = slide.level_dimensions[RAW_CROP_LEVEL]
            if cropParams[1] == 0:
                # The cropping starts in the middle of the slide and goes all the way to the right hand side.
                cropStart = (cropParams[0][0] * fullSlideDimensions[0], cropParams[0][1] * fullSlideDimensions[1])
                cropStart = [int(i) for i in cropStart]
                cropDimensions = (desiredSlideDimensions[0] - (cropParams[0][0] * desiredSlideDimensions[0]),
                                  desiredSlideDimensions[1] - (cropParams[0][1] * desiredSlideDimensions[1]))
            else:
                # The cropping starts on the left hand side of the slide and ens somewhere in the middle.
                cropStart = (0, 0)
                cropDimensions = (cropParams[0][0] * desiredSlideDimensions[0],
                                  cropParams[0][1] * desiredSlideDimensions[1])
            cropDimensions = [int(i) for i in cropDimensions]
            rawCrop = slide.read_region(cropStart, RAW_CROP_LEVEL, cropDimensions)
            rawCrop.save(fileThumbnailCrop)
