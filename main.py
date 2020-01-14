from Interpreter import Interpreter
from Lexer import Lexer
from Parser import Parser
from SusekaException import *


def main():
	file = open("examples/example2.txt", 'r').read()

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