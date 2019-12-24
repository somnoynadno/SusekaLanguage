from Token import Token

class Lexer:
	def __init__(self, program):
		self.program = program
		self.tokens = []


	def run(self):
		print("Start lexer")

		split_tokens()


	def split_tokens(self):
		line = 0
		position = 0
		content = ''

		for elem in self.program:
			if elem == ' ' or elem == '\n':
				content = content.strip()
				if content != '':
					t = Token(position, line, content)
					content = ''
					self.tokens.append(t)

			if elem == '\n':
				line += 1
				position = 0

				t = Token(position, line, "<endln>")
				self.tokens.append(t)

			position += 1
			content += elem