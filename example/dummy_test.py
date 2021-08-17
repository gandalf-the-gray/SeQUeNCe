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
#network_config = "../example/linear_test_topology.json"

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
    #SWAP_SUCC_PROB = 0.99
    SWAP_SUCC_PROB = 0.95
    #SWAP_SUCC_PROB = 1
    
    #SWAP_DEGRADATION = 0.99
    #SWAP_DEGRADATION = 1
    SWAP_DEGRADATION = 0.99
    
    for node in topology.get_nodes_by_type("QuantumRouter"):
        node.network_manager.protocol_stack[1].set_swapping_success_rate(SWAP_SUCC_PROB)
        node.network_manager.protocol_stack[1].set_swapping_degradation(SWAP_DEGRADATION)
        
    # set quantum channel parameters
    #ATTENUATION = 1e-5
    #ATTENUATION = 1e-10
    #ATTENUATION = 1e-8
    ATTENUATION = 1e-3
    QC_FREQ = 1e11
    for qc in topology.qchannels:
        qc.attenuation = ATTENUATION
        qc.frequency = QC_FREQ

if __name__ == "__main__":

    set_parameters(network_topo)

    node1 = "h"
    node2 = "g"
    nm = network_topo.nodes[node1].network_manager
    nm.createvirtualrequest(node2, start_time=3e12, end_time=20e12, memory_size=1, target_fidelity=0.5)
  
    node1 = "j"
    node2 = "d"
    nm = network_topo.nodes[node1].network_manager
    nm.createvirtualrequest(node2, start_time=3e12, end_time=20e12, memory_size=1, target_fidelity=0.5)
  

    tl.init()
    tl.run()

    print("H memories")
    print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
    for info in network_topo.nodes["h"].resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))
    """
    #Going through the events queue of current timeline
    #object to find what events are currently present
    #Event counters for virtual links
    j_counter = 0
    d_counter = 0
    d_events_time = []
    i_counter = 0
    i_events_time = []
    g_counter = 0
    h_counter = 0
    a_counter = 0
    b_counter = 0
    c_counter = 0
    k_counter = 0
    l_counter = 0
    type_set={'EMPTY'}
    type_name_set={'EMPTY'}
    d_process_set = {'EMPTY'}
    i_process_set = {'EMPTY'}
    h_process_set = {'EMPTY'}
    d_args_set = []
    i_args_set = []
    h_args_set = []
    d_remote_protocols = []
    h_remote_protocols = []

    prev_event_d, prev_event_d_time, event_after_d_begin_time = False, 0 , []
    prev_event_i, prev_event_i_time, event_after_i_begin_time = False, 0 , []
    prev_event_g, prev_event_g_time, event_after_g_begin_time = False, 0 , []
    prev_event_c, prev_event_c_time, event_after_c_begin_time = False, 0 , []
    d_event_duration, i_event_duration = [], []
    g_event_duration, c_event_duration = [], []

    while len(tl.events) > 0:
        print('Events are still remaining')
        event = tl.events.pop()
        print('Event start time: ', event.time)
        print('event.process.owner.name: ', event.process.owner.name)
        print('type(event.process.act_params[1]).__name__: ', type(event.process.act_params[1]).__name__)

        if prev_event_d:
            event_after_d_begin_time.append(event.time)
            d_event_duration.append(event.time - prev_event_d_time)
            prev_event_d = False
            prev_event_d_time = 0

        if prev_event_i:
            event_after_i_begin_time.append(event.time)
            i_event_duration.append(event.time - prev_event_i_time)
            prev_event_i = False
            prev_event_i_time = 0

        if prev_event_g:
            event_after_g_begin_time.append(event.time)
            g_event_duration.append(event.time - prev_event_g_time)
            prev_event_g = False
            prev_event_g_time = 0

        if prev_event_c:
            event_after_c_begin_time.append(event.time)
            c_event_duration.append(event.time - prev_event_c_time)
            prev_event_c = False
            prev_event_c_time = 0

        
        if event.time>5e12 and event.time<5.4e12:
            #if type(event.process.owner) not in type_dict:
            type_set.add(type(event.process.owner))
            type_name_set.add(event.process.owner.name)
            #print('event owner: ', event.process.owner.name)
            if event.process.owner.name == 'j':
                j_counter = j_counter+1
            
            if event.process.owner.name == 'd':
                prev_event_d = True
                prev_event_d_time = event.time
                d_counter = d_counter+1
                d_process_set.add(event.process.activation)
                #d_args_set.append(type(event.process.act_params[1]).__name__)
                d_args_set.append(event.process.act_params)
                if type(event.process.act_params[1]).__name__ ==  'ResourceManagerMessage':
                    print('d remote protocol: ', event.process.act_params[1].ini_protocol.name)
                d_events_time.append(event.time)
                
            if event.process.owner.name == 'i':
                prev_event_i = True
                prev_event_i_time = event.time
                i_counter = i_counter+1
                i_process_set.add(event.process.activation)
                i_args_set.append(type(event.process.act_params[1]).__name__)
                if type(event.process.act_params[1]).__name__ ==  'ResourceManagerMessage':
                    print('i remote protocol: ', event.process.act_params[1].ini_protocol.name)
                i_events_time.append(event.time)
            
            if event.process.owner.name == 'g':
                prev_event_g = True
                prev_event_g_time = event.time
                g_counter = g_counter+1
                
                #i_process_set.add(event.process.activation)
                #i_args_set.append(type(event.process.act_params[1]).__name__)
                #if type(event.process.act_params[1]).__name__ ==  'ResourceManagerMessage':
                #    print('i remote protocol: ', event.process.act_params[1].ini_protocol.name)
                #g_events_time.append(event.time)
            
            if event.process.owner.name == 'c':
                prev_event_c = True
                prev_event_c_time = event.time
                c_counter = c_counter+1
                
                #i_process_set.add(event.process.activation)
                #i_args_set.append(type(event.process.act_params[1]).__name__)
                #if type(event.process.act_params[1]).__name__ ==  'ResourceManagerMessage':
                #    print('i remote protocol: ', event.process.act_params[1].ini_protocol.name)
                #c_events_time.append(event.time)
            
            if event.process.owner.name == 'h':
                h_counter = h_counter+1
                h_process_set.add(event.process.activation)
                h_args_set.append(type(event.process.act_params[1]).__name__)
                if type(event.process.act_params[1]).__name__ == 'ResourceManagerMessage':
                    print('h remote protocol: ', event.process.act_params[1].ini_protocol.name)
            if event.process.owner.name == 'a':
                a_counter = a_counter+1
            if event.process.owner.name == 'b':
                b_counter = b_counter+1
            #if event.process.owner.name == 'c':
            #   c_counter = c_counter+1
            if event.process.owner.name == 'k':
                k_counter = k_counter+1
            if event.process.owner.name == 'l':
                l_counter = l_counter+1
            
        
    print('j_counter: ', j_counter)
    print('d_counter: ', d_counter)
    print()
    print('d_events_time: ', d_events_time)
    print()
    print()
    print('event_after_d_begin_time: ', event_after_d_begin_time)
    print()
    print('i_counter: ', i_counter)
    print()
    print('i_events_time: ', i_events_time)
    print()
    print()
    print('event_after_i_begin_time: ', event_after_i_begin_time)
    print()
    print('g_counter: ', g_counter)
    print('h_counter: ', h_counter)
    print('a_counter: ', a_counter)
    print('b_counter: ', b_counter)
    print('c_counter: ', c_counter)
    print('k_counter: ', k_counter)
    print('l_counter: ', l_counter)
    print('type_set: ', type_set)
    print('type_name_set: ', type_name_set)
    print('d_process_set', d_process_set)
    print('i_process_set', i_process_set)
    #print('h_process_set', h_process_set)
    print('d_args_set', d_args_set)
    #print('h_args_set', h_args_set)
    print('d_event_duration', d_event_duration)
    print('i_event_duration', i_event_duration)
    print('g_event_duration', g_event_duration)
    print('c_event_duration', c_event_duration)
    print('d events sum: ', sum(d_event_duration))
    print('i events sum: ', sum(i_event_duration))
    print('g events sum: ', sum(g_event_duration))
    print('c events sum: ', sum(c_event_duration))
    print('d+i+g+c sum: ', (sum(d_event_duration)+sum(i_event_duration)+sum(g_event_duration)+sum(c_event_duration)))
    """

    
    for i in range(2):
        event = tl.events.pop()
        print('Event start time: ', event.time)
        print('event.process.owner.name: ', event.process.owner.name)
        print('type(event.process.act_params[1]).__name__: ', type(event.process.act_params[1]).__name__)
        if type(event.process.act_params[1]).__name__ ==  'ResourceManagerMessage':
            print('remote protocol: ', event.process.act_params[1].ini_protocol.name)
        
        tl.run_counter += 1
        print('length of events: ', len(tl.events))
    

    
    tl.stop_time = 20e12#setting the simulation stop time, but ts not necessary that the simulation will stop at this, if all
                        #the simulation stops at the termination of last valid event, if valid events conitinue to be beyond this
                        #stop time then simulation stops at stop time.
    req_start_time = 5e12
    nm2 = network_topo.nodes['m'].network_manager
    nm2.request('f', start_time=req_start_time, end_time=20e12, memory_size=1, target_fidelity=0.5)

    tl.run()
    """

    print("H memories")
    print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
    for info in network_topo.nodes["h"].resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))
    
    print("D memories")
    print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
    for info in network_topo.nodes["d"].resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))
    
    print("I memories")
    print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
    for info in network_topo.nodes["i"].resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))
    
    print("M memories")
    print("Index:\tEntangled Node:\tFidelity:\tEntanglement Time:\tState:")
    for info in network_topo.nodes["m"].resource_manager.memory_manager:
        print("{:6}\t{:15}\t{:9}\t{}\t{}".format(str(info.index), str(info.remote_node),
                                            str(info.fidelity), str(info.entangle_time * 1e-12),str(info.state)))
    """