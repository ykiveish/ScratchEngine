#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
from subprocess import call

Code = ""
Sensors = ""
AddSensors = ""
Nodes = ""
InitNodes = ""
AddNodes = ""
SensorTableTranslator = {}

class Stack:
	def __init__(self):
		self.items = []
	
	def isEmpty(self):
		return self.items == []
	
	def push(self, item):
		self.items.append(item)
	
	def pop(self):
		return self.items.pop()
	
	def peek(self):
		return self.items[len(self.items)-1]
	
	def size(self):
		return len(self.items)
	
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

#
#	#word = "שלום"
#	#print int(word[0])
#

class CScriptParser:
	def __init__ (self, variabesTBLTranslator):
		self.BlocksCount = 0
		self.FlowControl = Stack();
		self.VariabesTBLTranslator = variabesTBLTranslator
	
	def FischertechnikBlock (self, block):
		global SensorTableTranslator
		global Sensors
		global AddSensors
		
		Header = block[0]
		if "onInput" in Header:
			print "_IF_SENSOR_VALUE_IS_"
			
			if block[1] in SensorTableTranslator:
				if 	SensorTableTranslator[block[1]] in "DistanceSensor":
					Sensors = Sensors + "scratch_distance_sensor \tdistSesnor;\n\t"
					AddSensors = AddSensors + "sensor_db_add (&sesnor_list, (void *)&(global_sensors.distSesnor));\n\t"
					print "_SENSOR_DISTANCE_"
		elif "doSetMotorSpeedDirDistSync" in Header:
			Sensors = Sensors + "scratch_motor \t\t\tmotor;\n\t"
			AddSensors = AddSensors + "sensor_db_add (&sesnor_list, (void *)&(global_sensors.scratch_motor));\n\t"
			print "_SET_MOTOR_POWER_ON_SPEED_DIRECTION_"
	
	def ParseBlocks (self, flow):
		global Nodes
		global InitNodes
		
		for block in flow:
			Header = block[0]
			if "fischertechnik" in Header:
				self.FischertechnikBlock(block)
			elif "setVar:to:" in Header:
				print "_SET_VARIABLE_VALUE_"
				Nodes = Nodes + "scratch_node setVariable_" + str(self.VariabesTBLTranslator.Get(block[1])) + ";\n\t"
				InitNodes = InitNodes + "global_nodes.setVariable_" + str(self.VariabesTBLTranslator.Get(block[1])) + ".data = &(global_vars.var_" + str(self.VariabesTBLTranslator.Get(block[1])) + ");\n\t"
				InitNodes = InitNodes + "global_nodes.setVariable_" + str(self.VariabesTBLTranslator.Get(block[1])) + ".type = SCRATCH_NODE_VARIABLE;\n\t"
				
			elif "wait:elapsed:from:" in Header:
				print "_WAIT_ELAPSED_TIME_"
			elif "doRepeat" in Header:
				print "_REPEAT_FLOW_"
				self.FlowControl.push("REPEAT_FLOW");
				self.ParseBlocks(block[2])
				if "REPEAT_FLOW" in self.FlowControl.pop():
					print "EXIT _REPEAT_FLOW_"
				else:
					sys.exit()
	
	def Parse (self, script):
		global Code
		global Sensors
		global AddSensors
		global Nodes
		global InitNodes
		
		for flow in script:
			print "FLOW"
			self.FlowControl.push("FLOW");
			self.ParseBlocks(flow[2])
			if "FLOW" in self.FlowControl.pop():
				print "EXIT FLOW"
			else:
				sys.exit()
		
		Sensors = Sensors[:-2]
		AddSensors = AddSensors[:-2]
		Nodes = Nodes[:-2]
		InitNodes = InitNodes[:-2]
		Code = Code.replace("/*[SENSORS]*/", Sensors);
		Code = Code.replace("/*[ADD_SENSORS]*/", AddSensors);
		Code = Code.replace("/*[NODES]*/", Nodes);
		Code = Code.replace("/*[INIT_FLOW]*/", InitNodes);

tblVarTranc = CVariabesTBLTranslator()
parser = CScriptParser(tblVarTranc)

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
	#call(["make.bat", ""])

if __name__ == "__main__":
    main()

