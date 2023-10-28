## PyOptic - A FreeCAD Workbench and Python Library for Creating Optical Layouts

<img width="624" alt="Screenshot 2023-10-27 221107" src="https://github.com/UMassIonTrappers/PyOptic/assets/103533593/bb37373c-c2fe-4d69-8a45-c3edd08fe944">

### Based on MIT QUANTA LAB repo - C4PO ('CAD for Precision Optics') which is written for OpenSCAD

FreeCAD has a few clear benifits for this purpose:
* Based on python with built-in support for python scripts
* Support for custom workbenches and python libraries
* Fully featured and customizable GUI
* Ability to work with various object formats

## Features

### Beam Simulation
* Beam paths are automatically calculated based on component placement
* Compnent placement can be defined "along beam" to remove the need for hard-coded coordinates
* Beam calculations include reflection, transmission, refraction, and diffraction (limited)

### Workbench Functions

Some GUI accessable functions have been implemented to perform various helpful actions:
* **Recalculate Beam Path** - Useful to check beam paths when applying in-editor modifications
* **Toggle Component Visibility** - Easily hide all beams and components  
* **Export STLs** - Export all baseplates and adapter components to STL for fabrication
* **Export Cart** - Export all parts to both a spreadsheet and a csv compatible with Thorlabs upload-a-cart system
* **Auto-Fit Top View** - Quickly switch to a fitted top down view
* **Reload Modules** - Reload all PyOptic modules, great for debugging new parts

These functions can also be scripted into macros if desired

## Getting Setup
There are a few important things to ensure before you can use PyOptic:

1. **Install FreeCAD, Python, and Git**

2. **Clone the GitHub repo into your FreeCAD user folder**  
	To do this on windows, run the following in a terminal:  
	```cd "C:/Users/<username goes here>/AppData/Roaming/FreeCAD/Mod"```   
	```git clone "https://github.com/UMassIonTrappers/PyOptic.git"```  
	```git config --global --add safe.directory "C:/Users/<username goes here>/AppData/Roaming/FreeCAD/Mod/PyOptic"```  
		
3. **Check everything is setup correctly**  
   You should now be able to re-launch FreeCAD and see the "PyOptic" workbench in the dropdown  
<img width="250" alt="Screenshot 2023-10-27 225345" src="https://github.com/UMassIonTrappers/PyOptic/assets/103533593/6eeec81a-e7de-4bde-8509-0c30bda0b9b7">

5. **Check out the [wiki](https://github.com/UMassIonTrappers/PyOptic/wiki) for examples and guides**
