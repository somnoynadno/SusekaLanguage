from SusekaException import *
from Syntax import *


class Variable:
	def __init__(self, vartype, value):
		self.vartype = vartype
		self.value = value


class Interpreter:
	def __init__(self, commands):
		self.commands = commands
		self.DEBUG = False
		self.message = ''

		self.variables = {}


	def run(self):
		if self.DEBUG:
			print("Start interpreter")

		for command in self.commands:
			self.handle_declaration(command)
			self.handle_assigment(command)
			self.handle_print(command)


	def handle_declaration(self, command):
		if command[0].type == 'DATA_TYPE':
			var     = command[1].content
			vartype = command[0].content

			if self.variables.get(var) != None:
				self.message = "Variable '{}' already declared (line {})".format(
								var, command[0].line)
				raise RuntimeError(self.message)

			else:
				v = Variable(vartype, None)
				self.variables[var] = v


	def handle_assigment(self, command):
		if command[0].type == 'VARIABLE':
			var = command[0].content
			if self.variables.get(var) == None:
				self.message = "Variable '{}' is not defined (line {})".format(
								var, command[0].line)
				raise RuntimeError(self.message)

			value = self.count_expression(command[1])
			
			if self.variables[var].vartype == 'bool':
				self.variables[var].value = bool(value)
			else:
				self.variables[var].value = int(value)


	def count_expression(self, expression):
		if self.DEBUG:
			print("Counting expression:")
			print(expression)

		stack = []
		for elem in expression:
			if elem.type == 'VARIABLE':
				var = elem.content
				if self.variables.get(var) == None:
					self.message = "Variable '{}' is not defined (line {})".format(
									var, command[0].line)
					raise RuntimeError(self.message)

				stack.append(self.variables[var].value)
			elif elem.type == 'INTEGER_VALUE':
				stack.append(int(elem.content))
			elif elem.type == 'BOOL_VALUE':
				if elem.content == 'false':
					stack.append(False)
				else:
					stack.append(True)
			elif elem.type == 'OPERATOR' or elem.type == 'B_OPERATOR':
				try:
					e1 = stack.pop()
					e2 = stack.pop()
				except IndexError:
					self.message = "Invalid expression at line {}".format(
									elem.line)
					raise RuntimeError(self.message)					

				if elem.content == '-':
					stack.append(e2 - e1)
				elif elem.content == '+':
					stack.append(e2 + e1)
				elif elem.content == '*':
					stack.append(e2 * e1)
				elif elem.content == '/':
					stack.append(e2 // e1)
				elif elem.content == '%':
					stack.append(e2 % e1)
				elif elem.content == '||':
					stack.append(e2 or e1)
				elif elem.content == '&&':
					stack.append(e2 and e1)

			if self.DEBUG:
				print(stack)

		if len(stack) != 1:
			if self.DEBUG:
				print("Values on stack:")
				print(stack)
			self.message = "Check your expression at line {}".format(
							expression[0].line)
			raise RuntimeError(self.message)

		return stack[0]


	def handle_print(self, command):
		if command[0].type == 'PRINT':
			var = command[1].content

			if self.variables.get(var) == None:
				self.message = "Variable '{}' is not declared (line {})".format(
								var, command[0].line)
				raise RuntimeError(self.message)
			else:
				print(var + ": " + str(self.variables[var].value))