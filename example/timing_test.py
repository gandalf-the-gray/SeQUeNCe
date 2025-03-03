import os
import statistics as stats
import sys
import time
import subprocess
import numpy as np
import matplotlib.pyplot as plt
import ast


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
        
        #Change this
        #For Time vs Distance
        destinations = ['c','d','e','f','g','h','i','j','k']
        attenuation = [1e-3]

        #For Time vs Attenuation
        #destinations = ['i']
        #attenuation = [10**(-x) for x in range(1, 5, 1)]

        
    except IndexError:
        num_trials = 5
        

    @timeit_wrapper
    def run(fidelityInt, fidelityE2E, isvirtual ,dest, attenuation):
        sys.stdout = open(os.devnull, 'w')
        retval = subprocess.check_output([sys.executable, 'conti_code.py', str(fidelityInt), str(fidelityE2E) , str(isvirtual), str(dest), str(attenuation)]).decode(sys.stdout.encoding)
        sys.stdout = sys.__stdout__
        return retval

    print("running timing test for {} with {} trials".format(script, num_trials))

    Physical_Ent_Time = []
    Virtual_Ent_Time = []
    distance_from_src = []
    fidelity_physical = []
    fidelity_virtual = []


    #for i in range(num_trials):
    for dest in destinations:
        for f_i in fidelityIntermediate:
            for f_e2e in fidelityE2E:            
                for atten in attenuation:
                    distance_from_src.append(destinations.index(dest))
                    print(f"Running for Destination: {dest}  intermediate fidelity value {round(f_i, 3)} and E2E fidelity value {round(f_e2e, 3)} and attenuation {atten} \n", end='', flush=True)
                    print('Running for Physical')
                    retvalPhy = run(f_i, f_e2e, 'False' ,dest, atten)
                    print('From retval ---- ', retvalPhy)
                    Physical_Ent_Time.append(float(ast.literal_eval(retvalPhy)[0]))
                    fidelity_physical.append(float(ast.literal_eval(retvalPhy)[1]))
                    print(Physical_Ent_Time)
                   

                    print('Running for Virtual')
                    retvalVirt = run(f_i, f_e2e, 'True' ,dest, atten)
                    Virtual_Ent_Time.append(float(ast.literal_eval(retvalVirt)[0]))
                    fidelity_virtual.append(float(ast.literal_eval(retvalVirt)[1]))
                    print(Virtual_Ent_Time)

                    print('From retval ---- ', retvalVirt)
        
        
        #print("ran in {}s".format(runtimes[-1]))

    #print("mean time: {}".format(stats.mean(runtimes)))
    #print("min time:  {}".format(min(runtimes)))
    #print("max time:  {}".format(max(runtimes)))
    #print("standard deviation: {}".format(stats.stdev(runtimes)))

fig, ax = plt.subplots()

"""
#Change this
#For change in distance from source
ax.plot(distance_from_src, Physical_Ent_Time, color = 'blue' ,label = r'Time for physical')
ax.plot(distance_from_src, Virtual_Ent_Time, color = 'red', label = r'Time for virtual')

ax.legend(loc = 'upper left')
plt.xlabel('Distance From Source')
plt.ylabel('Entanglement Time')
plt.show()


print(attenuation)
#For change in attenuation
ax.plot(attenuation, Physical_Ent_Time, color = 'blue' ,label = r'Time for physical')
ax.plot(attenuation, Virtual_Ent_Time, color = 'red', label = r'Time for virtual')

ax.set_xscale('log')
ax.legend(loc = 'upper left')
plt.xlabel('Attenuation')
plt.ylabel('Entanglement Time')
plt.show()
"""

ax.plot(distance_from_src, fidelity_physical, alpha= 0.5,  color = 'red' ,label = r'Fidelity for physical')
ax.plot(distance_from_src, fidelity_virtual, '--' , alpha= 0.5, color = 'black', label = r'Fidelity for virtual')

ax.legend(loc = 'upper right')
plt.xlabel('Distance From Source')
plt.ylabel('Entanglement Fidelity')
plt.show()



