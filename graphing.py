import io
import numpy as np
import matplotlib.pyplot as plt
from typing import Callable, List, Tuple
from PIL import Image
import mathparser as mp
import re

# plot equation on cartesian graph and return png byte array
def static_cartesian(expr: str, x_range: Tuple[float, float]) -> io.BytesIO:
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
	y = mp.eval_2d(expr, {"x": x})

	ax.plot(x, y)
	fig.text(0.02, 0.92, f"y = {expr}", fontsize=16)

	buf = io.BytesIO()
	plt.savefig(buf, format="png")

	return buf


# plot equation on cartesian graph and return gif byte array of animating a value over specified range
def animated_cartesian(expr: str, x_range: Tuple[float, float], a_range: Tuple[float, float]) -> io.BytesIO:
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
	a1, a2 = a_range

	x = np.linspace(x1, x2, 10*int(x2-x1))
	a = np.linspace(a1, a2, int(a2-a1)+1)


	plt.xlim(x1, x2)
	plt.ylim(min(0, mp.evaluate(expr, {"x": x1, "a": a2})), mp.evaluate(expr, {"x": x2, "a": a2}))

	plt.autoscale(False)

	frames = []
	for a_val in a:
		y = mp.eval_2d(expr, {"a": a_val, "x": x})

		curve = ax.plot(x, y)
		plt.title(f"a = {a_val}", bbox={"facecolor": "black", "alpha": 0.75, "pad": 5}, loc="left", color="white")

		_buf = io.BytesIO()
		plt.savefig(_buf, format="png")
		frames.append(_buf)

		curve.pop(0).remove()

	buf = io.BytesIO()
	frames = [Image.open(frame) for frame in frames]
	frames[0].save(buf, format="GIF", save_all=True, append_images=frames[1:], duration=250, loop=0)

	return buf


# plot equation on polar graph and return png byte array
def static_polar(expr: str, theta_range: Tuple[float, float]) -> io.BytesIO:
	fig, ax = plt.subplots(subplot_kw={"projection": "polar"})

	ax.grid(True, which="both")

	theta1, theta2 = theta_range
	theta = np.linspace(theta1, theta2, 36000)

	r = mp.eval_2d(expr, {"theta": theta}, polar=True)

	ax.plot(r, theta)
	fig.text(0.02, 0.92, f"r = {expr}", fontsize=16)

	buf = io.BytesIO()
	plt.savefig(buf, format="png")

	return buf


# plot equation on polar graph and return gif byte array of animating a value over specified range
def animated_polar(expr: str, theta_range: Tuple[float, float], a_range: Tuple[float, float]) -> io.BytesIO:
	fig, ax = plt.subplots(subplot_kw={"projection": "polar"})

	ax.grid(True, which="both")

	theta1, theta2 = theta_range
	a1, a2 = a_range

	theta = np.linspace(theta1, theta2, 36000)
	a = np.linspace(a1, a2, int(a2-a1)+1)

	frames = []
	for a_val in a:
		r = mp.eval_2d(expr, {"a": a_val, "theta": theta}, polar=True)

		curve = ax.plot(r, theta)
		plt.title(f"a = {a_val}", bbox={"facecolor": "black", "alpha": 0.75, "pad": 5}, loc="left", color="white")

		_buf = io.BytesIO()
		plt.savefig(_buf, format="png")
		frames.append(_buf)

		curve.pop(0).remove()

	buf = io.BytesIO()
	frames = [Image.open(frame) for frame in frames]
	frames[0].save(buf, format="GIF", save_all=True, append_images=frames[1:], duration=250, loop=0)

	return buf


def static_surface(expr: str, x_range: Tuple[float, float], y_range: Tuple[float, float]) -> io.BytesIO:
	fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

	x1, x2 = x_range
	y1, y2 = y_range

	point_count = max(10*int(x2-x1), 10*int(y2-y1))

	x = np.linspace(x1, x2, point_count)
	y = np.linspace(y1, y2, point_count)

	xv, yv = np.meshgrid(x, y)

	z = mp.eval_3d(expr, {"x": x, "y": y})
	z = np.reshape(z, np.shape(xv))

	ax.plot_surface(xv, yv, z)

	buf = io.BytesIO()
	plt.savefig(buf, format="png")

	return buf


def static_surface_rotate(expr: str, x_range: Tuple[float, float], y_range: Tuple[float, float]) -> io.BytesIO:
	fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

	x1, x2 = x_range
	y1, y2 = y_range

	point_count = max(10*int(x2-x1), 10*int(y2-y1))

	x = np.linspace(x1, x2, point_count)
	y = np.linspace(y1, y2, point_count)

	xv, yv = np.meshgrid(x, y)

	z = mp.eval_3d(expr, {"x": x, "y": y})
	z = np.reshape(z, np.shape(xv))

	ax.plot_surface(xv, yv, z)

	frames = []
	for a in range(0, 360, 18):
		ax.view_init(30, a)

		_buf = io.BytesIO()
		plt.savefig(_buf, format="png")
		frames.append(_buf)

	buf = io.BytesIO()
	frames = [Image.open(frame) for frame in frames]
	frames[0].save(buf, format="GIF", save_all=True, append_images=frames[1:], duration=200, loop=0)

	return buf


def animated_surface(expr: str, x_range: Tuple[float, float], y_range: Tuple[float, float], a_range: Tuple[float, float]) -> io.BytesIO:
	fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

	x1, x2 = x_range
	y1, y2 = y_range
	a1, a2 = a_range

	point_count = max(10*int(x2-x1), 10*int(y2-y1))

	x = np.linspace(x1, x2, point_count)
	y = np.linspace(y1, y2, point_count)
	a = np.linspace(a1, a2, int(a2-a1)+1)

	xv, yv = np.meshgrid(x, y)

	plt.xlim(x1, x2)
	plt.ylim(y1, y2)
	ax.set_zlim(min(0, mp.evaluate(expr, {"x": x1, "y": y1, "a": a2})), mp.evaluate(expr, {"x": x2, "y": y2, "a": a2}))

	frames = []
	for a_val in a:
		z = mp.eval_3d(expr, {"x": x, "y": y, "a": a_val})
		z = np.reshape(z, np.shape(xv))

		surface = ax.plot_surface(xv, yv, z)
		plt.title(f"a = {a_val}", bbox={"facecolor": "black", "alpha": 0.75, "pad": 5}, loc="left", color="white")

		_buf = io.BytesIO()
		plt.savefig(_buf, format="png")
		frames.append(_buf)

		surface.remove()

	buf = io.BytesIO()
	frames = [Image.open(frame) for frame in frames]
	frames[0].save(buf, format="GIF", save_all=True, append_images=frames[1:], duration=250, loop=0)

	return buf


def animated_surface_rotate(expr: str, x_range: Tuple[float, float], y_range: Tuple[float, float], a_range: Tuple[float, float]) -> io.BytesIO:
	fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

	x1, x2 = x_range
	y1, y2 = y_range
	a1, a2 = a_range

	point_count = max(10*int(x2-x1), 10*int(y2-y1))

	x = np.linspace(x1, x2, point_count)
	y = np.linspace(y1, y2, point_count)
	a = np.linspace(a1, a2, 60)

	xv, yv = np.meshgrid(x, y)

	plt.xlim(x1, x2)
	plt.ylim(y1, y2)
	ax.set_zlim(min(0, mp.evaluate(expr, {"x": x1, "y": y1, "a": a2})), mp.evaluate(expr, {"x": x2, "y": y2, "a": a2}))

	frames = []
	for angle in range(0, 360, 18):
		a_val = a[angle//18]

		z = mp.eval_3d(expr, {"x": x, "y": y, "a": a_val})
		z = np.reshape(z, np.shape(xv))

		surface = ax.plot_surface(xv, yv, z)
		plt.title(f"a = {a_val}", bbox={"facecolor": "black", "alpha": 0.75, "pad": 5}, loc="left", color="white")

		ax.view_init(30, angle)

		_buf = io.BytesIO()
		plt.savefig(_buf, format="png")
		frames.append(_buf)

		surface.remove()

	buf = io.BytesIO()
	frames = [Image.open(frame) for frame in frames]
	frames[0].save(buf, format="GIF", save_all=True, append_images=frames[1:], duration=300, loop=0)

	return buf


#remove from here down, just for testing
def display_gif(gif: io.BytesIO) -> None:
	import pyglet

	gif.seek(0)

	animation = pyglet.image.load_animation("noname.gif", file=gif)
	sprite = pyglet.sprite.Sprite(animation)

	win = pyglet.window.Window(width=sprite.width, height=sprite.height)
	pyglet.gl.glClearColor(0, 0, 0, 1)

	@win.event
	def on_draw() -> None:
		win.clear()
		sprite.draw()

	pyglet.app.run()


def main() -> None:
	display_gif(animated_surface_rotate("a(x+y)", (-10, 10), (-10, 10), (-10, 10)))


if __name__ == "__main__":
	main()