from SusekaException import *
from Syntax import *

class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.DEBUG = False
		self.message = ''

		self.commands = []


	def run(self):
		if self.DEBUG:
			print("Start parser")

		for line in self.tokens:
			self.handle_comment(line)
			self.handle_declaration(line)
			self.handle_assigment(line)
			self.handle_print(line)

		if self.DEBUG:
			print("Commands:")
			for command in self.commands:
				print(command)
				print()
				

	def handle_comment(self, line):
		if line[0].type == 'COMMENT':
			return


	def handle_declaration(self, line):
		if line[0].type == 'DATA_TYPE':
			try:
				if line[1].type == 'VARIABLE' or line[1].type == 'ARRAY_VARIABLE':
					self.commands.append(line)
				else:
					self.message = "Variable name expected at line {} position {}, meet '{}'".format(
									line[1].line, line[1].position, line[1].content)
					raise SyntaxError(self.message)

			except IndexError:
				self.message = "Wrong syntax at line {}".format(line[0].line)
				raise SyntaxError(self.message)


	def handle_assigment(self, line):
		if line[0].type == 'VARIABLE' or line[0].type == 'ARRAY_VARIABLE':
			try:
				if line[1].type == 'EQ':
					expression = self.handle_expression(line[2:])

					out = []
					out.append(line[0])
					out.append(expression)
					self.commands.append(out)

			except IndexError:
				self.message = "Assigment expected at line {}".format(line[0].line)
				raise SyntaxError(self.message)


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
					self.message = "Incorrect number of brackets at line {}".format(elem.line)
					raise SyntaxError(self.message)

			elif elem.content in BINARY_OPERATORS:
				if not stack:
					stack.append(elem)
				else:
					e = stack[len(stack)-1]
					if e.content in OPERATORS:
						stack.pop()
						stack.append(elem)
						out.append(e)
					else:
						stack.append(elem)

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
			elif elem.type == 'VARIABLE' or elem.type == 'INTEGER_VALUE' or elem.type == 'BOOL_VALUE' or elem.type == 'ARRAY_VARIABLE':
				out.append(elem)

			else:
				self.message = "Unexpected expression at line {} position {}".format(
					elem.line, elem.position)
				raise SyntaxError(self.message)

		while stack:
			e = stack.pop()
			if e.type == 'OPEN_BRACKET':
				self.message = "Wrong number of brackets at line {}".format(
					e.line)
				raise SyntaxError(self.message)
			out.append(e)

		if self.DEBUG:
			print('Handled expression:')
			print(out)

		return out


	def handle_print(self, line):
		if line[0].type == 'PRINT':
			if len(line) == 1 or len(line) > 2:
				self.message = "Wrong print sintax at line {}. Correct is 'print <variable>'.".format(
								line[0].line)
				raise SyntaxError(self.message)
			if line[1].type != 'VARIABLE' and line[1].type != 'ARRAY_VARIABLE':
				self.message = "Variable expected at line {} position {}".format(
								line[0].line, line[0].position)
				raise SyntaxError(self.message)

			self.commands.append(line)


