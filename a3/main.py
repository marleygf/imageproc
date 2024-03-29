#!/usr/bin/python
#
# Canny edge detection
#
# Use Python 2.7 with these packages: numpy, PyOpenGL, Pillow
#
# Can test this with
#
#   python main.py
#
# This loads 'images/small.png', then applies the 'c' command.
#
# Press '?' to see a list of available commands.  Use + and - to see
# the intermediate stages of the computation.


import sys, os, math

import numpy as np

from PIL import Image, ImageOps

from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *


# Globals

windowWidth  = 1000    # window dimensions (not image dimensions)
windowHeight =  800

texID = None           # for OpenGL

zoom = 1.0             # amount by which to zoom images
translate = (0.0,0.0)  # amount by which to translate images


# Image

imageDir      = 'images'
imageFilename = 'small.png'
imagePath     = os.path.join( imageDir, imageFilename )

image          = None    # the image as a 2D np.array
smoothImage    = None    # the smoothed image
gradientMags   = None    # the image with gradient magnitudes (in 0...255)
gradientDirs   = None    # array of gradient directions in [0,7] with direction i = i*45 degrees.
maximaImage    = None    # gradient magnitues with non-maxima set to 0
thresholdImage = None    # thresholded pixels (= 255 or 128 or 0)
edgeImage      = None    # final edges pixels (= 255 or 0)

imageNames = [ 'original image', 'smoothed image', 'gradients', 'gradient directions', 'maxima', 'thresholded maxima', 'Canny edges' ]

currentImage = 0 # the image being displayed

normalizeImage = True # scale image so that its pixels are in the range [0,255]

upperThreshold = 25
lowerThreshold = 5


# Apply Canny edge detection
#
# Returns list of edge pixels

def compute():

  global image, smoothImage, gradientMags, gradientDirs, maximaImage, thresholdImage, edgeImage, currentImage

  height = image.shape[0]
  width  = image.shape[1]

  print 'smoothing'

  if smoothImage is None:
    smoothImage = np.zeros( (height,width), dtype=np.float_ )

  smooth( image, smoothImage )
  print 'finding gradients'

  if gradientMags is None:
    gradientMags = np.zeros( (height,width), dtype=np.float_ )

  if gradientDirs is None:
    gradientDirs = np.zeros( (height,width), dtype=np.float_ )

  findGradients( smoothImage, gradientMags, gradientDirs )

  print 'suppressing non-maxima'

  if maximaImage is None:
    maximaImage = np.zeros( (height,width), dtype=np.float_ )

  suppressNonMaxima( gradientMags, gradientDirs, maximaImage )

  print 'double thresholding'

  if thresholdImage is None:
    thresholdImage = np.zeros( (height,width), dtype=np.float_ )

  doubleThreshold( maximaImage, thresholdImage )

  print 'edge tracking'

  if edgeImage is None:
    edgeImage = np.zeros( (height,width), dtype=np.float_ )

  trackEdges( thresholdImage, edgeImage )

  # extract edge pixels

  edgePixels = list( np.transpose( np.nonzero( edgeImage ) ) )

  # for debugging: show the image that we're interested in

  currentImage = len(imageNames)-1

  return edgePixels


# Smooth image
#
# Apply the 5x5 filter (below) to 'image' and store the result in
# 'smoothedImage'.
#
# [1 mark]

def smooth( image, smoothedImage ):

  height = image.shape[0]
  width  = image.shape[1]
  
  kernel = (1/273.0) * np.array( [[1,  4,  7,  4, 1],
                                  [4, 16, 26, 16, 4],
                                  [7, 26, 41, 26, 7],
                                  [4, 16, 26, 16, 4],
                                  [1,  4,  7,  4, 1]] )

  # YOUR CODE HERE

      
# Compute the image's gradient magnitudes and directions
#
# The directions are in the range [0,7], where 0 is to the right, 2 is
# up, 4 is left, and 6 is down.  You should *calculate* the direction
# instead of having a big if-then-else.
#
# [2 marks]
#
# 1 of the two marks is for a *good* (i.e. simple, one-line)
# calculation of direction.

def findGradients( image, gradientMags, gradientDirs ):

  height = image.shape[0]
  width  = image.shape[1]

  # YOUR CODE HERE
  '''
  Dx = np.array( [[1, 0, -1],
                  [2, 0, -2],
                  [1, 0, -1]] )
				  
  Dy = np.array( [[ 1,  2,  1],
                  [ 0,  0,  0],
                  [-1, -2, -1]] )
				  
  Convolve Dx and Dy with Image to get Gx and Gy
  (see part 1 for steps)
  
  At each pixel, compute gradientMags
  gradientMags[i] = sqrt(Gx[i]^2 + Gy[i]^2)
  
  At each pixel, compute gradientDirs ***0-7 slices in one line***
  gradientDirs[i] = (nearest int(arctan2(Gy[i]/Gx[i])/(pi/4)))modulo 8
  
  '''

# Suppress the non-maxima in the gradient directions
#
# Use the 'offset' array to get the gradient direction for each
# gradient in [0,7].  Do not use a big if-then-else.
#
# [1 mark]

def suppressNonMaxima( magnitude, gradientDirs, maximaImage ):

  # gradient offsets for each gradient direction in [0,7]

  offset = [ (1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1) ]

  height = magnitude.shape[0]
  width  = magnitude.shape[1]

  # YOUR CODE HERE  



# Apply double thresholding
#
# Set pixels < 'lowerThreshold' to 0, pixels above 'upperThreshold' to
# 255, and all other pixels to 128.
#
# [1 mark]

def doubleThreshold( maximaImage, thresholdImage ):

  height = maximaImage.shape[0]
  width  = maximaImage.shape[1]

  # YOUR CODE HERE  



# Attach weak pixels to strong pixels
#
# Weak pixels = 128.  Strong pixels = 255.  The 'edgePixels' should,
# when done, contain only 0s and 255s.
#
# Use the 'offsets' to find pixels in the neighbourhood of a strong
# pixel.  Use a list of strong pixels, which gets updated as new
# strong pixels are made.
#
# [2 marks]
#
# 1 of the two marks is for an *efficient* implementation.

def trackEdges( thresholdImage, edgePixels ):

  height = thresholdImage.shape[0]
  width  = thresholdImage.shape[1]
  
  edgePixels.fill(0)

  offsets = [ (1,0), (1,1), (0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1) ]

  # YOUR CODE HERE


    
# File dialog

if sys.platform != 'darwin':
  import Tkinter, tkFileDialog
  root = Tkinter.Tk()
  root.withdraw()



# Set up the display and draw the current image


def display():

  # Clear window

  glClearColor ( 1, 1, 1, 0 )
  glClear( GL_COLOR_BUFFER_BIT )

  glMatrixMode( GL_PROJECTION )
  glLoadIdentity()

  glMatrixMode( GL_MODELVIEW )
  glLoadIdentity()
  glOrtho( 0, windowWidth, 0, windowHeight, 0, 1 )

  # Set up texturing

  global texID
  
  if texID == None:
    texID = glGenTextures(1)

  glPixelStorei( GL_UNPACK_ALIGNMENT, 1 )
  glBindTexture( GL_TEXTURE_2D, texID )

  glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
  glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, [1,0,0,1] );

  # Images to draw, in rows and columns

  toDraw, rows, cols, maxHeight, maxWidth, scale, horizSpacing, vertSpacing = getImagesInfo()

  for r in range(rows):
    for c in range(cols):

      # Find lower-left corner
      
      baseX = (horizSpacing + maxWidth ) * c + horizSpacing
      baseY = (vertSpacing  + maxHeight) * (rows-1-r) + vertSpacing

      if toDraw[r][c] is not None:

        img = toDraw[r][c]

        height = scale * img.shape[0]
        width  = scale * img.shape[1]

        # Get pixels and draw

        show = np.real(img)

        # Normalize image so all pixels are in [0,255].  This is useful when debugging because small details are more visible.
        
        if normalizeImage:
          min = np.min(show)
          max = np.max(show)
          if min == max:
            max = min+1
          show = (show - min) / (max-min) * 255

        # Put the image into a texture, then draw it

        imgData = np.array( np.ravel(show), np.uint8 ).tostring()

        # with open( 'out.pgm', 'wb' ) as f:
        #   f.write( 'P5\n%d %d\n255\n' % (img.shape[1], img.shape[0]) )
        #   f.write( imgData )

        glTexImage2D( GL_TEXTURE_2D, 0, GL_INTENSITY, img.shape[1], img.shape[0], 0, GL_LUMINANCE, GL_UNSIGNED_BYTE, imgData )

        # Include zoom and translate

        cx     = 0.5 - translate[0]/width
        cy     = 0.5 - translate[1]/height
        offset = 0.5 / zoom

        glEnable( GL_TEXTURE_2D )

        glBegin( GL_QUADS )
        glTexCoord2f( cx-offset, cy-offset )
        glVertex2f( baseX, baseY )
        glTexCoord2f( cx+offset, cy-offset )
        glVertex2f( baseX+width, baseY )
        glTexCoord2f( cx+offset, cy+offset )
        glVertex2f( baseX+width, baseY+height )
        glTexCoord2f( cx-offset, cy+offset )
        glVertex2f( baseX, baseY+height )
        glEnd()

        glDisable( GL_TEXTURE_2D )

        if zoom != 1 or translate != (0,0):
          glColor3f( 0.8, 0.8, 0.8 )
          glBegin( GL_LINE_LOOP )
          glVertex2f( baseX, baseY )
          glVertex2f( baseX+width, baseY )
          glVertex2f( baseX+width, baseY+height )
          glVertex2f( baseX, baseY+height )
          glEnd()

      # Draw image captions

      glColor3f( 0.2, 0.5, 0.7 )
      drawText( baseX, baseY-20, imageNames[currentImage] )

  # Done

  glutSwapBuffers()

  

# Get information about how to place the images.
#
# toDraw                       2D array of images 
# rows, cols                   rows and columns in array
# maxHeight, maxWidth          max height and width of images
# scale                        amount by which to scale images
# horizSpacing, vertSpacing    spacing between images


def getImagesInfo():

  allImages = [ image, smoothImage, gradientMags, gradientDirs, maximaImage, thresholdImage, edgeImage ]

  # Only display a single image

  rows = 1
  cols = 1

  # Find max image dimensions

  maxHeight = 0
  maxWidth  = 0
  
  for img in allImages:
    if img is not None:
      if img.shape[0] > maxHeight:
        maxHeight = img.shape[0]
      if img.shape[1] > maxWidth:
        maxWidth = img.shape[1]

  # Scale everything to fit in the window

  minSpacing = 30 # minimum spacing between images

  scaleX = (windowWidth  - (cols+1)*minSpacing) / float(maxWidth  * cols)
  scaleY = (windowHeight - (rows+1)*minSpacing) / float(maxHeight * rows)

  if scaleX < scaleY:
    scale = scaleX
  else:
    scale = scaleY

  maxWidth  = scale * maxWidth
  maxHeight = scale * maxHeight

  # Draw each image

  horizSpacing = (windowWidth-cols*maxWidth)/(cols+1)
  vertSpacing  = (windowHeight-rows*maxHeight)/(rows+1)

  # only return a single image: the current image

  return [ [ allImages[currentImage] ] ], 1, 1, maxHeight, maxWidth, scale, horizSpacing, vertSpacing
  

  
# Handle keyboard input

def keyboard( key, x, y ):

  global image, imageFilename, smoothImage, gradientMags, gradientDirs, maximaImage, thresholdImage, edgeImage, zoom, translate, currentImage, normalizeImage

  if key == '\033': # ESC = exit
    sys.exit(0)

  elif key == 'i':

    if sys.platform != 'darwin':
      imagePath = tkFileDialog.askopenfilename( initialdir = imageDir )
      if imagePath:

        image = loadImage( imagePath )
        imageFilename = os.path.basename( imagePath )
        currentImage  = 0
        
        smoothImage    = None
        gradientMags   = None
        gradientDirs   = None
        maximaImage    = None
        thresholdImage = None
        edgeImage      = None

  elif key == 'z':
    zoom = 1
    translate = (0,0)

  elif key == 'n':
    normalizeImage = not normalizeImage
    if normalizeImage:
      print 'normalized image'
    else:
      print 'unnormalized image'

  elif key == 'c': # compute
    edgePixels = compute()
    # print 'Edge pixels:'
    # for px in edgePixels:
    #   print ' %.1f,%.1f' % (px[0],px[1])

  elif key in ['+','=']:
    currentImage = (currentImage + 1) % len(imageNames)

  elif key in ['-','_']:
    currentImage = (currentImage - 1 + len(imageNames)) % len(imageNames)

  else:
    print '''keys:
           c  compute the solution
           i  load image
           z  reset the translation and zoom
           +  next image
           -  previous image
    
              translate with left mouse dragging
              zoom with right mouse draggin up/down'''

  glutPostRedisplay()


# Handle special key (e.g. arrows) input

def special( key, x, y ):

  # Nothing done

  glutPostRedisplay()



# Load an image

def loadImage( path ):

  try:
    img = Image.open( path ).convert( 'L' ).transpose( Image.FLIP_TOP_BOTTOM )
    # img = ImageOps.invert(img)
  except:
    print 'Failed to load image %s' % path
    sys.exit(1)

  return np.array( list( img.getdata() ), np.float_ ).reshape( (img.size[1],img.size[0]) )



# Handle window reshape

def reshape( newWidth, newHeight ):

  global windowWidth, windowHeight

  windowWidth  = newWidth
  windowHeight = newHeight

  glViewport( 0, 0, windowWidth, windowHeight )

  glutPostRedisplay()



# Output an image

def outputImage( image, filename ):

  show = np.real(image)

  img = Image.fromarray( np.uint8(show) ).transpose( Image.FLIP_TOP_BOTTOM )

  img.save( filename )




# Draw text in window

def drawText( x, y, text ):

  glRasterPos( x, y )
  for ch in text:
    glutBitmapCharacter( GLUT_BITMAP_8_BY_13, ord(ch) )

    

# Handle mouse click


currentButton = None
initX = 0
initY = 0
initZoom = 0
initTranslate = (0,0)

def mouse( button, state, x, y ):

  global currentButton, initX, initY, initZoom, initTranslate, translate, zoom

  if state == GLUT_DOWN:

    currentButton = button
    initX = x
    initY = y
    initZoom = zoom
    initTranslate = translate

  elif state == GLUT_UP:

    currentButton = None

    if button == GLUT_LEFT_BUTTON and initX == x and initY == y: # Process a left click (with no dragging)

      # Find which image the click is in

      toDraw, rows, cols, maxHeight, maxWidth, scale, horizSpacing, vertSpacing = getImagesInfo()

      row = (y-vertSpacing ) / float(maxHeight+vertSpacing)
      col = (x-horizSpacing) / float(maxWidth+horizSpacing)

      if row < 0 or row-math.floor(row) > maxHeight/(maxHeight+vertSpacing):
        return

      if col < 0 or col-math.floor(col) > maxWidth/(maxWidth+horizSpacing):
        return

      # Get the image

      image = toDraw[ int(row) ][ int(col) ]

      if image is None:
        return

      # Get bounds of visible image
      #
      # Bounds are [cx-offset,cx+offset] x [cy-offset,cy+offset]
      
      height = scale * image.shape[0]
      width  = scale * image.shape[1]

      cx     = 0.5 - translate[0]/width
      cy     = 0.5 - translate[1]/height
      offset = 0.5 / zoom

      # Find pixel position within the image array

      xFraction = (col-math.floor(col)) / (maxWidth /float(maxWidth +horizSpacing))
      yFraction = (row-math.floor(row)) / (maxHeight/float(maxHeight+vertSpacing ))

      pixelX = int( image.shape[1] * ((1-xFraction)*(cx-offset) + xFraction*(cx+offset)) )
      pixelY = int( image.shape[0] * ((1-yFraction)*(cy+offset) + yFraction*(cy-offset)) )
      
      # Perform the operation
      #
      # No operation is implemented here, but could be (e.g. image modification at the mouse position)

      # applyOperation( image, pixelX, pixelY, isFT )  

      print 'click at', pixelX, pixelY, '=', image[pixelY][pixelX]

      # Done

      glutPostRedisplay()



# Handle mouse dragging
#
# Zoom out/in with right button dragging up/down.
# Translate with left button dragging.


def mouseMotion( x, y ):

  global zoom, translate

  if currentButton == GLUT_RIGHT_BUTTON:

    # zoom

    factor = 1 # controls the zoom rate
    
    if y > initY: # zoom in
      zoom = initZoom * (1 + factor*(y-initY)/float(windowHeight))
    else: # zoom out
      zoom = initZoom / (1 + factor*(initY-y)/float(windowHeight))

  elif currentButton == GLUT_LEFT_BUTTON:

    # translate

    translate = ( initTranslate[0] + (x-initX)/zoom, initTranslate[1] + (initY-y)/zoom )

  glutPostRedisplay()


# For an image coordinate, if it's < 0 or >= max, wrap the coorindate
# around so that it's in the range [0,max-1].  This is useful dealing
# with FT images.

def wrap( val, max ):

  if val < 0:
    return val+max
  elif val >= max:
    return val-max
  else:
    return val



# Load initial data
#
# The command line (stored in sys.argv) could have:
#
#     main.py {image filename}

if len(sys.argv) > 1:
  imageFilename = sys.argv[1]
  imagePath = os.path.join( imageDir,  imageFilename  )

image  = loadImage(  imagePath  )


# If commands exist on the command line (i.e. there are more than two
# arguments), process each command, then exit.  Otherwise, go into
# interactive mode.

if len(sys.argv) > 2:

  outputMagnitudes = True

  # process commands

  cmds = sys.argv[2:]

  while len(cmds) > 0:
    cmd = cmds.pop(0)
    if cmd == 'c':
      edgePixels = compute()
      # print 'Edge pixels:'
      # for px in edgePixels:
      #   print ' %.1f,%.1f' % (px[0],px[1])
    elif cmd[0] == 'o': # image name follows in 'cmds'
      filename = cmds.pop(0)
      allImages = [ image, smoothImage, gradientMags, gradientDirs, maximaImage, thresholdImage, edgeImage ]
      outputImage( allImages[currentImage], filename )
    elif cmd[0] in ['0','1','2','3','4','5','6']:
      currentImage = int(cmd[0]) - int('0')
    else:
      print """command '%s' not understood.
command-line arguments:
  c   - apply Canny 
  0-6 - set current image
  o   - output current image
""" % cmd

else:
      
  # Run OpenGL

  glutInit()
  glutInitDisplayMode( GLUT_DOUBLE | GLUT_RGB )
  glutInitWindowSize( windowWidth, windowHeight )
  glutInitWindowPosition( 50, 50 )

  glutCreateWindow( 'Canny edges' )

  glutDisplayFunc( display )
  glutKeyboardFunc( keyboard )
  glutSpecialFunc( special )
  glutReshapeFunc( reshape )
  glutMouseFunc( mouse )
  glutMotionFunc( mouseMotion )

  glDisable( GL_DEPTH_TEST )

  glutMainLoop()
