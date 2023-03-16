# Upper limit to the number of extracted colors presented in the output.
COLOR_LIMIT = 12

# Group colors to limit the output and give a better visual representation.
# Based on a scale from 0 to 100. Where 0 won't group any color and 100 will group all colors into one.
COLOR_TOLERANCE = 15

# Image Filter for Mask to Smooth Edges
# lower = more image data but jagged edges
# higher = crops more image but cleaner edges
MASK_SMOOTH_SIZE = 8

# Utility Constants ( must be divisible by 32, best quality is 1024, but best performance is 512  )
MAX_IMAGE_SIZE = 512

# Ignore Colors that fall below this percent within the image
MIN_COLOR_PERCENT = 0.035