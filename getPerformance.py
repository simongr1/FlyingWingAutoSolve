import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import scipy as sp
import WingSolver_dependencies.WingSolver_Dependencies as wp

# WIP ---------------------------------
dir="/home/simongr/Desktop/relevant data/FinalOptimization/20250308_results/results"
results, parameter, mass, cost, diff, iterations=wp.extract_data(dir)
n=0
#pitch stability
#in trimmed position alpha=0
pitch_torque_trimmed_fligth=results["data"]["PitchTorque"][n][-1] # must be zero
#calculate static margin:
staticMarginGoal=0.12
TaperRatio=parameter["TaperRatio"][n]
RootChord=parameter["RootChord"][n]
#RootChord=730.314
meanChordLength_mm=2/3*RootChord*(1+TaperRatio+TaperRatio**2)/(1+TaperRatio)
roots=np.roots(results["data"]["LiftForce"][n])
reals=roots[np.isreal(roots)]
best=np.inf
for r in reals:
    if np.abs(r)<np.abs(best):
        best=r

alphaZeroLift=best
pitch_torque_AC=np.polyval(results["data"]["PitchTorque"][n],alphaZeroLift) #evalute pitch torque at zero lift angle


#catch possible division by zero
liftForcePoly=results["data"]["LiftForce"][n]
pitchTorquePoly=results["data"]["PitchTorque"][n]
xPositionaAC_reverse_m=(pitch_torque_AC-pitchTorquePoly[-1])/liftForcePoly[-1] #calculate ac position for alpha=0
staticMargin= xPositionaAC_reverse_m/(meanChordLength_mm*1e-3)

Power= results["data"]["DragForce"][n][-1]*parameter["Velocity"][n]
Trim=results["data"]["PitchTorque"][n][-1]
Lift_diff=9.81*mass["TotalMass"][n]-results["data"]["LiftForce"][n][-1]
TotalCost=results["data"]["TotalCost"][n]
print(f"Lift: "+str(results["data"]["LiftForce"][n]))
print(f"Pitch: "+str(results["data"]["PitchTorque"][n]))
print(f"Drag: "+str(results["data"]["DragForce"][n]))
print(f"SM: {staticMargin}")
print(f"Power: {Power}")
print(f"Trim:{Trim}")
print(f"G-L:{Lift_diff}")
print(f"Total Cost:{TotalCost}")


