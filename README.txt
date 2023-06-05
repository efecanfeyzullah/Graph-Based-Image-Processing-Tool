Graph Based Image Processing Tool

Mustafa Ali Akçay 2330678
Efe Can Feyzullah 2448371

Usage:

python tcp_service.py --port 1234


Server Commands:

-Multi-instance commands-
newgraph
listgraphs
open <graph_id>
close <graph_id>

-Graph specific commands-
newnode <node_type>
connect <node1_id> <node1_outport> <node2_id> <node2_inport>
disconnect <node1_id> <node1_outport> <node2_id> <node2_inport>
set <node_id>
execute
