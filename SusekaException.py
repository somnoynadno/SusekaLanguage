# Lexer errors
class LexerError(Exception):
	def __init__(self, message):
		super().__init__(message)


# Parser errors
class SyntaxError(Exception):
	def __init__(self, message):
		super().__init__(message)


# Interpreter errors
class RuntimeError(Exception):
	def __init__(self, message):
		super().__init__(message)