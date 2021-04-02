import cexprtk
import numpy as np

class Expression(cexprtk.Expression):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def value(self, *args, **kwargs):
		v = round(super().value(*args, **kwargs), 8)

		try:
			v = int(v) if v == int(v) else v
		except OverflowError:
			pass

		return v if v else 0


def evaluate(expr, vars={}):
	st = cexprtk.Symbol_Table(vars, add_constants=True)
	expr = Expression(expr, st)

	return expr.value()


def eval_2d(expr, vars, polar=False):
	var = "theta" if polar else "x"

	if "a" in vars.keys():
		st = cexprtk.Symbol_Table({"a": vars["a"], var: 1}, add_constants=True)
	else:
		st = cexprtk.Symbol_Table({var: 1}, add_constants=True)

	expr = Expression(expr, st)

	values = []
	for val in vars[var]:

		st.variables[var] = val
		values.append(expr.value())

	return values


def eval_3d(expr, vars):
	if "a" in vars.keys():
		st = cexprtk.Symbol_Table({"a": vars["a"], "x": 1, "y": 1}, add_constants=True)
	else:
		st = cexprtk.Symbol_Table({"x": 1, "y": 1}, add_constants=True)

	expr = Expression(expr, st)

	x_values = vars["x"].tolist()
	y_values = vars["y"].tolist()

	values = []
	for x_val in x_values:

		vals = []
		for y_val in y_values:

			st.variables["x"] = x_val
			st.variables["y"] = y_val

			vals.append(expr.value())

		values.append(vals)

	return values


if __name__ == "__main__":
	print(evaluate(input(">> ")))