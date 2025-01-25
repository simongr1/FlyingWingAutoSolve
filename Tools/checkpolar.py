import matplotlib.pyplot as plt
import numpy as np

import pandas as pd
import os
import sys

#import dependecies
dependencies_dir= os.path.abspath(os.path.join(os.getcwd(),"../WingSolver_dependencies"))
sys.path.append(dependencies_dir)
import WingSolver_dependencies.WingSolver_Dependencies as wd
################Information##################
"""You can change the PolyKey and the reference Key to switch between differnet results like LiftForce, DragForce, PitchTorque, RollTorque, YawTorque.
If you want to plot anything else iteration by iteration you have to change the 4 Variables in Input (e.g to cA and cD)"""

path="/home/simongr/Downloads/Archive/20250117_results/results"
PolyKey= "PitchTorque"
ReferenceKey= "alpha"



results, parameter, mass, cost,diff, iterations = wd.extract_data(path,ignore_numbers=[])
length=len(parameter["RootIncidence"])
    
#Input
"""CurrentPolys= results["data"][PolyKey]
PolyReference=results[ReferenceKey]
CurrentAllPoints= results["data"][PolyKey+"Raw"]
PointsReference = results["data"][ReferenceKey+"Raw"]"""
#the poly using the real ca
CurrentPolystrue= [ wd.drag_curve(results["data"]["cL"][i],results["data"]["cD"][i]) for i in range(0,length)]
#the points from the ca/cd approx
density=1
velocity=10
try:
	reference_area=parameter["WingArea"]
except:
	reference_area= [parameter["RootChord"][i]*(parameter["TaperRatio"][i]+1)*parameter["WingLength"][i] for i in range(0,length)]
CurrentAllPointscA= [wd.total_to_coefficient(results["data"]["LiftForceRaw"][i], density, velocity, reference_area[i]*1e-6) for i in range(0,length)]
CurrentAllPointscD= [wd.total_to_coefficient(results["data"]["DragForceRaw"][i], density, velocity, reference_area[i]*1e-6) for i in range(0,length)]
CurrentPolysApprox=results["data"]["DragPolar"]
PolyReference=np.linspace(-1.5,1.5,100)
CurrentAllPoints=results["data"]["cD"]
PointsReference=results["data"]["cL"]

datasets={}
for i, poly in enumerate(CurrentPolysApprox):
    values=wd.calculate_function(PolyReference,poly)
    truevalues= wd.calculate_function(PolyReference,CurrentPolystrue[i])
    points=np.array(CurrentAllPoints[i])
    datasets[i]=[points,values,truevalues,CurrentAllPointscA[i],CurrentAllPointscD[i]] #############################the points are saved in 0 and the approximation is svaed under 1

# Determine the global y-axis range for consistent scaling
datasetValues=datasets.values()
y_min = min(min(data[0]) for data in datasetValues)
y_max = max(max(data[0]) for data in datasetValues)


# Initialize variables
current_index_iteration = 0
current_index_dataset = 0

# Create a figure and axis
fig, ax = plt.subplots()
line, = ax.plot(PolyReference,datasets[current_index_iteration][1], label=f"Approximation with wingArea")
line2, = ax.plot(PolyReference,datasets[current_index_iteration][2],"g", label=f"Approximation cA/cD")
points, = ax.plot(PointsReference[current_index_iteration],datasets[current_index_iteration][0],"go", label=f"Dataset(from paraview)")
points2, = ax.plot(datasets[current_index_iteration][3],-1*np.array(datasets[current_index_iteration][4]),"bo", label=f"Dataset (from analyse result) ")
hline= ax.axvline(x=1 , ls="--", c="r")
ax.legend()
ax.set_title(f"Plot Iteration: {current_index_iteration + 1} for {PolyKey}")
ax.axhline(0, color='black', linewidth=0.8)  # Horizontal axis
ax.axvline(0, color='black', linewidth=0.8)  # Vertical axis
#ax.set_xlabel("Alpha[°]")
#ax.set_ylabel("Torque [Nm]")
ax.grid(True)

# Set consistent axis limits
ax.set_xlim(-1.5, 1.5)  # Assuming all datasets have the same length
ax.set_ylim(-1, 3)

# Define a function to update the plot
def update_plot(index):
    line.set_ydata(datasets[index][1])  # Update the line data
    line2.set_ydata(datasets[index][2])
    points.set_ydata(datasets[index][0])
    points2.set_data(datasets[index][3],-1* np.array(datasets[index][4]))
    hline.set_xdata(index)
    ax.set_title(f"Plot Iteration: {current_index_iteration + 1} for {PolyKey}")
    fig.canvas.draw()


# Define a function to handle key presses
def on_key(event):
    global current_index_iteration
    if event.key == "right":
        current_index_iteration = (current_index_iteration + 1) % len(datasets)  # Move to the next dataset
    elif event.key == "left":
        current_index_iteration = (current_index_iteration - 1) % len(datasets)  # Move to the previous dataset
    elif event.key == "up":
        pass
    elif event.key == "down":
        pass
    update_plot(current_index_iteration)

# Connect the key press event to the handler
fig.canvas.mpl_connect("key_press_event", on_key)

plt.show()