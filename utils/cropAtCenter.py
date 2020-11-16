""" Ike Kilinc (aykilinc)
"""
import sys
import typing

from PIL import Image

def cropImageCenter(targetPath: str, outputPath: str, cropFactor: int) -> Image.Image:
    """ Crops length and width of PNG at targetPath by cropFactor.

    Parameters
    ----------
        param: targetPath   str path to image to be cropped.
    
        param: outputPath   str path to save cropped image to.
    
        param: cropFactor   int factor by which length and width should be cropped.

    Returns
    ----------
    PIL Image object of the cropped result being saved to the outputPath.
    """

    im = Image.open(targetPath)
    width, height = im.size

    # cropFactor = cropFactor**0.5 # Uncomment to have crop

    left = width/2 * (1 - 1/cropFactor)
    top = height/2 * (1 - 1/cropFactor)
    right = width/2 * (1 + 1/cropFactor)
    bottom = height/2 * (1 + 1/cropFactor)

    im = im.crop((left, top, right, bottom))
    im.save(outputPath, "PNG")

    return im


if __name__=='__main__':
    if len(sys.argv) != 4:
        print("Error: Incorrect number of command line arguments passed.")
        raise Exception
    elif not sys.argv[2].endswith(".png"):
        print("Erorr: Indicated output filepath is not PNG.")
    
    croppedImage = cropImageCenter(sys.argv[1], sys.argv[2], int(sys.argv[3]))
    croppedImage.show()
