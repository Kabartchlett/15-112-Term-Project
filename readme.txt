#Author: Kevin Bartchlett
#Email: kbartchl@andrew.cmu.edu

This project is an attempt to recreate the basics of Mario Kart. The game is developed
in 3D using Panda3D (python). It can also be controlled by a handmade controller with an accelerometer tilting device.


In Order to run my program: 
	(First make sure you have all of the files) 
		Is there a folder called “All_Tracks” and a folder called “Images”?
			If yes you should have all the files need to load the game
	If all files are there, go to “CurrentProject/Project/main.py”
		I configured my sublime Text Editor to run Python and then CMD B to build the game
		
		



Libraries:

Uses Panda3d to generate the environment and have the game mode played
	Files are included in the folder “Panda3D”
	Install: 
		As noted by the TPInstall folder from 112 TAs 
		https://drive.google.com/drive/folders/0BxDuZsVP9TXlTjQ3ZTROM1JwMk0

		“
		Panda3D Installation Guide:

		Windows:
		1) Go to https://www.panda3d.org/download.php?sdk
		2) Click whatever version of Panda3D you want (probably the most recent version).
		3) Go to the Microsoft Windows download page.
		4) Download the "Panda3D Installer for Windows" .exe file
			-get the 64-bit version if its compatible with your computer
		5) Run the executable file that downloads. This should pull up the setup wizard!
			-decide where to install panda3D. It doesn't matter where you put it, as long
			 as you can find it later
		6) Click "Install"

		Mac:
		1) Go to https://www.panda3d.org/download.php?sdk
		2) Click whatever version of Panda3D you want (probably the most recent version).
		3) Go to the Mac OS X download page.
		4) Download the "Panda3D Installer for Mac OSX" .dmg file
		5) Run the executable file that downloads. This should pull up the setup wizard!
			-decide where to install panda3D. It doesn't matter where you put it, as long
			 as you can find it later
		6) Click "Install"

		”

Uses DirectGUI to create the UI interface
	DirectGUI is a library within panda3D. No install needed

Uses Pyserial to read a constant serial read and use the information in python
	Documentation to install is: http://pyserial.readthedocs.io/en/latest/pyserial.html
	Link to the actual install here: https://github.com/pyserial/pyserial
	Files are included in folder called Pyserial

Uses an Arduino hardware and sketch file to create the controller and constantly read input
	Arduino is a micro controller that has open source framework
	To install the program called Sketch which will enable you to program and read the micro controller through serial port
	visit this link: https://www.arduino.cc/en/Main/Software
	and install for your computer. Open up a blank sketch file, click on file —> open and select the arduino sketch in
	the folder “arduino” and name “marioSensorData” 
	With hardware plugged in to a usb port, check Tools and that port has a value 
	(copy this value such as: “'/dev/tty.usbmodem1421’”) for inputting into the Python main.py file later
	Also on Tools check board and change it to Arduino Mega
	Top left of the sketch file hit the Upload button to load the sketch to the controller (though it doesn’t need it) 
	Hit Top Right to open Serial monitor to test the controller is working
	Back to main.py (found in folder currentProject) CMD or Control F and type serial.Serial 
		enter the value that was copied early and run that python file to use the controller



