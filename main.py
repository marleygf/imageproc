# Image manipulation
#
# You'll need Python 2.7 and must install these packages:
#
#   numpy, PyOpenGL, Pillow
#
# Note that file loading and saving (with 'l' and 's') do not work on
# Mac OSX, so you will have to change 'imgFilename' below, instead, if
# you want to work with different images.
#
# Note that images, when loaded, are converted to the YCbCr
# colourspace, and that you should manipulate only the Y component of
# each pixel when doing intensity changes.

import sys, os, numpy, math

try: # Pillow
  from PIL import Image
except:
  print 'Error: Pillow has not been installed.'
  sys.exit(0)

try: # PyOpenGL
  from OpenGL.GLUT import *
  from OpenGL.GL import *
  from OpenGL.GLU import *
except:
  print 'Error: PyOpenGL has not been installed.'
  sys.exit(0)



# Globals

windowWidth  = 600 # window dimensions
windowHeight =  800

localHistoRadius = 5  # distance within which to apply local histogram equalization



# Current image

imgDir      = 'images'
imgFilename = 'mandrill.png'

currentImage = Image.open( os.path.join( imgDir, imgFilename ) ).convert( 'YCbCr' ).transpose( Image.FLIP_TOP_BOTTOM )
tempImage    = None



# File dialog (doesn't work on Mac OSX)

if sys.platform != 'darwin':
  import Tkinter, tkFileDialog
  root = Tkinter.Tk()
  root.withdraw()



# Apply brightness and contrast to tempImage and store in
# currentImage.  The brightness and constrast changes are always made
# on tempImage, which stores the image when the left mouse button was
# first pressed, and are stored in currentImage, so that the user can
# see the changes immediately.  As long as left mouse button is held
# down, tempImage will not change.

def applyBrightnessAndContrast( brightness, contrast ):

  width  = currentImage.size[0]
  height = currentImage.size[1]

  srcPixels = tempImage.load()
  dstPixels = currentImage.load()
  
  for w in range(width): 				#increment through width of image
	for h in range (height): 			#increment through height of image
		
	  dstPixels[w,h] = ((contrast*srcPixels[w,h][0])+brightness, srcPixels[w,h][1], srcPixels[w,h][2])
	  
  print 'adjust brightness = %f, contrast = %f' % (brightness,contrast)

  

# Perform local histogram equalization on the current image using the given radius.

def performHistoEqualization( radius ):

  pixels = currentImage.load()
  width  = currentImage.size[0]
  height = currentImage.size[1]
  
  equalized = [[0 for x in range(width)] for y in range(height)] # Temporary array to store new intensity values     
  
  for w in range(width):
    for h in range(height):
      
      # Get intensity of current pixel
      r = pixels[w,h]
      r = r[0] 
      
      # Acts as pseudo-histogram to store surrounding pixel intensities. This is done to avoid having 256 empty buckets
      # that then need to be emptied each time
      box = [] 
      
      # Calculate size of area covered by radius 
      N = numpy.power((radius * 2) + 1, 2) 
      
      #Itterate through area covered by radius around target pixel
      for j in range(w - radius , w + radius + 1):
        for k in range(h - radius , h + radius + 1):
	  
	  # Ensure in bounds and add to list.
          if j < width and j >= 0 and k < height and k >= 0: 
            p = pixels[j,k]
            box.append(p[0])
	  # If sourcing from out of bounds, that means we're at a corner
	  # or edge pixel, so we ignore and shrink N value for calculation
	  else:
	    N = N - 1
      
      theSum = 0
      for i in range(r + 1): # For each intensity...
        cc = box.count(i) # ...count the occurences of the intensity...
        theSum = theSum + cc # ...and add it to the sum
      
      # Calculate new pixel intensity and store in temporary list
      s = ((256/N) * theSum) - 1
      equalized[h][w] = s

  #Copy new intensities to current image
  for w in range(width):
    for h in range(height):
      eq = list(pixels[w,h])
      eq[0] = equalized[h][w]
      eq = tuple(eq)
      pixels[w,h] = eq      
  print 'perform local histogram equalization with radius %d' % radius



# Scale the tempImage by the given factor and store it in
# currentImage.  Use backward projection.  This is called when the
# mouse is moved with the right button held down.

def scaleImage( factor ):

  width  = currentImage.size[0]
  height = currentImage.size[1]

  srcPixels = tempImage.load()
  dstPixels = currentImage.load()
  
  # xp, yp are x' and y' (prime) respectively, the points in the destination image for backwards projection
  # We loop through the current width and height because we are only concerned about drawing the pixels within
  # this "canvas" area
  for xp in range(width):
    for yp in range(height):
      
      # Translate coordinates by center coordinate
      xp = xp - width/2
      yp = yp - height/2    
      
      # Backwards projection to source image by diving by factor instead of multiplying, rounding to ensure legal value
      x = round(xp/factor)
      y = round(yp/factor)
      
      # Translate back to image origin (0,0)
      x = x + width/2
      y = y + height/2 
      
      # Translate xp and yp back as well, to draw to correct area in canvas
      xp = xp + width/2
      yp = yp + height/2  
      
      # Only source from legal image values within dimensions of canvas
      if x < width and y < height and x > -1 and y > -1:
        dstPixels[xp,yp] = srcPixels[x,y]
	
      # Otherwise, assign to pixel to white 
      else:
        dstPixels[xp,yp] = (255,128,128)      
  
  print 'scale image by %f' % factor

  

# Set up the display and draw the current image

def display():

  # Clear window

  glClearColor ( 1, 1, 1, 0 )
  glClear( GL_COLOR_BUFFER_BIT )

  # rebuild the image

  img = currentImage.convert( 'RGB' )

  width  = img.size[0]
  height = img.size[1]

  # Find where to position lower-left corner of image

  baseX = (windowWidth-width)/2
  baseY = (windowHeight-height)/2

  glWindowPos2i( baseX, baseY )

  # Get pixels and draw

  imageData = numpy.array( list( img.getdata() ), numpy.uint8 )

  glDrawPixels( width, height, GL_RGB, GL_UNSIGNED_BYTE, imageData )

  glutSwapBuffers()


  
# Handle keyboard input

def keyboard( key, x, y ):

  global localHistoRadius

  if key == '\033': # ESC = exit
    sys.exit(0)

  elif key == 'l':
    if sys.platform != 'darwin':
      path = tkFileDialog.askopenfilename( initialdir = imgDir )
      if path:
        loadImage( path )

  elif key == 's':
    if sys.platform != 'darwin':
      outputPath = tkFileDialog.asksaveasfilename( initialdir = '.' )
      if outputPath:
        saveImage( outputPath )

  elif key == 'h':
    performHistoEqualization( localHistoRadius )

  elif key in ['+','=']:
    localHistoRadius = localHistoRadius + 1
    print 'radius =', localHistoRadius

  elif key in ['-','_']:
    localHistoRadius = localHistoRadius - 1
    if localHistoRadius < 1:
      localHistoRadius = 1
    print 'radius =', localHistoRadius

  else:
    print 'key =', key    # DO NOT REMOVE THIS LINE.  It will be used during automated marking.

  glutPostRedisplay()



# Load and save images.
#
# Modify these to load to the current image and to save the current image.
#
# DO NOT CHANGE THE NAMES OR ARGUMENT LISTS OF THESE FUNCTIONS, as
# they will be used in automated marking.


def loadImage( path ):

  global currentImage

  currentImage = Image.open( path ).convert( 'YCbCr' ).transpose( Image.FLIP_TOP_BOTTOM )


def saveImage( path ):

  global currentImage

  currentImage.transpose( Image.FLIP_TOP_BOTTOM ).convert('RGB').save( path )
  


# Handle window reshape


def reshape( newWidth, newHeight ):

  global windowWidth, windowHeight

  windowWidth  = newWidth
  windowHeight = newHeight

  glutPostRedisplay()



# Mouse state on initial click

button = None
initX = 0
initY = 0



# Handle mouse click/release

def mouse( btn, state, x, y ):

  global button, initX, initY, tempImage

  if state == GLUT_DOWN:
    tempImage = currentImage.copy()
    button = btn
    initX = x
    initY = y
  elif state == GLUT_UP:
    tempImage = None
    button = None

  glutPostRedisplay()

  

# Handle mouse motion

def motion( x, y ):

  if button == GLUT_LEFT_BUTTON:

    diffX = x - initX
    diffY = y - initY

    applyBrightnessAndContrast( 255 * diffX/float(windowWidth), 1 + diffY/float(windowHeight) )

  elif button == GLUT_RIGHT_BUTTON:

    initPosX = initX - float(windowWidth)/2.0
    initPosY = initY - float(windowHeight)/2.0
    initDist = math.sqrt( initPosX*initPosX + initPosY*initPosY )
    if initDist == 0:
      initDist = 1

    newPosX = x - float(windowWidth)/2.0
    newPosY = y - float(windowHeight)/2.0
    newDist = math.sqrt( newPosX*newPosX + newPosY*newPosY )

    scaleImage( newDist / initDist )

  glutPostRedisplay()
  


# Run OpenGL

glutInit()
glutInitDisplayMode( GLUT_DOUBLE | GLUT_RGB )
glutInitWindowSize( windowWidth, windowHeight )
glutInitWindowPosition( 50, 50 )

glutCreateWindow( 'imaging' )

glutDisplayFunc( display )
glutKeyboardFunc( keyboard )
glutReshapeFunc( reshape )
glutMouseFunc( mouse )
glutMotionFunc( motion )

glutMainLoop()
