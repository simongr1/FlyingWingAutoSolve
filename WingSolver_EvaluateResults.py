# -*- coding: utf-8 -*-



import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
from matplotlib import cm,colors
import re
import csv
import os
import math
import pandas as pd
from matplotlib.ticker import MaxNLocator
import copy
import WingSolver_dependencies.WingSolver_Dependencies as wd


def plot_function(parameter_values,y_polys,iterations,name="Lift Force",x_label="Alpha[deg]",y_label="Force [N]",hLines=None):
    #parameter_values: list of all alpha values
    fig, ax=plt.subplots()
    x= parameter_values
    #y_polys
    number_of_iterations= iterations
    fraction_of_iterations= 1  # set to 2 to only plot half the iterations
    
    cmap = cm.winter
    norm= colors.Normalize(vmin=1, vmax=number_of_iterations)
    colors_list= cmap(norm(range(1, number_of_iterations +1 )))

    # Plot horizontal line (y=0) with thicker line
    ax.axhline(y=0, color='black', linewidth=2)

    # Plot vertical line (x=0) with thicker line
    ax.axvline(x=0, color='black', linewidth=2)


    #ax.yaxis.set_major_locator(MaxNLocator(integer=True, prune='both', numticks=10))  # numticks controls the number of ticks
    #ax.yaxis.set_major_locator(MaxNLocator(integer=True, prune='both', numticks=10))  # numticks controls the number of ticks
    #plot all iterations
    for iteration in range(0,number_of_iterations,fraction_of_iterations):
        poly = y_polys[iteration]  # Generate data for plot
        y= wd.calculate_function(x,poly)
        ax.plot(x, y, color=colors_list[iteration])
    ax.set_title(name, fontsize=LABEL_FONTSIZE)
    ax.set_xlabel(x_label, fontsize=LABEL_FONTSIZE)
    ax.set_ylabel(y_label, fontsize=LABEL_FONTSIZE)
    ax.tick_params(axis='both', labelsize=LABEL_FONTSIZE * 0.7)
    ax.grid(True)

    if isinstance(hLines, list):
        for h_value in hLines:
            ax.axhline(y=h_value, color="r", linestyle="--")

    # Add the colorbar
    sm = cm.ScalarMappable(cmap=cmap, norm=norm)  # Scalar mappable for the colorbar
    sm.set_array([])  # Required for ScalarMappable
    cbar = plt.colorbar(sm, ax=plt.gca())
    cbar.set_label('Number of iterations', rotation=270, fontsize=LABEL_FONTSIZE, labelpad=15)
    cbar.ax.tick_params(labelsize=LABEL_FONTSIZE * 0.7)
    #cbar.set_label("Iteration Number", fontsize=12)  # Label for the colorbar

    #plt.legend() #this line causes tis error: No handles with labels found to put in legend. 
    plt.tight_layout()
    return fig

def plotOverIterations(y_values,name="Cost",x_label="Iterations",y_label="Value", hLines=None):
    fig,ax = plt.subplots()
    x=range(1,len(y_values)+1)
    ax.scatter(x,y_values,color="red",label=name)
    ax.set_title(name, fontsize=LABEL_FONTSIZE)
    ax.set_xlabel(x_label, fontsize=LABEL_FONTSIZE)
    ax.set_ylabel(y_label, fontsize=LABEL_FONTSIZE)
    ax.tick_params(axis='both', labelsize=LABEL_FONTSIZE * 0.7)
    if isinstance(hLines, list):
         for h_value in hLines:
              ax.axhline(y=h_value, color="r", linestyle="--")
    ax.grid(True)
    return fig

#########Constants#######
plt.rcParams['font.family'] = 'Nimbus Roman'
LABEL_FONTSIZE = 18  # 10% increase over matplotlib default (10pt)
density=1.2
g=9.81

#You also need to add a 1st iteration

#Get subfolders and sort them
working_dir= "/path/to/results"  # Replace with the actual path to your results folder
results_path=os.path.join(working_dir,"results")
#Create evaluation directories:
# List of directories to check
directories = ["evaluation/cost", "evaluation/parameter"]

# Extract the date using a regular expression
match = re.search(r"\d{8}", working_dir)
if match:
    date = match.group()
else:
    print("No date found")

for directory in directories:
    # Check if the directory exists
    joined_directory = os.path.join(working_dir,directory)
    if not os.path.exists(joined_directory):
        # Create the directory if it doesn't exist
        print(joined_directory)
        os.makedirs(joined_directory)
        print(f"Created directory: {joined_directory}")
   


results, parameter, mass, cost, diff, iterations = wd.extract_data(results_path)

figLiftForce=plot_function(results["alpha"],results["data"]["LiftForce"],iterations,name="Lift Force Polar", hLines=[mass["TotalMass"][-1]*9.81])
figDragForce=plot_function(results["alpha"],results["data"]["DragForce"],iterations,name="Drag force polar ")
figPitchTorque=plot_function(results["alpha"],results["data"]["PitchTorque"],iterations,name="Pitch torque polar")
figYawTorque=plot_function(results["beta"],results["data"]["YawTorque"],iterations,name="YawTorque "+date,x_label="Beta [°]", y_label="Torque [Nm]")
figRollTorque=plot_function(results["beta"],results["data"]["RollTorque"],iterations,name="RollTorque "+date,x_label="Beta [°]", y_label="Torque [Nm]")
figCosts=plotOverIterations(results["data"]["TotalCost"], name="Objective function value over iterations")
figCosts.savefig(os.path.join(working_dir,"evaluation/TotalCost.eps"))
plots={"figLiftForce":figLiftForce,"figDragForce":figDragForce,"figPitchTorque":figPitchTorque,"figYawTorque":figYawTorque,"figRollTorque":figRollTorque}
#save plots
for key in plots:
     plots[key].savefig(os.path.join(working_dir, f"evaluation/{key}.eps"))
plt.close("all")
parameterPlots={}
for parameterName in parameter:
    parameterPlots[parameterName]=plotOverIterations(parameter[parameterName],name=parameterName+" "+date,y_label=parameterName)
    parameterPlots[parameterName].savefig(os.path.join(working_dir,f"evaluation/parameter/{parameterName}.eps"))
    #Die Einheiten sind noch nicht im plot
for costterm in cost:
     plot=plotOverIterations(cost[costterm], name=costterm + " "+date, y_label=costterm)
     plot.savefig(os.path.join(working_dir,f"evaluation/cost/cost_{costterm}.eps"))
for costterm in cost:
     plot=plotOverIterations(diff[costterm], name=f"diff {costterm} {date}", y_label="difference to goal")
     plot.savefig(os.path.join(working_dir,f"evaluation/cost/diff_{costterm}.eps"))

fig_all_costs, ax_all_costs = plt.subplots()
for costterm in cost:
    ax_all_costs.plot(range(1, len(cost[costterm]) + 1), cost[costterm], marker='o', label=costterm)
ax_all_costs.plot(range(1, len(results["data"]["TotalCost"]) + 1), results["data"]["TotalCost"], marker='o', label="Total", linewidth=2, linestyle='--', color='black')
ax_all_costs.set_title("Individual objective-function components", fontsize=LABEL_FONTSIZE)
ax_all_costs.set_xlabel("Iterations", fontsize=LABEL_FONTSIZE)
ax_all_costs.set_ylabel("Value", fontsize=LABEL_FONTSIZE)
ax_all_costs.tick_params(axis='both', labelsize=LABEL_FONTSIZE * 0.7)
ax_all_costs.legend()
ax_all_costs.grid(True)
fig_all_costs.tight_layout()
fig_all_costs.savefig(os.path.join(working_dir, "evaluation/cost/all_costterms.eps"))

plt.close("all")

#print information on program:
print(f"Read from: {working_dir}")
print(f"Used parameter: {parameter.keys()}")
print(f"CostTerms: {cost.keys()}")
finalcost= results["data"]["TotalCost"][-1]
staticmargin  =cost["StaticMargin"][-1]
liftcost= cost["Lift"][-1]
power=cost["Power"] [-1]
trimcost=cost["Trim"][-1]
print(f"FinalCost:{finalcost} \nStaticMargin cost: {staticmargin}\nLift cost: {liftcost}\nPower cost: {power}\nTrim cost: {trimcost}")


