"""File to initiate the running of the cell percentage prediction."""

# Python imports.
import json
import sys

# User imports.
import HistogramPrediction.histogram_predictions
import Utilities.json_to_ascii

# Globals
PYVERSION = sys.version_info[0]  # Determine major version number.


fileParams = sys.argv[1]
readParams = open(fileParams, 'r')
parsedArgs = json.load(readParams)
if PYVERSION < 3:
    # Convert unicode characters to ascii (needed for Python < 3).
    parsedArgs = Utilities.json_to_ascii.json_to_ascii(parsedArgs)
readParams.close()

HistogramPrediction.histogram_predictions.main(parsedArgs)
