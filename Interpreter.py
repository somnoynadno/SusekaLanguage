import re

from SusekaException import *
from Syntax import *


array_name_regexp = r'\w+\['
array_index_regexp = r'\[\w+\]'
integer_regexp = r'\d+'


class Variable:
	def __init__(self, vartype, value):
		self.vartype = vartype
		self.value = value

	def __repr__(self):
		return str(self.vartype) + ': ' + str(self.value)


# TODO: refactoring =)
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

		if self.DEBUG:
			print("Variable table")
			print(self.variables)


	def handle_declaration(self, command):
		if command[0].type == 'DATA_TYPE':
			if command[1].type == 'ARRAY_VARIABLE':
				self.declare_array(command)
			else:
				self.declare_variable(command)


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

		elif command[0].type == 'ARRAY_VARIABLE':
			arr_var = command[0].content
			array_name = re.findall(array_name_regexp, arr_var)[0]
			# drop '['
			array_name = array_name[:len(array_name)-1]

			array_index = re.findall(array_index_regexp, arr_var)[0]
			# drop '[' and ']'
			array_index = array_index[1:len(array_index)-1]

			if re.findall(integer_regexp, array_index):
				array_index = int(array_index)
			else:
				# get array index from variable
				if self.variables.get(array_index) == None:
					self.message = "Variable '{}' is not declared (line {})".format(
									array_index, command[0].line)
					raise RuntimeError(self.message)
				else:
					if self.variables.get(array_index).vartype != 'int':
						self.message = "Variable '{}' must be integer (line {})".format(
										array_index, command[0].line)
						raise RuntimeError(self.message)

					array_index = self.variables.get(array_index).value

			
			if self.variables.get(array_name) == None:
				self.message = "Array '{}' is not declared (line {})".format(
								array_name, command[0].line)
				raise RuntimeError(self.message)

			value = self.count_expression(command[1])
			try:
				self.variables.get(array_name).value[array_index].value = value
			except IndexError:
				self.message = "Index is out of range (line {})".format(
								array_name, command[0].line)
				raise RuntimeError(self.message)


	def count_expression(self, expression):
		if self.DEBUG:
			print("Counting expression:")
			print(expression)

		stack = []
		for elem in expression:
			if elem.type == 'ARRAY_VARIABLE':
				v = get_array_value(elem)
				stack.append(v)
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
			if command[1].type == 'ARRAY_VARIABLE' or command[1].type == 'VARIABLE':
				var = command[1].content

				if self.variables.get(var) == None:
					self.message = "Variable '{}' is not declared (line {})".format(
									var, command[0].line)
					raise RuntimeError(self.message)
				else:
					print(var + ": " + str(self.variables[var].value))


	def declare_variable(self, command):
		var     = command[1].content
		vartype = command[0].content

		if self.variables.get(var) != None:
			self.message = "Variable '{}' already declared (line {})".format(
							var, command[0].line)
			raise RuntimeError(self.message)

		else:
			v = Variable(vartype, None)
			self.variables[var] = v


	def declare_array(self, command):
		arr_var = command[1].content
		vartype = command[0].content

		array_name = re.findall(array_name_regexp, arr_var)[0]
		# drop '['
		array_name = array_name[:len(array_name)-1]

		array_index = re.findall(array_index_regexp, arr_var)[0]
		# drop '[' and ']'
		array_index = array_index[1:len(array_index)-1]

		if self.variables.get(array_name) != None:
			self.message = "Array '{}' already defined (line {})".format(
							array_index, command[0].line)
			raise RuntimeError(self.message)

		if re.findall(integer_regexp, array_index):
			array_index = int(array_index)
		else:
			# get array index from variable
			if self.variables.get(array_index) == None:
				self.message = "Variable '{}' is not declared (line {})".format(
								array_index, command[0].line)
				raise RuntimeError(self.message)
			else:
				if self.variables.get(array_index).vartype != 'int':
					self.message = "Variable '{}' must be integer (line {})".format(
									array_index, command[0].line)
					raise RuntimeError(self.message)

				array_index = self.variables.get(array_index).value

		if array_index < 0:
			self.message = "Index value must be positive, meet {} (line {})".format(
							value, command[0].line)
			raise RuntimeError(self.message)

		temp = []
		for i in range(array_index):
			v = Variable(vartype, None)
			temp.append(v)

		v = Variable('array', temp)
		self.variables[array_name] = v


	def get_array_value(self, token):
		arr_var = token.content
		array_name = re.findall(array_name_regexp, arr_var)[0]
		# drop '['
		array_name = array_name[:len(array_name)-1]

		array_index = re.findall(array_index_regexp, arr_var)[0]
		# drop '[' and ']'
		array_index = array_index[1:len(array_index)-1]

		if re.findall(integer_regexp, array_index):
			array_index = int(array_index)
		else:
			# get array index from variable
			if self.variables.get(array_index) == None:
				self.message = "Variable '{}' is not declared (line {})".format(
								array_index, token.line)
				raise RuntimeError(self.message)
			else:
				if self.variables.get(array_index).vartype != 'int':
					self.message = "Variable '{}' must be integer (line {})".format(
									array_index, token.line)
					raise RuntimeError(self.message)

				array_index = self.variables.get(array_index).value

		
		if self.variables.get(array_name) == None:
			self.message = "Array '{}' is not declared (line {})".format(
							array_name, token.line)
			raise RuntimeError(self.message)

		try:
			value = self.variables.get(array_name).value[array_index].value
		except IndexError:
			self.message = "Index is out of range (line {})".format(
							token.line)
			raise RuntimeError(self.message)

		return value
