import os
import csv
from qutip import *


def safety():
    '''
    The safety function ensures that each Slurm job has its own, unique temporary file system. 
    '''
    job_id = os.getenv('SLURM_JOB_ID')
    jobs=[]
    safety = 0

    if os.path.isdir("/home/farmer/temporary_files/safety")==False:
        os.mkdir("/home/farmer/temporary_files/safety")

    with open("/home/farmer/temporary_files/safety/active_jobs.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"',quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            val = row
        for i in range(len(val)):
            jobs.append(row[i])

    if job_id not in jobs:
        jobs.append(job_id)
    safety = len(jobs)
    with open("/home/farmer/temporary_files/safety/active_jobs.csv", 'w') as f:
        write = csv.writer(f)
        write.writerow(jobs)
        
    return safety
    
def split_func(num_of_divs):
    '''
    The split function specifies how many tasks each node will accomplish.
    '''
    split = num_of_divs // total_ranks
    split_arr = []
    for i in range(total_ranks):
        split_arr.append(split)
    for i in range(num_of_divs % total_ranks):
        split_arr[i]+=1
    return split_arr

    
def get_rank():
    rank = int(os.getenv('SLURM_PROCID', 0))
    total_ranks = int(os.getenv('SLURM_NTASKS', 1))
    return rank, total_ranks

        
def parallelize(func, num_of_divs):
    '''
    The Parallelize function uses Qutip's parallel_map feature and splits the number of tasks created by parallel_map and gives a specified amount to each node. 
    Data is sent to a temporary file system and collected by the last node to complete its computation(s).
    '''
    split_arr = split_func(num_of_divs)
    
    #Safety - deletes any existing filesystem that there might be before job execution
    safety_val = safety()
    try:
        os.remove("/home/farmer/temporary_files/tmp" + str(safety_val) + "/results_array.csv")
        os.rmdir("/home/farmer/temporary_files/tmp" + str(safety_val))
    except Exception as e:
        print(f"Error: {e}")
    
    
    rank, total_ranks = get_rank()
    
    
    detunings_arr=[]
    for i in range(total_ranks):
        if i == 0:
            detunings_arr.append(detunings[i:split_arr[i]])
        else:
            detunings_arr.append(detunings[sum(split_arr[:i]):sum(split_arr[:i])+split_arr[i]])

    for i in range(total_ranks):
        if i == rank:
            results = parallel_map(detuning_func,detunings_arr[i])
            results_array = np.array(results).tolist()
            
    try: #Makes a temporary folder
        if os.path.isdir("home/farmer/temporary_files/tmp" + str(safety_val)) == False:
            os.mkdir("/home/farmer/temporary_files/tmp"+ str(safety_val))

    except Exception as e:
        print(f"Error (skip): {e}")


    if os.path.isfile("/home/farmer/temporary_files/tmp" + str(safety_val) + "/results_array.csv")==True:
        with open("/home/farmer/temporary_files/tmp" + str(safety_val) + "/results_array.csv", newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"',quoting=csv.QUOTE_MINIMAL)
            tmp = 0
            for row in reader:
                results_arr[tmp] = row
                tmp+=1

        results_arr[rank] = results_array
        results_arr[-1][0]=int(results_arr[-1][0])
        results_arr[-1][0]+=1
        val = results_arr[-1][0]
        with open("/home/farmer/temporary_files/tmp" + str(safety_val) + "/results_array.csv", 'w') as f:

            # using csv.writer method from CSV package
            write = csv.writer(f)

            write.writerows(results_arr)
    else:
        results_arr[rank] = results_array
        results_arr[-1]=[1]
        with open("/home/farmer/temporary_files/tmp" + str(safety_val) + "/results_array.csv", 'w') as f:

                # using csv.writer method from CSV package
                write = csv.writer(f)

                write.writerows(results_arr) 
        val = results_arr[-1][0]
    if int(val) == total_ranks:
        with open("/home/farmer/temporary_files/tmp" + str(safety_val) + "/results_array.csv", newline='') as csvfile:
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
                if os.path.isfile("/home/farmer/sim_data/" + str(n) + ".png") == True:
                    n += 1         
                else:
                    name_dat = "/home/farmer/sim_data/" + str(n) + ".csv"
                    with open(name_dat, 'w') as f:
                        write = csv.writer(f)
                        write.writerow(results_arr)
                    name = "/home/farmer/sim_data/" + str(n) + ".png"
                    plt.savefig(name) 
                    print("Figure saved as " + str(n) + ".png")
                    print("Data saved as " + str(n) + ".csv") 
                    sv = 1
            jobs.remove(job_id)

            with open("/home/farmer/temporary_files/safety/active_jobs.csv", 'w') as f:
                # using csv.writer method from CSV package
                write = csv.writer(f)
                write.writerow(jobs)
                
            try:
                os.remove("/home/farmer/temporary_files/tmp" + str(safety_val) + "/results_array.csv")
                os.rmdir("/home/farmer/temporary_files/tmp" + str(safety_val))
            except Exception as e:
                print(f"Error: {e}")
            
        except Exception as e:
            print(f"Error: {e}")
