import sequence
from numpy import random
from sequence.kernel.timeline import Timeline
from sequence.topology.topology import Topology
from sequence.topology.node import *
import math, sys
import networkx as nx
import matplotlib.pyplot as plt

random.seed(0)
network_config = "test_topology.json"

tl = Timeline(4e12)
network_topo = Topology("network_topo", tl)
network_topo.load_config(network_config)

def set_parameters(topology: Topology):
    # set memory parameters
    MEMO_FREQ = 2e3
    MEMO_EXPIRE = 0
    MEMO_EFFICIENCY = 1
    MEMO_FIDELITY = 0.9349367588934053
    for node in topology.get_nodes_by_type("QuantumRouter"):
        node.memory_array.update_memory_params("frequency", MEMO_FREQ)
        node.memory_array.update_memory_params("coherence_time", MEMO_EXPIRE)
        node.memory_array.update_memory_params("efficiency", MEMO_EFFICIENCY)
        node.memory_array.update_memory_params("raw_fidelity", MEMO_FIDELITY)

    # set detector parameters
    DETECTOR_EFFICIENCY = 0.9
    DETECTOR_COUNT_RATE = 5e7
    DETECTOR_RESOLUTION = 100
    for node in topology.get_nodes_by_type("BSMNode"):
        node.bsm.update_detectors_params("efficiency", DETECTOR_EFFICIENCY)
        node.bsm.update_detectors_params("count_rate", DETECTOR_COUNT_RATE)
        node.bsm.update_detectors_params("time_resolution", DETECTOR_RESOLUTION)
        
    # set entanglement swapping parameters
    SWAP_SUCC_PROB = 0.90
    SWAP_DEGRADATION = 0.99
    for node in topology.get_nodes_by_type("QuantumRouter"):
        node.network_manager.protocol_stack[1].set_swapping_success_rate(SWAP_SUCC_PROB)
        node.network_manager.protocol_stack[1].set_swapping_degradation(SWAP_DEGRADATION)
        
    # set quantum channel parameters
    ATTENUATION = 1e-5
    QC_FREQ = 1e11
    for qc in topology.qchannels:
        qc.attenuation = ATTENUATION
        qc.frequency = QC_FREQ

set_parameters(network_topo)

# the start and end nodes may be edited as desired 
node1 = "u"
node2 = "v"
nm = network_topo.nodes[node1].network_manager
nm.request("v", start_time=2e12, end_time=10e12, memory_size=5, target_fidelity=0.9)

nm2 = network_topo.nodes["s"].network_manager
nm2.request("t", start_time=3e12, end_time=10e12, memory_size=5, target_fidelity=0.9)

tl.init()
tl.run()
"""
print('tl.time= ',tl.time)
print(node1, "memories")
print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:")
for info in network_topo.nodes[node1].resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}".format(str(info.index), str(info.remote_node),
                                         str(info.fidelity), str(info.entangle_time * 1e-12)))
"""
print('--------------------------------------')

tl.stop_time = 9e12#setting the simulation stop time, but ts not necessary that the simulation will stop at this, if all
                    #the simulation stops at the termination of last valid event, if valid events conitinue to be beyond this
                    #stop time then simulation stops at stop time.
tl.run()
print('tl.time= ',tl.time)
print(node1, "memories")
print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:")
for info in network_topo.nodes[node1].resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}".format(str(info.index), str(info.remote_node),
                                         str(info.fidelity), str(info.entangle_time * 1e-12)))

print("s memories")
print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:")
for info in network_topo.nodes["s"].resource_manager.memory_manager:
    print("{:6}\t{:15}\t{:9}\t{}".format(str(info.index), str(info.remote_node),
                                         str(info.fidelity), str(info.entangle_time * 1e-12)))

#Obtaining the physical graph
nx_graph = network_topo.generate_nx_graph()
#nx.draw(nx_graph, with_labels = True)
#plt.show()
network_topo.plot_graph(nx_graph)

#Obtaining the virtual graph
virt_graph = network_topo.get_virtual_graph()
network_topo.plot_graph(virt_graph)




"""
    for other in network_topo.nodes.keys():

        #Check if this is middle node then skip it
        if type(network_topo.nodes[other]) == BSMNode:
            continue

        if node == other:
            continue

"""