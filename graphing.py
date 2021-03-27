import io
import numpy as np
import matplotlib.pyplot as plt
from typing import Callable

from PIL import Image #remove, just for testing

# plot equation on cartesian graph and return png byte array
def create_graph_cartesian(func: Callable[[np.ndarray], np.ndarray], x_start: float, x_end: float) -> io.BytesIO:
	fig, ax = plt.subplots()

	ax.grid(True, which="both")

	# set up spines
	ax.spines["left"].set_position("zero")
	ax.spines["right"].set_color("none")
	ax.yaxis.tick_left()
	ax.spines["bottom"].set_position("zero")
	ax.spines["top"].set_color("none")
	ax.xaxis.tick_bottom()


	x = np.linspace(x_start, x_end, 10*int(x_end-x_start))
	y = func(x)

	ax.plot(x, y)

	buf = io.BytesIO()
	plt.savefig(buf, format="png")

	return buf


# plot equation on polar graph and return png byte array
def create_graph_polar(func: Callable[[np.ndarray], np.ndarray], theta_start: float, theta_end: float) -> io.BytesIO:
	fig, ax = plt.subplots(subplot_kw={"projection": "polar"})

	ax.grid(True, which="both")

	theta = np.linspace(theta_start, theta_end, 10*int(theta_end-theta_start))
	r = func(theta)

	ax.plot(r, theta)

	buf = io.BytesIO()
	plt.savefig(buf, format="png")

	return buf


#remove, just for testing
def main() -> None:
	graph = create_graph_polar(lambda theta: np.cos(theta), 0, 2*np.pi)
	im = Image.open(graph)
	im.show()


if __name__ == "__main__":
	main()