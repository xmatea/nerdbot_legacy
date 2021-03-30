import io
import random
from math import sqrt, prod
from types import SimpleNamespace
from functools import reduce
from PIL import Image

# generate colour palette using k-means algorithm
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


	def join_img(img1, img2):
		img = Image.new("RGB", (img1.width + img2.width, img1.height))
		img.paste(img1, (0, 0))
		img.paste(img2, (img1.width, 0))
		return img
	

	points = [point for index, point in img.getcolors(prod(img.size))]
	clusters = get_clusters(points)
	clusters.sort(key=lambda c: len(c.points), reverse=True)

	palette_colours_rgb = [map(int, c.center) for c in clusters]
	palette_colours_hex = list(map(lambda c: '#%s' % ''.join(('%02x' % p for p in c)), palette_colours_rgb))

	palette = [Image.new("RGB", (128, 128), colour) for colour in palette_colours_hex]
	palette = reduce(join_img, palette)

	buf = io.BytesIO()
	palette.save(buf, format="PNG")

	return buf