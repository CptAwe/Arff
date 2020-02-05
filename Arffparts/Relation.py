class Relation(object):
	"""docstring for Relation"""
	def __init__(self, name):
		self._relation_declaration = "@RELATION"
		
		name = validate_name(name)

		self.name = self._relation_declaration + " " + name
	
	def validate_name(name):
		return name