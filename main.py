#!/usr/bin/env python3

from Interpreter import Interpreter
from Lexer import Lexer
from Parser import Parser
from SusekaException import *

from sys import argv


def main():
	try:
		filename = argv[1]
	except IndexError:
		print("Usage: python3 main.py <filename>")
		exit(1)

	file = open(filename, 'r').read()

	lexer = Lexer(file)
	# lexer.DEBUG = True
	lexer.run()

	parser = Parser(lexer.tokens)
	# parser.DEBUG = True
	parser.run()

	interpreter = Interpreter(parser.commands)
	# interpreter.DEBUG = True
	interpreter.run()


if __name__ == "__main__":
	main()