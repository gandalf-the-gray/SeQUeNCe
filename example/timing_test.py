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


if __name__ == "__main__":
    '''
    Program for timing a script, returns average of several runs
    input: relative path to script
    '''

    script = sys.argv[1]
    #isvirtual = sys.argv[2]
    current_iter=0
    try:
        
        fidelityIntermediate=[x for x in np.arange(0.7,0.71,0.03)]
        fidelityE2E = [x for x in np.arange(0.5,0.51,0.03)]
        num_trials = len(fidelityE2E)*len(fidelityIntermediate)
        
        with open('linear_test_topology.json') as handle:
            topology_json = json.loads(handle.read())

        #print(topology_json["qconnections"])

        G = nx.Graph()
        for conn in topology_json["qconnections"]:
            print(f'src: {conn["node1"]} and dest: {conn["node2"]}')
            G.add_edge(conn["node1"], conn["node2"], color='b') 

        colors = nx.get_edge_attributes(G,'color').values()
        nx.draw(G, edge_color=colors, with_labels = True)
        plt.show()

        all_pair_shortest_dict = nx.floyd_warshall(G)
        all_pair_shortest_dict = json.loads(json.dumps(all_pair_shortest_dict))
        #print(all_pair_shortest_dict)

        source_nodes = ['a']
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
        

    @timeit_wrapper
    def run(fidelityInt, fidelityE2E, isvirtual ,dest, attenuation, random_seed, src):
        sys.stdout = open(os.devnull, 'w')
        retval = subprocess.check_output([sys.executable, 'conti_code.py', str(fidelityInt), str(fidelityE2E) , str(isvirtual), str(dest), str(attenuation), str(random_seed), str(src)]).decode(sys.stdout.encoding)
        sys.stdout = sys.__stdout__
        return retval

    print("running timing test for {} with {} trials".format(script, num_trials))

    #seed = 1
    #for i in range(num_trials):
    #iter_seed = np.random.randint(2, 100, dtype='uint32')
    
    simul_trials = 1
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
                            print(f"Running for Destination: {dest}  intermediate fidelity value {round(f_i, 3)} and E2E fidelity value {round(f_e2e, 3)} and attenuation {atten} \n", end='', flush=True)
                            #print('Running for Physical')                        
                            retvalPhy = run(f_i, f_e2e, 'False' ,dest, atten, seeds[i], src)
                            print('From retval ---- ', retvalPhy)
                            Physical_Ent_Time.append(float(ast.literal_eval(retvalPhy)[0]))
                            Avg_Physical_Ent_Time[int(dist)-1] = Avg_Physical_Ent_Time[int(dist)-1] + Physical_Ent_Time[-1]
                            fidelity_physical.append(float(ast.literal_eval(retvalPhy)[1]))
                            #print(Physical_Ent_Time)
                           

                            #print('Running for Virtual')
                            retvalVirt = run(f_i, f_e2e, 'True' ,dest, atten, seeds[i], src)
                            Virtual_Ent_Time.append(float(ast.literal_eval(retvalVirt)[0]))
                            Avg_Virtual_Ent_Time[int(dist)-1] = Avg_Virtual_Ent_Time[int(dist)-1] + Virtual_Ent_Time[-1]
                            fidelity_virtual.append(float(ast.literal_eval(retvalVirt)[1]))
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


