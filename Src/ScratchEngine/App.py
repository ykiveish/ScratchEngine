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
GlobalData = ""
SensorTableTranslator = {}
Pinouts = {}

FlowIndex = 0;
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
		global Nodes
		global InitNodes
		global Flow
		global SensorTableTranslator
		global Sensors
		global AddSensors
		global FlowIndex
		global Pinouts
		
		Header = block[0]
		if "onInput" in Header:
			# print "_IF_SENSOR_VALUE_IS_"
			
			if block[1] in SensorTableTranslator:
				if SensorTableTranslator[block[1]] in "DistanceSensor":
					# print "_SENSOR_DISTANCE_"
					Sensors = Sensors + "struct scratch_distance_sensor \tdistSensor;\n\t"
					# Set distance.
					AddSensors = AddSensors + "g_sensors.distSensor.distance.reference = FALSE;\n\t"
					AddSensors = AddSensors + "g_sensors.distSensor.distance.value = (void *)" + str(block[2]) + ";\n\t"
					AddSensors = AddSensors + "g_sensors.distSensor.pin = " + str(Pinouts[block[4]]) + ";\n\t"
					AddSensors = AddSensors + "g_sensors.distSensor.action.type = SCRATCH_ACTION_TYPE_COMPARE;\n\t"
					AddSensors = AddSensors + "g_sensors.distSensor.action.compare_type = SCRATCH_COMPARE_TYPE_LESS;\n\t"
					AddSensors = AddSensors + "sensor_db_add (&sesnor_list, (void *)&(g_sensors.distSensor));\n\t\n\t"
					
					# Add node.
					Nodes = Nodes + "struct scratch_node distSensorMonitor;\n\t"
					InitNodes = InitNodes + "g_nodes.distSensorMonitor.index = " + str(FlowIndex) + ";\n\t"
					InitNodes = InitNodes + "g_nodes.distSensorMonitor.data = (void *)&(g_sensors.distSensor);\n\t"
					InitNodes = InitNodes + "g_nodes.distSensorMonitor.type = SCRATCH_NODE_ULTRASONIC_SENSOR;\n\t\n\t"

					# Add monitor
					InitNodes = InitNodes + "ctx.monitor_blocks[++ctx.monitor_blocks_count] = (void *)&(g_nodes.distSensorMonitor);\n\t"
					
					Flow = Flow + "scratch_node_list[" + str(FlowIndex) + "] = (void *)&g_nodes.distSensorMonitor;\n\t"
					FlowIndex = FlowIndex + 1
		elif "doSetMotorSpeedDirDistSync" in Header:
			DistanceBlock = block[3]
			SpeedBlock = block[4]
			
			DistanceVariable = self.VariabesTBLTranslator.Get(DistanceBlock[1])
			SpeedVariable = self.VariabesTBLTranslator.Get(SpeedBlock[1])
			
			# Create sensor imstance.
			Sensors = Sensors + "struct scratch_motor \t\t\tmotor;\n\t"
			# Set speed.
			AddSensors = AddSensors + "g_sensors.motor.speed.reference = TRUE;\n\t"
			AddSensors = AddSensors + "g_sensors.motor.speed.value = (void *)&(globals.var_" + str(SpeedVariable) + ");\n\t"
			# Set distance.
			AddSensors = AddSensors + "g_sensors.motor.distance.reference = TRUE;\n\t"
			AddSensors = AddSensors + "g_sensors.motor.distance.value = (void *)&(globals.var_" + str(DistanceVariable) + ");\n\t"
			# Set direction.
			if block[5] in SensorTableTranslator:
				if SensorTableTranslator[block[5]] in "Forward":
					AddSensors = AddSensors + "g_sensors.motor.direction.reference = FALSE;\n\t"
					AddSensors = AddSensors + "g_sensors.motor.direction.value = (void *)FORWARD;\n\t"
				elif SensorTableTranslator[block[5]] in "Backward":
					AddSensors = AddSensors + "g_sensors.motor.direction.reference = FALSE;\n\t"
					AddSensors = AddSensors + "g_sensors.motor.direction.value = BACKWARD;\n\t"
			# Add sensor.
			AddSensors = AddSensors + "sensor_db_add (&sesnor_list, (void *)&(g_sensors.motor));\n\t\n\t"
			# Create block and add to the flow.
			Nodes = Nodes + "struct scratch_node doSetMotorSpeedDirDistSync;\n\t"
			InitNodes = InitNodes + "g_nodes.doSetMotorSpeedDirDistSync.index = " + str(FlowIndex) + ";\n\t"
			InitNodes = InitNodes + "g_nodes.doSetMotorSpeedDirDistSync.data = (void *)&(g_sensors.motor);\n\t"
			InitNodes = InitNodes + "g_nodes.doSetMotorSpeedDirDistSync.type = SCRATCH_NODE_MOTOR_ENGINE;\n\t\n\t"
			Flow = Flow + "scratch_node_list[" + str(FlowIndex) + "] = (void *)&g_nodes.doSetMotorSpeedDirDistSync;\n\t";
			FlowIndex = FlowIndex + 1
			# print "_SET_MOTOR_POWER_ON_SPEED_DIRECTION_"
	
	def ParseBlocks (self, flow):
		global Nodes
		global InitNodes
		global Flow
		global FlowIndex
		global GlobalData
		
		for block in flow:
			Header = block[0]
			if "fischertechnik" in Header:
				self.FischertechnikBlock(block)
			elif "setVar:to:" in Header:
				# print "_SET_VARIABLE_VALUE_"
				VarId = self.VariabesTBLTranslator.Get(block[1])
				Nodes = Nodes + "struct scratch_node setVariable_" + str(VarId) + ";\n\t"
				InitNodes = InitNodes + "g_nodes.setVariable_" + str(VarId) + ".index = " + str(FlowIndex) + ";\n\t"
				InitNodes = InitNodes + "g_nodes.setVariable_" + str(VarId) + ".data = (void *)&(globals.var_" + str(VarId) + ");\n\t"
				InitNodes = InitNodes + "g_nodes.setVariable_" + str(VarId) + ".type = SCRATCH_NODE_VARIABLE;\n\t\n\t"
				Flow = Flow + "scratch_node_list[" + str(FlowIndex) + "] = (void *)&g_nodes.setVariable_" + str(VarId) + ";\n\t"
				FlowIndex = FlowIndex + 1
			elif "wait:elapsed:from:" in Header:
				# print "_WAIT_ELAPSED_TIME_"
				timer = block[1]
				VarId = self.VariabesTBLTranslator.Get(timer[1])
				Nodes = Nodes + "struct scratch_node waitCmd_" + str(VarId) + ";\n\t"
				InitNodes = InitNodes + "g_nodes.waitCmd_" + str(VarId) + ".index = " + str(FlowIndex) + ";\n\t"
				InitNodes = InitNodes + "g_nodes.waitCmd_" + str(VarId) + ".data = (void *)&(globals.var_" + str(VarId) + ");\n\t"
				InitNodes = InitNodes + "g_nodes.waitCmd_" + str(VarId) + ".type = SCRATCH_NODE_WAIT;\n\t\n\t"
				Flow = Flow + "scratch_node_list[" + str(FlowIndex) + "] = (void *)&g_nodes.waitCmd_" + str(VarId) + ";\n\t"
				FlowIndex = FlowIndex + 1
			elif "doRepeat" in Header:
				# print "_REPEAT_FLOW_"
				self.FlowControl.push("REPEAT_FLOW");
				Nodes = Nodes + "struct scratch_node forLoop_" + str(LoopIndex) + ";\n\t"
				InitNodes = InitNodes + "g_nodes.forLoop_" + str(LoopIndex) + ".index = " + str(FlowIndex) + ";\n\t"
				InitNodes = InitNodes + "g_nodes.forLoop_" + str(LoopIndex) + ".type = SCRATCH_NODE_FOR;\n\t"
				Flow = Flow + "scratch_node_list[" + str(FlowIndex) + "] = (void *)&g_nodes.forLoop_" + str(LoopIndex) + ";\n\t";
				GlobalData = GlobalData + "struct scratch_loop_data forLoop_" + str(LoopIndex) + ";\n\t"
				InitNodes = InitNodes + "ctx.forLoop_" + str(LoopIndex) + ".limit = " + str(block[1]) + ";\n\t"
				InitNodes = InitNodes + "ctx.forLoop_" + str(LoopIndex) + ".index = 0;\n\t"
				InitNodes = InitNodes + "g_nodes.forLoop_" + str(LoopIndex) + ".data = (void *)&(ctx.forLoop_" + str(LoopIndex) + ");\n\t\n\t"
				FlowIndex = FlowIndex + 1
				self.ParseBlocks(block[2])
				if "REPEAT_FLOW" in self.FlowControl.pop():
					# print "EXIT _REPEAT_FLOW_"
					Nodes = Nodes + "struct scratch_node forLoopEnd_" + str(LoopIndex) + ";\n\t"
					InitNodes = InitNodes + "g_nodes.forLoopEnd_" + str(LoopIndex) + ".index = " + str(FlowIndex) + ";\n\t"
					InitNodes = InitNodes + "g_nodes.forLoopEnd_" + str(LoopIndex) + ".jump = &(g_nodes.forLoop_" + str(LoopIndex) + ");\n\t"
					InitNodes = InitNodes + "ctx.forLoop_" + str(LoopIndex) + ".node = &(g_nodes.forLoopEnd_" + str(LoopIndex) + ");\n\t"
					InitNodes = InitNodes + "g_nodes.forLoopEnd_" + str(LoopIndex) + ".type = SCRATCH_NODE_END_LOOPS;\n\t\n\t"
					Flow = Flow + "scratch_node_list[" + str(FlowIndex) + "] = (void *)&g_nodes.forLoopEnd_" + str(LoopIndex) + ";\n\t";
					FlowIndex = FlowIndex + 1
				else:
					sys.exit()
	
	def Parse (self, script):
		global Code
		global Sensors
		global AddSensors
		global Nodes
		global InitNodes
		global Flow
		global GlobalData
		
		for flow in script:
			# print "FLOW"
			self.FlowControl.push("FLOW");
			Flow = Flow + "ctx.branch[0].current = ctx.branch[0].start;\n\t";
			self.ParseBlocks(flow[2])
			if "FLOW" not in self.FlowControl.pop():
				sys.exit()
				
		
		Sensors = Sensors[:-2]
		AddSensors = AddSensors[:-2]
		Nodes = Nodes[:-2]
		InitNodes = InitNodes[:-2]
		Flow = Flow[:-2]
		GlobalData = GlobalData[:-2]
		
		Code = Code.replace("/*[SENSORS]*/", Sensors);
		Code = Code.replace("/*[ADD_SENSORS]*/", AddSensors);
		Code = Code.replace("/*[NODES]*/", Nodes);
		Code = Code.replace("/*[INIT_FLOW]*/", InitNodes);
		Code = Code.replace("/*[FLOW]*/", Flow);
		Code = Code.replace("/*[GLOBAL_DATA]*/", GlobalData);

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

def LoadPinouts():
	global Pinouts
	file = open("../../Misc/Pinouts", "r")
	jsonStr = file.read().decode('utf-8')
	data = json.loads(jsonStr, encoding='utf-8')
	
	Items = data["Items"]
	for item in Items:
		Pinouts[item[0]] = item[1]

def LoadC ():
	global Code
	#file = open("Template.c", "r+")
	file = open("LinuxTemplate.c", "r+")
	Code = file.read()

def SaveC ():
	global Code
	file = open("ScratchEngine.c", "w")
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
	LoadPinouts()
	tblVarTranc.LoadToC()
	parser.Parse(Script)

	# print Code
	SaveC ()
	# call(["python", "make.sh", ""])

if __name__ == "__main__":
    main()

