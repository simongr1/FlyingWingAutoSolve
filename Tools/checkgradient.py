import pandas as pd
import numpy as np
import copy
import os
import matplotlib.pyplot as plt
from matplotlib import cm, colors
working_dir= "/home/sgrimm/Archive/20250205_results/results"
#which two components do you want to compare?
#'Lift', 'Drag', 'StaticMargin', 'Trim'
comp1="Lift"
comp2="Trim"
####################################################################################################
dirs = [d for d in os.listdir(working_dir) if os.path.isdir(os.path.join(working_dir, d))and d.isdigit()]
dirs=sorted(dirs,key=int)


keywords=[d for d in os.listdir(os.path.join(working_dir,"1")) if os.path.isdir(os.path.join(working_dir, "1",d))]

cost_names_path=os.path.join(working_dir,dirs[0],"0","result.csv")
cost_names=pd.read_csv(cost_names_path, usecols=[0,1],header=None,skiprows=29)
cost_names= cost_names.dropna()
cost_names=cost_names[0].to_list()
cost={}
for keyword in keywords:
    cost[keyword]={}
    for i in range(len(cost_names)):
        cost[keyword][cost_names[i]]=[] 
diff=copy.deepcopy(cost)
for keyword in keywords:
    for dir in dirs:
        
        cost_names_path=os.path.join(working_dir,dir,keyword,"result.csv")
        #Open CSV file for cost
        cost_values=pd.read_csv(cost_names_path, usecols=[1,2,3,7], header=None, skiprows=29)
        cost_values=cost_values.dropna()
        cost_values_squared=cost_values[7].to_list()
        diff_values=cost_values[3].tolist()
        target_values=cost_values[1].tolist()
        current_values=cost_values[2].tolist()

        #Add values
        for i in range(len(cost_names)):
            cost[keyword][cost_names[i]].append(float(cost_values_squared[i]))
            diff[keyword][cost_names[i]].append(float(diff_values[i]))

number_of_iterations=len(dirs)
colors_list = plt.get_cmap("tab10").colors

#First plot
for i,keyword in enumerate(keywords):
    color1=colors_list[i]
    if keyword == "0":
        #skip the standart
        continue
    data= np.array(cost[keyword][comp1]-np.array(cost["0"][comp1]))
    plt.plot(data,label=keyword,color=color1)
plt.axhline(0, color='black', linewidth=0.8)  # Horizontal axis
plt.legend()
plt.grid()
plt.title(f"Coordinate-wise of {comp1} cost")
plt.xlabel("Iterations")
plt.ylabel(f"{comp1}cost(0+h)-{comp1}cost(0)")
plt.figure()

#second plot
for i,keyword in enumerate(keywords):
    color1=colors_list[i]
    if keyword == "0":
        #skip the standart
        continue
    data= np.array(cost[keyword][comp2])-np.array(cost["0"][comp2])
    plt.plot(data,label=keyword,color=color1)
plt.axhline(0, color='black', linewidth=0.8)  # Horizontal axis
plt.legend()
plt.grid()
plt.title(f"Coordinate-wise difference of {comp2} cost ")
plt.xlabel("Iterations")
plt.ylabel(f"{comp2}cost(0+h)-{comp2}cost(0)")
plt.show()
