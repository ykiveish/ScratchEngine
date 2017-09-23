#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
from subprocess import call

Code = ""
Sensors = ""
AddSensors = ""
SensorTableTranslator = {}

class CVariabesTBLTranslator:
	"""A class for mapping Variable name to ID"""
	def __init__ (self):
		self.VariabesTBLTranslator = {}
		self.VariableTBLTranslatorCounter = 0
	
	def Set(self, name):
		self.VariableTBLTranslatorCounter = self.VariableTBLTranslatorCounter + 1
		self.VariabesTBLTranslator[name] = self.VariableTBLTranslatorCounter
		return self.VariableTBLTranslatorCounter
	
	def Get (self, name):
		return self.VariabesTBLTranslator[name]
	
	def LoadToC (self):
		global Code
		appendCode = ""
		for key, value in self.VariabesTBLTranslator.iteritems():
			appendCode = appendCode + "float var" + str(value) + " = 0;\n\t"
		
		appendCode = appendCode[:-2]
		Code = Code.replace("/*[GLOBALS]*/", appendCode);

class CScriptParser:
	def __init__ (self):
		self.BlocksCount = 0
	
	def FischertechnikBlock (self, block):
		global SensorTableTranslator
		global Sensors
		global AddSensors
		
		Header = block[0]
		print block
		if "onInput" in Header:
			print "_IF_SENSOR_VALUE_IS_"
			
			if block[1] in SensorTableTranslator:
				if 	SensorTableTranslator[block[1]] in "DistanceSensor":
					Sensors = Sensors + "scratch_distance_sensor distSesnor ();"
					AddSensors = AddSensors + "sensor_db_add (&sesnor_list, (void *)&distSesnor);"
					print "_SENSOR_DISTANCE_"
			#word = "שלום"
			#print int(word[0])
		elif "doSetMotorSpeedDirDistSync" in Header:
			print "_SET_MOTOR_POWER_ON_SPEED_DIRECTION_"
	
	def Parse (self, script):
		global Code
		global Sensors
		
		for flow in script:
			for block in flow[2]:
				Header = block[0]
				if "fischertechnik" in Header:
					self.FischertechnikBlock(block)
				elif "setVar:to:" in Header:
					print "_SET_VARIABLE_VALUE_"
				elif "doRepeat" in Header:
					print "_REPEAT_FLOW_"
		
		Code = Code.replace("/*[SENSORS]*/", Sensors);
		Code = Code.replace("/*[ADD_SENSORS]*/", AddSensors);

tblVarTranc = CVariabesTBLTranslator()
parser = CScriptParser()

def LoadSensorTranslator():
	global SensorTableTranslator
	file = open("../../Misc/BlockTranslator", "r")
	jsonStr = file.read().decode('utf-8')
	data = json.loads(jsonStr, encoding='utf-8')
	
	Items = data["Items"]
	
	for item in Items:
		SensorTableTranslator[item[0]] = item[1]

def LoadC ():
	global Code
	file = open("ScratchEngine.c", "r+")
	Code = file.read()

def main():
	global tblVarTranc
	global Code
	global SensorTableTranslator
	
	file = open("../../sbx/project2/project.json", "r")
	jsonStr = file.read().decode('utf-8')
	data = json.loads(jsonStr, encoding='utf-8')
	
	Variables = data["variables"]
	Script = data["scripts"]
	
	for item in Variables:
		tblVarTranc.Set(item["name"])
	
	LoadC()
	LoadSensorTranslator()
	tblVarTranc.LoadToC()
	parser.Parse(Script)

	print Code
	call(["make.bat", ""])

if __name__ == "__main__":
    main()

