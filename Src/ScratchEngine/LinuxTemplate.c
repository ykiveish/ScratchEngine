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

struct global_vars {
	/*[GLOBALS]*/
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
	/*[GLOBAL_DATA]*/
};
struct context ctx;

struct global_sensors {
	/*[SENSORS]*/
};
struct global_sensors g_sensors;

struct global_actions {
	/*[ACTIONS]*/
};
struct global_actions g_actions;

struct global_nodes {
	/*[NODES]*/
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
	/*[ADD_SENSORS]*/
	
	// Initiata the Scratch flow items.
	/*[INIT_FLOW]*/
	
	// Build the flow.
	/*[FLOW]*/
}

int
main (int argc, char ** argv) {
	// FISH_X1_TRANSFER    *pTArea;
	int branch_idx = 0,
		branch_count = ctx.branch_count;

	Setup ();
	while(1) {
		for (branch_idx = 0; branch_idx < branch_count; branch_idx++) {
			handle_branch_flow (branch_idx);
		}
	}
	
    return 0;
}

void OperateMotor () {

}

float ReadSensor () {
	return 0;
}
