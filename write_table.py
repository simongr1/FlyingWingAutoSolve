import math

v=10
def deg2rad(x):
    return math.pi*x/180.

for a in range(-20,21):
    x=v*-math.cos(deg2rad(a))
    z=v*math.sin(deg2rad(a))
    if a==-20:
        print(("    ( 0.0 ( %.3f"%x)+(" 0.0 %.3f"%z)+(")) // %i"%a)+" degrees")
    print("    ("+("%.3f"%(1.0+(a-(-20))*1))+(" ( %.3f"%x)+(" 0.0 %.3f"%z)+(")) // %i"%a)+" degrees")


    
