# FreeCAD Mini Optics

### Based on MIT QUANTA LAB repo - C4PO ('CAD for Precision Optics') which is written for OpenSCAD

This port is motivated by FreeCADs ability to utilize python libraries, and utilize custom worbenches.
This repository contains a custom optics workbench for freecad which allows for the creation of optical layouts through python scripting.
Once created, freecad also facilitates the ability to easily view and modify the baseplate for testing.
Lastly, GUI functions are also integrated into the workbench, allowing for easy toggling of component visibility, export to stl, etc.

## Features

### Beam Simulation
A primary feature of this project is the automated simulation of beam paths for designed baseplates.
To simulate a beam path, an incomming beam can be added to the script and the path of the beam will be calculated automatically taking into account all components on the baseplate. This calculation includes reflection, transmission, refraction, and diffraction (limited).

Taking advantage of this functionality, optical components can also be defined *along* the beam path at some distance from the last component rather than by absolute position. This allows for very intuitive and efficient scripting of baseplates as well as ease in creation of dynamic and parameterized designs.

The beam path function tracks reflections through PBS and pick offs using a binary encoding where a transmission is represented by a bitwise left shift and reflection is represented by a bitwise left shift plus one. For example if the incomming beam has index 1, the two beams that result from a split are named 0b10 (transmission) and 0b11 (reflection)

### Workbench Functions
Only a few GUI functions are currently integrated into the optics workbench, but there is potential for many more.
Current functions include:
**Recalculate Beam Path** - useful to check beam paths when applying in-editor modifications  
**Toggle Component Visibility** - easily hide all beams and components  
**Export STLs** - export all baseplates and adapter components to STL for fabrication  
**Auto-Fit Top View** - quickly switch to a fitted top down view

These functions can also be scripted into macros for applications such as auto-exporting when the macro is run.

### 'Universal' Mirror Mounts
Polaris mirrors are expensive. To tryout other mount options you can use universal mirror mount adapters. These adapters allow you create a single baseplate that can accommodate multiple different mirrors, even if they require drastically different mounting holes or even different mounting heights. Simply specify the dimentions and position offset of universal mount that fits the range of mirrors you want to try and you can generate a version of that mount for any of the mirrors, all with the same baseplate drilling.

## Examples

A double pass AOM scripted purely using along-beam component placement. This modular double pass AOM baseplate is small enough to print on a resin 3D printer:

![image](https://user-images.githubusercontent.com/103533593/226716244-0ecad33d-71e4-46a8-a218-f00bf779ac8a.png)

![image](https://user-images.githubusercontent.com/103533593/226716319-9bad9d81-a907-4680-9812-3d6e7ccdd8c4.png)

Modular designs are stackable and independent:

![image](https://user-images.githubusercontent.com/103533593/225907411-c28c953b-345c-4921-9965-d5707ece66d7.png)

Example of the beam angle being deliberately skewed, causing the subsequent optics to shift as well:
![image](https://user-images.githubusercontent.com/103533593/225908758-4c196c09-486d-4347-9094-3af1f606a397.png)

3D printed prototype before getting an aluminum plate machined:
![image](https://user-images.githubusercontent.com/103533593/225912508-68dd4000-5342-4b57-9fbf-bde178d6664b.png)

The same universal mirror mount for three mirrors:

![image](https://user-images.githubusercontent.com/103533593/226721943-3984bdcd-9abe-4df4-a6c2-102d04fe3eb1.png)
![image](https://user-images.githubusercontent.com/103533593/226722031-bafe2a32-d902-4fc2-bf7d-2c830fe7318f.png)
![image](https://user-images.githubusercontent.com/103533593/226722154-ab0ab1ce-a737-48ac-afea-57c727d85642.png)
![image](https://user-images.githubusercontent.com/103533593/226722557-86e42a58-b71e-4d6f-b20a-2aa73beaa77e.png)


## Getting Setup
There are a few important things to ensure before you can use the FreeCAD for optics packages:

1. Install FreeCAD, Python, and Git

2. Clone the GitHub repo into your FreeCAD user folder
	On windows, in a terminal run:  
	```cd "C:\Users\<username goes here>\AppData\Roaming\FreeCAD```  
	```git init -b main```  
	```git remote add origin "https://github.com/UMassIonTrappers/FreeCAD.git``` 
	```git config --global --add safe.directory C:/Users/<username goes here>/AppData/Roaming/FreeCAD``` 
	```git pull origin main```  
		
To check everything is setup correctly, should now be able to launch FreeCAD and see the "Optics" workbench in the dropdown

![image](https://user-images.githubusercontent.com/103533593/226724665-77b05f5b-1faa-43ca-9329-f6a0894ec1fc.png)


Example of a MWE baseplate:

````
layout.place_element_along_beam("Input_Mirror_1", optomech.mirror_mount_k05s2, beam, 0b1, up_right, 15)
layout.place_element_along_beam("Input_Mirror_2", optomech.mirror_mount_k05s2, beam, 0b1, right_up,  INCH)
layout.place_element_along_beam("Half_waveplate", optomech.rotation_stage_rsp05, beam, 0b1, up, 55)
layout.place_element_along_beam("Beam_Splitter", optomech.pbs_on_skate_mount, beam, 0b1, up, 25)

layout.place_element_along_beam("AOM_R2", optomech.isomet_1205c_on_km100pm_doublepass, beam, 0b11, right, 30)
layout.place_element_along_beam("Quarter_waveplate", optomech.rotation_stage_rsp05, beam, 0b11, left, 45)
layout.place_element_along_beam("f_75_Collimation_Lens", optomech.lens_holder_l05g, beam, 0b11, left, 30)
layout.place_element_along_beam("Iris", optomech.pinhole_ida12, beam, 0b11, left, 10)
layout.place_element_along_beam("Retro_Mirror", optomech.mirror_mount_k05s2, beam, 0b11, right, 10)

layout.place_element_along_beam("Output_Mirror_1", optomech.mirror_mount_k05s2, beam, 0b110, right_down, 20)
# layout.place_element_along_beam("Iris", optomech.pinhole_ida12, beam, 0b110, down, 25)
layout.place_element_along_beam("Output_Mirror_2", optomech.mirror_mount_k05s2, beam, 0b110, down_left, 55)
layout.place_element_along_beam("Half_waveplate_Out", optomech.rotation_stage_rsp05, beam, 0b110, left, 100)
layout.place_element_along_beam("Output_Fiberport", optomech.fiberport_holder, beam, 0b110, right, y=0)

offset = 0
layout.place_element("Mount_Hole", optomech.baseplate_mount, (2-offset)*INCH-gap/2, (1-offset)*INCH-gap/2, 0)
layout.place_element("Mount_Hole", optomech.baseplate_mount, (4-offset)*INCH-gap/2, (1-offset)*INCH-gap/2, 0)
layout.place_element("Mount_Hole", optomech.baseplate_mount, (3-offset)*INCH-gap/2, (4-offset)*INCH-gap/2, 0)
layout.place_element("Mount_Hole", optomech.baseplate_mount, (3-offset)*INCH-gap/2, (6-offset)*INCH-gap/2, 0)
layout.place_element("Mount_Hole", optomech.baseplate_mount, (2-offset)*INCH-gap/2, (7-offset)*INCH-gap/2, 0)
````
