# Oddball Tasks

## Overview
This study consists of two oddball tasks:
* an Auditory Oddball Task (auditory_oddball.py)
* a Visual Oddball Task (visual_oddball.py)

During both tasks, pupil dilation is measured via eye tracker and parallel port triggers are sent to an EEG recording PC. Several baseline phases are used to determine tonic pupil size. 

## Install Instructions
NOTE: inpout32.dll file is required in experiment folder (driver file) to send parallel port triggers

Rather install psychopy standalone on presentation PC, see: https://www.psychopy.org/recipes/appFromScript.html -> run script via standalone from prompt: https://discourse.psychopy.org/t/run-psychopy-experiment-without-opening-builder/9290 -> path to standalone python install: C:\Users\stimulation\AppData\Local\Programs\PsychoPy\python.exe -> CMD to rund script: C:\Users\stimulation\AppData\Local\Programs\PsychoPy\python.exe C:\Users\stimulation\Desktop\project_py_oddball_280322\auditory_oddball.py

Install presentation PC:
  * download and install standalone version of psychopy: https://www.psychopy.org/download.html
    --> run scripts from built-in python instance
  * ALTERNATIVE: install psychopy via pip:
      * install python 3.6
      * setup SWIG (this is necessary to install pyWinhook that is a dependency for psychopy)
        -download swig
        -extract zip content
        -set environment variable to swig.exe folder (requires visual studio c++ build tolls) (visual studio build tools 2019)
        -restart cmd window
      * note: I also had to adapt environment variables and remove visual studio reference of python 3.6 install in system path
      * optional: pip install h5py - to read HDF5 files that are written by iohub for the eyetracking data
      * py -m pip install --upgrade pip
      * pip install psychopy

## Monitor and Display Settings
Monitor parameters are adapted to the presentation PC. The name is saved with psychopy monitor manager. Please note:
* avoid integrated graphics for experiment computers wherever possible as no accurate frame timing
* set Windows scaling to 100% - otherwise onscreen units will not get right
* experiment screen will be FUllHD, thus testscreen is specified accordingly
Screen resolution is 1920/1080.

## Parallel Port
send parallel port trigger: https://psychopy.org/api/parallel.html -> send trigger -> C:\Users\stimulation\AppData\Local\Programs\PsychoPy\python.exe C:\Users\stimulation\Desktop\project_py_oddball_280322\test_parallelport.py -> see: https://stackoverflow.com/questions/26762015/psychopy-sending-triggers-on-64bit-os/26889541#26889541 -> see also: https://osdoc.cogsci.nl/3.3/manual/devices/parallel/#windows-7-32-and-64-bit.

*port = parallel.ParallelPort(0x03FF8)*
**Don't quote this setting!** <br/>The correct port needs to be identified (use standalone "Parallel Port Tester programm" -> set all pins to low -> port.setData(0))

## Eyetracking
* difference to psychopy documentation required: Define name as tracker and define a presentation window before.
* in case testmode = True: the mouse is used as eyetracker and data stored in hdf5 file: -> import h5py -> acess data: dset1 = f['data_collection/events/eyetracker/MonocularEyeSampleEvent']

## The Auditory Oddball Task
The task is used to manipulate Locus-Coeruleus-Norepinephrine (LC-NE) activity. A frequent tone is presented with a probability of 80% while an infrequent tone of a different pitch (oddball) is presented with a probability of 20%. The task contains a manipulation according to Mather et al., 2020. 

### Task sequence
1. instruction slide 1
2. baseline calibration
3. oddball block
4. baseline phase
5. oddball block
6. baseline phase
7. instruction slide 2
8. manipulation block
9. baseline phase
10. oddball block
11. baseline phase
12. oddball block
13. baseline phase

For yellow: Luminance of manipulation stimuli is matched. Luminance formula: 0.3 R + 0.59 G + 0.11 B -> 0.2 + 0.1 -> luminance = = 0.119; see:  https://www.w3.org/TR/AERT/#color-contrast.
For blue: Luminance matched to squeeze; luminance formula: 0.3 R + 0.59 G + 0.11 B --> luminance = 0.11; see: https://www.w3.org/TR/AERT/#color-contrast.

## The Visual Oddball Task
The task is used and to observe effects of task utility and stimulus salience. It contains independent manipulations of both. A frequent purple circle is presented with a probability of 80% while an infrequent smaller purple circle (oddball) is presented with a probability of 20%. 

### Task sequence
1. ...

### Annotations
* automatic conversion of visual angle to pixels in script: *size_fixation_cross_in_pixels = 132* also defines standard stimulus size and translates to 3.2 degrees visual angle on 24 inch screen with 25.59 inches screen distance (see https://elvers.us/perception/visualAngle/)
* *high_salience_ball_size = round(0.5 * size_fixation_cross_in_pixels)* translates to 1.6 degrees visual angle on 24 inch screen with 25.59 inches screen distance.
* *low_salience_ball_size = round(0.91 * size_fixation_cross_in_pixels)* translates to 2.9 degrees visual angle on 24 inch screen with 25.59 inches screen distance.
