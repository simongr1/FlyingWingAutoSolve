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

path="/home/sgrimm/Archive/20250117_results/results"
PolyKey= "PitchTorque"
ReferenceKey= "alpha"



results, parameter, mass, cost,diff, iterations = wd.extract_data(path,ignore_numbers=[])

    
#Input
CurrentPolys= results["data"][PolyKey]
PolyReference=results[ReferenceKey]
CurrentAllPoints= [inner_list for inner_list in results["data"][PolyKey+"Raw"]]
PointsReference = [inner_list for inner_list in results["data"][ReferenceKey+"Raw"]]

datasets={}
for i, poly in enumerate(CurrentPolys):
    values=wd.calculate_function(PolyReference,poly)
    points=np.array(CurrentAllPoints[i])
    datasets[i]=[points,values] #############################the points are saved in 0 and the approximation is svaed under 1

# Determine the global y-axis range for consistent scaling
datasetValues=datasets.values()
y_min = min(min(data[0]) for data in datasetValues)
y_max = max(max(data[0]) for data in datasetValues)


# Initialize variables
current_index_iteration = 0
current_index_dataset = 0

# Create a figure and axis
fig, ax = plt.subplots()
line, = ax.plot(PolyReference,datasets[current_index_iteration][1], label=f"Approximation")
points, = ax.plot(PointsReference[current_index_iteration],datasets[current_index_iteration][0],"ro", label=f"Dataset")
ax.legend()
ax.set_title(f"Plot Iteration: {current_index_iteration + 1} for {PolyKey}")
ax.axhline(0, color='black', linewidth=0.8)  # Horizontal axis
ax.axvline(0, color='black', linewidth=0.8)  # Vertical axis
#ax.set_xlabel("Alpha[°]")
#ax.set_ylabel("Torque [Nm]")
ax.grid(True)

# Set consistent axis limits
ax.set_xlim(-25, 25)  # Assuming all datasets have the same length
ax.set_ylim(y_min, y_max)

# Define a function to update the plot
def update_plot(index):
    line.set_ydata(datasets[index][1])  # Update the line data
    points.set_ydata(datasets[index][0])
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
