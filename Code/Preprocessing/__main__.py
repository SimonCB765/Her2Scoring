"""File to initiate the running of the image preprocessing."""

# Python imports.
import json
import os
import sys

# User imports.
import Utilities.json_to_ascii

# Globals
PYVERSION = sys.version_info[0]  # Determine major version number.


# Get the openslide bin directory.
fileParams = sys.argv[1]
readParams = open(fileParams, 'r')
parsedArgs = json.load(readParams)
if PYVERSION == 2:
    parsedArgs = Utilities.json_to_ascii(parsedArgs)  # Convert unicode characters to ascii (needed for Python < 3).
readParams.close()

# Run the preprocessing.
# OpenSlide depends on DLLs in the OpenSlide bin directory. Loading these in a relative manner (as OpenSlide does)
# relies on the DLLs being either on the path of the working directory, or in system defined locations.
# You can't add paths to be looked in from outside OpenSlide. In order to circumvent this, temporarily swap to
# the bin directory of OpenSlide when it's imported and then swap back to the directory that the program was
# called from.
currentDir = os.getcwd()
os.chdir(parsedArgs["Preprocessing"]["OpenSlideBinLocation"])
import Preprocessing.generate_images  # Have to import this after the OpenSlide bin directory is added to the path.
os.chdir(currentDir)
Preprocessing.generate_images.main(parsedArgs)