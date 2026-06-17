[![Quantum Paper](https://img.shields.io/badge/Quantum-2026-blue)](https://quantum-journal.org/papers/q-2026-06-15-2135/)
[![arXiv](https://img.shields.io/badge/arXiv-2501.14957-b31b1b)](https://arxiv.org/abs/2501.14957)
[![Citations](https://img.shields.io/badge/Cite%20PyOpticL-Quantum%202026-blue)](https://quantum-journal.org/papers/q-2026-06-15-2135/)
[![Discord](https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white)](https://discord.gg/vV4NP6rXmp)
[![FreeCAD](https://img.shields.io/badge/FreeCAD-1.0+-orange)](https://www.freecad.org/)
![Version](https://img.shields.io/badge/version-v2.0-success)

<!-- <img height="100" alt="PyOpticL_logo" src="https://github.com/user-attachments/assets/6abdeee1-0d27-4417-b13f-469ae00388c7" /> -->

# PyOpticL - Code-to-CAD Optical Engineering

Design optical systems in Python and automatically generate manufacturable CAD models with integrated beam-path simulation, automatic routing, and modular subsystem design.

<img width="700" alt="banner" src="https://github.com/user-attachments/assets/725264e8-112d-42e8-a89b-91602258fd7d" />
 
## Publication – High-Fidelity Trapped-Ion Qubit Operations with PyOpticL

<a href="https://quantum-journal.org/papers/q-2026-06-15-2135/">
    <img width="500" src="https://github.com/user-attachments/assets/4f8e2af5-2d51-4a9c-bdf8-13fc257014b8" />
</a>

PyOpticL is used in our trapped ion laboratory at UMass Amherst to design and deploy modular optical systems for trapped-ion quantum computing. We demonstrate laser cooling, state detection, and >99% fidelity single-qubit gates in our trapped-ion system using PyOpticL baseplates and lasers.

### Read the paper

- **Quantum (2026):**  
  [Qubit operations using a modular optical system engineered with PyOpticL: a code-to-CAD optical layout tool](https://quantum-journal.org/papers/q-2026-06-15-2135/)

- **arXiv preprint:**  
  [arXiv:2501.14957](https://arxiv.org/abs/2501.14957)

### Citation

> Myers, J., Caron, C., Helaly, N., Wei, Z., Oh, J., Gotobed, Z., Yabe, K., & Niffenegger, R. J.  
> *Qubit operations using a modular optical system engineered with PyOpticL: a code-to-CAD optical layout tool*.  
> Quantum **10**, 2135 (2026).

## About PyOpticL (Python Optics Layout)

PyOpticL (Python Optical Layout) is a code-to-CAD tool for optical design that combines automatic beam-path routing with CAD generation. Optical components are placed directly along simulated beam paths, enabling automatic routing, dynamic layouts, and modular optical system design without hard-coded coordinates. This enables modular optical engineering from baseplates to subsystems to a full apparatus.

<img src="https://github.com/user-attachments/assets/b24b1d63-7b17-4de1-95dd-dcf176b8d9d6" width=400>


### [UMass Amherst Trapped Ion system built with PyOpticL](https://websites.umass.edu/rniffenegger/pyopticl-code-to-cad-optical-layout/):
<a href="https://github.com/UMassIonTrappers/PyOpticL/wiki/Apparatus-%E2%80%90-Trapped-Ions-%E2%80%90-Strontium">
	<img width="700" alt="UMass Amherst Trapped Ions" src="https://github.com/user-attachments/assets/2b61827e-5624-4590-b8a4-2e94640a9535" />
</a>

### Modular abstraction: Optics → Baseplates → Subsystems → Apparatus:
<img width="700" alt="Abstraction" src="https://github.com/user-attachments/assets/1b857ff6-a425-4261-a6f4-b00795de6f05" />

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

<img width="300" src="https://github.com/user-attachments/assets/b3237dba-d979-49b2-821d-6eaf26edf847" />

### Modular Subsystems based on baseplates:
* [Laser Cooling and Detection](https://github.com/UMassIonTrappers/PyOpticL/wiki/Subsystem-‐-Laser-Cooling-and-Detection)
* [Raman Zeeman qubit](https://github.com/UMassIonTrappers/PyOpticL/wiki/Subsystem-%E2%80%90-Raman)
* [Photoionization](https://github.com/UMassIonTrappers/PyOpticL/wiki/Subsystem-%E2%80%90-Photoionization-Laser)
* [State Preparation and Measurement](https://github.com/UMassIonTrappers/PyOpticL/wiki/Subsystem-%E2%80%90-SPAM)

<img width="300" alt="image" src="https://github.com/user-attachments/assets/d0d951dc-ae7c-4db3-a713-b24ece516477" />

### Apparatus based on modular subsystems:
* [Trapped Ions - Strontium](https://github.com/UMassIonTrappers/PyOpticL/wiki/Apparatus-%E2%80%90-Trapped-Ions-%E2%80%90-Strontium)
* [Trapped Ions - Calcium](https://github.com/UMassIonTrappers/PyOpticL/wiki/Apparatus-%E2%80%90-Trapped-Ions-%E2%80%90-Calcium)
* [Project Redstone](https://github.com/UMassIonTrappers/PyOpticL/wiki/Apparatus-%E2%80%90-Quantum-Optics-%E2%80%90-Project-Redstone)

<img width="300" src="https://github.com/user-attachments/assets/1fd957f5-4196-419c-a6ce-1ff5015ce9ec" />

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
