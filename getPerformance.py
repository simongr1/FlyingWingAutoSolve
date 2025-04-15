import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import scipy as sp
import WingSolver_dependencies.WingSolver_Dependencies as wp

# WIP ---------------------------------
dir="/home/simongr/Desktop/relevant data/FinalOptimization/20250306_results/results"
results, parameter, mass, cost, diff, iterations=wp.extract_data(dir)

#pitch stability
#in trimmed position alpha=0
pitch_torque_trimmed_fligth=results["data"]["PitchTorque"][-1][-1] # must be zero
#calculate static margin:
staticMarginGoal=0.12
TaperRatio=parameter["TaperRatio"][-1]
RootChord=parameter["RootChord"][-1]
#RootChord=730.314
meanChordLength_mm=2/3*RootChord*(1+TaperRatio+TaperRatio**2)/(1+TaperRatio)
roots=np.roots(results["data"]["LiftForce"][-1])
reals=roots[np.isreal(roots)]
best=np.inf
for r in reals:
    if np.abs(r)<np.abs(best):
        best=r

alphaZeroLift=best
pitch_torque_AC=np.polyval(results["data"]["PitchTorque"][-1],alphaZeroLift) #evalute pitch torque at zero lift angle


#catch possible division by zero
liftForcePoly=results["data"]["LiftForce"][-1]
pitchTorquePoly=results["data"]["PitchTorque"][-1]
xPositionaAC_reverse_m=(pitch_torque_AC-pitchTorquePoly[-1])/liftForcePoly[-1] #calculate ac position for alpha=0
staticMargin= xPositionaAC_reverse_m/(meanChordLength_mm*1e-3)

	
print(f"Lift: "+str(results["data"]["LiftForce"][-1]))
print(f"Pitch: "+str(results["data"]["PitchTorque"][-1]))
print(f"Drag: "+str(results["data"]["DragForce"][-1]))
print(f"SM: {staticMargin}")




