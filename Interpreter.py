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


class Interpreter:
	def __init__(self, commands):
		self.commands = commands
		self.current_command_pos = 0
		self.DEBUG = False
		self.message = ''

		self.variables = {}

		self.condition_stack = []

		self.while_pointers_stack = []


	def run(self):
		if self.DEBUG:
			print("Start interpreter")

		while self.current_command_pos < len(self.commands):
			command = self.commands[self.current_command_pos]

			self.handle_end(command)
			self.handle_if(command)

			if len(self.condition_stack) == 0 or self.check_condition_stack():
				self.handle_declaration(command)
				self.handle_assigment(command)
				self.handle_print(command)
				self.handle_endwhile(command)
				self.handle_while(command)

			self.current_command_pos += 1

			if self.DEBUG:
				print('while pointers stack:')
				print(self.while_pointers_stack)

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
				v = self.get_array_value(elem)
				stack.append(v)
			if elem.type == 'VARIABLE':
				var = elem.content
				if self.variables.get(var) == None:
					self.message = "Variable '{}' is not defined (line {})"
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
				# print(array_name + ": " + str(self.variables[array_name].value))
        
        
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


	def handle_if(self, command):
		if (command[0].type == 'IF'):
			if (len(self.condition_stack) == 0 or self.check_condition_stack()):
				# Короче, тема такая: мы отмечаем любые скобки в condition stack. даже те, которые 
				# находятся в if (False){ if(){} <- вот эти скобки тоже отмечаем }
				# НО выполняем все, смотря на весь стек. если есть в стеке хоть один False
				# То ничего не выполняем. Но стек продолжаем забивать содержимым,
				# если видим if или else, а также удалять из стека, когда видим }
				operator_pos = self.find_in_line(command, 'C_OPERATOR')

				first_exp = command[2:operator_pos]
				second_exp = command[operator_pos + 1:len(command) - 3]
				
				first_res = self.count_expression(first_exp)
				second_res = self.count_expression(second_exp)
				res = self.compare(first_res, second_res, command[operator_pos].content)
				if (res):
					self.condition_stack.append(True)
				else:
					self.condition_stack.append(False)
			else:
				self.condition_stack.append(False)

	
	def handle_end(self, command):
		if (command[0].type == 'END'):
			condition = self.condition_stack.pop() 

			# если есть else, то стек в любом случае забивется true или false
			# если предыдущее условие было ложным, но при этом мы находимся в if(true), то идем в else
			# ну и соответственно добавляем True
			if (len(command) > 1 and condition == False and self.check_condition_stack()):
				print ("ELSE STATEMENT")
				self.condition_stack.append(True)
			elif (len(command) > 1 and (condition or self.check_condition_stack() == False)):
				# Ну а если предыдущее условие давало True или мы находимся в if(false), то в else не идем
				self.condition_stack.append(False)
			

	def compare(self, first, second, operator):
		if (operator == '=='):
			if (first == second):
				return True
		elif (operator == '>'):
			if (first > second):
				return True
		elif (operator == '<'):
			if (first < second):
				return True
		elif (operator == '!='):
			if (first != second):
				return True
		return False


	def find_in_line(self, line, type_to_find):
		for i in range(len(line)):
			if (line[i].type == type_to_find):
				return i


	def check_condition_stack(self):
		for i in self.condition_stack:
			if (i == False):
				return False
		return True


	def handle_while(self, command):
		if (command[0].type == 'WHILE'):

			operator_pos = self.find_in_line(command, 'C_OPERATOR')

			first_exp = command[2:operator_pos]
			second_exp = command[operator_pos + 1:len(command) - 3]
			
			first_res = self.count_expression(first_exp)
			second_res = self.count_expression(second_exp)

			res = self.compare(first_res, second_res, command[operator_pos].content)

			if res:
				# just remember the cycle position
				self.while_pointers_stack.append(self.current_command_pos)
			else:
				# pass lines until 'endwhile' not found
				while True:
					self.current_command_pos += 1

					if self.current_command_pos >= len(self.commands):
						self.message = "'}endwhile' expected, but not found"
						raise RuntimeError(self.message)

					command = self.commands[self.current_command_pos]

					if command[0].type == 'ENDWHILE':
						break


	def handle_endwhile(self, command):
		if command[0].type == 'ENDWHILE':
			# get previous line position, because it will be incremented in next operation
			try:
				self.current_command_pos = self.while_pointers_stack.pop() - 1
			except IndexError:
				if self.DEBUG:
					print('empty while pointer stack')
				return
				