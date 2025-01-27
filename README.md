## PyOpticL - Code-to-CAD optical system engineering


<img src="https://github.com/user-attachments/assets/b24b1d63-7b17-4de1-95dd-dcf176b8d9d6" width=700>

<!-- Trapped Ion quantum computer at UMass Amherst engineered with PyOpticL: -->
<!-- <img src="https://github.com/user-attachments/assets/1dbe2986-20e2-4f4e-9b4c-00dd31a4b656" width=50%> -->

### ReadMe
* [Library Features and Information](https://github.com/UMassIonTrappers/PyOpticL#about-PyOpticL)
* [Installation Guide](https://github.com/UMassIonTrappers/PyOpticL#getting-setup)

### Wiki
* [Quickstart Guide](https://github.com/UMassIonTrappers/PyOpticL/wiki#quickstart-guide)
* [Model Import Guide](https://github.com/UMassIonTrappers/PyOpticL/wiki#model-import-guide)
  
### Modular baseplate examples:
* [ECDL Baseplate](https://github.com/UMassIonTrappers/PyOpticL/wiki/Module-‐-ECDL-with-Isolation-Baseplate)
* [Doublepass Baseplate](https://github.com/UMassIonTrappers/PyOpticL/wiki/Module-‐-Doublepass-Baseplate)
* [Singlepass Baseplate](https://github.com/UMassIonTrappers/PyOpticL/wiki/Module-‐-Singlepass-Baseplate)
* [Saturation Absorption Spectroscopy Baseplate](https://github.com/UMassIonTrappers/PyOpticL/wiki/Module-‐-Saturation-Absoption-Spectroscopy-Baseplate)
* [Periscope](https://github.com/UMassIonTrappers/PyOpticL/wiki/Module-‐-Periscope)
### Modular Subsystems based on baseplates:
* [Laser Cooling and Detection](https://github.com/UMassIonTrappers/PyOpticL/wiki/Subsystem-‐-Laser-Cooling-and-Detection)
* [Raman Zeeman qubit](https://github.com/UMassIonTrappers/PyOpticL/wiki/Subsystem-%E2%80%90-Raman)
* [Photoionization](https://github.com/UMassIonTrappers/PyOpticL/wiki/Subsystem-%E2%80%90-Photoionization-Laser)
* [State Preparation and Measurement](https://github.com/UMassIonTrappers/PyOpticL/wiki/Subsystem-%E2%80%90-SPAM)
<img src="https://github.com/user-attachments/assets/728fd555-c74e-45da-b026-38bfa01f9a87" width=700>


## About PyOpticL
PyOpticL is a Python Library for Optical Layout which uses beam-path simulation and dynamic beam-path routing for quick and easy optical layout by placing optical elements along the beam path without a priori specification, enabling dynamic layouts with automatic routing and connectivity. This opens a new paradigm of optical system engineering using modular sub-systems of modular baseplates with commerical optical elements (see abstraction layers below).

### Beam Simulation
* Beam paths are automatically calculated based on component placement
* Component placement can be defined "along beam" to remove the need for hard-coded coordinates
* Beam calculations include reflection, transmission, refraction, and diffraction (limited)


## Getting Setup

1. **Install FreeCAD, Python, and Git**

2. **Add PyOpticL as an custom addon repository in FreeCAD**  
	Under _Edit>Preferences>Addons>Custom Repositories,_ enter the following information: \
    _Repository URL:_ https://github.com/UMassIonTrappers/PyOpticL.git \
    _Branch:_ main

3. **Install the PyOpticL library**
    In the Addon Manager _(Tools>Addon Manager),_ search for "PyOpticL" and click install.
		
4. **Check everything is setup correctly**  
   You should now be able to re-launch FreeCAD and see the "PyOpticL" workbench in the dropdown
   <!-- <img width="250" alt="Screenshot 2023-10-27 225345" src="https://github.com/user-attachments/assets/7a43cac3-7d3b-4a3b-8e5f-189f39729251"> -->

5. **Check out the [wiki](https://github.com/UMassIonTrappers/PyOpticL/wiki) for guides on how to [get started](https://github.com/UMassIonTrappers/PyOpticL/wiki#quickstart-guide) and examples**

6. **Read the [docs](https://github.com/UMassIonTrappers/PyOpticL/tree/main/docs) library documentation**

___



## Design abstraction layers applied to a strontium trapped ion quantum computer:

<img src="https://github.com/user-attachments/assets/75341182-ff6c-4106-bd7c-8fa9ee56bba2" width=700>


## Dynamic layouts 
Same code compiled with different optical elements at different scales:
![image](https://github.com/user-attachments/assets/5340ac9b-0a6f-4758-803f-e5a5f15b18a3)

<!--
### Modular Doublepass Baseplate (f50 & f100 design)
<p align="center">
  <img src="https://github.com/user-attachments/assets/5d332f5a-defc-4eb4-8ca6-a720dad9cfe6" alt="doublepass_f50_f100" width="55%" />
</p>


### Simple ECDL (all off-the-shelf components)
![image](https://github.com/user-attachments/assets/41fba0be-d6c5-48b3-9fd5-c1e4fdddcd74)
-->

#### We thank the MIT QUANTA LAB for sharing their C4PO ('CAD for Precision Optics') based on OpenSCAD which inspired this library.
