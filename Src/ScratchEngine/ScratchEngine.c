//=============================================================================
// Demo program "Motor run".
//
// Can be run under control of the ROBO TX Controller
// firmware in download (local) mode.
// Controls motor connected to outputs M1 with different
// speeds and in different rotation directions.
//
// Disclaimer - Exclusion of Liability
//
// This software is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
// FITNESS FOR A PARTICULAR PURPOSE. It can be used and modified by anyone
// free of any license obligations or authoring rights.
//=============================================================================

// #include "ROBO_TX_PRG.h"
#include "KeLibTxtDl.h"          // TXT Lib
#include "FtShmem.h"             // TXT Transfer Area

#include <stdio.h>
#include <unistd.h>

#define TRUE 								1
#define FALSE 								0

#define FORWARD 							1
#define BACKWARD 							0

#define MAX_BRANCHES 						8
#define MAX_SCRATCH_NODES 					256
#define MAX_SCRATCH_SENSORS 				64

#define FLOW_START 							0
#define FLOW_END 							MAX_SCRATCH_NODES

#define SCRATCH_NODE_EXIT					0
#define SCRATCH_NODE_MOTOR_ENGINE			1
#define SCRATCH_NODE_ULTRASONIC_SENSOR		2
#define SCRATCH_NODE_FOR					10
#define SCRATCH_NODE_IF						11
#define SCRATCH_NODE_VARIABLE				12
#define SCRATCH_NODE_WAIT					13
#define SCRATCH_NODE_END_LOOPS				14

#define SCRATCH_ACTION_TYPE_COMPARE			1

#define SCRATCH_COMPARE_TYPE_LESS			1

#define SCRATCH_ACTION_SET_VAR_STATIC		1

void OperateMotor ();
float ReadSensor ();

//============================================================================
// Common debugging stuff for RoboProLib
//============================================================================
unsigned int DebugFlags;
FILE *DebugFile;

FISH_X1_TRANSFER *pTArea;

struct global_vars {
	float var_1;
	float var_3;
	float var_2;
};
struct global_vars g_vars;

struct scratch_action_compare {
	int 	type;
	int		compare_type;
};

struct scratch_action_set_static_var {
	int 	type;
	float	value;
};

struct parameter {
	int 	reference;
	void 	*value;
};

struct scratch_motor {
	int 				id;
	int 				pin;
	struct parameter	direction;
	struct parameter	speed;
	struct parameter	distance;
};

struct scratch_distance_sensor {
	int 							id;
	int 							pin;
	float							data;
	struct parameter				distance;
	struct scratch_action_compare 	action;
};

struct scratch_node {
	int 				type;
	int					index;
	struct scratch_node *next;
	
	void 				*data;
	struct scratch_node *jump;
	void				*action;
};

struct scratch_loop_data {
	int limit;
	int index;
	scratch_node* node;
};

struct sensor_db {
	void 	*sensors[MAX_SCRATCH_SENSORS];
	int 	index;
};

struct flow_branch {
	struct scratch_node *start;
	struct scratch_node *end;
	struct scratch_node *current;
};

struct context {
	struct flow_branch 	branch[MAX_BRANCHES];
	int 				branch_count;
	void *				monitor_blocks[16];
	int 				monitor_blocks_count;
	struct scratch_loop_data forLoop_1;
};
struct context ctx;

struct global_sensors {
	struct scratch_distance_sensor 	distSensor;
	struct scratch_motor 			motor;
};
struct global_sensors g_sensors;

struct global_actions {
	struct scratch_action_set_static_var actionSetStaticVariable_1;
	struct scratch_action_set_static_var actionSetStaticVariable_2;
	struct scratch_action_set_static_var actionSetStaticVariable_3;
};
struct global_actions g_actions;

struct global_nodes {
	struct scratch_node distSensorMonitor;
	struct scratch_node setVariable_1;
	struct scratch_node setVariable_2;
	struct scratch_node setVariable_3;
	struct scratch_node forLoop_1;
	struct scratch_node doSetMotorSpeedDirDistSync;
	struct scratch_node waitCmd_3;
	struct scratch_node forLoopEnd_1;
};
struct global_nodes g_nodes;

struct global_monitors {
	/*[MONITOR_NODES]*/
};
struct global_monitors g_monitors;

void
sensor_db_init (struct sensor_db *item) {
	int i = 0;
	item->index = 0;
	for (i = 0; i < MAX_SCRATCH_SENSORS; i++) {
		item->sensors[i] = 0;
	}
}

int
sensor_db_add (struct sensor_db *item, void * sensor) {
	item->sensors[item->index] = item;
	item->index++;
	return 1;
}

struct global_vars 	globals;
struct sensor_db 	sesnor_list;
void * scratch_node_list[MAX_SCRATCH_NODES];

void
handle_branch_flow (int branch_idx) {
	struct scratch_node *current_node = ctx.branch[branch_idx].current;

	switch (current_node->type) {
		case SCRATCH_NODE_MOTOR_ENGINE:
			OperateMotor ();
		break;
		case SCRATCH_NODE_ULTRASONIC_SENSOR: {
			float value = ReadSensor();
			scratch_distance_sensor* sensor = (scratch_distance_sensor *)current_node->data;
			float* comparable = (float *)sensor->distance.value;

			switch (sensor->action.compare_type) {
				case SCRATCH_COMPARE_TYPE_LESS:
					if (value > *comparable) {
						// Value of sensor bigger than limit
					}
				break;
				default:
				break;
			}
		}
		break;
		case SCRATCH_NODE_FOR: {
			scratch_loop_data* data = (scratch_loop_data *)current_node->data;
			if (data->index < data->limit) {
				data->index++;
			} else {
				// Go back to the end of loop.
				ctx.branch[branch_idx].current = data->node;
			}
		}
		break;
		case SCRATCH_NODE_IF:
			// Check the condition.
		break;
		case SCRATCH_NODE_VARIABLE: {
			int type = ((struct scratch_action_set_static_var *)(current_node->action))->type;
			switch (type) {
				case SCRATCH_ACTION_SET_VAR_STATIC:{
					struct scratch_action_set_static_var * action = (struct scratch_action_set_static_var *)current_node->action;
					*((float *)current_node->data) = action->value;
				}
				break;
				default:
				break;
			}
		}
		break;
		case SCRATCH_NODE_WAIT:
			usleep (*((float *)current_node->data));
		break;
		case SCRATCH_NODE_END_LOOPS:
			ctx.branch[branch_idx].current = current_node->next;
			return;
		break;
		default:
		break;
	}

	current_node = current_node->next;

	// Handle monitor nodes.
}

void 
Setup () {
	int idx = 0;
	ctx.monitor_blocks_count = 0;

	for (idx = 0; idx < MAX_SCRATCH_NODES; idx++) {
		((struct scratch_node *)scratch_node_list[MAX_SCRATCH_NODES])->type = SCRATCH_NODE_EXIT;
	}

	sensor_db_init (&sesnor_list);
	
	// Add sensors to the DB.
	g_sensors.distSensor.distance.reference = FALSE;
	g_sensors.distSensor.distance.value = (void *)30;
	g_sensors.distSensor.pin = 8;
	g_sensors.distSensor.action.type = SCRATCH_ACTION_TYPE_COMPARE;
	g_sensors.distSensor.action.compare_type = SCRATCH_COMPARE_TYPE_LESS;
	sensor_db_add (&sesnor_list, (void *)&(g_sensors.distSensor));
	
	g_sensors.motor.speed.reference = TRUE;
	g_sensors.motor.speed.value = (void *)&(globals.var_2);
	g_sensors.motor.distance.reference = TRUE;
	g_sensors.motor.distance.value = (void *)&(globals.var_1);
	g_sensors.motor.direction.reference = FALSE;
	g_sensors.motor.direction.value = (void *)FORWARD;
	sensor_db_add (&sesnor_list, (void *)&(g_sensors.motor));
	
	
	// Initiata the Scratch flow items.
	g_nodes.distSensorMonitor.index = 0;
	g_nodes.distSensorMonitor.data = (void *)&(g_sensors.distSensor);
	g_nodes.distSensorMonitor.type = SCRATCH_NODE_ULTRASONIC_SENSOR;
	g_nodes.distSensorMonitor.next = (struct scratch_node *)&scratch_node_list[g_nodes.distSensorMonitor.index + 1];
	
	ctx.monitor_blocks[++ctx.monitor_blocks_count] = (void *)&(g_nodes.distSensorMonitor);
	g_nodes.setVariable_1.index = 1;
	g_nodes.setVariable_1.data = (void *)&(globals.var_1);
	g_nodes.setVariable_1.type = SCRATCH_NODE_VARIABLE;
	g_actions.actionSetStaticVariable_1.type = SCRATCH_ACTION_SET_VAR_STATIC;
	g_actions.actionSetStaticVariable_1.value = 50;
	g_nodes.setVariable_1.action = (void *)&(g_actions.actionSetStaticVariable_1);
	g_nodes.setVariable_1.next = (struct scratch_node *)&scratch_node_list[g_nodes.setVariable_1.index + 1];
	
	g_nodes.setVariable_2.index = 2;
	g_nodes.setVariable_2.data = (void *)&(globals.var_2);
	g_nodes.setVariable_2.type = SCRATCH_NODE_VARIABLE;
	g_actions.actionSetStaticVariable_2.type = SCRATCH_ACTION_SET_VAR_STATIC;
	g_actions.actionSetStaticVariable_2.value = 5;
	g_nodes.setVariable_2.action = (void *)&(g_actions.actionSetStaticVariable_2);
	g_nodes.setVariable_2.next = (struct scratch_node *)&scratch_node_list[g_nodes.setVariable_2.index + 1];
	
	g_nodes.setVariable_3.index = 3;
	g_nodes.setVariable_3.data = (void *)&(globals.var_3);
	g_nodes.setVariable_3.type = SCRATCH_NODE_VARIABLE;
	g_actions.actionSetStaticVariable_3.type = SCRATCH_ACTION_SET_VAR_STATIC;
	g_actions.actionSetStaticVariable_3.value = 6;
	g_nodes.setVariable_3.action = (void *)&(g_actions.actionSetStaticVariable_3);
	g_nodes.setVariable_3.next = (struct scratch_node *)&scratch_node_list[g_nodes.setVariable_3.index + 1];
	
	g_nodes.forLoop_1.index = 4;
	g_nodes.forLoop_1.type = SCRATCH_NODE_FOR;
	ctx.forLoop_1.limit = 10;
	ctx.forLoop_1.index = 0;
	g_nodes.forLoop_1.data = (void *)&(ctx.forLoop_1);
	g_nodes.forLoop_1.next = (struct scratch_node *)&scratch_node_list[g_nodes.forLoop_1.index + 1];
	
	g_nodes.doSetMotorSpeedDirDistSync.index = 5;
	g_nodes.doSetMotorSpeedDirDistSync.data = (void *)&(g_sensors.motor);
	g_nodes.doSetMotorSpeedDirDistSync.type = SCRATCH_NODE_MOTOR_ENGINE;
	g_nodes.doSetMotorSpeedDirDistSync.next = (struct scratch_node *)&scratch_node_list[g_nodes.doSetMotorSpeedDirDistSync.index + 1];
	
	g_nodes.waitCmd_3.index = 6;
	g_nodes.waitCmd_3.data = (void *)&(globals.var_3);
	g_nodes.waitCmd_3.type = SCRATCH_NODE_WAIT;
	g_nodes.waitCmd_3.next = (struct scratch_node *)&scratch_node_list[g_nodes.waitCmd_3.index + 1];
	
	g_nodes.forLoopEnd_1.index = 7;
	g_nodes.forLoopEnd_1.jump = &(g_nodes.forLoop_1);
	ctx.forLoop_1.node = &(g_nodes.forLoopEnd_1);
	g_nodes.forLoopEnd_1.type = SCRATCH_NODE_END_LOOPS;
	g_nodes.forLoopEnd_1.next = (struct scratch_node *)&scratch_node_list[g_nodes.forLoopEnd_1.index + 1];
	
	
	// Build the flow.
	ctx.branch[0].current = ctx.branch[0].start;
	scratch_node_list[0] = (void *)&g_nodes.distSensorMonitor;
	scratch_node_list[1] = (void *)&g_nodes.setVariable_1;
	scratch_node_list[2] = (void *)&g_nodes.setVariable_2;
	scratch_node_list[3] = (void *)&g_nodes.setVariable_3;
	scratch_node_list[4] = (void *)&g_nodes.forLoop_1;
	scratch_node_list[5] = (void *)&g_nodes.doSetMotorSpeedDirDistSync;
	scratch_node_list[6] = (void *)&g_nodes.waitCmd_3;
	scratch_node_list[7] = (void *)&g_nodes.forLoopEnd_1;
}

int
main (int argc, char ** argv) {
	int branch_idx = 0,
		branch_count = ctx.branch_count;

	if (StartTxtDownloadProg() == KELIB_ERROR_NONE) {
		pTArea = GetKeLibTransferAreaMainAddress();
        
        if (pTArea) {
        	Setup ();
			while(1) {
				for (branch_idx = 0; branch_idx < branch_count; branch_idx++) {
					handle_branch_flow (branch_idx);
				}
			}
        }
	}
	
    return 0;
}

void OperateMotor () {

}

float ReadSensor () {
	return 0;
}
