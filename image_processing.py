import io
import random
from math import sqrt
from numpy import prod
from types import SimpleNamespace
from process import colour_convert
from functools import reduce
from PIL import Image, ImageDraw, ImageFont

# generate colour palette using the k-means algorithm
def generate_palette(img: Image, n_colours:int = 5) -> io.BytesIO:

	dist = lambda p, q: sqrt(sum((p[i] - q[i]) ** 2 for i in range(len(p))))

	def assign_points(clusters, points):
		point_lists = [[] for i in range(n_colours)]

		for point in points:
			smallest_distance = float('inf')

			for i in range(n_colours):
				distance = dist(point, clusters[i].center)

				if distance < smallest_distance:
				  smallest_distance = distance
				  idx = i

			point_lists[idx].append(point)

		return point_lists


	def get_center(points):
		n_dim = len(points[0])

		vals = [0.0 for i in range(n_dim)]
		for point in points:

			for i in range(n_dim):
			  vals[i] += point[i]

		center = [(val / len(points)) for val in vals]
		return center


	def get_clusters(points):
		clusters = [SimpleNamespace(center=point, points=[point]) for point in random.sample(points, n_colours)]

		while True:

			point_lists = assign_points(clusters, points)

			diff = 0

			for i in range(n_colours):

				if not point_lists[i]:
					continue

				old = clusters[i]
				center = get_center(point_lists[i])
				new = SimpleNamespace(center=center, points=point_lists[i])
				clusters[i] = new

				diff = max(diff, dist(old.center, new.center))

			if diff < 1.0:
				break

		return clusters


	def generate_image(colour_rgb):
		colour_hex = "".join(map(lambda x: x.upper() if isinstance(x, str) else x, "#%02x%02x%02x")) % colour_rgb
		colour_int = colour_convert(colour_hex)

		img = Image.new("RGB", (256, 256), colour_hex)
		draw = ImageDraw.Draw(img)

		r, g, b = colour_rgb
		perceptive_luminance = (0.299 * r + 0.587 * g + 0.114 * b)/255

		# white for dark background, black for light background
		font_colour = "#000000" if perceptive_luminance > 0.5 else "#FFFFFF"
		font = ImageFont.truetype("RobotoMono.ttf", 25)

		hex_w, h = draw.textsize(colour_hex, font=font)
		rgb_w, _ = draw.textsize(f"({r},{g},{b})", font=font)
		int_w, _ = draw.textsize(str(colour_int), font=font)

		draw.text(((256-hex_w)/2, ((256-h)/2)-1.5*h), colour_hex, font_colour, font)
		draw.text(((256-rgb_w)/2, ((256-h)/2)-0.5*h), f"({r},{g},{b})", font_colour, font)
		draw.text(((256-int_w)/2, ((256-h)/2)+0.5*h), str(colour_int), font_colour, font)

		return img


	def join_imgs(img1, img2):
		img = Image.new("RGB", (img1.width + img2.width, img1.height))
		img.paste(img1, (0, 0))
		img.paste(img2, (img1.width, 0))

		return img


	points = [point for index, point in img.getcolors(prod(img.size))]
	clusters = get_clusters(points)

	palette_colours = [tuple(map(int, c.center)) for c in clusters]

	palette = [generate_image(colour) for colour in palette_colours]
	palette = reduce(join_imgs, palette)

	buf = io.BytesIO()
	palette.save(buf, format="PNG")

	return buf
