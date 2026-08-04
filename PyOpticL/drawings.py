# This code is to generate 2D drawing of the baseplate indicating threaded holes with their thread designation

import FreeCAD
import TechDraw
import Part
from PySide import QtCore
from math import isclose
from PyOpticL import layout
from PyOpticL.library.hardware import Bolt
from numpy import isclose

from inspect import cleandoc
import FreeCAD as App
from PySide import QtGui, QtCore

# ==========================
# Configuration
# ==========================

MARGIN_MM = 10.0      # Margin around page
TITLE_BLOCK_MM = 60
FILL_FACTOR = 0.90    # Use 90% of available area

# A4 dimensions
PORTRAIT = (210.0, 297.0)
LANDSCAPE = (297.0, 210.0)


# Preferred engineering scales
STANDARD_SCALES = [
    10.0,
    5.0,
    2.0,
    1.0,
    0.5,
    0.2,
    0.1,
]

RESOURCE_DIR = App.getResourceDir()

PORTRAIT_TEMPLATE = (
    RESOURCE_DIR
    + "Mod/TechDraw/Templates/A4_Portrait_ISO5457_minimal.svg"
)

LANDSCAPE_TEMPLATE = (
    RESOURCE_DIR
    + "Mod/TechDraw/Templates/A4_Landscape_ISO5457_minimal.svg"
)

def get_view_extent(source, direction):
    """
    Return model size projected into the view plane.

    Args:
        source (Part::PartFeature): the geometry to be drawn
        direction (tuple): the view direction

    Returns:
        width, height (float): extent of the projected view 
    """

    shape = source.Shape
    bb = shape.BoundBox

    x_size = bb.XLength
    y_size = bb.YLength
    z_size = bb.ZLength

    direction = direction

    dx = abs(direction[0])
    dy = abs(direction[1])
    dz = abs(direction[2])

    # Determine dominant viewing direction
    if dx >= dy and dx >= dz:
        # Looking along X
        width = y_size
        height = z_size

    elif dy >= dx and dy >= dz:
        # Looking along Y
        width = x_size
        height = z_size

    else:
        # Looking along Z
        width = x_size
        height = y_size

    return width, height


def fit_scale(view_width, view_height, page_w, page_h):
    """
    Compute scale which fits the view inside page.

    Args:
        view_width (float): Width of the view in mm
        view_height (float): Height of the view in mm
        page_w (float): Width of the page in mm
        page_h (float):  Height of the page in mm

    Returns:
        scale (float): Largest scale where the view fits onto the page 
    """

    usable_w = page_w - 2 * MARGIN_MM
    usable_h = page_h - 2 * MARGIN_MM - TITLE_BLOCK_MM

    sx = usable_w / view_width
    sy = usable_h / view_height

    return min(sx, sy) * FILL_FACTOR


def scale_label(scale):
    """
    Convert numeric scale to engineering notation.
    
    Args:
        scale (float): numerical scale

    Returns:
        scale_label (str): string representation of the scale
    """
    
    if abs(scale - 1.0) < 1e-6:
        return "1 : 1"
    
    if scale > 1:
        return f"{scale:g} : 1"
    
    return f"1 : {round(1.0/scale):g}"

def choose_standard_scale(max_scale):
    """
    Largest standard scale that fits.

    Args:
        max_scale (float): Largest acceptable scale

    Returns:
        standard_scale (float): Largest standard scale
    """

    for s in STANDARD_SCALES:
        if s <= max_scale:
            return s

    return STANDARD_SCALES[-1]



def make_drawing(baseplate, views = 'top'):
        """
        Generate drawings for a baseplate

        Args:
            baseplate (PartFeature): baseplate object for which to generate drawings
            views (str): views to generate - currently 'top' for simple baseplates that have no threaded holes on the sides, or 'all'
        """

        doc = App.ActiveDocument

        if views.lower() == 'top':
             directions = [
            ("Top", (0, 0, 1)),
            ]
        elif views.lower() == 'all':
            directions = [
             ("Top", (0, 0, 1)),
             ("Front", (0, -1, 0)),
             ("Back", (0, 1, 0)),
             ("Left", (-1, 0, 0)),
             ("Right", (1, 0, 0)),
        ]
        baseplate_name = baseplate.Label

        for i, (name, direction) in enumerate(directions):

            # Determine scale to fit page
                        
            # Get projected dimensions
            view_w, view_h = get_view_extent(baseplate, direction)

            # Calculate possible scales
            portrait_scale = fit_scale(
                view_w,
                view_h,
                PORTRAIT[0],
                PORTRAIT[1]
            )

            landscape_scale = fit_scale(
                view_w,
                view_h,
                LANDSCAPE[0],
                LANDSCAPE[1]
            )

            # Choose orientation giving largest scale
            if landscape_scale > portrait_scale:
                scale = choose_standard_scale(landscape_scale)
                page_w, page_h = LANDSCAPE
                orientation = "Landscape"
            else:
                scale = choose_standard_scale(portrait_scale)
                page_w, page_h = PORTRAIT
                orientation = "Portrait"


            page = doc.addObject("TechDraw::DrawPage", f"{baseplate_name} - {name} View")

            # Create a default template for the page
            template = doc.addObject(
                "TechDraw::DrawSVGTemplate",
                "LandscapeTemplate" if orientation == "Landscape" else "PortraitTemplate"
            )
            template.Template = LANDSCAPE_TEMPLATE if orientation == "Landscape" else  PORTRAIT_TEMPLATE
            page.Template = template 

            # Create a TechDraw view for the baseplate and add it to the page
            view = doc.addObject("TechDraw::DrawViewPart", f"Baseplate{name}")
            view.Source = [baseplate]
            view.Direction = direction

            page.Scale = scale
            view.Scale = scale

            page.addView(view)
            doc.recompute()
            page.ViewObject.show()

            # Center view on page
            view.X = page_w / 2.0
            view.Y = page_h / 2.0 + TITLE_BLOCK_MM /2

            # update title block 
            page.Template.setEditFieldContent('scale',scale_label(scale))
            page.Template.setEditFieldContent('creator', 'PyOpticL')
            page.Template.setEditFieldContent('document_type', 'Threaded holes')
            page.Template.setEditFieldContent('approval_person', '')
            page.Template.setEditFieldContent('part_material', 'Aluminium')
            page.Template.setEditFieldContent('title', f"{baseplate_name} - {name}")
            page.Template.setEditFieldContent('sheet_number', f"{i+1} / {len(directions)}")
            
            view.touch()
            doc.recompute()
            doc.recompute()

            # some parts take a while to generate the view, so poll for up to 10s until there are edges
            loop = QtCore.QEventLoop()

            timer = QtCore.QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(loop.quit)
            for i in range(100):
                timer.start(100)
                loop.exec_()
                edges = view.getVisibleEdges()
                if len(edges) >0:
                    break
            doc.recompute()

            # traverse all edges and look for circles matching tap drill diameters
            for i, edge in enumerate(edges):
                if isinstance(edge.Curve, (Part.Circle, Part.ArcOfCircle)):
                    radius = edge.Curve.Radius / view.Scale
                    label = None
                    for bolt_type, dimensions in Bolt.available_bolt_types.items():
                            if isclose(dimensions["tap_diameter"], 2 * radius):
                                label = bolt_type
                    if label != None:
                        # create balloon label with thread designation
                        x, y, _ = edge.Curve.Center
                        x, y = x / view.Scale, y / view.Scale
                        balloon = FreeCAD.ActiveDocument.addObject(
                            "TechDraw::DrawViewBalloon", "Balloon"
                        )

                        balloon.SourceView = view
                        balloon.OriginX = x
                        balloon.OriginY = -y

                        if orientation == "Landscape":
                            view_height = view.Y.getValueAs('mm')
                            if y > 0:
                                balloon.X = x  + .5*view_height*.25
                                balloon.Y = - y - view_height*.25
                            else:
                                balloon.X = x - .5*view_height*.25
                                balloon.Y = - y + view_height*.25
                        else:
                            view_width = view.X.getValueAs('mm')
                            if x > 0:
                                balloon.X = x  + view_width*.5
                                balloon.Y = - y - .5*view_width*.5
                            else:
                                balloon.X = x - view_width*.5
                                balloon.Y = - y + .5*view_width*.5
                        balloon.Text = label
                        balloon.BubbleShape = "Line"
                        balloon.KinkLength = 0
                        balloon.ShapeScale = 0.75
                        balloon.ViewObject.Font = "MS Sans Serif"
                        balloon.ViewObject.Fontsize = 4
                        page.addView(balloon)

            view.touch()
            view.recompute()
            doc.recompute()



def count_drawings():
    """
    Count the number of TechDraw pages in the current document
    
    Returns:
        num_pages (int): number of pages

    """
    doc = FreeCAD.ActiveDocument

    # Collect pages first to avoid modifying the document
    # while iterating through it.
    pages = [
        obj for obj in doc.Objects
        if obj.isDerivedFrom("TechDraw::DrawPage")
    ]
    return len(pages)


def delete_drawings():

    """
    Clean up any drawing pages generated in previous runs
    """

    doc = FreeCAD.ActiveDocument

    # Collect pages first to avoid modifying the document
    # while iterating through it.
    pages = [
        obj for obj in doc.Objects
        if obj.isDerivedFrom("TechDraw::DrawPage")
    ]

    for page in pages:
        # Remove associated template if present
        try:
            if page.Template:
                template_name = page.Template.Name
                doc.removeObject(template_name)
        except Exception:
            pass

        doc.removeObject(page.Name)

    doc.recompute()





class DrawingOptionsDialog(QtGui.QDialog):

    """
    Dialog for selecting drawing options
    
    """

    def __init__(self, baseplate_names, drawing_pages, parent=None):
        super(DrawingOptionsDialog, self).__init__(parent)

        self.setWindowTitle("Generate drawings for PyOpticL baseplates")
        self.setModal(True)

        self.instructions = QtGui.QLabel(
            cleandoc(
                f"""
                Generate drawings for the selected baseplates. The primary use of these drawings is to supplement the CAD file by calling out threaded holes.
                Select 'Top view only' for simple baseplates that only have threaded holes on the top surface, and 'All views' for baseplates that use eg FiberPorts mounted on the edges.
                All views will be placed on separate pages, with pages numbered per baseplate.
                To export the drawings to PDF use the 'Print all pages' function of the TechDraw workbench.
                """
            )
        )


        # Baseplate selection
        self.baseplate_list = QtGui.QListWidget()
        self.baseplate_list.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        for name in baseplate_names:
            item = QtGui.QListWidgetItem(name)
            self.baseplate_list.addItem(item)
            item.setSelected(True) # default = selected

        # Delete existing drawings checkbox
        self.delete_checkbox = QtGui.QCheckBox(
            f"Delete existing drawing pages (This will delete {drawing_pages} pages!)"
        )
        self.delete_checkbox.setChecked(True)

        # View selection
        self.view_combo = QtGui.QComboBox()
        self.view_combo.addItems([
            "Top view only",
            "All views"
        ])

        form_layout = QtGui.QFormLayout()
        form_layout.addRow("Views:", self.view_combo)

        # OK / Cancel buttons
        self.button_box = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok |
            QtGui.QDialogButtonBox.Cancel
        )

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # Main layout
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.instructions)
        layout.addWidget(self.baseplate_list)
        layout.addWidget(self.delete_checkbox)
        layout.addLayout(form_layout)
        layout.addWidget(self.button_box)

    @property
    def delete_existing(self):
        return self.delete_checkbox.isChecked()

    @property
    def view_mode(self):
        return self.view_combo.currentText()

    @property
    def selected_baseplates(self):
        return [
            item.text()
            for item in self.baseplate_list.selectedItems()
        ]



def generate_drawings():
    """
    Generate drawing for the active document
    """
    doc = FreeCAD.ActiveDocument

    #check that all defined threads are distinguishable from their tap diameter
    for bolt_type, dimensions in Bolt.available_bolt_types.items():
        for bolt_type2, dimensions2 in Bolt.available_bolt_types.items():
            if isclose(dimensions["tap_diameter"], dimensions2["tap_diameter"]) and (bolt_type != bolt_type2):
                print(f"Caution: Tap diameters for {bolt_type} and {bolt_type2} are indistinguishable!")

    doc = App.ActiveDocument

    if doc is None:
        raise RuntimeError("No active document")
    
    #collect names of baseplates in the current document
    baseplates = []
    for obj in doc.Objects:
            if hasattr(obj, 'Proxy'):
                if hasattr(obj.Proxy, 'object_group'):
                    if obj.Proxy.object_group == 'baseplate':
                        baseplates.append(obj.Name)

    # Show options dialog
    dialog = DrawingOptionsDialog(baseplate_names=baseplates, drawing_pages=count_drawings())

    if dialog.exec_():
        if dialog.delete_existing:
            delete_drawings()

        views = dialog.view_mode.split(" ")[0] # reduce verbose labels to keywords 'top' or 'all'

        # traverse the document and create drawings for all baseplate objects
        for obj in doc.Objects:
            if hasattr(obj, 'Proxy'):
                if hasattr(obj.Proxy, 'object_group'):
                    if obj.Proxy.object_group == 'baseplate':
                            if obj.Name in dialog.selected_baseplates:
                                make_drawing(obj, views)

if __name__ == "__main__":
    generate_drawings()

