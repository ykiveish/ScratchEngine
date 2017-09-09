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

struct global_vars {
	/* Injection - Variables. [GLOBALS] */
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

struct scratch_node {
	int 		type;
	void 		*data;
	void		*action;
	struct node *jump;
};

struct node {
	struct scratch_node *scratch_flow_item;
	struct node 		*next;
};

struct sensor_db {
	void 	*sensors[64];
	int 	index;
};

void
sensor_db_init (struct sensor_db *item) {
	int i = 0;
	item->index = 0;
	for (i = 0; i < 64; i++) {
		item->sensors[i] = NULL;
	}
}

int
sesnsor_db_add (struct sensor_db *item, void * sensor) {
	item->sensors[item->index] = item;
	item->index++;
	return 1;
}

struct global_vars 	globals;
struct sensor_db 	sesnor_list;
struct scratch_node scratch_node_list[256];

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
	/* Injection - Adding sensors. [SENSORS] */
	/* Injection - Adding flow. [FLOW] */
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
    return 0;
}
