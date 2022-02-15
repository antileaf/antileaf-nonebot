from PIL import Image as im
import os

for name in os.listdir('.'):
	# print(image)

	if name.endswith('.jfif'):
		image = im.open(name, 'r')
		cropped = image.crop((221, 60, 745, 497))
		cropped.save(name[:-5] + '.png', 'png')

		image.close()