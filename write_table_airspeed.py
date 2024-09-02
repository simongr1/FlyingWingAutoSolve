import math

maxv=20
steps=80
timestep=10
firsttime=200

ot=0
a=-0.0
print("    ( "+("%i"%ot)+(" ( %.1f"%-a)+(" 0.0 0.0)) // %.1f"%a)+" m/s")
for b in range(0,steps+1):
    a=b/steps*maxv
    t=firsttime+(b)*timestep
    print("    ( "+("%i"%t)+(" ( %.1f"%-a)+(" 0.0 0.0)) // %.1f"%a)+" m/s")
    ot=t+1


    
