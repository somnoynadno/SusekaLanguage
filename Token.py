class Token:
	def __init__(self, position, line, content):
		self.position = position
		self.line = line
		self.content = content
		self.type = ''
