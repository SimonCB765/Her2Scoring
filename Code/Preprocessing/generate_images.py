# Python imports.
import os
import re

# 3rd party imports.
import openslide


def main(arguments):
    """

    :param arguments:
    :type arguments:    A loaded JSON object.

    """

    dirInputImages = arguments["Preprocessing"]["RawImageLocation"]
    dirOutputImages = arguments["Preprocessing"]["CroppedImageLocation"]

    for i in os.listdir(dirInputImages):
        nameOfFile = i.split('.')[0].lower()  # Strip off the file extension.
        fileRawImage = "{0:s}/{1:s}".format(dirInputImages, i)
        fileThumbnail = "{0:s}/{1:s}.png".format(dirOutputImages, nameOfFile)

        if re.search("her2", nameOfFile):
            # If the file is an IHC slide.
            try:
                slide = openslide.OpenSlide(fileRawImage)
                thumbnail = slide.get_thumbnail((1000, 1000))
                thumbnail.save(fileThumbnail)
            except Exception:
                print("File {0:s} could not be opened.".format(nameOfFile))