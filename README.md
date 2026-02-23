<img height="100" alt="PyOpticL_logo" src="https://github.com/user-attachments/assets/6abdeee1-0d27-4417-b13f-469ae00388c7" />

## PyOpticL - Code-to-CAD optical system engineering

<img width="3341" height="1411" alt="image" src="https://github.com/user-attachments/assets/1b857ff6-a425-4261-a6f4-b00795de6f05" />

#### Discord Server: https://discord.gg/vV4NP6rXmp

<!-- Trapped Ion quantum computer at UMass Amherst engineered with PyOpticL: -->
<!-- <img src="https://github.com/user-attachments/assets/1dbe2986-20e2-4f4e-9b4c-00dd31a4b656" width=50%> -->

### ReadMe
* [Library Features and Information](https://github.com/UMassIonTrappers/PyOpticL#about-pyopticl-python-optics-layout)
* [Installation Guide](https://github.com/UMassIonTrappers/PyOpticL#getting-setup)

### Wiki
* [Quickstart Guide](https://github.com/UMassIonTrappers/PyOpticL/wiki#quickstart-guide)
* [Model Import Guide](https://github.com/UMassIonTrappers/PyOpticL/wiki#model-import-guide)
* [Contributing to PyOpticL](https://github.com/UMassIonTrappers/PyOpticL/wiki/Contributing-to-PyOpticL)
  
### Modular baseplate examples:
* [Laser - Extended Cavity Diode Laser (with optical isolator)](https://github.com/UMassIonTrappers/PyOpticL/wiki/Module-‐-ECDL-with-Isolation-Baseplate)
* [Doublepass AOM Baseplate](https://github.com/UMassIonTrappers/PyOpticL/wiki/Module-‐-Doublepass-Baseplate)
* [Singlepass AOM Baseplate](https://github.com/UMassIonTrappers/PyOpticL/wiki/Module-‐-Singlepass-Baseplate)
* [Saturation Absorption Spectroscopy Baseplate](https://github.com/UMassIonTrappers/PyOpticL/wiki/Module-‐-Saturation-Absoption-Spectroscopy-Baseplate)
* [Periscope](https://github.com/UMassIonTrappers/PyOpticL/wiki/Module-‐-Periscope)
* [CoverBox](https://github.com/UMassIonTrappers/PyOpticL/wiki/CoverBox)

### Modular Subsystems based on baseplates:
* [Laser Cooling and Detection](https://github.com/UMassIonTrappers/PyOpticL/wiki/Subsystem-‐-Laser-Cooling-and-Detection)
* [Raman Zeeman qubit](https://github.com/UMassIonTrappers/PyOpticL/wiki/Subsystem-%E2%80%90-Raman)
* [Photoionization](https://github.com/UMassIonTrappers/PyOpticL/wiki/Subsystem-%E2%80%90-Photoionization-Laser)
* [State Preparation and Measurement](https://github.com/UMassIonTrappers/PyOpticL/wiki/Subsystem-%E2%80%90-SPAM)

### AMO Apparatus based on modular subsystems:
* [Trapped Ions - Strontium](https://github.com/UMassIonTrappers/PyOpticL/wiki/Apparatus-%E2%80%90-Trapped-Ions-%E2%80%90-Strontium)
* [Trapped Ions - Calcium](https://github.com/UMassIonTrappers/PyOpticL/wiki/Apparatus-%E2%80%90-Trapped-Ions-%E2%80%90-Calcium)

## 3D Models and Technical Drawings
* [Click Here for 3D Models and Technical Drawings for All Modules](https://github.com/UMassIonTrappers/PyOpticL/tree/main/Design/Module/3DModel)

<img src="https://github.com/user-attachments/assets/b24b1d63-7b17-4de1-95dd-dcf176b8d9d6" width=500>

## About PyOpticL (Python Optics Layout)
PyOpticL is a Python library for optics layout which uses beam-path simulation and dynamic beam-path routing for quick and easy optical layout by placing optical elements along the beam path without a priori specification, enabling dynamic layouts with automatic routing and connectivity.
The beam paths are automatically calculated as components are placed in the layout. Component placement can be defined "along beam" to remove the need for hard-coded coordinates. Beam calculations include reflection, transmission, refraction, and diffraction (limited). This library enables a new paradigm of optical engineering using modular sub-systems of modular baseplates with commerical optical elements (see abstraction layers below).

## Demonstration with Trapped Ion Qubits:
See our recent preprint for more details about our results using these laser sources and baseplates in our lab: </br>
<a href="https://arxiv.org/abs/2501.14957"> arXiv:2501.14957 - Qubit operations using a modular optical system engineered with PyOpticL: a code-to-CAD optical layout tool</a>


## Getting Setup

1. **Install FreeCAD, Python, and Git**

2. **Add PyOpticL as a custom addon repository in FreeCAD**  
	Under _Edit>Preferences>Addon Manager>Custom Repositories,_ click the plus icon and enter the following information: \
    _Repository URL:_ https://github.com/UMassIonTrappers/PyOpticL.git \
    _Branch:_ main \
   Press _OK_ to save settings

4. **Install the PyOpticL library**
    In the Addon Manager _(Tools>Addon Manager),_ search for "PyOpticL" and click install. \
   _Note: if you get an error related to git, try disabling it - Edit>Preferences>Addon Manager>Disable git_
		
6. **Check everything is setup correctly**  
   You should now be able to re-launch FreeCAD and see the "PyOpticL" workbench in the workbench dropdown
   <!-- <img width="250" alt="Screenshot 2023-10-27 225345" src="https://github.com/user-attachments/assets/7a43cac3-7d3b-4a3b-8e5f-189f39729251"> -->

7. **Check out the [wiki](https://github.com/UMassIonTrappers/PyOpticL/wiki) for guides on how to [get started](https://github.com/UMassIonTrappers/PyOpticL/wiki#quickstart-guide) and examples**

8. **Read the [docs](https://github.com/UMassIonTrappers/PyOpticL/tree/main/docs) library documentation**

### Pre-made Layouts

Macro files for pre-made layouts can be found in the PyOpticL directory. This can be found in: \
```<FreeCAD User Data Directory>/Mod/PyOpticL/Design``` \
On windows this is: \
```%APPDATA%\FreeCAD\Mod\PyOpticL\Design```
___


### Example - Laser cooling and detection:

```python
from PyOpticL import layout, optomech
from ECDL import ECDL
from Rb_SAS_V2 import Rb_SAS
from modular_doublepass import doublepass
from modular_singlepass import singlepass

def laser_cooling_subsystem():
    layout.table_grid(dx=36, dy=22)
    ECDL(x=27, y=20, angle=180)
    Rb_SAS(x=20, y=1, angle=90)
    singlepass(x=14, y=12, angle=90)
    doublepass(x=1, y=21, angle=270)
```

![full_setup](https://github.com/user-attachments/assets/98261868-0474-4b8d-a73f-8785c20799b5)

 
## Dynamic layouts:

```python
Rb_SAS(0, 16, optic_type=one_inch_mounted)
Rb_SAS(0, 8, optic_type=half_inch_mounted)
Rb_SAS(0, 3, optic_type=half_inch_unmounted)
Rb_SAS(0, 0, optic_type=mini_optics)
```

Same code compiled with different optical elements at different scales:
![image](https://github.com/user-attachments/assets/5340ac9b-0a6f-4758-803f-e5a5f15b18a3)


## Design abstraction layers applied to a strontium trapped ion quantum computer:

```python
from PyOpticL import layout, optomech
from SPAM_subsystem import subsystem_spam
from Laser_cooling_subsystem import laser_cooling_subsystem
from Raman_subsystem import Raman_subsystem
from Photoionization_subsystem import PI_subsystem_ECDL, PI_subsystem_commercial

layout.table_grid(dx=52, dy=92)
laser_cooling_subsystem(x=-1, y=0, thumbscrews=True)
Raman_subsystem(x=1 , y=26.5, thumbscrews=True)
PI_subsystem_commercial(x=29 , y=8, angle = 0, thumbscrews=True) #405 for sr88+ 
PI_subsystem_ECDL(x=38 , y=8, thumbscrews=True) # 461 for sr88+
subsystem_spam(x=32 , y=50, thumbscrews=True)
```

<img src="https://github.com/user-attachments/assets/75341182-ff6c-4106-bd7c-8fa9ee56bba2" width=700>


<!--
### Modular Doublepass Baseplate (f50 & f100 design)
<p align="center">
  <img src="https://github.com/user-attachments/assets/5d332f5a-defc-4eb4-8ca6-a720dad9cfe6" alt="doublepass_f50_f100" width="55%" />
</p>


### Simple ECDL (all off-the-shelf components)
![image](https://github.com/user-attachments/assets/41fba0be-d6c5-48b3-9fd5-c1e4fdddcd74)
-->


## PyOpticL Community Members:

 * MIT QUANTA LAB (Prof. Isaac Chuang created the initial C4PO library which inspired this project)
 * MIT Quantum Photonics & AI Group (Prof. Dirk Englund)
 * UCONN - Prof. Simone Colombo
 * Montana St. - Prof. Matt Jaffe
 * UC Berkeley - Prof. Aziza Suleymanzade
 * UW Madison - Prof. Josiah Sinclair
 * NUS - Prof. Dzmitry Matsukevich
 * Stanford - Prof. Jonathan Simon
 * Quera
 * Durham University

<img width="800" src="https://github.com/user-attachments/assets/da1f5e60-a97e-493c-a372-581fa3e241eb" />


#### Again we thank the MIT QUANTA LAB for sharing their C4PO ('CAD for Precision Optics') based on OpenSCAD which inspired this library.



## Temporary v2.0 Wiki
_While v2.0 is still in pre-release development, this section of the ReadMe will be used for our wiki documentation. Once v2.0 is released the contents here will be moved to the Github wiki._

### PyOpticL Components and Terminology

#### Object
An instance of the layout class or any of its subclasses (components, beams, etc.).

#### Layout
A layout is the base class of most objects in PyOpticL. Simply, a layout is a grouping of objects. All objects within the layout are positioned relative to the layouts origin.

#### Component
A subclass of layout. This is a layout with it's own physical geometry, drilling, and optical properties. These aspects of the component are defined by instantiating it with a component definition.

#### Component Definition
A component definition is an abstract class which allows for the definition of various properties of a component:
* Geometry: Mesh or part based
* Drilling: Pre-defined drilling for part placement / mounting
* Subcomponents: Pre-defined components grouped with the parent component
* Interfaces: Definitions of the optical properties of the component

#### Interface
An abstract representation of an optical interface. This can be used to represent optical interactions such as reflection, refraction, thin lenses, and beyond. Any number of interfaces along with their positioning and properties can be defined with a component definition.

#### Beam Path
A subclass of layout. This object allows for simulation of a gaussian beam propagating through the layout. It supports focusing, polarization, wavelength, and power tracking all dictated by the interface parameters within the layout. It also overrides the add function of the layout class to allow for objects to be placed along the beam. This allows simple layout design via specifying only the rotation of the component and the distance from the last component.

### PyOpticL Usage Basics
At the top of every design we must have a base *layout* object. This could either be a component such as a baseplate object for all the components to mount to, or it could be a generic layout in which several baseplates or other designs could be nested. The key here is that all subclasses of layout can be treated largely the same. That is to say we could start our design as:
```
example_layout = layout( ... )
```
or
```
example_layout = component(definition=baseplate, ... )
```
and it will make no difference to the process of adding additional components to the layout.

To add components to any layout or object you use the add() function. In the case of a layout or component object, this takes arguments for the object you wish to add, the position, and the rotation. It is important to remember that generally all layouts and components can be treated the same. For instance one could define several small layouts, then add them all to a single baseplate:

```
layout1 = layout( ... )
layout1.add(component( ... ))

layout2 = layout( ... )
layout2.add(component( ... ))

baseplate = component(definition=baseplate, ... )
baseplate.add(layout1, ... )
baseplate.add(layout2, ... )
```

Similarly, there is no difference in adding a beam_path object to a layout, as it is also a subclass of the base layout class:
```
beam = example_layout.add(beam_path( ... ), ... )
```

Then for adding compoenent along the beam path, the placement arguments change, but the function is the same:
```
beam.add(component( ... ), ... )
```


### How to Create a Component Definition

General conventions:
* Component definition naming should follow clear convention. In the case of an off-the-shelf component, the name should follow:
type_of_component_partnumber, ie mirror_mount_km01
For custom components try to use highly descriptive names such as isomet_aom_bracket_for_km100.
* Transparency in calculations. Always try to make it clear where positions or value are derived from. If possible, it is always best to define any important positions as class constants with clear names, then reference them as needed. Hand calculating values from measurements and then hardcoding them in is typically discouraged.

The following properties are available to be define in component definition:

#### Class Variable
Pre-defined class constants such as:
* object_color: The color of the geometry
* object_icon: The icon displayed in FreeCAD tree view
* object_group: The group the object belongs to
* object_transparency: The transparency of the geometry
As well as any additional constants such as positions used for geometry or mounting.

#### __init__()
The init function is where you should define all user-adjustable parameter

#### shape() (optional)
This function defined the objects geometry, it should return a FreeCAD Part object. Refer to FreeCAD documentation for more info on how to create parts.

#### mesh (optional)
Define geometry mesh. This can be used instead of shape() for mesh-based components. See model importing for more details on adding a model to the library

#### subcomponents() (optional)
This function should return a list of components which will be automatically added to the component when added to a layout. Use the subcomponent namedTuple object to define the definition and placement of the subcomponent.

#### drill() (optional)
This defines the drilling which will be automatically cut from all parents and peers of this object in the layout. It must return a FreeCAD part object.

#### interfaces() (optional)
Define any optical interfaces for this component. This should return a list of optical interfaces that define the optical properties of the component.




