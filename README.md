

<!-- <img height="100" alt="PyOpticL_logo" src="https://github.com/user-attachments/assets/6abdeee1-0d27-4417-b13f-469ae00388c7" /> -->

# PyOpticL - Code-to-CAD optical system engineering

<img width="700" alt="banner" src="https://github.com/user-attachments/assets/725264e8-112d-42e8-a89b-91602258fd7d" />
 
## About PyOpticL (Python Optics Layout)
PyOpticL is a Python library for optics layout which uses beam-path simulation and dynamic beam-path routing for quick and easy optical layout by placing optical elements along the beam path without a priori specification, enabling dynamic layouts with automatic routing and connectivity.
The beam paths are automatically calculated as components are placed in the layout. Component placement can be defined "along beam" to remove the need for hard-coded coordinates. Beam calculations include reflection, transmission, refraction, and diffraction. This library enables a new paradigm of optical engineering using modular sub-systems of modular baseplates with commerical optical elements (see abstraction layers below).

<img src="https://github.com/user-attachments/assets/b24b1d63-7b17-4de1-95dd-dcf176b8d9d6" width=400>

## PyOpticL Demonstration with Trapped Ion Qubits:
Our paper in the journal [*Quantum*](https://quantum-journal.org/?s=Qubit%20operations%20using%20a%20modular%20optical%20system%20engineered%20with%20PyOpticL:%20a%20code-to-CAD%20optical%20layout%20tool&reason=title-click) shows how we use PyOpticL in our lab for trapped ion cooling, detection and single qubit gates.</br>

<a href="https://arxiv.org/abs/2501.14957"> arXiv:2501.14957 - Qubit operations using a modular optical system engineered with PyOpticL: a code-to-CAD optical layout tool</a>

### [UMass Amherst Trapped Ion system built with PyOpticL](https://websites.umass.edu/rniffenegger/pyopticl-code-to-cad-optical-layout/):
<img width="600" alt="UMass Amherst Trapped Ions" src="https://github.com/user-attachments/assets/2b61827e-5624-4590-b8a4-2e94640a9535" />

### Modular abstraction: Optics → Baseplates → Subsystems → Apparutus:
<img width="600" alt="Abstraction" src="https://github.com/user-attachments/assets/1b857ff6-a425-4261-a6f4-b00795de6f05" />

---

###  PyOpticL v2.0 🚀 released! It is a complete rewrite of the PyOpticL library!
* [Migrate from 1.0 to 2.0](https://github.com/UMassIonTrappers/PyOpticL/tree/main#pyopticl-v1v2-migration) 
* [v2.0-Highlights](https://github.com/UMassIonTrappers/PyOpticL/wiki/v2.0-Highlights)
   * Including Improved Optics Simulation (Gaussian beam simulation)

<img width="300" alt="image" src="https://github.com/user-attachments/assets/6ebfe1a3-06ec-457c-a59f-b1aafaa17a6a" />

### Discord Server: https://discord.gg/vV4NP6rXmp


<!-- Trapped Ion quantum computer at UMass Amherst engineered with PyOpticL: -->
<!-- <img src="https://github.com/user-attachments/assets/1dbe2986-20e2-4f4e-9b4c-00dd31a4b656" width=50%> -->

### ReadMe
* [Library Features and Information](https://github.com/UMassIonTrappers/PyOpticL#about-pyopticl-python-optics-layout)
* [Installation Guide](https://github.com/UMassIonTrappers/PyOpticL#getting-setup)

### [Wiki](https://github.com/UMassIonTrappers/PyOpticL/wiki)
* [Quick Start Guide](https://github.com/UMassIonTrappers/PyOpticL/wiki/Quick-Start)
* [Contributing to PyOpticL](https://github.com/UMassIonTrappers/PyOpticL/wiki/Contributing-to-PyOpticL)

### Modular baseplate examples:
* [Laser - Extended Cavity Diode Laser (with optical isolator)](https://github.com/UMassIonTrappers/PyOpticL/wiki/Module-‐-ECDL-with-Isolation-Baseplate)
* [Doublepass AOM Baseplate](https://github.com/UMassIonTrappers/PyOpticL/wiki/Module-‐-Doublepass-Baseplate)
* [Singlepass AOM Baseplate](https://github.com/UMassIonTrappers/PyOpticL/wiki/Module-‐-Singlepass-Baseplate)
* [Saturation Absorption Spectroscopy Baseplate](https://github.com/UMassIonTrappers/PyOpticL/wiki/Module-%E2%80%90-Saturation-Absorption-Spectroscopy-Baseplate))
* [Periscope](https://github.com/UMassIonTrappers/PyOpticL/wiki/Module-‐-Periscope)
* [CoverBox](https://github.com/UMassIonTrappers/PyOpticL/wiki/CoverBox)

### Modular Subsystems based on baseplates:
* [Laser Cooling and Detection](https://github.com/UMassIonTrappers/PyOpticL/wiki/Subsystem-‐-Laser-Cooling-and-Detection)
* [Raman Zeeman qubit](https://github.com/UMassIonTrappers/PyOpticL/wiki/Subsystem-%E2%80%90-Raman)
* [Photoionization](https://github.com/UMassIonTrappers/PyOpticL/wiki/Subsystem-%E2%80%90-Photoionization-Laser)
* [State Preparation and Measurement](https://github.com/UMassIonTrappers/PyOpticL/wiki/Subsystem-%E2%80%90-SPAM)

### Apparatus based on modular subsystems:
* [Trapped Ions - Strontium](https://github.com/UMassIonTrappers/PyOpticL/wiki/Apparatus-%E2%80%90-Trapped-Ions-%E2%80%90-Strontium)
* [Trapped Ions - Calcium](https://github.com/UMassIonTrappers/PyOpticL/wiki/Apparatus-%E2%80%90-Trapped-Ions-%E2%80%90-Calcium)
* [Project - Redstone](https://github.com/UMassIonTrappers/PyOpticL/wiki/Apparatus-%E2%80%90-Quantum-Optics-%E2%80%90-Project-Redstone)

### Baseplate Examples and Designs
* [Designs](https://github.com/UMassIonTrappers/PyOpticL/tree/main/Designs)
* [3D Models and Technical Drawings](https://github.com/UMassIonTrappers/PyOpticL/tree/v1-legacy/Design/Module/3DModel)

---


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

7. **Check out the [wiki](https://github.com/UMassIonTrappers/PyOpticL/wiki) for guides on how to [get started](https://github.com/UMassIonTrappers/PyOpticL/wiki/Quick-Start) and examples**

### Pre-made Layouts

Macro files for pre-made layouts can be found in the PyOpticL directory. This can be found in: \
```<FreeCAD User Data Directory>/Mod/PyOpticL/Design``` \
On windows this is: \
```%APPDATA%\FreeCAD\Mod\PyOpticL\Design```

## PyOpticL v1/v2 Migration

The main branch of this project has been updated to PyOpticL v2.0! **This is a breaking change for existing designs.** Unless you manually update PyOpticL within FreeCAD, existing installs should be unaffected.

If you need to install v1:
* Use _Branch:_ v1-legacy when following the install instructions

To update to v2.0:
* Backup all locally changed files (optomech.py, stls, etc.)
* Uninstall PyOpticL from addon manager (This will delete all PyOpticL source files, **backup your changes**)
* Restart FreeCAD
* Re-install PyOpticL
___

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
