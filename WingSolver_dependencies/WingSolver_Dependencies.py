import shutil
import os
import numpy as np
import scipy as sp
import copy
import csv
import pandas as pd
import re

def empty_directory(directory):
    try:
        shutil.rmtree(directory)  # Remove all contents
        os.makedirs(directory)  # Recreate the empty directory
    except Exception as e:
        print(f"Failed to empty directory. Reason: {e}")

def main():
    print("This file only conatains functions usefull for data evaluation!")

def quadratic(x,a,b,c):
	return a* x**2 +b* x+ c

def drag_curve(lift_coefficient, drag_coeffcient):
	#c_w(c_a)=a*c_a�+b*c_a+d
	initial_guess = [1, -1, 1]
	bounds = ([0, -np.inf, 0], [np.inf, 0, np.inf])
	if len(lift_coefficient) != len(drag_coeffcient):
		return 0
	params, _ = sp.optimize.curve_fit(quadratic, lift_coefficient, drag_coeffcient, p0=initial_guess, bounds=bounds)
	#a,b,d= np.polyfit(lift_coefficient,drag_coeffcient,2)
	a,b,d= params
	return [a,b,d]

def calculate_function(reference,coefficients):
    # Define the polynomial coefficients as a tuple
    #coefficients = (-0.00601809876176738, -0.0602287380735399, 7.39222409124886, 44.7487686030506)  # Example: x^2 - 3x + 2

    # Generate the polynomial function from the coefficients
    polynomial = np.poly1d(coefficients)

    # Generate x values for plotting
    x = reference  

    # Evaluate the polynomial for the x valuesa
    y = polynomial(x)

    return y

def total_to_coefficient(lift_or_drag, density, velocity, reference_area):
	Force= np.array(lift_or_drag)
	lift_or_drag_coefficient= Force/(0.5*density*velocity**2*reference_area)
	return lift_or_drag_coefficient.tolist()

def extract_tupel(cell_content):
    #cell_content = "tuple(-0.0876859194475919; -0.390034184491187; -3.2973569606838)"
    # Extract numbers using a regular expression
    numbers = re.findall(r"-?\d+\.\d+", cell_content)  # Matches decimal numbers, including negatives

    # Convert the strings to floats
    numbers = [float(num) for num in numbers]
    return numbers #extracted list

def read_csv(csv_path):
    # Open the CSV file
    with open(csv_path, "r") as file:
        reader = csv.reader(file)  # Read the CSV file
        rows = list(reader)        # Convert the reader object to a list
    return rows

def extract_data(working_dir,ignore_numbers=[]):
    #ignore_numbers: you can add some number you want to skip in the data (e.g. faulty data)
    # example ignore_numbers=["8"]
    dirs = [d for d in os.listdir(working_dir) if os.path.isdir(os.path.join(working_dir, d))and d.isdigit() and d  not in ignore_numbers]
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

    #read raw data:
    alphaRaw=[]
    betaRaw=[]
    LiftForceRaw=[]
    DragForceRaw=[]
    PitchTorqueRaw=[]
    RollTorqueRaw=[]
    YawTorqueRaw=[]
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
                    "PitchTorque":PitchTorquePoly,"RollTorque":RollTorquePoly,"YawTorque":YawTorquePoly,"DragPolar":DragPolarPoly, "TotalCost":TotalCost,
                    "alphaRaw":alphaRaw,"betaRaw":betaRaw,"LiftForceRaw":LiftForceRaw,"DragForceRaw":DragForceRaw,"PitchTorqueRaw":PitchTorqueRaw,"RollTorqueRaw":RollTorqueRaw,"YawTorqueRaw":YawTorqueRaw}
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
        

        LiftForcePoly.append(LiftForce)
        DragForcePoly.append(DragForce)
        PitchTorquePoly.append(PitchTorque)
        RollTorquePoly.append(RollTorque)
        YawTorquePoly.append(YawTorque)
        TotalCost.append(TotalCost_value)
        DragPolarPoly.append(DragPolar)

        #open rawresults.csv
        rawresults=pd.read_csv(path_raw,usecols=[0,2,9,10,11,19,20],header=None, skiprows=1)
        LiftForceRaw.append(rawresults[2].to_list())
        DragForceRaw.append(rawresults[0].to_list())
        PitchTorqueRaw.append(rawresults[10].to_list())
        RollTorqueRaw.append(rawresults[9].to_list())
        YawTorqueRaw.append(rawresults[11].to_list())
        alphaRaw.append(rawresults[19].to_list())
        betaRaw.append(rawresults[20].to_list())
        current_iteration +=1

    return results, parameter, mass, cost,diff, iterations,

if __name__=="__main__":
    main()