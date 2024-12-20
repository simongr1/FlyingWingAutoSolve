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

#########Constants#######
density=1
g=9.81
velocity=10
v_target=15

#You also need to add a 1st iteration

#Get subfolders and sort them
working_dir= "/home/sgrimm/src/FlyingWing/results"

dirs = [d for d in os.listdir(working_dir) if os.path.isdir(os.path.join(working_dir, d))]
dirs=sorted(dirs,key=int)

# Create Empty parameter dictionary {'WingArea': [], 'WingSweepAngleLE': [], 'AspectRatio': [], 'TaperRatio': [], 'RootIncidence': [], 'WingTwist': [], 'DihedralAngle': []}
# e.g. wing area contains the values for all iterations 
#get parameter names:
param_names_path= os.path.join(working_dir,dirs[0],"0","parameters.csv")
param_names=pd.read_csv(param_names_path, usecols=[0,1], header=None)
param_names=param_names[0].to_list()

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
    

    #extract Polynomial of Total functions
    cells =rows_res[1][1:6] #The first cell contains the name of the row
    polynomials=[extract_tupel(cell) for cell in cells] #extract the polynomial
    LiftForce,DragForce,PitchTorque,RollTorque,YawTorque=polynomials

    #extract costs
    TotalCost_value=float(rows_res[30][-1])
    
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

print(geometry)

def plotit(parameter_name,names,results,iterations):
    x= results[parameter_name]
    number_of_iterations= iterations
    fraction_of_iterations= 1  # set to 2 to only plot half the iterations
    # Create a figure with subplots
    n_plots=len(names)
    cols=3
    rows= math.ceil(n_plots/cols)
    fig, axes = plt.subplots(rows, cols, figsize=(10, 6))
    cmap = cm.Greys
    norm= colors.Normalize(vmin=1, vmax=number_of_iterations)
    colors_list= cmap(norm(range(1, number_of_iterations +1 )))

    # Plot on each subplot
    for i, ax in enumerate(axes.flat):  # Flatten axes for easier indexing
        if i < n_plots:
            name=names[i]
            # Use a colormap to generate progressively lighter colors
            #colors = cm.viridis(np.linspace(0.2, 1, number_of_iterations))  # Adjust range for lighter colors

            #plot all iterations
            for iteration in range(0,number_of_iterations,fraction_of_iterations):
                poly = results["data"][name][iteration]  # Generate data for plot
                y= calculate_function(x,poly)
                ax.plot(x, y, color=colors_list[iteration])
            ax.set_title(name)
            ax.set_xlabel(parameter_name+" [°]")
            ax.grid(True)
            
        else:
            # Turn off unused axes
            ax.axis('off')

    # Adjust layout
    #fig.suptitle()
    # Add the colorbar
    sm = cm.ScalarMappable(cmap=cmap, norm=norm)  # Scalar mappable for the colorbar
    sm.set_array([])  # Required for ScalarMappable
    cbar = plt.colorbar(sm)
    #cbar.set_label("Iteration Number", fontsize=12)  # Label for the colorbar

    plt.legend()
    plt.tight_layout()
    return fig

def plotcosts(costs):
    plt.figure()
    x=range(1,len(costs)+1)
    plt.scatter(x,costs,color="red",label="Data")
    plt.title("Costfunction")
    plt.xlabel("Iterations")
    plt.ylabel("Cost")
    plt.show()




#plot alphas
plotit("alpha",results["names_alpha"],results,iterations)
fig=plotit("beta",results["names_beta"],results,iterations)
costs=results["data"]["TotalCost"]
plotcosts(costs)
#plot_graph(alpha_t,lift, hline=4.7*9.81)
#print(calculate_function(alpha,tuple(results["data"]["LiftForce"][-1])))
plt.show()
