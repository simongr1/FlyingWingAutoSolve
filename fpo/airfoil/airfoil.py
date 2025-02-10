import FreeCAD as App
import Part
import numpy as np
from .utils import process

"""
https://wiki.freecad.org/Create_a_FeaturePython_object_part_I
Like this you can add an object to a part:
import FreeCAD as App

doc = App.newDocument()
part = App.ActiveDocument.addObject("App::Part", "Part")

obj1 = App.ActiveDocument.addObject("PartDesign::Body", "Body")
obj2 = App.ActiveDocument.addObject("Part::Box", "Box")
part_root=App.ActiveDocument.getObjectsByLabel("RootProfile")[0]
part_tip=App.ActiveDocument.getObjectsByLabel("TipProfile")[0]

part_root.addObjects()
App.ActiveDocument.recompute()

usage:
from fpo.airfoil import airfoil
from importlib import reload

reload(airfoil) #reloads the module if there were any changes !!The previous objects are not updated if the code is changed
airfoil.create("name") #this creates an initial airfoil
"""
def create(obj_name):
    """
    Object creation method
    """

    obj = App.ActiveDocument.addObject('Part::FeaturePython', obj_name)

    airfoil(obj)
    ViewProviderBox(obj.ViewObject)
    App.ActiveDocument.recompute()
    return obj

class airfoil():

    def __init__(self, obj):
        """
        Default constructor
        """

        self.Type = 'airfoil'

        obj.Proxy = self
        obj.addProperty('App::PropertyString', 'Description', 'Base', 'Box description').Description = "Custom airfoil using Bernstein polynomials. Currently camber controll"
        obj.addProperty('App::PropertyFloat', 'U1', 'Parameter', 'Function parameter').U1=0.07497288
        obj.addProperty('App::PropertyFloat', 'U2', 'Parameter', 'Function parameter').U2=0.18129897
        obj.addProperty('App::PropertyFloat', 'U3', 'Parameter', 'Function parameter').U3=-0.00487776
        obj.addProperty('App::PropertyFloat', 'U4', 'Parameter', 'Function parameter').U4=0.07436278
        obj.addProperty('App::PropertyLength', 'ChordLength', 'Dimensions', 'Chord length').ChordLength=100
        obj.addProperty('App::PropertyFloatList', 'ThicknessParameterList', 'Special', "Thickness").ThicknessParameterList=[0.15023359, 0.17078099, 0.12732937, 0.14198486]
        obj.addProperty('App::PropertyFloatList', 'CamberParameterList', 'Special', "Camber").CamberParameterList=[ 0.07497288,  0.18129897, -0.00487776,  0.07436278]
    def execute(self, obj):
        """
        Called on document recompute
        """
        #Calculate for constant thickness distubution
        u_camber=np.array([obj.U1,obj.U2,obj.U3,obj.U4])
        u_thickness=np.array(obj.ThicknessParameterList)
        u_upper=u_camber+u_thickness
        u_lower=u_camber-u_thickness
        obj.Shape= process(obj.ChordLength.Value,u_upper,u_lower)

class ViewProviderBox:

    def __init__(self, obj):
        """
        Set this object to the proxy object of the actual view provider
        """

        obj.Proxy = self

    def attach(self, obj):
        """
        Setup the scene sub-graph of the view provider, this method is mandatory
        """
        return

    def updateData(self, fp, prop):
        """
        If a property of the handled feature has changed we have the chance to handle this here
        """
        return

    def getDisplayModes(self,obj):
        """
        Return a list of display modes.
        """
        return []

    def getDefaultDisplayMode(self):
        """
        Return the name of the default display mode. It must be defined in getDisplayModes.
        """
        return "FlatLines"

    def setDisplayMode(self,mode):
        """
        Map the display mode defined in attach with those defined in getDisplayModes.
        Since they have the same names nothing needs to be done.
        This method is optional.
        """
        return mode

    def onChanged(self, vp, prop):
        """
        Print the name of the property that has changed
        """

        App.Console.PrintMessage("Change property: " + str(prop) + "\n")

    def getIcon(self):
        """
        Return the icon in XMP format which will appear in the tree view. This method is optional and if not defined a default icon is shown.
        """

        return """
            /* XPM */
            static const char * ViewProviderBox_xpm[] = {
            "16 16 6 1",
            "    c None",
            ".   c #141010",
            "+   c #615BD2",
            "@   c #C39D55",
            "#   c #000000",
            "$   c #57C355",
            "        ........",
            "   ......++..+..",
            "   .@@@@.++..++.",
            "   .@@@@.++..++.",
            "   .@@  .++++++.",
            "  ..@@  .++..++.",
            "###@@@@ .++..++.",
            "##$.@@$#.++++++.",
            "#$#$.$$$........",
            "#$$#######      ",
            "#$$#$$$$$#      ",
            "#$$#$$$$$#      ",
            "#$$#$$$$$#      ",
            " #$#$$$$$#      ",
            "  ##$$$$$#      ",
            "   #######      "};
            """

    def dumps(self):
        """
        Called during document saving.
        """
        return None

    def loads(self,state):
        """
        Called during document restore.
        """
        return None