import sequence
from numpy import random
from sequence.kernel.timeline import Timeline
from sequence.topology.topology import Topology
from sequence.topology.node import *
import math, sys
import networkx as nx
import matplotlib.pyplot as plt
  
def conti_code(fidelityIntermediate, fidelityE2E, isvirtual, dest, attenuation, seed, src):
  random.seed(0)
  network_config = "../example/test_topology.json"

  tl = Timeline(4e12)
  network_topo = Topology("network_topo", tl)
  network_topo.load_config(network_config)

  def set_parameters(topology: Topology, attenuation, seed):
      # set memory parameters
      MEMO_FREQ = 2e3
      MEMO_EXPIRE = 0
      MEMO_EFFICIENCY = 1
      MEMO_FIDELITY = 0.9349367588934053
      #MEMO_FIDELITY = 0.99
      for node in topology.get_nodes_by_type("QuantumRouter"):
          node.random_seed = seed
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
      #SWAP_SUCC_PROB = 0.50
      
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
      ATTENUATION = attenuation
      QC_FREQ = 1e11
      for qc in topology.qchannels:
          qc.attenuation = ATTENUATION
          qc.frequency = QC_FREQ


  set_parameters(network_topo, attenuation, seed)

  if isvirtual == 'True':
      #node1 = "m"
      #node2 = "a"
      #nm = network_topo.nodes[node1].network_manager
      #nm.createvirtualrequest(node2, start_time=2e12, end_time=20e12, memory_size=1,target_fidelity=fidelityIntermediate )

      node1 = "d"
      node2 = "f"
      nm = network_topo.nodes[node1].network_manager
      nm.createvirtualrequest(node2, start_time=3e12, end_time=20e12, memory_size=1, target_fidelity=fidelityIntermediate)

      #the start and end nodes may be edited as desired 
      #node1 = "g"
      #node2 = "i"
      #nm = network_topo.nodes[node1].network_manager
      #nm.createvirtualrequest(node2, start_time=2e12, end_time=20e12, memory_size=1, target_fidelity=fidelityIntermediate)


      tl.init()
      tl.run()

      """max_time = 0
      max_time_fidelity = 0
      for info in network_topo.nodes["m"].resource_manager.memory_manager:
          if info.remote_node == 'a' and info.entangle_time > max_time:
              max_time = info.entangle_time
              max_time_fidelity = info.fidelity

      print('Fidelity obtained between m to a: ', max_time_fidelity)
      
      max_time = 0
      max_time_fidelity = 0
      for info in network_topo.nodes["e"].resource_manager.memory_manager:
          if info.remote_node == 'k' and info.entangle_time > max_time:
              max_time = info.entangle_time
              max_time_fidelity = info.fidelity

      print('Fidelity obtained between e to k: ', max_time_fidelity)

  
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
  nm2 = network_topo.nodes[src].network_manager
  nm2.request(dest, start_time=req_start_time, end_time=20e12, memory_size=1, target_fidelity=fidelityE2E)

  tl.run()

  
  #Find the max entanglement time at A or I to find max timestep taken
  max_time = -10
  max_time_fidelity = 0
  max_time_state = None
  for info in network_topo.nodes[src].resource_manager.memory_manager:
      if info.remote_node == dest and info.entangle_time > max_time:
          max_time = info.entangle_time
          max_time_fidelity = info.fidelity
          max_time_state = info.state

  if max_time < req_start_time:
      max_time = req_start_time

  #print(f"['{(max_time - req_start_time)*1e-12}','{round(max_time_fidelity, 3)}','{round(fidelityE2E, 3)}', '{max_time_state}']")
  return [(max_time - req_start_time)*1e-12, round(max_time_fidelity, 3), round(fidelityE2E, 3), max_time_state]

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

#%matplotlib inline

import os
import statistics as stats
import sys
import time
import subprocess
import numpy as np
import matplotlib.pyplot as plt
import ast
import json
import networkx as nx

from collections import OrderedDict
from operator import itemgetter

runtimes = []


def timeit_wrapper(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        return_val = func(*args, **kwargs)
        end = time.perf_counter()
        runtimes.append(end - start)
        return return_val
    return wrapper

"""
if __name__ == "__main__":
    '''
    Program for timing a script, returns average of several runs
    input: relative path to script
    '''

    script = sys.argv[1]
    #isvirtual = sys.argv[2]
    current_iter=0
"""
try:
    
    fidelityIntermediate=[x for x in np.arange(0.7,0.71,0.03)]
    fidelityE2E = [x for x in np.arange(0.5,0.51,0.03)]
    num_trials = len(fidelityE2E)*len(fidelityIntermediate)
    
    with open('test_topology.json') as handle:
        topology_json = json.loads(handle.read())

    #print(topology_json["qconnections"])

    G = nx.Graph()
    for conn in topology_json["qconnections"]:
        print(f'src: {conn["node1"]} and dest: {conn["node2"]}')
        G.add_edge(conn["node1"], conn["node2"], color='b') 

    colors = nx.get_edge_attributes(G,'color').values()
    #nx.draw(G, edge_color=colors, with_labels = True)
    #plt.show()

    all_pair_shortest_dict = nx.floyd_warshall(G)
    all_pair_shortest_dict = json.loads(json.dumps(all_pair_shortest_dict))
    #print(all_pair_shortest_dict)

    #source_nodes = ['a', 'd', 'f', 'i', 'k']
    source_nodes = ['j', 'k']
    source_wise_dests = {}
    max_distance_from_src = 0
    for src in source_nodes:
        dest_dict = all_pair_shortest_dict[src]
        dest_dict = OrderedDict(sorted(dest_dict.items(), key=itemgetter(1)))
        source_wise_dests[src] = dest_dict

        for (dest, dist) in source_wise_dests[src].items():
            if dist > max_distance_from_src:
                max_distance_from_src = int(dist)

    print(source_wise_dests)

    #max_distance_from_src = 0
    #for (dest, dist) in source_wise_dests['a'].items():
    #    print(dest, dist)
    #    if dist > max_distance_from_src:
    #        max_distance_from_src = int(dist)


    #Change this
    #For Time vs Distance
    #destinations = ['c','d','e','f','g','h','i','j','k','l','m']
    attenuation = [1e-3]

    #For Time vs Attenuation
    #destinations = ['i']
    #attenuation = [10**(-x) for x in range(1, 5, 1)]

    
except IndexError:
    num_trials = 5
    

def run(fidelityInt, fidelityE2E, isvirtual ,dest, attenuation, random_seed, src):
    sys.stdout = open(os.devnull, 'w')
    #retval = subprocess.check_output([sys.executable, 'conti_code.py', str(fidelityInt), str(fidelityE2E) , str(isvirtual), str(dest), str(attenuation), str(random_seed), str(src)]).decode(sys.stdout.encoding)
    retval = conti_code(fidelityInt, fidelityE2E, isvirtual, dest, attenuation, random_seed, src)
    sys.stdout = sys.__stdout__
    return retval

#print("running timing test for {} with {} trials".format(script, num_trials))

#seed = 1
#for i in range(num_trials):
#iter_seed = np.random.randint(2, 100, dtype='uint32')

simul_trials = 5
Avg_Physical_Ent_Time = [0 for i in range(max_distance_from_src)]
Avg_Virtual_Ent_Time = [0 for i in range(max_distance_from_src)]
Avg_fidelity_physical = []
Avg_fidelity_virtual = []
index_source_counter = {}

print(f'Running simulation for: {simul_trials} trials')
for i in range(simul_trials):
    print('Trial #: ', i)
    #iter_seed = np.random.randint(2, 100, dtype='uint32')
    Physical_Ent_Time = []
    Virtual_Ent_Time = []
    distance_from_src = []
    fidelity_physical = []
    fidelity_virtual = []

    for src in source_nodes:
        print('Src: ', src)
        index = 0
        #for dest in destinations:            
        for (dest, dist) in source_wise_dests[src].items():           
            if src == dest:
                continue
        
            for f_i in fidelityIntermediate:
                for f_e2e in fidelityE2E:            
                    for atten in attenuation:
                        
                        #seeds=np.random.choice(16, 5)
                        #np.random.shuffle(seeds)
                        seeds = [0 for i in range(simul_trials)]
                        #print(f"Running for Destination: {dest}  intermediate fidelity value {round(f_i, 3)} and E2E fidelity value {round(f_e2e, 3)} and attenuation {atten} \n", end='', flush=True)
                        print(f"Running for Destination: {dest} at the distance of {int(dist)} hops")
                        #print('Running for Physical')                        
                        retvalPhy = conti_code(f_i, f_e2e, 'False' ,dest, atten, seeds[i], src)
                        print('From retval ---- ', retvalPhy)
                        #Physical_Ent_Time.append(float(ast.literal_eval(retvalPhy)[0]))
                        Physical_Ent_Time.append(retvalPhy[0])
                        Avg_Physical_Ent_Time[int(dist)-1] = Avg_Physical_Ent_Time[int(dist)-1] + Physical_Ent_Time[-1]
                        #fidelity_physical.append(float(ast.literal_eval(retvalPhy)[1]))
                        fidelity_physical.append(retvalPhy[1])
                        #print(Physical_Ent_Time)
                        

                        #print('Running for Virtual')
                        retvalVirt = conti_code(f_i, f_e2e, 'True' ,dest, atten, seeds[i], src)
                        #Virtual_Ent_Time.append(float(ast.literal_eval(retvalVirt)[0]))
                        Virtual_Ent_Time.append(retvalVirt[0])
                        Avg_Virtual_Ent_Time[int(dist)-1] = Avg_Virtual_Ent_Time[int(dist)-1] + Virtual_Ent_Time[-1]
                        #fidelity_virtual.append(float(ast.literal_eval(retvalVirt)[1]))
                        fidelity_virtual.append(retvalVirt[1])
                        #print(Virtual_Ent_Time)

                        print('From retval ---- ', retvalVirt)
                        #seed = seed + 1
                        if int(dist)-1 not in index_source_counter:
                            index_source_counter[int(dist)-1] = {src}
                        else:
                            source_set = index_source_counter[int(dist)-1]
                            source_set.add(src)
                            index_source_counter[int(dist)-1] = source_set           
            index = index + 1
            #print("ran in {}s".format(runtimes[-1]))

    #print("mean time: {}".format(stats.mean(runtimes)))
    #print("min time:  {}".format(min(runtimes)))
    #print("max time:  {}".format(max(runtimes)))
    #print("standard deviation: {}".format(stats.stdev(runtimes)))

fig, ax = plt.subplots()

for i in range(max_distance_from_src):
  Avg_Physical_Ent_Time[i] = Avg_Physical_Ent_Time[i]/(simul_trials*len(index_source_counter[i]))
  Avg_Virtual_Ent_Time[i] = Avg_Virtual_Ent_Time[i]/(simul_trials*len(index_source_counter[i]))

#Change this
#For change in distance from source
ax.plot([i for i in range(1, max_distance_from_src+1)], Avg_Physical_Ent_Time, color = 'blue' ,label = r'Time for physical')
ax.plot([i for i in range(1, max_distance_from_src+1)], Avg_Virtual_Ent_Time, color = 'red', label = r'Time for virtual')

ax.legend(loc = 'upper left')
plt.xlabel('Distance From Source')
plt.ylabel('Entanglement Time')
plt.show()

"""
print(attenuation)
#For change in attenuation
ax.plot(attenuation, Physical_Ent_Time, color = 'blue' ,label = r'Time for physical')
ax.plot(attenuation, Virtual_Ent_Time, color = 'red', label = r'Time for virtual')

ax.set_xscale('log')
ax.legend(loc = 'upper left')
plt.xlabel('Attenuation')
plt.ylabel('Entanglement Time')
plt.show()


ax.plot(distance_from_src, fidelity_physical, alpha= 0.5,  color = 'red' ,label = r'Fidelity for physical')
ax.plot(distance_from_src, fidelity_virtual, '--' , alpha= 0.5, color = 'black', label = r'Fidelity for virtual')

ax.legend(loc = 'upper right')
plt.xlabel('Distance From Source')
plt.ylabel('Entanglement Fidelity')
plt.show()
"""


