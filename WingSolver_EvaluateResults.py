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

def read_csv(csv_path):
    # Open the CSV file
    with open(csv_path, "r") as file:
        reader = csv.reader(file)  # Read the CSV file
        rows = list(reader)        # Convert the reader object to a list
    return rows
#Extract parameters of out of the csv
def extract_tupel(cell_content):
    #cell_content = "tuple(-0.0876859194475919; -0.390034184491187; -3.2973569606838)"
    # Extract numbers using a regular expression
    numbers = re.findall(r"-?\d+\.\d+", cell_content)  # Matches decimal numbers, including negatives

    # Convert the strings to floats
    numbers = [float(num) for num in numbers]
    return numbers #extracted list


def calculate_function(reference,coefficients):
    # Define the polynomial coefficients as a tuple
    #coefficients = (-0.00601809876176738, -0.0602287380735399, 7.39222409124886, 44.7487686030506)  # Example: x^2 - 3x + 2

    # Generate the polynomial function from the coefficients
    polynomial = np.poly1d(coefficients)

    # Generate x values for plotting
    x = reference  

    # Evaluate the polynomial for the x values
    y = polynomial(x)

    return y

def quadratic(x,a,b,c):
	return a* x**2 +b* x+ c
def drag_curve(lift_coefficient, drag_coeffcient):
	#c_w(c_a)=a*c_a²+b*c_a+d
	initial_guess = [1, -1, 1]
	bounds = ([0, -np.inf, 0], [np.inf, 0, np.inf])
	if len(lift_coefficient) != len(drag_coeffcient):
		return 0
	params, _ = sp.optimize.curve_fit(quadratic, lift_coefficient, drag_coeffcient, p0=initial_guess, bounds=bounds)
	#a,b,d= np.polyfit(lift_coefficient,drag_coeffcient,2)
	a,b,d= params
	return [a,b,d]
def total_to_coefficient(lift_or_drag, density, velocity, reference_area):
	Force= np.array(lift_or_drag)
	lift_or_drag_coefficient= Force/(0.5*density*velocity**2*reference_area)
	return lift_or_drag_coefficient.tolist()

def plot_function(parameter_values,y_polys,iterations,name="Lift Force",x_label="Alpha[�]",y_label="Force [N]",hLines=None):
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


    ax.yaxis.set_major_locator(MaxNLocator(integer=True, prune='both', numticks=10))  # numticks controls the number of ticks
    #plot all iterations
    for iteration in range(0,number_of_iterations,fraction_of_iterations):
        poly = y_polys[iteration]  # Generate data for plot
        y= calculate_function(x,poly)
        ax.plot(x, y, color=colors_list[iteration])
    ax.set_title(name)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.grid(True)

    if isinstance(hLines, list):
        for h_value in hLines:
            ax.axhline(y=h_value, color="r", linestyle="--")   
   
    # Add the colorbar
    sm = cm.ScalarMappable(cmap=cmap, norm=norm)  # Scalar mappable for the colorbar
    sm.set_array([])  # Required for ScalarMappable
    cbar = plt.colorbar(sm, ax=plt.gca())
    cbar.set_label('Number of iteration', rotation=270)
    #cbar.set_label("Iteration Number", fontsize=12)  # Label for the colorbar

    #plt.legend() #this line causes tis error: No handles with labels found to put in legend. 
    plt.tight_layout()
    return fig

def plotOverIterations(y_values,name="Cost",x_label="Iterations",y_label="Cost", hLines=None):
    fig,ax = plt.subplots()
    x=range(1,len(y_values)+1)
    ax.scatter(x,y_values,color="red",label=name)
    ax.set_title(name)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    if isinstance(hLines, list):
         for h_value in hLines:
              ax.axhline(y=h_value, color="r", linestyle="--")
    return fig

#########Constants#######
density=1
g=9.81
velocity=10
v_target=15

#You also need to add a 1st iteration

#Get subfolders and sort them
working_dir= os.path.join(os.getcwd(),"results")


#Create evaluation directories:
# List of directories to check
directories = ["./evaluation/cost", "./evaluation/parameter"]

for directory in directories:
    # Check if the directory exists
    if not os.path.exists(directory):
        # Create the directory if it doesn't exist
        os.makedirs(directory)
        print(f"Created directory: {directory}")
   

dirs = [d for d in os.listdir(working_dir) if os.path.isdir(os.path.join(working_dir, d))and d.isdigit()]
dirs=sorted(dirs,key=int)

# Create Empty parameter dictionary {'WingArea': [], 'WingSweepAngleLE': [], 'AspectRatio': [], 'TaperRatio': [], 'RootIncidence': [], 'WingTwist': [], 'DihedralAngle': []}
# e.g. wing area contains the values for all iterations 
#get parameter names:
param_names_path= os.path.join(working_dir,dirs[0],"0","parameters.csv")
param_names=pd.read_csv(param_names_path, usecols=[0,1], header=None)
param_names=param_names[0].to_list()

#read parameter
parameter={}
for i in range(len(param_names)):
      parameter[param_names[i]]=[]  

geometry_names_path= os.path.join(working_dir,dirs[0],"0","geometry.csv")
geometry_names=pd.read_csv(geometry_names_path, usecols=[3,4],header=None,skiprows=1)
geometry_names= geometry_names.dropna()
geometry_names=geometry_names[3].to_list()

geometry={}
for i in range(len(geometry_names)):
      geometry[geometry_names[i]]=[]  

mass_names_path= os.path.join(working_dir,dirs[0],"0","mass.csv")
mass_names=pd.read_csv(mass_names_path, usecols=[0,1],header=None,skiprows=1)
mass_names= mass_names.dropna()
mass_names=mass_names[0].to_list()
mass={}
for i in range(len(mass_names)):
      mass[mass_names[i]]=[] 

cost_names_path= os.path.join(working_dir,dirs[0],"0","result.csv")
cost_names=pd.read_csv(cost_names_path, usecols=[0,1],header=None,skiprows=29)
cost_names= cost_names.dropna()
cost_names=cost_names[0].to_list()
cost={}
for i in range(len(cost_names)):
      cost[cost_names[i]]=[] 
diff=copy.deepcopy(cost)
#Results
iterations=len(dirs)
names_alpha=["LiftForce","DragForce","PitchTorque"]
names_beta=["RollTorque","YawTorque"]
names_iterations=["TotalCost"]
alpha=range(-20,20,1)
beta=range(-20,20,1)

LiftForcePoly=[]
DragForcePoly=[]
PitchTorquePoly=[]
RollTorquePoly=[]
YawTorquePoly=[]
DragPolarPoly=[] 
TotalCost=[]

target_values_lift=[]
current_values_lift=[]
data={"LiftForce":LiftForcePoly,"DragForce":DragForcePoly,
                  "PitchTorque":PitchTorquePoly,"RollTorque":RollTorquePoly,"YawTorque":YawTorquePoly,"DragPolar":DragPolarPoly, "TotalCost":TotalCost}
results={"names_alpha":names_alpha,"names_beta":names_beta,"alpha":alpha,"beta":beta,"data":data}

current_iteration=0
for dir in dirs:
    #read files
    path=os.path.join(working_dir,dir,"0")
    path_res= os.path.join(path,"result.csv")
    path_parameter=os.path.join(path,"parameters.csv")
    path_raw=os.path.join(path,"rawresult.csv")
    path_geometry=os.path.join(path,"geometry.csv")
    path_mass=os.path.join(path,"mass.csv")
    rows_res=read_csv(path_res)

    #read Parameter
    
    # Open the CSV file for paramter
    params=pd.read_csv(path_parameter, usecols=[0,1], header=None)
    params_values=params[1].to_list()
    #Add parameters
    for i in range(len(param_names)):
          parameter[param_names[i]].append(float(params_values[i]))
    
    #Open CSV file for geometry
    geometry_values=pd.read_csv(path_geometry, usecols=[3,4], header=None, skiprows=1)
    geometry_values=geometry_values.dropna()
    geometry_values=geometry_values[4].to_list()
    #Add values
    for i in range(len(geometry_names)):
          geometry[geometry_names[i]].append(float(geometry_values[i]))

    #Open CSV file for mass
    mass_values=pd.read_csv(path_mass, usecols=[0,1], header=None, skiprows=1)
    mass_values=mass_values.dropna()
    mass_values=mass_values[1].to_list()
    #Add values
    for i in range(len(mass_names)):
          mass[mass_names[i]].append(float(mass_values[i]))

    #Open CSV file for cost
    cost_values=pd.read_csv(path_res, usecols=[1,2,3,7], header=None, skiprows=29)
    cost_values=cost_values.dropna()
    cost_values_squared=cost_values[7].to_list()
    diff_values=cost_values[3].tolist()
    target_values=cost_values[1].tolist()
    current_values=cost_values[2].tolist()
    target_values_lift.append(target_values[0])
    current_values_lift.append(current_values[0])
    #Add values
    for i in range(len(cost_names)):
          cost[cost_names[i]].append(float(cost_values_squared[i]))
          diff[cost_names[i]].append(float(diff_values[i]))
    #extract Polynomial of Total functions
    cells =rows_res[1][1:7] #The first cell contains the name of the row
    polynomials=[extract_tupel(cell) for cell in cells] #extract the polynomial
    LiftForce,DragForce,PitchTorque,RollTorque,YawTorque,DragPolar=polynomials

    #extract costs
    TotalCost_value=float(rows_res[33][-1])
    
    #determine drag_polar
    DragPolar=[0]
    #ToDo import drag polar from results

    LiftForcePoly.append(LiftForce)
    DragForcePoly.append(DragForce)
    PitchTorquePoly.append(PitchTorque)
    RollTorquePoly.append(RollTorque)
    YawTorquePoly.append(YawTorque)
    TotalCost.append(TotalCost_value)
    DragPolarPoly.append(DragPolar)

    current_iteration +=1


figLiftForce=plot_function(results["alpha"],results["data"]["LiftForce"],iterations, hLine=mass["TotalMass"][-1]*9.81)
figDragForce=plot_function(results["alpha"],results["data"]["DragForce"],iterations,name="DragForce")
figPitchTorque=plot_function(results["alpha"],results["data"]["PitchTorque"],iterations,name="PitchTorque")
figYawTorque=plot_function(results["beta"],results["data"]["YawTorque"],iterations,name="YawTorque",x_label="Beta [°]", y_label="Torque [Nm]")
figRollTorque=plot_function(results["beta"],results["data"]["RollTorque"],iterations,name="RollTorque",x_label="Beta [°]", y_label="Torque [Nm]")
figCosts=plotOverIterations(results["data"]["TotalCost"])
figCosts.savefig("./evaluation/TotalCost.png")
plots={"figLiftForce":figLiftForce,"figDragForce":figDragForce,"figPitchTorque":figPitchTorque,"figYawTorque":figYawTorque,"figRollTorque":figRollTorque}
#save plots
for key in plots:
     plots[key].savefig(f"./evaluation/{key}.png")
plt.close("all")
parameterPlots={}
for parameterName in parameter:
    parameterPlots[parameterName]=plotOverIterations(parameter[parameterName],name=parameterName,y_label=parameterName)
    parameterPlots[parameterName].savefig(f"./evaluation/parameter/{parameterName}.png")
    #Die Einheiten sind noch nicht im plot
for costterm in cost:
     plot=plotOverIterations(cost[costterm], name=costterm, y_label=costterm)
     plot.savefig(f"./evaluation/cost/cost_{costterm}.png")
for costterm in cost:
     plot=plotOverIterations(diff[costterm], name=f"diff {costterm}", y_label="difference to goal")
     plot.savefig(f"./evaluation/cost/diff_{costterm}.png")
plt.close("all")

#print information on program:
print(f"Read from: {working_dir}")
print(f"Used parameter: {parameter.keys()}")
print(f"CostTerms: {cost.keys()}")


