<img src="https://github.com/user-attachments/assets/d20bf57a-f602-48b8-b033-8d03141b6e97" width=300>

## PyOpticL - Code-to-CAD optical system engineering

![image](https://github.com/user-attachments/assets/780dbadd-5971-4b00-a471-07538e7d65ba)

#### Discord Server: https://discord.gg/y8aqDe8RxN

<!-- Trapped Ion quantum computer at UMass Amherst engineered with PyOpticL: -->
<!-- <img src="https://github.com/user-attachments/assets/1dbe2986-20e2-4f4e-9b4c-00dd31a4b656" width=50%> -->

### ReadMe
* [Library Features and Information](https://github.com/UMassIonTrappers/PyOpticL#about-pyopticl-python-optics-layout)
* [Installation Guide](https://github.com/UMassIonTrappers/PyOpticL#getting-setup)

### Wiki
* [Quickstart Guide](https://github.com/UMassIonTrappers/PyOpticL/wiki#quickstart-guide)
* [Model Import Guide](https://github.com/UMassIonTrappers/PyOpticL/wiki#model-import-guide)
  
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
 * UC Berkeley
 * Stanford
 * Quera

![image](https://github.com/user-attachments/assets/d3b5ad85-33ed-4655-9377-891c7e96972d)


#### Again we thank the MIT QUANTA LAB for sharing their C4PO ('CAD for Precision Optics') based on OpenSCAD which inspired this library.
