"""Code to create a permuted image through affine transformations."""

# Python imports.
import random

# 3rd party imports.
import numpy as np
import scipy.ndimage

# Testing imports.
from matplotlib import pyplot as plt


def main(fileImage, maxRotation=0, maxShear=(0,), maxTranslation=(0,), maxScale=(1,), scaleUpProb=(0.5,),
         inversionProb=(0.0,), backgroundColor=255):
    """

    Transformations are treated as symmetric. A maximum rotation of 45 degrees is therefore a maximum rotation
    of 45 degrees clockwise and 45 degrees counterclockwise, thereby giving you a maximum total rotation of 90 degrees.

    sacle up prob is the probability of scaling up compared to scaling down

    we would need to center the image at (0, 0) first. However, at present
    # doing this causes the image to clip, and so the full transformation is done in non-clipping steps.

    """

    # Load the image and determine its size.
    imageArray = scipy.ndimage.imread(fileImage)
    numRows, numCols = imageArray.shape

    # Center the image on the origin (0, 0). This is necessary if you are using the full affine transformation matrix
    # at once, as the rotation and shearing are with respect to the origin. As we want the rotation to be around
    # the center of the image, we would need to translate the image and center it on (0, 0) first.
    centerMatrix = np.identity(3)
    centerMatrix[:2, 2] = numRows / 2., numCols / 2.

    # Create the scale matrix.
    # The difficulty with this is ensuring that the probability of scaling up and down is the same.
    # For example, if maxXScale == 5, then the probability of getting a scale value in (1, 5] is far greater
    # than the probability of getting a value in the range [0, 1). As the maximum scale factor gets bigger, it
    # only becomes more likely that scaling up will occur. Avoid this by uncoupling the scaling factor choice from
    # the direction of scaling.
    scaleMatrix = np.identity(3)
    maxXScale = maxScale[0]
    maxYScale = maxScale[1] if len(maxScale) > 1 else maxScale[0]
    if maxXScale > 1:
        scaleX = random.uniform(1, maxXScale)
        scaleXDown = random.random() < scaleUpProb[0]
        scaleMatrix[0, 0] = (1. / scaleX) if scaleXDown else scaleX
    if maxYScale > 1:
        scaleY = random.uniform(1, maxYScale)
        scaleYDown = random.random() < (scaleUpProb[1] if len(scaleUpProb) > 1 else scaleUpProb[0])
        scaleMatrix[1, 1] = (1. / scaleY) if scaleYDown else scaleY

    # Create the rotation matrix.
    rotateMatrix = np.identity(3)
    degreeRotation = random.uniform(0, maxRotation * 2) - maxRotation
    radianRotation = np.deg2rad(degreeRotation)
    rotateMatrix[:2, :2] = [np.cos(radianRotation), np.sin(radianRotation)],\
                           [-np.sin(radianRotation), np.cos(radianRotation)]

    # Create the shear matrix.
    shearMatrix = np.identity(3)
    maxXShear = maxShear[0]
    maxYShear = maxShear[1] if len(maxShear) > 1 else maxShear[0]
    degreeShearX = random.uniform(0, maxXShear * 2) - maxXShear
    degreeShearY = random.uniform(0, maxYShear * 2) - maxYShear
    radianShearX = np.deg2rad(degreeShearX)
    radianShearY = np.deg2rad(degreeShearY)
    shearMatrix[0, 1] = np.tan(radianShearX)
    shearMatrix[1, 0] = np.tan(radianShearY)

    # Create the translation matrix.
    translationMatrix = np.identity(3)
    maxXTranslation = maxTranslation[0]
    maxYTranslation = maxTranslation[1] if len(maxTranslation) > 1 else maxTranslation[0]
    translationX = random.randint(0, maxXTranslation)
    translationY = random.randint(0, maxYTranslation)
    translationMatrix[:2, 2] = [translationX, translationY]

    # Create the inversion matrix.
    inversionMatrix = np.identity(3)
    xInversionProb = inversionProb[0]
    yInversionProb = inversionProb[1] if len(inversionProb) > 1 else inversionProb[0]
    isXInverted = random.random() < xInversionProb
    isYInverted = random.random() < yInversionProb
    inversionMatrix[1, 1] = -1 if isXInverted else 1
    inversionMatrix[0, 0] = -1 if isYInverted else 1

    # Create the affine matrix.
    affineMatrix = np.dot(inversionMatrix,
                          np.dot(translationMatrix,
                                 np.dot(shearMatrix,
                                        np.dot(rotateMatrix,
                                               np.dot(scaleMatrix, centerMatrix)))))

    # Transform the image. Perform operations sequentially in order to gain the desired control over the output.

    # Scale the image. The goal is to 'zoom' in or out of the image while keeping the array the same size.
    # the scaling therefore can't be performed with ndimage.zoom as this messes with the aspect ratio and changes the
    # size of the array. Using affine_transform also doesn't work, as the 'zoom' is performed with respect to the
    # origin (0, 0), and we want it done wth respect to the center of the image.

    # do some sort of map coordinates thing in order to take the visible section of the image (i.e. imageArray)
    # and map the coordinates to anoher array so that when scaling the image down, the whole image fits inside the
    # middle of the new array (padding with background color),
    # and when zooming out you map the middle pixels of the imageArray to the whole new array.

    transformedImage = imageArray#, scaleMatrix[:2, :2], cval=backgroundColor)

    # Rotate the image. This must be done with ndimage.rotate rather than ndimage.affine_transform as we want to rotate
    # around the center of the image. If we used affine_transform, then the rotation would be performed around (0, 0).
    # This could be countered by setting the center of the image to (0, 0), but then the rotation clips the image.
    transformedImage = scipy.ndimage.rotate(transformedImage, degreeRotation, cval=backgroundColor)

    # TODO - decide whether to crop the image back to the original size here
    # TODO - this would cut out some of the foreground (possibly), but I can' crop down the image after scaling
    # TODO - or I will ruin the scaling when I scale down (as all added padding will be removed)

    # Shear the image.
    # this can be done with affine_transform as we don't need this to occur aat the center of the image

    # TODO - decide whether to crop the image back to the original size here
    # TODO - this would cut out some of the foreground (possibly), but I can' crop down the image after scaling
    # TODO - or I will ruin the scaling when I scale down (as all added padding will be removed)

    # Invert the image.

    # Translate the image.

    plt.imshow(imageArray, cmap="Greys_r")
    plt.show()
    newImg = scipy.ndimage.rotate(imageArray, 45, cval=backgroundColor)
    plt.imshow(newImg, cmap="Greys_r")
    plt.show()
    newImg = scipy.ndimage.affine_transform(newImg, np.array([[2, 0],[0, 0.5]]), cval=backgroundColor)
    plt.imshow(newImg, cmap="Greys_r")
    plt.show()

    return imageArray
