"""Code to create a permuted image through affine transformations."""

# Python imports.
import random

# 3rd party imports.
import numpy as np
import scipy.ndimage

# Testing imports.
from matplotlib import pyplot as plt


def main(fileImage, maxRotation=0, maxShear=(0,), maxTranslation=(0,), maxScale=(1,), scaleUpProb=(0.5,),
         jointScale=False, inversionProb=(0.0,), backgroundColor=255):
    """

    Transformations are treated as symmetric. A maximum rotation of 45 degrees is therefore a maximum rotation
    of 45 degrees clockwise and 45 degrees counterclockwise, thereby giving you a maximum total rotation of 90 degrees.

    sacle up prob is the probability of scaling up compared to scaling down

    we would need to center the image at (0, 0) first. However, at present
    # doing this causes the image to clip, and so the full transformation is done in non-clipping steps.

    joint scaling will cause the x axis scalingto be calcualted and then used for both axes (any entry in the maxScale
    list/tuple except the first will be ignroed)

    Perform operations sequentially in order to gain the desired control over the output.

    """

    # Load the image and determine its size.
    imageArray = scipy.ndimage.imread(fileImage)

    # Create the scaling factors.
    # The difficulty with this is ensuring that the probability of scaling up and down is similar.
    # For example, if maxXScale == 5, then the probability of getting a scale value in (1, 5] is far greater
    # than the probability of getting a value in the range [0, 1). As the maximum scale factor gets bigger, it
    # only becomes more likely that scaling up will occur. Avoid this by uncoupling the scaling factor choice from
    # the direction of scaling.
    maxXScale = maxScale[0]
    maxYScale = maxScale[1] if len(maxScale) > 1 else maxScale[0]
    scaleX = 1
    scaleY = 1
    if maxXScale > 1:
        scaleX = random.uniform(1, maxXScale)
        scaleXDown = random.random() < scaleUpProb[0]
        scaleX = (1. / scaleX) if scaleXDown else scaleX
    if maxYScale > 1:
        if jointScale:
            # Scale the Y axis the same as the X axis.
            scaleY = scaleX
        else:
            # Potentially scale the axes differently.
            scaleY = random.uniform(1, maxYScale)
            scaleYDown = random.random() < (scaleUpProb[1] if len(scaleUpProb) > 1 else scaleUpProb[0])
            scaleY = (1. / scaleY) if scaleYDown else scaleY

    # Calculate the degree of rotation.
    degreeRotation = random.uniform(0, maxRotation * 2) - maxRotation

    # Create the shear matrix.
    shearMatrix = np.identity(2)
    maxXShear = maxShear[0]
    maxYShear = maxShear[1] if len(maxShear) > 1 else maxShear[0]
    degreeShearX = random.uniform(0, maxXShear * 2) - maxXShear
    degreeShearY = random.uniform(0, maxYShear * 2) - maxYShear
    radianShearX = np.deg2rad(degreeShearX)
    radianShearY = np.deg2rad(degreeShearY)
    shearMatrix[0, 1] = np.tan(radianShearY)
    shearMatrix[1, 0] = np.tan(radianShearX)

    # Create the translation.
    maxXTranslation = maxTranslation[0]
    maxYTranslation = maxTranslation[1] if len(maxTranslation) > 1 else maxTranslation[0]
    translationX = random.randint(0, maxXTranslation)
    translationY = random.randint(0, maxYTranslation)

    # Determine whether to invert the axes.
    xInversionProb = inversionProb[0]
    yInversionProb = inversionProb[1] if len(inversionProb) > 1 else inversionProb[0]
    isXInverted = random.random() < xInversionProb
    isYInverted = random.random() < yInversionProb

    # Create the transformed image.
    transformedImage = np.empty(imageArray.shape)  # Create the correctly sized transformed image.
    transformedImage.fill(backgroundColor)  # Fill the transformed image with only background.

    # Scale the image. The goal is to 'zoom' in or out of the image while keeping the array the same size.
    # This works by first zooming, and then placing the portion of the zoomed image desired into a correctly sized
    # (and possibly padded) array.
    # For example, if the zoom factor is 2, then the result of scipy.ndimage.zoom will be an array that is twice
    # the desired size. In order to resize this, the central portion of the zoomed array is taken and placed into
    # the transformed array. If the zoom factor was a fraction, then the entire zoomed image would be placed into
    # the transformed array with background padding around it.
    zoomedImage = scipy.ndimage.zoom(imageArray, [scaleY, scaleX], cval=backgroundColor)  # Zoom.
    transSlice = {'X': [0, transformedImage.shape[1]],
                  'Y': [0, transformedImage.shape[0]]}  # Slice of the transformed image where the zoom will be placed.
    zoomSlice = {'X': [0, zoomedImage.shape[1]],
                 'Y': [0, zoomedImage.shape[0]]}  # Slice of the zoomed image to copy into the transformed image.
    pixelDifference = [abs(i - j) for i, j in zip(imageArray.shape, zoomedImage.shape)]  # Image size difference.
    if scaleX < 1:
        # The zoomed image is smaller along the X axis than it should be. Take the zoomed image and center it along
        # the transformed image's X axis.
        transSlice['X'][0] = int(np.floor(pixelDifference[1] / 2))
        transSlice['X'][1] = transSlice['X'][0] + zoomedImage.shape[1]
    elif scaleX > 1:
        # The zoomed image is larger along the X axis than it should be. Take the zoomed image and remove some of
        # the left and right columns of pixels.
        zoomSlice['X'][0] = int(np.floor(pixelDifference[1] / 2))
        zoomSlice['X'][1] = zoomSlice['X'][0] + transformedImage.shape[1]
    if scaleY < 1:
        # The zoomed image is smaller along the Y axis than it should be. Take the zoomed image and center it along
        # the transformed image's Y axis.
        transSlice['Y'][0] = int(np.floor(pixelDifference[0] / 2))
        transSlice['Y'][1] = transSlice['Y'][0] + zoomedImage.shape[0]
    elif scaleY > 1:
        # The zoomed image is larger along the Y axis than it should be. Take the zoomed image and remove some of
        # the top and bottom of pixels.
        zoomSlice['Y'][0] = int(np.floor(pixelDifference[0] / 2))
        zoomSlice['Y'][1] = zoomSlice['Y'][0] + transformedImage.shape[0]
    transformedImage[transSlice['Y'][0]:transSlice['Y'][1], transSlice['X'][0]:transSlice['X'][1]] = \
        zoomedImage[zoomSlice['Y'][0]:zoomSlice['Y'][1], zoomSlice['X'][0]:zoomSlice['X'][1]]

    # Rotate the image. This must be done with ndimage.rotate rather than ndimage.affine_transform as we want to rotate
    # around the center of the image. If we used affine_transform, then the rotation would be performed around (0, 0).
    # This could be countered by setting the center of the image to (0, 0), but then the rotation clips the image.
    transformedImage = scipy.ndimage.rotate(transformedImage, degreeRotation, cval=backgroundColor)

    # Shear the image. This can be done with affine_transform as we don't need it to occur at the center of the image.
    transformedImage = scipy.ndimage.affine_transform(transformedImage, shearMatrix, cval=backgroundColor)

    # Crop out any excess rows and columns that consist only of background pixels.
    backgroundRows = np.all(transformedImage == backgroundColor, axis=1)
    backgroundCols = np.all(transformedImage == backgroundColor, axis=0)
    transformedImage = transformedImage[~backgroundRows, :][:, ~backgroundCols]

    # Invert the image.
    if isXInverted:
        transformedImage = np.fliplr(transformedImage)
    if isYInverted:
        transformedImage = np.flipud(transformedImage)

    # Translate the image.
    transformedImage = scipy.ndimage.shift(transformedImage, [translationX, translationY], cval=backgroundColor)

    print("Translation : ", translationX, translationY)
    print("Inverserion : ", isXInverted, isYInverted)
    print("Shear : ", degreeShearX, degreeShearY)
    print("Scaled : ", scaleX, scaleY)
    print("Rotation", degreeRotation)
    plt.imshow(transformedImage, cmap="Greys_r")
    plt.show()

    return transformedImage
