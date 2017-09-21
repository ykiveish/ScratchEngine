import sys
import json

class CVariabesTBLTranslator:
	"""A class for mapping Variable name to ID"""
	def __init__(self):
		self.VariabesTBLTranslator = {}
		self.VariableTBLTranslatorCounter = 0
	
	def Set(self, name):
		self.VariableTBLTranslatorCounter = self.VariableTBLTranslatorCounter + 1
		self.VariabesTBLTranslator[name] = self.VariableTBLTranslatorCounter
		return self.VariableTBLTranslatorCounter
	
	def Get (self, name):
		return self.VariabesTBLTranslator[name]
	
	def LoadToC (self):
		file = open("ScratchEngine.c", "r+")
		code = file.read()
		
		appendCode = ""
		for key, value in self.VariabesTBLTranslator.iteritems():
			appendCode = appendCode + "float var" + str(value) + " = 0;\n\t"
		
		appendCode = appendCode[:-2]
		code = code.replace("/*[GLOBALS]*/", appendCode);
		
		print code

tblVarTranc = CVariabesTBLTranslator()

def main():
	global tblVarTranc
	
	file = open("../../sbx/project2/project.json", "r")
	jsonStr = file.read().decode('utf-8')
	data = json.loads(jsonStr, encoding='utf-8')
	
	Variables = data["variables"]
	Script = data["scripts"]
	
	for item in Variables:
		tblVarTranc.Set(item["name"])
	
	print tblVarTranc.VariabesTBLTranslator
	tblVarTranc.LoadToC()
	
if __name__ == "__main__":
    main()