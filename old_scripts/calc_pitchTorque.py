import FreeCAD,FreeCADGui,Part,re
from FreeCAD import Base

def readpointsonfile(filename):
    # The common airfoil dat format has many flavors, This code should work with almost every dialect,
    # Regex to identify data rows and throw away unused metadata
    regex = re.compile(r'^\s*(?P<xval>(\-|\d*)\.\d+(E\-?\d+)?)\,?\s*(?P<yval>\-?\s*\d*\.\d+(E\-?\d+)?)\s*$')
    afile = open(filename,'r')
    coords=[]
    # Collect the data for the upper and the lower side separately if possible
    for lin in afile:
        curdat = regex.match(lin)
        if curdat != None:
            x = float(curdat.group("xval"))
            y = 0#posY
            z = float(curdat.group("yval"))
            #ignore points out of range, small tolerance for x value and arbitrary limit for y value, this is necessary because Lednicer
            #format airfoil files include a line indicating the number of coordinates in the same format of the coordinates.
            if (x < 1.01) and (z < 1) and (x > -0.01) and (z > -1):
                coords.append(FreeCAD.Vector(x,y,z))
            else:
                FreeCAD.Console.PrintWarning("Ignoring coordinates out of range -0.01<x<1.01 and/or -1<z<1. If this is a Lednicer format airfoil this is normal.")
        # End of if curdat != None
    # End of for lin in file
    afile.close

    if len(coords) < 3:
        FreeCAD.Console.PrintError('Did not find enough coordinates\n')
        return
    # sometimes coords are divided in upper an lower side
    # so that x-coordinate begin new from leading or trailing edge
    # check for start coordinates in the middle of list
    if coords[0:-1].count(coords[0]) > 1:
       
        flippoint = coords.index(coords[0],1)
        coords[:flippoint+1]=coords[flippoint-1::-1]
    

    return coords
def BPO03(x,u):
    u1,u2,u3,u4=u
    return u1*x**0.5*(1-x)**4 + 3*u2*x**1.5*(1-x)**3+3*u3*x**2.5*(1-x)**2+u4*x**3.5*(1-x) # Change this function as needed
def BPO05(x,u):
    u1,u2,u3,u4,u5,u6=u
    return u1*x**0.5*(1-x)**6 + 5*u2*x**1.5*(1-x)**5+10*u3*x**2.5*(1-x)**4+10*u4*x**3.5*(1-x)**3+5*u5*x**4.5*(1-x)**2+u6*x**5.5*(1-x)  # Change this function as needed

def getcoordsfromBPO(func,u_upper,u_lower):
    x_points= [
    0.0000100, 0.0001600, 0.0008200, 0.0053600, 0.0138500, 0.0262400, 0.0424800, 
    0.0624800, 0.0860700, 0.1130600, 0.1432400, 0.1763700, 0.2122300, 0.2506600, 
    0.2915500, 0.3348800, 0.3805100, 0.4280600, 0.4771000, 0.5271500, 0.5776600, 
    0.6280700, 0.6777400, 0.7260100, 0.7722100, 0.8156600, 0.8557000, 0.8916900, 
    0.9230700, 0.9493100, 0.9702700, 0.9861200, 0.9963800, 1.0000000
    ]
    first_column_neg=[
    0.0000100, 0.0001000, 0.0003600, 0.0005500, 0.0008000, 0.0011000, 0.0015000, 
    0.0020000, 0.0025900, 0.0039900, 0.0056700, 0.0086800, 0.0171200, 0.0352300, 
    0.0593200, 0.0891300, 0.1241800, 0.1637900, 0.2072700, 0.2539500, 0.3032200, 
    0.3545200, 0.4072500, 0.4608300, 0.5146300, 0.5680400, 0.6204500, 0.6712700, 
    0.7199000, 0.7657900, 0.8083900, 0.8475900, 0.8836500, 0.9162600, 0.9446200, 
    0.9679200, 0.9853900, 0.9962900, 1.0000000]
    coords=[]
    for x in reversed(x_points):
        z=func(x,u_upper)
        coords.append(FreeCAD.Vector(x,0,z))
    for x in first_column_neg: #need to be iterated in reverse for continuity
        z=func(x,u_lower)
        coords.append(FreeCAD.Vector(x,0,z))

    
        

    return coords 

def define_airfoil(coords,scale):
    scale=100
    spline=Part.BSplineCurve()
    
    spline.interpolate(coords)
    wire=Part.Wire(spline.toShape())
    face= Part.Face(wire)


    myScale = Base.Matrix() # issue31
    myScale.scale(-scale,scale,scale)# issue31
    face=face.transformGeometry(myScale)# issue31
    return face

filename="/home/sgrimm/.local/share/FreeCAD/Mod/AirPlaneDesign/wingribprofil/eppler/e207.dat"
u_upper=[0.22520647, 0.35207996, 0.12245162, 0.21634764]
u_lower=[-0.0752607 ,  0.01051798, -0.13220713, -0.06762208] #toDo: get parameter for E334 airfoil
coords=getcoordsfromBPO(BPO03,u_upper,u_lower)
#coords=readpointsonfile(filename)
x_coords=[v.x for v in coords]
print(x_coords)
face= define_airfoil(coords,100)

doc=FreeCAD.ActiveDocument
wireobj=doc.addObject("Part::Feature","myAirfoil")
#wireobj=FreeCAD.ActiveDocument.getObjectsByLabel("myAirfoil")[0]
wireobj.Shape=face


doc.recompute()