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

#include "ROBO_TX_PRG.h"

#define MAX_BRANCHES 						8
#define MAX_SCRATCH_NODES 					256
#define MAX_SCRATCH_SENSORS 				64

#define FLOW_START 							0
#define FLOW_END 							MAX_SCRATCH_NODES

#define SCRATCH_NODE_MOTOR_ENGINE			1
#define SCRATCH_NODE_ULTRASONIC_SENSOR		2
#define SCRATCH_NODE_WHILE					10
#define SCRATCH_NODE_IF						11
#define SCRATCH_NODE_VARIABLE				12

struct global_vars {
	/*[GLOBALS]*/
};

struct scratch_action {
	int 	type;
	void 	*from;
	void 	*to;
	int 	value;
};

struct scratch_motor {
	int id;
	int value;
};

struct scratch_distance_sensor {
	int id;
	int value;
};

struct scratch_node {
	int 				type;
	void 				*data;
	void				*action;
	struct scratch_node *jump;
	struct scratch_node *next;
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
};
struct context this;

struct global_sensorss {
	/*[SENSORS]*/
};

void
sensor_db_init (struct sensor_db *item) {
	int i = 0;
	item->index = 0;
	for (i = 0; i < MAX_SCRATCH_SENSORS; i++) {
		item->sensors[i] = NULL;
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
struct scratch_node scratch_node_list[MAX_SCRATCH_NODES];

void
handle_branch_flow (int branch_idx) {
	struct scratch_node *current_node = this.branch[branch_idx].current;

	switch (current_node->type) {
		case SCRATCH_NODE_MOTOR_ENGINE:
		break;
		default:
		break;
	}

	current_node = current_node->next;
}

/*-----------------------------------------------------------------------------
 * Function Name       : PrgInit
 *
 * This it the program initialization.
 * It is called once.
 *
 * p_ta_array - pointer to the array of transfer areas
 * ta_count - number of transfer areas in array (equal to TA_COUNT)
 *-----------------------------------------------------------------------------*/
void 
PrgInit (TA * p_ta_array, int ta_count) {
	sensor_db_init (&sesnor_list);
	/*[ADD_SENSORS]*/
	/*[FLOW]*/
}

/*-----------------------------------------------------------------------------
 * Function Name       : PrgTic
 *
 * This is the main function of this program.
 * It is called every tic (1 ms) realtime.
 *
 * p_ta_array - pointer to the array of transfer areas
 * ta_count - number of transfer areas in array (equal to TA_COUNT)
 *-----------------------------------------------------------------------------*/
int PrgTic (TA * p_ta_array, int ta_count) {
	int branch_idx = 0,
		branch_count = this.branch_count;

	for (branch_idx = 0; branch_idx < branch_count; branch_idx++) {
		handle_branch_flow (branch_idx);
	}

    return 0;
}