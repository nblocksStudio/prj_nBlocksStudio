#include "nblocks.h"
#include "or.h"

// -*-*- begin automatically generated code -*-*-
nBlock_GPI               nb_gpi1;        //xy=122,228
nBlock_GPO               nb_gpo1;        //xy=638.4615384615383,221.5384615384615
nBlock_OR               nb_or1;
nBlockConnection         n_conn2(&nb_gpi1, 0, &nb_or1, 0);
nBlockConnection	     n_conn3(&nb_gpi1, 1, &nb_or1,1);



nBlockConnection         n_conn1(&nb_or1, 0, &nb_gpo1, 0);

int main(void) {
    SetupWorkbench();
    while(1) {
    }
}
// -*-*- end automatically generated code -*-*-


