# Run in FreeCAD Python console (no file changes)
import FreeCAD as App
from pprint import pprint


def dump_obj(o):
    return {
        "Name": o.Name,
        "Placement.Base": getattr(o.Placement, "Base", None),
        "Placement.Rotation": getattr(o.Placement, "Rotation", None),
        "BasePlacement.Base": getattr(getattr(o, "BasePlacement", None), "Base", None),
        "BasePlacement.Rotation": getattr(
            getattr(o, "BasePlacement", None), "Rotation", None
        ),
        "InList": [p.Name for p in o.InList] if hasattr(o, "InList") else None,
    }


doc = App.ActiveDocument
parent = doc.getObject("Example_Component_2")  # replace name if different

print("=== (document-level snapshot) ===")
print("Document objects placements:")
for o in [parent.Parent] + [parent] + list(parent.Children):
    if o is None:
        continue
    pprint(dump_obj(o))
