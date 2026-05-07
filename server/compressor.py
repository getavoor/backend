from PIL import Image
from pathlib import Path
import math

TARGET_RES = 500

def compress_image(path: Path = None, image = None, out_folder: Path = None) -> Path:
	"""
	Compresses and crops an image to a square profile picture.
	"""

	# load the image
	if image:
		im = Image.open(image)
	else:
		im = Image.open(path)
	# convert the image to RGB (because it will be saved as a JPEG for more compression)
	im = im.convert('RGB')
	# get the resolution
	width, height = im.size
	# if it's already square and of the target resolution, return the image's path
	if width == height and height == TARGET_RES:
		return path
	# throw an exception if the image is too small
	if width < TARGET_RES or height < TARGET_RES:
		raise ValueError("Image is too small")
	# if it's larger, resize it, preserving the aspect ratio
	else:
		# calculate the new size
		i = min(TARGET_RES/width, TARGET_RES/height)
		a = max(TARGET_RES/width, TARGET_RES/height)
		width = math.ceil(width*a)
		height = math.ceil(height*a)
		im.thumbnail((width, height), Image.LANCZOS)
	# if it's not square, crop it
	if width != height:
		left = (width - TARGET_RES)/2
		top = (height - TARGET_RES)/2
		right = (width + TARGET_RES)/2
		bottom = (height + TARGET_RES)/2
		im = im.crop((left, top, right, bottom))
	# if no out folder was provided, use the provided file's parent
	if not out_folder:
		out_folder = path.parent
	# save the new image
	new_path = out_folder / (path.name + '_compressed.jpg')
	im.save(new_path)
	# return the path
	return Path(new_path)
