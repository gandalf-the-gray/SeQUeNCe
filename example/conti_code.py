import sequence
from numpy import random
from sequence.kernel.timeline import Timeline
from sequence.topology.topology import Topology
from sequence.topology.node import *
import math, sys
import networkx as nx
import matplotlib.pyplot as plt

random.seed(0)
network_config = "../example/test_topology.json"

tl = Timeline(4e12)
network_topo = Topology("network_topo", tl)
network_topo.load_config(network_config)

def set_parameters(topology: Topology):
    # set memory parameters
    MEMO_FREQ = 2e3
    MEMO_EXPIRE = 0
    MEMO_EFFICIENCY = 1
    MEMO_FIDELITY = 0.9349367588934053
    #MEMO_FIDELITY = 0.99
    for node in topology.get_nodes_by_type("QuantumRouter"):
        node.memory_array.update_memory_params("frequency", MEMO_FREQ)
        node.memory_array.update_memory_params("coherence_time", MEMO_EXPIRE)
        node.memory_array.update_memory_params("efficiency", MEMO_EFFICIENCY)
        node.memory_array.update_memory_params("raw_fidelity", MEMO_FIDELITY)

    # set detector parameters
    #DETECTOR_EFFICIENCY = 0.9
    DETECTOR_EFFICIENCY = 0.99
    DETECTOR_COUNT_RATE = 5e7
    DETECTOR_RESOLUTION = 100
    for node in topology.get_nodes_by_type("BSMNode"):
        node.bsm.update_detectors_params("efficiency", DETECTOR_EFFICIENCY)
        node.bsm.update_detectors_params("count_rate", DETECTOR_COUNT_RATE)
        node.bsm.update_detectors_params("time_resolution", DETECTOR_RESOLUTION)
        
    # set entanglement swapping parameters
    #SWAP_SUCC_PROB = 0.90
    SWAP_SUCC_PROB = 0.99
    #SWAP_DEGRADATION = 0.99
    SWAP_DEGRADATION = 1
    for node in topology.get_nodes_by_type("QuantumRouter"):
        node.network_manager.protocol_stack[1].set_swapping_success_rate(SWAP_SUCC_PROB)
        node.network_manager.protocol_stack[1].set_swapping_degradation(SWAP_DEGRADATION)
        
    # set quantum channel parameters
    #ATTENUATION = 1e-5
    ATTENUATION = 1e-10
    QC_FREQ = 1e11
    for qc in topology.qchannels:
        qc.attenuation = ATTENUATION
        qc.frequency = QC_FREQ



if __name__ == "__main__":

    fidelityIntermediate = float(sys.argv[1])
    fidelityE2E = float(sys.argv[2])
    isvirtual = str(sys.argv[3])
    dest = str(sys.argv[4])
    
    set_parameters(network_topo)

    if isvirtual == 'True':
        node1 = "a"
        node2 = "c"
        nm = network_topo.nodes[node1].network_manager
        nm.createvirtualrequest(node2, start_time=2e12, end_time=20e12, memory_size=1,target_fidelity=fidelityIntermediate )

        #node1 = "d"
        #node2 = "f"
        #nm = network_topo.nodes[node1].network_manager
        #nm.createvirtualrequest(node2, start_time=3e12, end_time=20e12, memory_size=1, target_fidelity=fidelityIntermediate)

        #the start and end nodes may be edited as desired 
        #node1 = "g"
        #node2 = "i"
        #nm = network_topo.nodes[node1].network_manager
        #nm.createvirtualrequest(node2, start_time=2e12, end_time=20e12, memory_size=1, target_fidelity=fidelityIntermediate)


        tl.init()
        tl.run()

        max_time = 0
        max_time_fidelity = 0
        for info in network_topo.nodes["a"].resource_manager.memory_manager:
            if info.remote_node == 'c' and info.entangle_time > max_time:
                max_time = info.entangle_time
                max_time_fidelity = info.fidelity

        #print('Fidelity obtained between a to c: ', max_time_fidelity)
        """
        max_time = 0
        max_time_fidelity = 0
        for info in network_topo.nodes["d"].resource_manager.memory_manager:
            if info.remote_node == 'f' and info.entangle_time > max_time:
                max_time = info.entangle_time
                max_time_fidelity = info.fidelity

        print('Fidelity obtained between d to f: ', max_time_fidelity)

        max_time = 0
        max_time_fidelity = 0
        for info in network_topo.nodes["g"].resource_manager.memory_manager:
            if info.remote_node == 'i' and info.entangle_time > max_time:
                max_time = info.entangle_time
                max_time_fidelity = info.fidelity

        print('Fidelity obtained between g to i: ', max_time_fidelity)
        """
    #print('tl.time= ',tl.time)
    """
    print('tl.time= ',tl.time)
    print(node1, "memories")
    print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:")
    for info in network_topo.nodes[node1].resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12)))
    """
    #print('--------------------------------------')
    #print("Second request starts")

    
    if isvirtual != 'True':
        tl.init()

    tl.stop_time = 20e12#setting the simulation stop time, but ts not necessary that the simulation will stop at this, if all
                        #the simulation stops at the termination of last valid event, if valid events conitinue to be beyond this
                        #stop time then simulation stops at stop time.
    req_start_time = 5e12
    nm2 = network_topo.nodes["a"].network_manager
    nm2.request(dest, start_time=req_start_time, end_time=20e12, memory_size=1, target_fidelity=fidelityE2E)

    tl.run()

    
    #Find the max entanglement time at A or I to find max timestep taken
    max_time = 0
    max_time_fidelity = 0
    max_time_state = None
    for info in network_topo.nodes["a"].resource_manager.memory_manager:
        if info.remote_node == dest and info.entangle_time > max_time:
            max_time = info.entangle_time
            max_time_fidelity = info.fidelity
            max_time_state = info.state

            if info.entangle_time > 0  and info.entangle_time < req_start_time:
                max_time = req_start_time


    print(f"['{(max_time - req_start_time)*1e-12}','{round(max_time_fidelity, 3)}','{round(fidelityE2E, 3)}', '{max_time_state}']")
    

    #Along with this we'll print the fidelity too

    #print('tl.time= ',tl.time)

    """print("A memories")
    print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
    for info in network_topo.nodes["a"].resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))
                                            
    print("B memories")
    print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:")
    for info in network_topo.nodes["b"].resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))                                

    print("C memories")
    print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:")
    for info in network_topo.nodes["c"].resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))

    print("D memories")
    print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
    for info in network_topo.nodes["d"].resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))

    print("E memories")
    print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:")
    for info in network_topo.nodes["e"].resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))

    print("F memories")
    print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:")
    for info in network_topo.nodes["f"].resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))
                                            
    print("G memories")
    print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:")
    for info in network_topo.nodes["g"].resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))

    
    print("J memories")
    print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:")
    for info in network_topo.nodes["j"].resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))
    print("K memories")
    print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:")
    for info in network_topo.nodes["k"].resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state))) 
                                           

    #Obtaining the physical graph
    nx_graph = network_topo.generate_nx_graph()
    #nx.draw(nx_graph, with_labels = True)
    #plt.show()
    network_topo.plot_graph(nx_graph)

    #Obtaining the virtual graph
    virt_graph = network_topo.get_virtual_graph()

    network_topo.plot_graph(virt_graph)




    
        for other in network_topo.nodes.keys():

            #Check if this is middle node then skip it
            if type(network_topo.nodes[other]) == BSMNode:
                continue

            if node == other:
                continue

    """