import FreeCAD as App
import Import
import Part

App.newDocument()
document = App.ActiveDocument

doc = App.ActiveDocument or App.newDocument()

path = r"C:\Users\jay\Downloads\POLARIS-B05G-Step.step"

shape = Part.read(path)

shape = shape.copy()

obj = doc.addObject("Part::Feature", "model_fixed")
obj.Shape = shape

vo = obj.ViewObject
vo.Deviation = 0.01

doc.recompute()
