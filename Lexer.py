import re
import string

from Token import Token
from SusekaException import *
from Syntax import *


ASCII_LETTERS = list(string.ascii_letters)

array_regexp = r'^\w+\[\w+\]$'
integer_regexp = r'^-?\d+$'

class Lexer:
	def __init__(self, program):
		self.program = program
		self.tokens = []
		self.DEBUG = False


	def run(self):
		if self.DEBUG:
			print("Start lexer")

		self.split_tokens()
		self.tokens_analysis()
		self.structurize_tokens()


	def split_tokens(self):
		line = 1
		position = 0
		content = ''

		if self.DEBUG:
			print("Program:")
			print(self.program)

		for elem in self.program:
			if elem == ' ' or elem == '\n':
				content = content.strip()
				if content != '':
					t = Token(position - len(content), line, content)
					content = ''
					self.tokens.append(t)

			if elem == '\n':
				line += 1
				position = 0

				t = Token(position, line, '<endln>')
				self.tokens.append(t)

			position += 1
			content += elem


	def tokens_analysis(self):
		for token in self.tokens:
			c = token.content
			if   c == 'if':
				token.type = 'IF'
			elif c == 'else':
				token.type = 'else'
			elif c == 'while':
				token.type = 'WHILE'
			elif c == 'print':
				token.type = 'PRINT'
			elif c == '=':
				token.type = 'EQ'
			elif c == 'do':
				token.type = 'DO'
			elif c == '{':
				token.type = 'BEGIN'
			elif c == '}':
				token.type = 'END'
			elif c == '}endwhile':
				token.type = 'ENDWHILE'
			elif c == '(':
				token.type = 'OPEN_BRACKET'
			elif c == ')':
				token.type = 'CLOSE_BRACKET'
			elif c == '<endln>':
				token.type = 'ENDLN'
			elif c in DATA_TYPES:
				token.type = 'DATA_TYPE'
			elif c in BOOL_VALUES:
				token.type = 'BOOL_VALUE'
			elif c in OPERATORS:
				token.type = 'OPERATOR'
			elif c in BINARY_OPERATORS:
				token.type = 'B_OPERATOR'
			elif c in COMPARISON_OPERATORS:
				token.type = 'C_OPERATOR'
			elif c.startswith('@@'):
				token.type = 'COMMENT'
			elif re.findall(array_regexp, c):
				token.type = 'ARRAY_VARIABLE'
			elif c[0] in ASCII_LETTERS:
				token.type = 'VARIABLE'
			elif re.findall(integer_regexp, c):
				token.type = 'INTEGER_VALUE'
			else:
				mes = "Unexpected token '{}' at line {} position {}".format(
						c, token.line, token.position)
				raise LexerError(mes)

			if self.DEBUG:
				print("Tokens:")
				print(token.type, token.content)


	def structurize_tokens(self):
		tokens_for_parser = []

		temp = []
		for token in self.tokens:
			if token.type == 'ENDLN':
				# check if not empty
				if temp:
					tokens_for_parser.append(temp)
					temp = []
			else:
				temp.append(token)

		self.tokens = tokens_for_parser

		if self.DEBUG:
			print("Structurize tokens:")
			for line in self.tokens:
				print(line)
				print()