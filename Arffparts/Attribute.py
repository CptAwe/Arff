from Arffparts.Exceptions.AttributeExceptions import AttributeExceptions

class Attribute():
	"""
	name	: The name of the attribute
	type	: Numeric, nominal, string, date
	content	: must be specified if nominal
	"""
	def __init__(self, name: str, type: str, content = None):

		if name == "a":
			raise AttributeExceptions("Hello")

		self._attribute_declaration = "@ATTRIBUTE"

		# Types
		self._types = {
			"number": {
				"title": "NUMERIC",
				"left": "",
				"right": ""
			},
			"string": {
				"title": "STRING",
				"left": "",
				"right": ""
			},
			"nominal": {
				"title": "",
				"left": "{",
				"right": "}"
			},
			"date": {
				"title": "DATE ",
				"left": "[",
				"right": "]"
			}
		}

	
		self.name = name

		type = type.lower()
		if type not in list(self._types.keys):
			raise

		self.content = content

	def __str__(self):

		string = "{declaration} {name} {type} {left}{content}{right}".format(
				declaration = self._attribute_declaration,
				name = self.name,
				type = self.type,
				left = self.left,
				content = self.content,
				right = self.right
			)

		return string