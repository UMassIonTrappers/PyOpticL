## PyOpticL - Code-to-CAD optical system engineering

Trapped Ion quantum computer at UMass Amherst engineered with PyOpticL:

<!-- <img src="https://github.com/user-attachments/assets/1dbe2986-20e2-4f4e-9b4c-00dd31a4b656" width=50%> -->

<img src="https://github.com/user-attachments/assets/728fd555-c74e-45da-b026-38bfa01f9a87" width=50%>

### ReadMe
* [Library Features and Information](https://github.com/UMassIonTrappers/PyOpticL#about-PyOpticL)
* [Installation Guide](https://github.com/UMassIonTrappers/PyOpticL#getting-setup)
* [Example Pictures](https://github.com/UMassIonTrappers/PyOpticL#examples)
### Wiki
* [Quickstart Guide](https://github.com/UMassIonTrappers/PyOpticL/wiki#quickstart-guide)
* [Model Import Guide](https://github.com/UMassIonTrappers/PyOpticL/wiki#model-import-guide)
### Modular baseplate examples
* [ECDL Baseplate](https://github.com/UMassIonTrappers/PyOpticL/wiki/ECDL-Baseplate)
* [Doublepass Baseplate](https://github.com/UMassIonTrappers/PyOpticL/wiki/Doublepass-Baseplate)
* [Singlepass Baseplate](https://github.com/UMassIonTrappers/PyOpticL/wiki/Singlepass-Baseplate)
* [Saturation Absorption Spectroscopy Baseplate](https://github.com/UMassIonTrappers/PyOpticL/wiki/Saturation-Absoption-Spectroscopy-Baseplate)
* [Periscope](https://github.com/UMassIonTrappers/PyOpticL/wiki/Periscope)

Design abstraction layers applied to a strontium trapped ion quantum computer:

<img src="https://github.com/user-attachments/assets/75341182-ff6c-4106-bd7c-8fa9ee56bba2" width=50%>


## Examples

### Modular Saturated Absorption Spectroscopy Baseplates compiled at different scales
![image](https://github.com/user-attachments/assets/5340ac9b-0a6f-4758-803f-e5a5f15b18a3)

### Modular Doublepass Baseplate (f50 & f100 design)
<p align="center">
  <img src="https://github.com/user-attachments/assets/5d332f5a-defc-4eb4-8ca6-a720dad9cfe6" alt="doublepass_f50_f100" width="55%" />
</p>

### Simple ECDL (all off-the-shelf components)
![image](https://github.com/user-attachments/assets/41fba0be-d6c5-48b3-9fd5-c1e4fdddcd74)


## About PyOpticL
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

2. **Add PyOpticL as an custom addon repository in FreeCAD**  
	Under _Edit>Preferences>Addons>Custom Repositories,_ enter the following information: \
    _Repository URL:_ https://github.com/UMassIonTrappers/PyOpticL.git \
    _Branch:_ main

3. **Install the PyOpticL library**
    In the Addon Manager _(Tools>Addon Manager),_ search for "PyOpticL" and click install.
		
4. **Check everything is setup correctly**  
   You should now be able to re-launch FreeCAD and see the "PyOpticL" workbench in the dropdown  
<img width="250" alt="Screenshot 2023-10-27 225345" src="https://github.com/UMassIonTrappers/PyOpticL/assets/103533593/6eeec81a-e7de-4bde-8509-0c30bda0b9b7">

5. **Check out the [wiki](https://github.com/UMassIonTrappers/PyOpticL/wiki) or the [docs](https://github.com/UMassIonTrappers/PyOpticL/tree/main/docs) for guides, examples, and library documentation**

#### We thank the MIT QUANTA LAB for sharing their C4PO ('CAD for Precision Optics') based on OpenSCAD which inspired this library.
