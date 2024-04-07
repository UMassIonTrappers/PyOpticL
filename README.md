## PyOpticL - A FreeCAD Workbench and Python Library for Creating Optical Layouts

<img width="624" alt="Screenshot 2023-10-27 221107" src="https://github.com/UMassIonTrappers/PyOpticL/assets/103533593/bb37373c-c2fe-4d69-8a45-c3edd08fe944">

## Useful Links

### ReadMe
* [Library Features and Information](https://github.com/UMassIonTrappers/PyOpticL#about-PyOpticL)
* [Installation Guide](https://github.com/UMassIonTrappers/PyOpticL#getting-setup)
* [Example Pictures](https://github.com/UMassIonTrappers/PyOpticL#examples)
### Wiki
* [Quickstart Guide](https://github.com/UMassIonTrappers/PyOpticL/wiki#quickstart-guide)
* [Model Import Guide](https://github.com/UMassIonTrappers/PyOpticL/wiki#model-import-guide)
* [ECDL Baseplate](https://github.com/UMassIonTrappers/PyOpticL/wiki/ECDL-Baseplate)
* [Modular Doublepass Baseplate](https://github.com/UMassIonTrappers/PyOpticL/wiki/Modular-Doublepass-Baseplate)
* [Rb SAS Baseplate](https://github.com/UMassIonTrappers/PyOpticL/wiki/Rb-SAS-Baseplate)

## About PyOpticL
### Based on MIT QUANTA LAB repo - C4PO ('CAD for Precision Optics') which is written for OpenSCAD
FreeCAD is based on python with built-in support for python scripts etc. It also has:
* Support for custom workbenches and python libraries
* Fully featured and customizable GUI
* Ability to work with various object formats

### Beam Simulation
* Beam paths are automatically calculated based on component placement
* Component placement can be defined "along beam" to remove the need for hard-coded coordinates
* Beam calculations include reflection, transmission, refraction, and diffraction (limited)

### Workbench Functions

Some GUI accessable functions have been implemented to perform various helpful actions:
* **Re-Run Last Macro** - Clears and re-draws last baseplate, great for quickly checking changes
* **Recalculate Beam Path** - Useful to check beam paths when applying in-editor modifications
* **Toggle Component Visibility** - Easily hide all beams and components
* **Toggle Draw Style** - Toggle wire-frame draw style to easily check for hidden issues
* **Export STLs** - Export all baseplates and adapter components to STL for fabrication
* **Export Cart** - Export all parts to both a spreadsheet and a csv compatible with Thorlabs upload-a-cart system
* **Reload Modules** - Reload all PyOpticL modules, great for debugging new parts
* **Get Orientation** - Automatic orientation and importing of new components from STEP files
* **Get Position** - Measure offsets and mount locations from oriented STEP file

These functions can also be scripted into macros if desired

## Getting Setup
There are a few important things to ensure before you can use PyOpticL:

1. **Install FreeCAD, Python, and Git**

2. **Clone the GitHub repo into your FreeCAD user folder**  
	To do this on windows, run the following in a terminal:  
	```cd "C:/Users/<username goes here>/AppData/Roaming/FreeCAD/Mod"```   
	```git clone "https://github.com/UMassIonTrappers/PyOpticL.git"```  
	```git config --global --add safe.directory "C:/Users/<username goes here>/AppData/Roaming/FreeCAD/Mod/PyOpticL"```
		
4. **Check everything is setup correctly**  
   You should now be able to re-launch FreeCAD and see the "PyOpticL" workbench in the dropdown  
<img width="250" alt="Screenshot 2023-10-27 225345" src="https://github.com/UMassIonTrappers/PyOpticL/assets/103533593/6eeec81a-e7de-4bde-8509-0c30bda0b9b7">

5. **Check out the [wiki](https://github.com/UMassIonTrappers/PyOpticL/wiki) or the [docs](https://github.com/UMassIonTrappers/PyOpticL/tree/main/docs) for guides, examples, and library documentation**

## Examples
### Modular Doublepass Baseplate
<img width="900" alt="image" src="https://github.com/UMassIonTrappers/PyOpticL/assets/103533593/6677d37d-d2ab-4938-b119-7d9bdd488a76">
<img width="900" alt="image" src="https://github.com/UMassIonTrappers/PyOpticL/assets/103533593/bcec73b6-b197-4c15-ab84-5962ccb32dcf">

### ECDL Baseplate
<img width="900" alt="image" src="https://github.com/UMassIonTrappers/PyOpticL/assets/103533593/9b169333-a5e8-4257-9e03-2dce2c6f0db3">
<img width="900" alt="image" src="https://github.com/UMassIonTrappers/PyOpticL/assets/103533593/ade01d2c-99c3-4e50-8a99-1446ed10fab9">  
