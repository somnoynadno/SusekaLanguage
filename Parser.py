from Syntax import *

class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.DEBUG = False

		self.error = False
		self.message = ''

		self.commands = []


	def run(self):
		if self.DEBUG:
			print("Start parser")

		for line in self.tokens:
			self.handle_declaration(line)
			self.handle_assigment(line)

			if self.error:
				raise SyntaxError(self.message)


	def handle_declaration(self, line):
		if line[0].type == 'DATA_TYPE':
			try:
				if line[1].type == 'VARIABLE':
					# TODO: make declaration
					return
				else:
					self.error = True
					self.message = "Variable name expected at line {} position {}, meet '{}'".format(
									line[1].line, line[1].position, line[1].content)
			except IndexError:
				self.error = True
				self.message = "Wrong syntax at line {}".format(line[0].line)


	def handle_assigment(self, line):
		if line[0].type == 'VARIABLE':
			try:
				if line[1].type == 'EQ':
					expression = self.handle_expression(line[2:])

			except IndexError:
				self.error = True
				self.message = "Assigment expected at line {}".format(line[0].line)


	def handle_expression(self, line):
		out   = []
		stack = []

		for elem in line:
			if elem.content == '(':
				stack.append(elem)
			elif elem.content == ')':
				try:
					while True:
						e = stack.pop()
						if e.content == '(':
							break
						else:
							out.append(e)
				except IndexError:
					self.error = True
					self.message = "Incorrect number of brackets at line {}".format(elem.line)

			elif elem.content in OPERATORS:
				if not stack:
					stack.append(elem)
				else:
					# switch operator priority
					if elem.content in SECOND_PRIORITY:
						e = stack[len(stack)-1]
						if e.content in FIRST_PRIORITY:
							stack.pop()
							stack.append(elem)
							out.append(e)
						else:
							stack.append(elem)
					else:
						stack.append(elem)

			# otherwise it is variable/constant
			elif elem.type == 'VARIABLE' or elem.type == 'INTEGER_VALUE':
				out.append(elem)

			else:
				self.error = True
				self.message = "Unexpected expression at line {} position {}".format(
					elem.line, elem.position)
				return

		while stack:
			e = stack.pop()
			out.append(e)

		if self.DEBUG:
			print('Handled expression:')
			print(out)

		return out

