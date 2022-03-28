# CAMTRACK

## Project
Camtrack is a prototype of autonomous tracking, it is able to follow an object defined in a completely autonomous way having a random trajectory. 
This object can also present variations of speeds more or less slow.
For further informations : https://www.linkedin.com/feed/update/urn:li:activity:6909494638844276736/

## Installation
Download following librairies in Python:
tkinter, pandas, serial, opencv

## Usage
First open and upload motors.ino on the Camtrack arduino card and remain it connected to your PC.
Then, run the pyhton script rproject.py to access the Camtrack interface, don't foregt to connect the external camera to your computer.
You can now start the tracking by clicking on the "Start" button.
You can now see on your PC screen a red circle indicating the position of the object, move it and you will see Camtrack correct automatically its inclination to follow it.
If you want to stop the track click on the "Stop" button.
In case of an error, a pop up will be displayed, close it and you can restart a tracking.
You can restart as many times as you want different trackings, if you want to quitt the app, click on the "Quitt" button.
