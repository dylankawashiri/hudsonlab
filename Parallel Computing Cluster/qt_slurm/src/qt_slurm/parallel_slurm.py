import os
import csv
from qutip import *
import numpy as np
from IPython.display import Javascript, display
import re
import shutil
from pathlib import Path
import time
import matplotlib.pyplot as plt
import nbformat
from nbconvert import PythonExporter


def initialize():
    home_dir = os.getenv('HOME')
    with open(home_dir + "/temporary_files/execute.csv", 'w') as f:
        write = csv.writer(f)
        write.writerow("0")
    
def split_func(num_of_divs):
    '''
    The split function specifies how many tasks each node will accomplish.
    '''
    rank, total_ranks = get_rank()
    
    split = num_of_divs // total_ranks
    split_arr = []
    for i in range(total_ranks):
        split_arr.append(split)
    for i in range(int(num_of_divs % total_ranks)):
        split_arr[i]+=1
    return split_arr

    
def get_rank():
    rank = int(os.getenv('SLURM_PROCID', 0))
    total_ranks = int(os.getenv('SLURM_NTASKS', 1))
    return rank, total_ranks

        
def parallelize(func, detunings, num_of_divs):
    '''
    The Parallelize function uses Qutip's parallel_map feature and splits the number of tasks created by parallel_map and gives a specified amount to each node. 
    Data is sent to a temporary file system and collected by the last node to complete its computation(s).
    '''
    home_dir = os.getenv('HOME')

    split_arr = split_func(num_of_divs)
    
    #Safety - deletes any existing filesystem that there might be before job execution
    job_id = os.getenv('SLURM_JOB_ID')    
    
    rank, total_ranks = get_rank()
    results_arr = [[] for _ in range(total_ranks + 1)]

    
    detunings_arr=[]
    for i in range(total_ranks):
        if i == 0:
            detunings_arr.append(detunings[i:split_arr[i]])
        else:
            detunings_arr.append(detunings[sum(split_arr[:i]):sum(split_arr[:i])+split_arr[i]])

    for i in range(total_ranks):
        if i == rank:
            results = parallel_map(func,detunings_arr[i])
            results_array = np.array(results).tolist()
            
    try: #Makes a temporary folder
        if os.path.isdir(home_dir + "/temporary_files/tmp" + str(job_id)) == False:
            os.mkdir(home_dir + "/temporary_files/tmp"+ str(job_id))
            with open(home_dir + "/temporary_files/execute.csv", 'w') as f:
                write = csv.writer(f)
                write.writerow("1")
    
    except Exception as e:
        print(f"Skip: {e}")


    if os.path.isfile(home_dir + "/temporary_files/tmp" + str(job_id) + "/results_array.csv")==True:
        with open(home_dir + "/temporary_files/tmp" + str(job_id) + "/results_array.csv", newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"',quoting=csv.QUOTE_MINIMAL)
            tmp = 0
            for row in reader:
                results_arr[tmp] = row
                tmp+=1

        results_arr[rank] = results_array
        results_arr[-1][0]=int(results_arr[-1][0])
        results_arr[-1][0]+=1
        val = results_arr[-1][0]
        with open(home_dir + "/temporary_files/tmp" + str(job_id) + "/results_array.csv", 'w') as f:

            # using csv.writer method from CSV package
            write = csv.writer(f)

            write.writerows(results_arr)
    else:
        results_arr[rank] = results_array
        results_arr[-1]=[1]
        print("here")
        with open(home_dir + "/temporary_files/tmp" + str(job_id) + "/results_array.csv", 'w') as f:

                # using csv.writer method from CSV package
                write = csv.writer(f)

                write.writerows(results_arr) 
        val = results_arr[-1][0]
    if int(val) == total_ranks:
        with open(home_dir + "/temporary_files/execute.csv", 'w') as f:
                write = csv.writer(f)
                write.writerow("0")
        with open(home_dir + "/temporary_files/tmp" + str(job_id) + "/results_array.csv", newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"',quoting=csv.QUOTE_MINIMAL)
            tmp = 0
            for row in reader:
                results_arr[tmp] = row
                tmp+=1
        for i in range(len(results_arr)):
            for j in range(len(results_arr[i])):
                results_arr[i][j] = float(results_arr[i][j])

        results_arr.pop(-1)
        results_arr = [i for j in results_arr for i in j]
        
        try:    
            graph=plt.plot(detunings/(2*np.pi),results_arr)
            sv = 0
            n = 0
            while(sv == 0):
                if os.path.isfile(home_dir + "/sim_data/" + str(n) + ".png") == True:
                    n += 1         
                else:
                    name_dat = home_dir + "/sim_data/" + str(n) + ".csv"
                    with open(name_dat, 'w') as f:
                        write = csv.writer(f)
                        write.writerow(results_arr)
                    name = home_dir + "/sim_data/" + str(n) + ".png"
                    plt.savefig(name) 
                    print("Figure saved as " + str(n) + ".png")
                    print("Data saved as " + str(n) + ".csv") 
                    sv = 1
                
            try:
                os.remove(home_dir + "/temporary_files/tmp" + str(job_id) + "/results_array.csv")
                os.rmdir(home_dir + "/temporary_files/tmp" + str(job_id))
            except Exception as e:
                print(f"{e}")
            
        except Exception as e:
            print(f"{e}")
    return results_arr

def execute(name, nodes, cores, tasks):
    #Parts from ChatGPT
    
    home_dir = os.getenv('HOME')
    with open(home_dir + "/temporary_files/execute.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"',quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            val = row
    if int(val[0]) != 1:        
        if os.path.isfile(home_dir + "/shared_scripts/" + name.split(".")[0]+ ".py") == False:
            file = name.split(".")[0]+ ".ipynb"
            try:
                with open(file, 'r') as notebook_file:
                    notebook_content = nbformat.read(file, as_version=4)

                # Convert the notebook to Python script
                python_exporter = PythonExporter()
                python_script, _ = python_exporter.from_notebook_node(notebook_content)

                # Write the script to a file
                with open(home_dir + "/shared_scripts/" + name.split(".")[0]+ ".py", 'w') as output_file:
                    output_file.write(python_script)

                os.system("srun -n" + str(nodes) + " -c " + str(cores) + " -N " + str(tasks) + " python " + home_dir + "/shared_scripts/" + name.split(".")[0]+ ".py")

            except Exception as e:
                print(f"Error: {e}")

        else:
            ans = input("A file with the name of your Jupyter notebook file already exists, would you like to delete it and restart (will be done automatically)?")
            if ans.lower().replace(" ", "") == "yes" or ans.lower().replace(" ", "") =="y":
                os.remove(home_dir + "/shared_scripts/" + name.split(".")[0]+ ".py")
                execute(name, nodes, cores, tasks)
            else:
                print("Exiting...")
           
