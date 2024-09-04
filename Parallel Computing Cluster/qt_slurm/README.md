# Test Packaging Slurm Thing with Qutip v1.0.1
This package is meant for Qutip integration with Slurm on Linux based systems. Please let me know if there are any bugs. 

## Release History

- v0.0.1-0.1.10 - Bug fixes (previous versions are fatal)
- v0.1.11 - Added return value to parallelize function, fixed deletion of job storage 
- v0.2.1 - Added Jupyter notebook integration, $HOME generalization
- v0.2.2 - Fixed fatal bug with import
- v1.0.0 - First release, removed safety feature (not necessary), removed unecessary comments, create initialization function, working Jupyter notebook loop and deletion (if necessasry)
- v1.0.1 - Forgot to add $HOME variable to initialization function

## How to Use
### Required Installations:
- qutip<=4.7.6
- feh (apt-package)
First, import the library as shown below:
```
from qt_slurm import parallel_slurm as pqt
```
### Jupyter Notebook

If using Jupyter Notebook, at the end of your code (in the same cell as the last thing you wish to run), implement the parallelize function.

```
pqt.parallelize(func, range, num_of_divs)
```
The first parameter of pqt.parallelize is 'func'. This is the function you wish to parallelize (usually a function incorporating the mesolve/sesolve functions of Qutip). The range parameter is the parameter of the other 'func' function. This is usually the range as to which your are calculating mesolve/sesolve over. Finally, the final parameter, num_of_divs, is the number of points within your range. If using np.linspace() function, it is the final parameter entered. 

In a new cell (which will be the first cell you execute - besides the importing of libraries and modules) add the following function:

```
pqt.execute("Name_of_notebook", num_of_nodes, num_of_cores, num_of_tasks)
```

pqt.execute() is responsible for converting the contents of your Jupyter Notebook to a Python file, moving that file to a shared folder, and then finally executing a Slurm command. To do this, you must enter the name of your notebook. If you are running the Jupyter Notebook out of your home directory, you do not need to include a path name. Otherwise, include a full path name if possible. The following three parameters are all variables required by Slurm. Set num_of_cores to the number of cores each computer has (in this case, 8) and num_of_nodes and num_of_tasks to the number of nodes you wish to use. 

Once you execute the last cell, the conversion will occur and the script will compute in parallel with Slurm. Outputs will be saved in the $HOME/sim_data folder in the form of a CSV file and PNG graph. If you have installed feh, the graph will be displayed on your screen. See the Python code for a more detailed breakdown. 
