#!/usr/bin/python
#
# Removal of periodic features using the FFT
#
# Use Python 2.7 with these packages: numpy, PyOpenGL, Pillow

import sys, os, math, pprint

import numpy as np

from PIL import Image, ImageOps

from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *


# Globals

windowWidth  = 1000 # window dimensions (not image dimensions)
windowHeight =  800

showMagnitude = True            # for the FT, show the magnitude.  Otherwise, show the phase
doHistoEq = False               # do histogram equalization on the FT to make features more obvious

texID = None                    # for OpenGL

zoom = 1.0                      # amount by which to zoom images
translate = (0.0,0.0)           # amount by which to translate images


# Image

imageDir      = 'images'
imageFilename = 'ecg-02.png'
imagePath     = os.path.join( imageDir, imageFilename )

image    = None                 # the image as a 2D np.array
imageFT  = None                 # the image's FT as a 2D np.array

gridImage   = None              # the grid, isolated from the image
gridImageFT = None              # the grid's FT

resultImage = None              # the final image


# Get the magnitude of a complex number

def magFromComplex( c ):
  ak =  2 * np.real( c )
  bk = -2 * np.imag( c )
  return np.sqrt( ak*ak + bk*bk )
  
  

# Remove the grid from the global 'image'.  Return the result image
# AND a list of [ [angle1,distance1], [angle2,distance2] ] describing
# the two principal grid lines.
#
# The angle is the angle, in degrees of the grid line from the horizontal.
#
# The distance is the distance from the origin, in pixels, of the
# first peak in the Fourier Transform corresponding to the lines at
# the given angle.  This will later be used to calculate the line
# spacing.
#
# Do the following in the compute() function:
#
#   1. Compute the FT of the image.  Store it in 'imageFT'.
#
#   2. Compute and store the FT magnitudes.  Find the maximum
#      magnitude, EXCLUDING the DC component in [0,0]. 
#
#   3. Set to zero the components of 'imageFT' that have magnitude
#      less than 40% the maximum magnitude.  Store this new FT in
#      'gridImageFT'.  Record in a list the (x,y) locations of the
#      non-zero magnitudes of 'gridImageFT'.
#
#   4. From the locations of the non-zero magnitudes, find the angles
#      of the two principal grid lines and, for each such line, find
#      the distance of the closest non-zero magnitude to the origin.
#      THIS IS DIFFICULT and can be left until everything else is
#      working.
#
#   5. Apply the inverse FT to 'gridImageFT' to get 'gridImage'.
#
#   6. For each (x,y) location in 'gridImage' that has a bright pixel
#      of value > 16 (i.e. is one of the grid lines), set to zero the
#      corresponding pixel in the original 'image'.  Do not modify
#      'image'; instead, store your result in 'resultImage'.



def compute():

  global image, imageFT, gridImage, gridImageFT, resultImage

  height = image.shape[0]
  width  = image.shape[1]

  # Forward FT
  print '1. compute FT'
  imageFT = forwardFT(image) #compute the fourier transform of image and store it in imageFT

  # Compute magnitudes and find the maximum (excluding the DC component)
  mags = [[0 for x in range(width)] for y in range(height)] #declare a 2D list the same size as imageFT
  print '2. computing FT magnitudes'
  for h in range(height):
    for w in range(width):
      mags[h][w] = magFromComplex(imageFT[h,w]) #compute the magnitude of imageFT and store the value in the corresponding location in mags
	  
  tempZero = mags[0][0] #store the DC component in a temporary variable
  mags[0][0] = 0 #set the DC component to 0
  maxMag = max(map(max, mags)) #compute maximum magnitude
  mags[0][0] = tempZero #return the original value to the origin

  # Zero the components that are less than 40% of the max
  print '3. removing low-magnitude components'

  if gridImageFT is None:
    gridImageFT = np.zeros( (height,width), dtype=np.complex_ )
	
  zeroed = [[False for x in range(width)] for y in range(height)] #storing which ones we did and did not set to zero for later
  threshold = 0.4 * maxMag #set threshold value
 
  for h in range(height):
    for w in range(width):
      if mags[h][w] < threshold:
        gridImageFT[h,w] = 0 #set to zero if below threshold
        zeroed[h][w] = True #indicate this pixel has been set to zero
      else:
        gridImageFT[h,w] = imageFT[h,w] #otherwise copy value to gridImageFT unchanged
  
  print '4. finding angles and distances of grid lines'
  
  # Find (angle, distance) to each peak
  # lines = [ (angle1,distance1), (angle2,distance2) ]
  
  points = [] #instantiate list

  #iterate through the pixels in the bottom half of gridImageFT
  
  for h in range((height/2)):
    for w in range(width):
      if (zeroed[h][w] == False): #filter out all pixels that have been set to zero
        
        angle = None
        distance = None

        if w > (width/2): #divide the bottom half of the image into two quadrants
          distance = np.sqrt(np.square(h) + np.square(w-width)) #calculate the distance to the point from the origin
          angle = (np.arctan2(h,(w - width))) * 180.0 / np.pi #calculate the angle of the point wrt the origin
          if angle >= 180:
            angle = angle - 180 #ensure all angles are under 180 degrees
        else: #iterate through the second quadrant
          distance = np.sqrt(np.square(h) + np.square(w)) #calculate the distance to the point from the origin
          angle = (np.arctan2(h,w)) * 180.0 / np.pi #calculate the angle of the point wrt the origin
          if angle >= 180:
            angle = angle - 180 #ensure all angles are under 180 degrees

        if distance > 15: #eliminate points that are too close to the origin
          point = [angle, distance]
          points.append(point) #add new points to the list points
  
  points = sorted(points,key=lambda x: x[0]) #sort the list by angle 
  
  firstAngle = points[0][0]
  split = None
  for i in range(len(points)):
    if abs(points[i][0] - firstAngle) > 60: #index where to split the list by angle value
      split = i 
      break

  pointsA = points[:split] #split the original list points into lists pointsA and pointsB
  pointsB = points[split:]

  angle1 = [float(sum(a))/len(a) for a in zip(*pointsA)][0] #calculate average angle for pointsA
  angle2 = [float(sum(b))/len(b) for b in zip(*pointsB)][0] #calculate average angle for pointsB

  distance1 = pointsA[0][1]
  for i in range(len(pointsA)):
    if pointsA[i][1] < distance1:
      distance1 = pointsA[i][1] #find the distance that is closest to the origin in pointsA

  distance2 = pointsB[0][1]
  for i in range(len(pointsB)):
    if pointsB[i][1] < distance2:
      distance2 = pointsB[i][1] #find the distance that is closest to the origin in pointsA

  lines = [ (angle1,distance1), (angle2,distance2) ]
  
  # Convert back to spatial domain to get a grid-like image
  print '5. inverse FT'

  gridImage = inverseFT(gridImageFT) #take the inverse FT of gridImageFT to get gridImage
  
  if gridImage is None:
    gridImage = np.zeros( (height,width), dtype=np.complex_ )

  # Remove grid image from original image
  print '6. remove grid'

  resultImage = np.zeros( (height,width), dtype=np.complex_ )

  for h in range(height):
    for w in range(width):
      if(gridImage[h,w] > 16): #if the grid is bright at this pixel
        resultImage[h,w] = 0 #remove the pixel in the original image (to remove grid)
      else:
        resultImage[h,w] = image[h,w].copy() #otherwise keep original value

  if resultImage is None:
    resultImage = image.copy()
  print 'done'

  return resultImage, lines


      

# File dialog

import Tkinter, tkFileDialog

root = Tkinter.Tk()
root.withdraw()



# Do a forward FT
#
# Input is a 2D numpy array of complex values.
# Output is the same.

def forwardFT( image ):

  return np.fft.fft2( image )



# Do an inverse FT
#
# Input is a 2D numpy array of complex values.
# Output is the same.


def inverseFT( image ):

  return np.fft.ifft2( image )



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
      if toDraw[r][c] is not None:

        if r == 0: # normal image in row 0 
          img = toDraw[r][c]
        else: # FT in column 1
          img = np.fft.fftshift( toDraw[r][c] ) # shift FT so that origin is in centre (just for display)

        height = scale * img.shape[0]
        width  = scale * img.shape[1]

        # Find lower-left corner

        baseX = (horizSpacing + maxWidth ) * c + horizSpacing
        baseY = (vertSpacing  + maxHeight) * (rows-1-r) + vertSpacing

        # Get pixels and draw

        if r == 0: # for images (in row 0), show the real part of each pixel
          show = np.real(img)
        else: # for FT (in column 1), show magnitude or phase
          ak =  2 * np.real(img)
          bk = -2 * np.imag(img)
          if showMagnitude:
            show = np.log( 1 + np.sqrt( ak*ak + bk*bk ) ) # take the log because there are a few very large values (e.g. the DC component)
          else:
            show = np.arctan2( -1 * bk, ak )

          if doHistoEq and c > 0:
            show = histoEq( show ) # optionally, perform histogram equalization on FT image (but this takes time!)

        # Put the image into a texture, then draw it

        max = show.max()
        min = show.min()
        if max == min:
          max = min+1
          
        imgData = np.array( (np.ravel(show) - min) / (max - min) * 255, np.uint8 )

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
 
  if image is not None:
    baseX = horizSpacing
    baseY = (vertSpacing  + maxHeight) * (rows) + 8
    drawText( baseX, baseY, imageFilename )

  if imageFT is not None:
    baseX = horizSpacing
    baseY = (vertSpacing  + maxHeight) * (rows-2) + vertSpacing - 18
    drawText( baseX, baseY, 'FT of %s' % imageFilename )

  if gridImage is not None:
    baseX = (horizSpacing + maxWidth) * 1 + horizSpacing
    baseY = (vertSpacing  + maxHeight) * rows + 8
    drawText( baseX, baseY, 'extracted grid' )

  if gridImageFT is not None:
    baseX = (horizSpacing + maxWidth) * 1 + horizSpacing
    baseY = (vertSpacing  + maxHeight) * (rows-2) + vertSpacing - 18
    drawText( baseX, baseY, 'FT of extracted grid' )

  if resultImage is not None:
    baseX = (horizSpacing + maxWidth) * 2 + horizSpacing
    baseY = (vertSpacing  + maxHeight) * (rows) + 8
    drawText( baseX, baseY, 'result' )

  # Draw mode information

  str = 'show %s' % ('magnitudes' if showMagnitude else 'phases')
  glColor3f( 0.5, 0.2, 0.4 )
  drawText( windowWidth-len(str)*8-8, 12, str )

  # Done

  glutSwapBuffers()

  

# Get information about how to place the images.
#
# toDraw                       2D array of complex images 
# rows, cols                   rows and columns in array
# maxHeight, maxWidth          max height and width of images
# scale                        amount by which to scale images
# horizSpacing, vertSpacing    spacing between images


def getImagesInfo():

  toDraw = [ [ image,   gridImage,   resultImage   ],
             [ imageFT, gridImageFT, None ] ]

  rows = len(toDraw)
  cols = len(toDraw[0])

  # Find max image dimensions

  maxHeight = 0
  maxWidth  = 0
  
  for row in toDraw:
    for img in row:
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

  return toDraw, rows, cols, maxHeight, maxWidth, scale, horizSpacing, vertSpacing
  

  
# Equalize the image histogram

def histoEq( pixels ):

  # build histogram

  h = [0] * 256 # counts

  width  = pixels.shape[0]
  height = pixels.shape[1]

  min = pixels.min()
  max = pixels.max()
  if max == min:
    max = min+1

  for i in range(width):
    for j in range(height):
      y = int( (pixels[i,j] - min) / (max-min) * 255 )
      h[y] = h[y] + 1

  # Build T[r] = s

  k = 256.0 / float(width * height) # common factor applied to all entries

  T = [0] * 256 # lookup table
  
  sum = 0
  for i in range(256):
    sum = sum + h[i]
    T[i] = int( math.floor(k * sum) - 1 )
    if T[i] < 0:
      T[i] = 0

  # Apply T[r]

  result = np.empty( pixels.shape )

  for i in range(width):
    for j in range(height):
      y = int( (pixels[i,j] - min) / (max - min) * 255 )
      result[i,j] = T[y]

  return result
  

# Handle keyboard input

def keyboard( key, x, y ):

  global image, imageFT, gridImage, gridImageFT, resultImage, showMagnitude, doHistoEq, imageFilename, zoom, translate

  if key == '\033': # ESC = exit
    sys.exit(0)

  elif key == 'i':

    imagePath = tkFileDialog.askopenfilename( initialdir = imageDir )
    if imagePath:
      image = loadImage( imagePath )
      imageFilename = os.path.basename( imagePath )
      imageFT = None
      gridImage = None
      gridImageFT = None
      resultImage = None

  elif key == 'm':
    showMagnitude = not showMagnitude

  elif key == 'h':
    doHistoEq = not doHistoEq

  elif key == 'z':
    zoom = 1
    translate = (0,0)

  elif key == 'c': # compute
    resultImage, lines = compute()
    print 'Grid lines:'
    for line in lines:
      print '  angle %.1f, distance %d' % (line[0],line[1])

  else:
    print '''keys:
           c  compute the solution
           m  toggle between magnitude and phase in the FT  
           h  toggle histogram equalization in the FT  
           i  load image
 right arrow  forward transform
  left arrow  inverse transform

              translate with left mouse dragging
              zoom with right mouse draggin up/down
           z  reset the translation and zoom'''

  glutPostRedisplay()


# Handle special key (e.g. arrows) input

def special( key, x, y ):

  if key == GLUT_KEY_DOWN:
    forwardFT_all()

  elif key == GLUT_KEY_UP:
    inverseFT_all()

  glutPostRedisplay()



# Do a forward FT to all images


def forwardFT_all():

  global image, imageFT

  if image is not None:
    imageFT = forwardFT( image )



# Do an inverse FT to all image FTs


def inverseFT_all():

  global image, imageFT

  if image is not None: 
    image = inverseFT( imageFT )


    
# Load an image
#
# Return the image as a 2D numpy array of complex_ values.


def loadImage( path ):

  try:
    img = Image.open( path ).convert( 'L' ).transpose( Image.FLIP_TOP_BOTTOM )
  except:
    print 'Failed to load image %s' % path
    sys.exit(1)

  img = ImageOps.invert(img)

  return np.array( list( img.getdata() ), np.complex_ ).reshape( (img.size[1],img.size[0]) )



# Handle window reshape

def reshape( newWidth, newHeight ):

  global windowWidth, windowHeight

  windowWidth  = newWidth
  windowHeight = newHeight

  glViewport( 0, 0, windowWidth, windowHeight )

  glutPostRedisplay()



# Output an image
#
# The image has complex values, so output either the magnitudes or the
# phases, according to the 'outputMagnitudes' parameter.

def outputImage( image, filename, outputMagnitudes, isFT, invert ):

  if not isFT:
    show = np.real(image)
  else:
    ak =  2 * np.real(image)
    bk = -2 * np.imag(image)
    if outputMagnitudes:
      show = np.log( 1 + np.sqrt( ak*ak + bk*bk ) ) # take the log because there are a few very large values (e.g. the DC component)
    else:
      show = np.arctan2( -1 * bk, ak )
    show = np.fft.fftshift( show ) # shift FT so that origin is in centre

  min = show.min()
  max = show.max()

  img = Image.fromarray( np.uint8( (show - min) * (255 / (max-min)) ) ).transpose( Image.FLIP_TOP_BOTTOM )

  if invert:
    img = ImageOps.invert(img) 

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
      
      # for the FT images, move the position half up and half right,
      # since the image is displayed with that shift, while the FT array
      # stores the unshifted values.

      isFT = (int(col) == 1)

      if isFT:

        pixelX = pixelX - image.shape[1]/2
        if pixelX < 0:
          pixelX = pixelX + image.shape[1]

        pixelY = pixelY - image.shape[0]/2
        if pixelY < 0:
          pixelY = pixelY + image.shape[0]

      # Perform the operation
      #
      # No operation is implemented here, but could be (e.g. image modification at the mouse position)

      # applyOperation( image, pixelX, pixelY, isFT )  

      print 'click at', pixelX, pixelY

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
    if cmd == 'f':
      forwardFT_all()
    elif cmd == 'i':
      inverseFT_all()
    elif cmd == 'm':
      outputMagnitudes = True
    elif cmd == 'p':
      outputMagnitudes = False
    elif cmd == 'c':
      resultImage, lines = compute()
      print lines
    elif cmd[0] == 'o': # image name follows in 'cmds'
      filename = cmds.pop(0)
      outputImage( resultImage, filename, False, False, True )
    else:
      print """command '%s' not understood.
command-line arguments:
  f - apply forward FT
  i - apply inverse FT
  o - output the image
  m - for output, use magnitudes (default)
  p - for output, use phases""" % cmd

else:
      
  # Run OpenGL

  glutInit()
  glutInitDisplayMode( GLUT_DOUBLE | GLUT_RGB )
  glutInitWindowSize( windowWidth, windowHeight )
  glutInitWindowPosition( 50, 50 )

  glutCreateWindow( 'imaging' )

  glutDisplayFunc( display )
  glutKeyboardFunc( keyboard )
  glutSpecialFunc( special )
  glutReshapeFunc( reshape )
  glutMouseFunc( mouse )
  glutMotionFunc( mouseMotion )

  glDisable( GL_DEPTH_TEST )

  glutMainLoop()
