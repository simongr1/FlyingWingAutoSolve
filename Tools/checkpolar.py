import matplotlib.pyplot as plt
import numpy as np

import pandas as pd
import os
import sys

#import dependecies
dependencies_dir= os.path.abspath(os.path.join(os.getcwd(),"../WingSolver_dependencies"))
sys.path.append(dependencies_dir)
import WingSolver_Dependencies as wd
################Information##################
"""You can change the PolyKey and the reference Key to switch between differnet results like LiftForce, DragForce, PitchTorque, RollTorque, YawTorque.
If you want to plot anything else iteration by iteration you have to change the 4 Variables in Input (e.g to cA and cD)"""

path="path/to/results"   # <-- edit to your results directory
PolyKey= "PitchTorque"
ReferenceKey= "alpha"



results, parameter, mass, cost,diff, iterations = wd.extract_data(path,ignore_numbers=[])
length=len(parameter["RootIncidence"])
    
#Input
"""CurrentPolys= results["data"][PolyKey]
PolyReference=results[ReferenceKey]
CurrentAllPoints= results["data"][PolyKey+"Raw"]
PointsReference = results["data"][ReferenceKey+"Raw"]"""

#the points from the ca/cd approx
density=1.2
velocity=10
try:
	reference_area=parameter["WingArea"]
except:
	reference_area= [parameter["RootChord"][i]*(parameter["TaperRatio"][i]+1)*parameter["WingLength"][i] for i in range(0,length)]

#the poly using the real ca
DragPolartrue= [ wd.drag_curve(results["data"]["cL"][i],results["data"]["cD"][i]) for i in range(0,length)]
True_cD=results["data"]["cD"]
True_cL=results["data"]["cL"]

CurrentAllPointscA_calc= [wd.total_to_coefficient(results["data"]["LiftForceRaw"][i], density, velocity, reference_area[i]*1e-6) for i in range(0,length)]
CurrentAllPointscD_calc= [wd.total_to_coefficient(results["data"]["DragForceRaw"][i], density, velocity, reference_area[i]*1e-6) for i in range(0,length)]
DragPolarApprox=results["data"]["DragPolar"]

PolyReference=np.linspace(-1.5,1.5,100)


datasets_approx={}
for i, poly in enumerate(DragPolarApprox):
    values=wd.calculate_function(PolyReference,poly)
    points_x=np.array(CurrentAllPointscA_calc[i])
    points_y=np.array(CurrentAllPointscD_calc[i])
    points= [points_x,points_y]
    bestcL,bestcD=wd.cL_cD_bestendurance(poly)
    point_best=[bestcL,bestcD]
    datasets_approx[i]=[points,values,point_best] #############################the points are saved in 0 and the approximation is svaed under 1

datasets_Noapprox={}
for i, poly in enumerate(DragPolartrue):
    values=wd.calculate_function(PolyReference,poly)
    points_x=np.array(True_cL[i])/(reference_area[i]*1e-6)
    points_y= np.array(True_cD[i])/(reference_area[i]*1e-6)
    points= [points_x,points_y]
    bestcL,bestcD=wd.cL_cD_bestendurance(poly)
    point_best=[bestcL,bestcD]
    datasets_Noapprox[i]=[points,values,point_best] #############################the points are saved in 0 and the approximation is svaed under 1
# Determine the global y-axis range for consistent scaling
datasetValues=datasets_approx.values()
"""y_min = min(min(data[0]) for data in datasetValues)
y_max = max(max(data[0]) for data in datasetValues)
"""

# Initialize variables
current_index_iteration = 0
current_index_dataset = 0

# Create a figure and axis
fig, ax = plt.subplots()
line_approx, = ax.plot(PolyReference,datasets_approx[current_index_iteration][1], label=f"Approximation with wingArea", c="g")
points_approx, = ax.plot(datasets_approx[current_index_iteration][0][0],datasets_approx[current_index_iteration][0][1],"gx", label=f"Dataset(approx with wingarea")
best_approx, = ax.plot(datasets_approx[current_index_iteration][2][0],datasets_approx[current_index_iteration][2][1],"ro", label=f"best endurance(approx with wingarea")

line_true, = ax.plot(PolyReference,datasets_Noapprox[current_index_iteration][1], label=f"Approximation with paraview", c="b")
points_true, = ax.plot(datasets_Noapprox[current_index_iteration][0][0],datasets_Noapprox[current_index_iteration][0][1],"bo", label=f"Dataset(approx with paraview")
best_true, = ax.plot(datasets_Noapprox[current_index_iteration][2][0],datasets_Noapprox[current_index_iteration][2][1],"rx", label=f"best endurance(approx with paraview")
ax.legend()
ax.set_title(f"Plot Iteration: {current_index_iteration + 1} for {PolyKey}")
ax.axhline(0, color='black', linewidth=0.8)  # Horizontal axis
ax.axvline(0, color='black', linewidth=0.8)  # Vertical axis
#ax.set_xlabel("Alpha[°]")
#ax.set_ylabel("Torque [Nm]")
ax.grid(True)

# Set consistent axis limits
ax.set_xlim(-1.5, 1.5)  # Assuming all datasets have the same length
ax.set_ylim(-0.05, 0.5)

# Define a function to update the plot
def update_plot(index):
    line_approx.set_ydata(datasets_approx[index][1])  # Update the line data
    points_approx.set_data(datasets_approx[index][0])
    best_approx.set_data([datasets_approx[index][2][0]],[datasets_approx[index][2][1]])
    line_true.set_ydata(datasets_Noapprox[index][1])  # Update the line data
    points_true.set_data(datasets_Noapprox[index][0])
    best_true.set_data([datasets_Noapprox[index][2][0]],[datasets_Noapprox[index][2][1]])
    #line2.set_ydata(datasets_approx[index][2])
    #points2.set_data(datasets_approx[index][3],-1* np.array(datasets_approx[index][4]))
    #hline.set_xdata([index])
    ax.set_title(f"Plot Iteration: {current_index_iteration + 1} for {PolyKey}")
    fig.canvas.draw()


# Define a function to handle key presses
def on_key(event):
    global current_index_iteration
    if event.key == "right":
        current_index_iteration = (current_index_iteration + 1) % len(datasets_approx)  # Move to the next dataset
    elif event.key == "left":
        current_index_iteration = (current_index_iteration - 1) % len(datasets_approx)  # Move to the previous dataset
    elif event.key == "up":
        pass
    elif event.key == "down":
        pass
    update_plot(current_index_iteration)

# Connect the key press event to the handler
fig.canvas.mpl_connect("key_press_event", on_key)

plt.show()