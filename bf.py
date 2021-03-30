def run(code):
	states = [0]
	pointer = 0
	index = 0
	loop = []

	output = ""

	while index < len(code):
		cmd = code[index]

		if cmd == ">":
			if pointer == len(states)-1:
				states.append(0)

			pointer += 1

		elif cmd == "<":
			if pointer == 0:
				raise NotImplementedError

			pointer -= 1

		elif cmd == "+":
			if states[pointer] == 255:
				states[pointer] = 0
			else:
				states[pointer] += 1

		elif cmd == "-":
			if states[pointer] == 0:
				states[pointer] = 255
			else:
				states[pointer] -= 1

		elif cmd == "[":
			if states[pointer] == 0:
				while code[index] != "]":
					index += 1
			else:
				loop.append(index)

		elif cmd == "]":
			if states[pointer] != 0:
				index = loop[-1]
			else:
				loop.pop()

		elif cmd == ".":
			output += chr(states[pointer])

		#elif cmd == ",":
			#states[pointer] = ord(input(">>")[0])

		#index += 1

	return output

if __name__ == "__main__":
	print(run("--[>--->->->++>-<<<<<-------]>--.>---------.>--..+++.>----.>+++++++++.<<.+++.------.<-.>>+."))