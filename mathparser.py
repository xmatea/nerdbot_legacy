import pyparsing as pp
from plusminus import ArithmeticParser
from typing import Union, Tuple, List
from numpy import ndarray
import math

class MathParser(ArithmeticParser):
	def customize(self):
		super().customize()

		golden_ratio = (1.0 + math.sqrt(5)) / 2.0

		self.initialize_variable("pi", math.pi)
		self.initialize_variable("e", math.e)
		self.initialize_variable("phi", golden_ratio)
		self.initialize_variable("golden_ratio", golden_ratio)

		self.add_function("sin", 1, math.sin)
		self.add_function("cos", 1, math.cos)
		self.add_function("tan", 1, math.tan)
		self.add_function("asin", 1, math.asin)
		self.add_function("acos", 1, math.acos)
		self.add_function("atan", 1, math.atan)
		self.add_function("sinh", 1, math.sinh)
		self.add_function("cosh", 1, math.cosh)
		self.add_function("tanh", 1, math.tanh)

		self.add_function("ln", 1, lambda x: math.log(x))
		self.add_function("log", (1, 2), math.log)

		# avoid clash with '!=' operator
		factorial_operator = (~pp.Literal("!=") + "!").setName("!")
		self.add_operator(
			factorial_operator, 1, ArithmeticParser.LEFT, self.factorial
		)
		self.add_operator("^", 2, ArithmeticParser.LEFT, lambda x, y: math.pow(x, y))


	def factorial(self, x: Union[int, float]) -> Union[int, float]:
		if x < 0:
			raise ValueError("value must be greater than or equal to 0.")

		else:
			if isinstance(x, int):
				return math.factorial(x)
			elif isinstance(x, float):
				return math.gamma(x+1)
			else:
				raise TypeError("value must be numerical.")


	def evaluate(self, expr: str, *values: Union[Tuple[str, List], Tuple[str, float]]) -> Union[float, List]:
		if len(values) == 0:
			return super().evaluate(expr)

		else: # MAKE IT WORK WITH MULTIPLE UNKNOWNS
			return [self.evaluate(expr.replace(values[0][0], str(values[0][1][i]) if values[0][1][i] >= 0 else f"({values[0][1][i]})")) for i in range(len(values[0][1]))]


if __name__ == "__main__":
	mp = MathParser()

	print(mp.evaluate(""))