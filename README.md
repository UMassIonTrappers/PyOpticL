# FreeCAD Mini Optics

## Based on MIT QUANTA LAB repo - C4PO ('CAD for Precision Optics') which is written for OpenSCAD

This port is motivated by FreeCADs ability to utilize python libraries.

For instance, python allows a function to track beam paths within the optics layout.

Beam path function tracks reflections through PBS and pick offs using a binary encoding
eg. two beams from a PBS are named 0b00 (transmission) and 0b01 (reflection)
Allows unique beam tracking even through a double pass AOM. This modular double pass AOM baseplate is small enough to print on a resin 3D printer:

![image](https://user-images.githubusercontent.com/103533593/225905737-54318378-d2fa-444c-aab7-e172df4a0bad.png)

![image](https://user-images.githubusercontent.com/103533593/225906192-615caded-70e3-43de-a46f-c5aa9236dd25.png)

Modular designs are stackable and independent:

![image](https://user-images.githubusercontent.com/103533593/225907411-c28c953b-345c-4921-9965-d5707ece66d7.png)


Optics can be placed ALONG the beam path and follow it. For example if the beam angle is deliberately skewed, the subsequent optics shift as well:
![image](https://user-images.githubusercontent.com/103533593/225908758-4c196c09-486d-4347-9094-3af1f606a397.png)

3D printed prototype before getting an aluminum plate machined:
![image](https://user-images.githubusercontent.com/103533593/225912508-68dd4000-5342-4b57-9fbf-bde178d6664b.png)

Universal mirror mounts:
Polaris mirrors are expensive. To tryout other mount options you can use 'universal' mirror mount adapters:
![image](https://user-images.githubusercontent.com/103533593/225914594-f241deee-e438-4b53-9f5f-39edc5ba4fc9.png)
![image](https://user-images.githubusercontent.com/103533593/225914625-2159fe6f-c0bc-4131-9200-ce152fada791.png)


Getting Setup:
There are a few important things to ensure before you can use the FreeCAD for optics packages:

	1. Install FreeCAD, Python, Git, and Visual Studio Code
	
	2. Clone the GitHub repo into your FreeCAD user folder
		○ On windows, in a terminal run:
		○ cd "C:\Users\<username goes here>\AppData\Roaming\FreeCAD"
		○ git init -b main
		○ git remote add origin "https://github.com/UMassIonTrappers/FreeCAD.git"
			§ May need to  - git config --global --add safe.directory C:/Users/<username goes here>/AppData/Roaming/FreeCAD
		○ git pull origin main
		
	• In VS Code, add a ".env" file that appends the FreeCAD and optics package info to the python path
		○ For windows it will look like this:
		FREECAD_BIN=C:\Program Files\FreeCAD 0.20\bin
		FREECAD_LIB=C:\Program Files\FreeCAD 0.20\lib
		FREECAD_MOD=C:\Program Files\FreeCAD 0.20\Mod
		FREECAD_EXT=C:\Program Files\FreeCAD 0.20\Ext
		FREECAD_STUBS=C:\Users\<username goes here>\AppData\Local\Programs\Python\Python310\Lib\site-packages\FreeCAD-stubs
		FREECAD_MODULES=C:\Users\<username goes here>\AppData\Roaming\FreeCAD\Mod\Optics
		PYTHONPATH=${FREECAD_BIN};${FREECAD_LIB};${FREECAD_MOD};${FREECAD_EXT};${FREECAD_STUBS};${FREECAD_OPTICS};${PYTHONPATH}
		
You should now be fully setup to start using the FreeCAD for optics packages

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
