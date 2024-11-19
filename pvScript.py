#### import the simple module from the paraview
from paraview.simple import *


LoadState("../../../../CSVonly.pvsm",".")

Render()
ResetCamera()
Render()
SaveData("./mycsv.csv",proxy=FindSource("YawCalc"))
Render()


#exit()

