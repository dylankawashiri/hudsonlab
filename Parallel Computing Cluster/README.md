# Parallel Computing Cluster (Farm) Guide
This is a guide on how to optimize your code for use in the Farm cluster. Please note that all of the systems run on Linux. 

## Slurm
Slurm is a workload manager that will allocate tasks and resources in a computing cluster. It **will not** parallelize your code for you and will only 'accelerate' any code that is built for parallelization in the first place. All Slurm commands are executed via text files and/or the command line. 

## Python via Slurm
This part of the guide is for the integration of Qutip and Slurm. 

### Parallel Map
You will need to use Qutip's [parallel map](https://qutip.org/docs/4.0.2/guide/guide-parfor.html) function for integration with Slurm. 
