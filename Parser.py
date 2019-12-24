class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.DEBUG = False

	def run(self):
		if self.DEBUG:
			print("Start parser")

		for line in self.tokens:
			for token in line:
				pass