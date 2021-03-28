import io
import numpy as np
import matplotlib.pyplot as plt
from typing import Callable, List, Tuple
from PIL import Image

# plot equation on cartesian graph and return png byte array
def static_cartesian(func: Callable[[np.ndarray], np.ndarray], x_range: Tuple[float, float]) -> io.BytesIO:
	fig, ax = plt.subplots()

	ax.grid(True, which="both")

	# set up spines
	ax.spines["left"].set_position("zero")
	ax.spines["right"].set_color("none")
	ax.yaxis.tick_left()
	ax.spines["bottom"].set_position("zero")
	ax.spines["top"].set_color("none")
	ax.xaxis.tick_bottom()

	x1, x2 = x_range
	x = np.linspace(x1, x2, 10*int(x2-x1))
	y = func(x)

	ax.plot(x, y)

	buf = io.BytesIO()
	plt.savefig(buf, format="png")

	return buf


# plot equation on cartesian graph and return gif byte array of animating specified value over specified range
def animated_cartesian(func: Callable[[np.ndarray], np.ndarray], x_range: Tuple[float, float], a_range: Tuple[float, float]) -> io.BytesIO:
	fig, ax = plt.subplots()

	ax.grid(True, which="both")

	# set up spines
	ax.spines["left"].set_position("zero")
	ax.spines["right"].set_color("none")
	ax.yaxis.tick_left()
	ax.spines["bottom"].set_position("zero")
	ax.spines["top"].set_color("none")
	ax.xaxis.tick_bottom()

	a1, a2 = a_range
	a = range(a1, a2+1)

	x1, x2 = x_range
	x = np.linspace(x1, x2, 10*int(x2-x1))

	plt.xlim(x1, x2)
	plt.ylim(min(0, func(x1, a2)), func(x2, a2))

	plt.autoscale(False)

	frames = []
	for a_val in a:
		y = func(x, a_val)

		curve = ax.plot(x, y)
		plt.title(f"a = {a_val}", bbox={"facecolor": "black", "alpha": 0.75, "pad": 5}, loc="left", color="white")

		_buf = io.BytesIO()
		plt.savefig(_buf, format="png")

		frames.append(_buf)

		curve.pop(0).remove()

	buf = io.BytesIO()
	frames = [Image.open(frame) for frame in frames]
	frames[0].save(buf, format="GIF", save_all=True, append_images=frames[1:], duration=200, loop=0)

	return buf


# plot equation on polar graph and return png byte array
def static_polar(func: Callable[[np.ndarray], np.ndarray], theta_range: Tuple[float, float]) -> io.BytesIO:
	fig, ax = plt.subplots(subplot_kw={"projection": "polar"})

	ax.grid(True, which="both")

	theta1, theta2 = theta_range
	theta = np.linspace(theta1, theta2, 10*int(theta2-theta1))
	r = func(theta)

	ax.plot(r, theta)

	buf = io.BytesIO()
	plt.savefig(buf, format="png")

	return buf


#remove, just for testing
def main() -> None:
	graph = animated_cartesian(lambda x, a: np.sin(a/x), (-np.pi*2, np.pi*2), (1, 10))

if __name__ == "__main__":
	main()