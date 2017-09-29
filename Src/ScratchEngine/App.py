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
Flow = ""
SensorTableTranslator = {}

FlowIndex = -1;
LoopIndex = 1;

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
			appendCode = appendCode + "float var_" + str(value) + ";\n\t"
		
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
					Sensors = Sensors + "struct scratch_distance_sensor \tdistSensor;\n\t"
					AddSensors = AddSensors + "sensor_db_add (&sesnor_list, (void *)&(g_sensors.distSensor));\n\t"
					print "_SENSOR_DISTANCE_"
		elif "doSetMotorSpeedDirDistSync" in Header:
			Sensors = Sensors + "struct scratch_motor \t\t\tmotor;\n\t"
			AddSensors = AddSensors + "sensor_db_add (&sesnor_list, (void *)&(g_sensors.motor));\n\t"
			print "_SET_MOTOR_POWER_ON_SPEED_DIRECTION_"
	
	def ParseBlocks (self, flow):
		global Nodes
		global InitNodes
		global Flow
		global FlowIndex
		
		for block in flow:
			Header = block[0]
			if "fischertechnik" in Header:
				self.FischertechnikBlock(block)
			elif "setVar:to:" in Header:
				print "_SET_VARIABLE_VALUE_"
				Nodes = Nodes + "struct scratch_node setVariable_" + str(self.VariabesTBLTranslator.Get(block[1])) + ";\n\t"
				InitNodes = InitNodes + "g_nodes.setVariable_" + str(self.VariabesTBLTranslator.Get(block[1])) + ".data = &(globals.var_" + str(self.VariabesTBLTranslator.Get(block[1])) + ");\n\t"
				InitNodes = InitNodes + "g_nodes.setVariable_" + str(self.VariabesTBLTranslator.Get(block[1])) + ".type = SCRATCH_NODE_VARIABLE;\n\t"
				InitNodes = InitNodes + "g_nodes.setVariable_" + str(self.VariabesTBLTranslator.Get(block[1])) + ".index = " + str(FlowIndex) + ";\n\t"
				Flow = Flow + "scratch_node_list[" + str(FlowIndex) + "] = &g_nodes.setVariable_" + str(self.VariabesTBLTranslator.Get(block[1])) + ";\n\t";
			elif "wait:elapsed:from:" in Header:
				print "_WAIT_ELAPSED_TIME_"
				timer = block[1]
				Nodes = Nodes + "struct scratch_node waitCmd_" + str(self.VariabesTBLTranslator.Get(timer[1])) + ";\n\t"
				InitNodes = InitNodes + "g_nodes.waitCmd_" + str(self.VariabesTBLTranslator.Get(timer[1])) + ".data = &(globals.var_" + str(self.VariabesTBLTranslator.Get(timer[1])) + ");\n\t"
				InitNodes = InitNodes + "g_nodes.waitCmd_" + str(self.VariabesTBLTranslator.Get(timer[1])) + ".type = SCRATCH_NODE_WAIT;\n\t"
				InitNodes = InitNodes + "g_nodes.waitCmd_" + str(self.VariabesTBLTranslator.Get(timer[1])) + ".index = " + str(FlowIndex) + ";\n\t"
				Flow = Flow + "scratch_node_list[" + str(FlowIndex) + "] = &g_nodes.waitCmd_" + str(self.VariabesTBLTranslator.Get(timer[1])) + ";\n\t";
			elif "doRepeat" in Header:
				print "_REPEAT_FLOW_"
				self.FlowControl.push("REPEAT_FLOW");
				Nodes = Nodes + "struct scratch_node forLoop_" + str(LoopIndex) + ";\n\t"
				InitNodes = InitNodes + "g_nodes.forLoop_" + str(LoopIndex) + ".type = SCRATCH_NODE_FOR;\n\t"
				InitNodes = InitNodes + "g_nodes.forLoop_" + str(LoopIndex) + ".index = " + str(FlowIndex) + ";\n\t"
				Flow = Flow + "scratch_node_list[" + str(FlowIndex) + "] = &g_nodes.forLoop_" + str(LoopIndex) + ";\n\t";
				self.ParseBlocks(block[2])
				if "REPEAT_FLOW" in self.FlowControl.pop():
					print "EXIT _REPEAT_FLOW_"
					Nodes = Nodes + "struct scratch_node forLoopEnd_" + str(LoopIndex) + ";\n\t"
					InitNodes = InitNodes + "g_nodes.forLoopEnd_" + str(LoopIndex) + ".data = &(g_nodes.forLoop_" + str(LoopIndex) + ");\n\t"
					InitNodes = InitNodes + "g_nodes.forLoopEnd_" + str(LoopIndex) + ".type = SCRATCH_NODE_END_LOOPS;\n\t"
					InitNodes = InitNodes + "g_nodes.forLoopEnd_" + str(LoopIndex) + ".index = " + str(FlowIndex) + ";\n\t"
					Flow = Flow + "scratch_node_list[" + str(FlowIndex) + "] = &g_nodes.forLoopEnd_" + str(LoopIndex) + ";\n\t";
				else:
					sys.exit()
			FlowIndex = FlowIndex + 1
	
	def Parse (self, script):
		global Code
		global Sensors
		global AddSensors
		global Nodes
		global InitNodes
		global Flow
		
		for flow in script:
			print "FLOW"
			self.FlowControl.push("FLOW");
			Flow = Flow + "this.branch[0].current = this.branch[0].start;\n\t";
			self.ParseBlocks(flow[2])
			if "FLOW" in self.FlowControl.pop():
				print "EXIT FLOW"
			else:
				sys.exit()
		
		Sensors = Sensors[:-2]
		AddSensors = AddSensors[:-2]
		Nodes = Nodes[:-2]
		InitNodes = InitNodes[:-2]
		Flow = Flow[:-2]
		Code = Code.replace("/*[SENSORS]*/", Sensors);
		Code = Code.replace("/*[ADD_SENSORS]*/", AddSensors);
		Code = Code.replace("/*[NODES]*/", Nodes);
		Code = Code.replace("/*[INIT_FLOW]*/", InitNodes);
		Code = Code.replace("/*[FLOW]*/", Flow);

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
	file = open("Template.c", "r+")
	Code = file.read()

def SaveC ():
	global Code
	file = open("ScratchEngine.c", "r+")
	file.write (Code)
	
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
	SaveC ()
	#call(["make.bat", ""])

if __name__ == "__main__":
    main()

