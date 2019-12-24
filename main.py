from Lexer import Lexer
from Token import Token

def main():
	file = open("examples/example1.txt", 'r').read()

	lexer = Lexer(file)
	lexer.run()


if __name__ == "__main__":
	main()