# Parameter Files #

## Preprocessing ##

The parameters for running the processing of the training and testing data are defined in a set of external JSON files.
They should consist of one JSON object with the following named entries:

- RawImageLocation - The directory containing the raw WSI files to process.
- CleanedImageLocation - The directory where the processed images crops should be saved.
- OpenSlideBinLocation - The OpenSlide bin directory. 
- RawCropLevel - The level of the WSI that should be used to produce the cleaned image. Level 0 is the highest resolution image.
- CropParameters - The parameters needed to crop each image.

The directory structure created at CleanedImageLocation is as follows:

    CleanedImageLocation/
     +---Color
     |    +---CroppedImages
     |    \---Thumbnails
     \---Greyscale
          +---CroppedImages
          +---InvertedCroppedImages
          \---Thumbnails

CroppedImages directories contain the cleaned and cropped images using the desired level.  
InvertedCroppedImages directories contain the cropped images with their colors inverted.  
Thumbnails directories contain thumbnails of the entire level 0 WSI.

For each image in RawImageLocation that you want cropped there needs to be an entry in the CropParameters object.  
For example, if you want to crop the images WSI_0, WSI_1 and WSI_2 in RawImageLocation (potentially ignoring
other images in the directory), you would need to set up the crop parameters as:

    "WSI_0" : {},
    "WSI_1" : {},
    "WSI_2" : {}

The actual JSON object for an image you want to crop (say image WSI_0), should be as follows:

    "WSI_0" : {
      "BackgroundThreshold" : 220,
      "CropCoordinates" : {"Start" : {"X" : 0.0, "Y" : 0.0}, "End" : {"X" : 1.0, "Y" : 1.0}},
      "MaxFilter" : 9,
      "ObjectsToKeep" : [0, 1, 2, 3, 4, 5],
      "Visualise" : true
    }

Values for these parameters should be as follows:

- BackgroundThreshold - The pixel value at which the background is deemed to start. All pixels with at least this value
will be treated as background pixels and assigned the same value (255).
- CropCoordinates - Fractional coordinates for the section of te desired level image to crop out. The "Left" object
defines the X and Y coordinates for the top left corner of the cropped image, while the "Right" object defines the
X and Y coordinates for the bottom right corner of the cropped image. All coordinates should be supplied as a
value between 0 and 1. These are not absolute pixel values, but rather give the fraction of the X/Y dimension at which
the cropping should begin/end.
- MaxFilter - The size in pixels of the max filter to run over the image prior to segmentation.
- ObjectsToKeep - Following segmentation, identified objects are ordered based on the number of pixels making up the
object. This parameter dictates which objects are kept in the cleaned image. Any object not in this list will be
treated as background and removed from the cleaned image. Object 0 is always the background in the original
binary thresholded image, so this list should start with 1 if the background is to be uniform. As an example, a list
of [1, 2, 3, 4] will keep the 4 largest objects (by pixel number) in the cleaned image, and will remove all other
objects by setting their pixels to be the background color (255).
- Visualise - Whether intermediate images in the cleaning process should be generated. This can be useful to determine
whether the cropping parameters are working as desired.