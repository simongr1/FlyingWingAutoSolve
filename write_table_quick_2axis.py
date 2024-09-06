import math

v=10
maxa=20
steps=4
timestep=100
firsttime=200
def deg2rad(x):
    return math.pi*x/180.

ot=0
x=0
y=0
z=0
t=0
for b in range(-steps,steps+1):
    a=int(b/steps*maxa)
    x=v*-math.cos(deg2rad(a))
    y=0
    z=v*math.sin(deg2rad(a))
    t=firsttime+(b-(-steps))*timestep+1
    print("    ( "+("%i"%ot)+(" ( %.3f"%x)+(" %.3f"%y)+(" %.3f"%z)+(")) // %i"%a)+" degrees")
    print("    ( "+("%i"%t)+(" ( %.3f"%x)+(" %.3f"%y)+(" %.3f"%z)+(")) // %i"%a)+" degrees")
    ot=t+1

x=-v
y=0
z=0
firsttime=t+2*timestep-1

for b in range(-steps,steps+1):
    a=int(b/steps*maxa)
    x=v*-math.cos(deg2rad(a))
    y=v*math.sin(deg2rad(a))
    z=0
    t=firsttime+(b-(-steps))*timestep+1
    print("    ( "+("%i"%ot)+(" ( %.3f"%x)+(" %.3f"%y)+(" %.3f"%z)+(")) // %i"%a)+" degrees")
    print("    ( "+("%i"%t)+(" ( %.3f"%x)+(" %.3f"%y)+(" %.3f"%z)+(")) // %i"%a)+" degrees")
    ot=t+1


    
