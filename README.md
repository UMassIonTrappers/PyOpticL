###  PyOpticL v2.0 released! See [migration guide](https://github.com/UMassIonTrappers/PyOpticL/tree/main#pyopticl-v1v2-migration) for details
---

<img height="100" alt="PyOpticL_logo" src="https://github.com/user-attachments/assets/6abdeee1-0d27-4417-b13f-469ae00388c7" />

## PyOpticL - Code-to-CAD optical system engineering

<img width="2483" height="1172" alt="image" src="https://github.com/user-attachments/assets/2b61827e-5624-4590-b8a4-2e94640a9535" />


<img width="3341" height="1411" alt="image" src="https://github.com/user-attachments/assets/1b857ff6-a425-4261-a6f4-b00795de6f05" />

#### Discord Server: https://discord.gg/vV4NP6rXmp

<!-- Trapped Ion quantum computer at UMass Amherst engineered with PyOpticL: -->
<!-- <img src="https://github.com/user-attachments/assets/1dbe2986-20e2-4f4e-9b4c-00dd31a4b656" width=50%> -->

### ReadMe
* [Library Features and Information](https://github.com/UMassIonTrappers/PyOpticL#about-pyopticl-python-optics-layout)
* [Installation Guide](https://github.com/UMassIonTrappers/PyOpticL#getting-setup)

### Wiki
* [Home](https://github.com/UMassIonTrappers/PyOpticL/wiki)
* [Quick Start Guide](https://github.com/UMassIonTrappers/PyOpticL/wiki/Quick-Start)

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

### Baseplate Examples and Designs
* [Designs](https://github.com/UMassIonTrappers/PyOpticL/tree/main/Designs)

---

<img src="https://github.com/user-attachments/assets/b24b1d63-7b17-4de1-95dd-dcf176b8d9d6" width=500>

## About PyOpticL (Python Optics Layout)
PyOpticL is a Python library for optics layout which uses beam-path simulation and dynamic beam-path routing for quick and easy optical layout by placing optical elements along the beam path without a priori specification, enabling dynamic layouts with automatic routing and connectivity.
The beam paths are automatically calculated as components are placed in the layout. Component placement can be defined "along beam" to remove the need for hard-coded coordinates. Beam calculations include reflection, transmission, refraction, and diffraction (limited). This library enables a new paradigm of optical engineering using modular sub-systems of modular baseplates with commerical optical elements (see abstraction layers below).

## Demonstration with Trapped Ion Qubits:
See our paper published in the journal Quantum for more details about our results using these laser sources and baseplates in our lab: </br>
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
