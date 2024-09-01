import math

v=10
maxa=20
steps=4
timestep=100
firsttime=200
def deg2rad(x):
    return math.pi*x/180.

ot=0
for b in range(-steps,steps+1):
    a=int(b/steps*maxa)
    x=v*-math.cos(deg2rad(a))
    z=v*math.sin(deg2rad(a))
    t=firsttime+(b-(-steps))*timestep+1
    print("    ( "+("%i"%ot)+(" ( %.3f"%x)+(" 0.0 %.3f"%z)+(")) // %i"%a)+" degrees")
    print("    ( "+("%i"%t)+(" ( %.3f"%x)+(" 0.0 %.3f"%z)+(")) // %i"%a)+" degrees")
    ot=t+1


    
