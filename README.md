##INSTALL INSTRUCTIONS

NOTE: inpout32.dll file is required in experiment folder (driver file) to send parallel port triggers

INSTALL - presentation PC:
  - download and install standalone version of psychopy: https://www.psychopy.org/download.html
    --> run scripts from built-in python instance
  - ALTERNATIVE: install psychopy via pip:
      - install python 3.6
      - setup SWIG (this is necessary to install pyWinhook that is a dependency for psychopy)
        -download swig
        -extract zip content
        -set environment variable to swig.exe folder (requires visual studio c++ build tolls) (visual studio build tools 2019)
        -restart cmd window
      - note: I also had to adapt environment variables and remove visual studio reference of python 3.6 install in system path
      - optional: pip install h5py - to read HDF5 files that are written by iohub for the eyetracking data
      - py -m pip install --upgrade pip
      - pip install psychopy

##TODO

BUGS: laptop - double duration of ISI in oddball phase - does not occur on PC

- define display

- integrate Tobii SDK
  - implement calibration (via Eyetrackingmanager?)
  - add tracker.trackerTime to trial table

- test auditory oddball task
  --> check matching of hdf5 and trial_data for real eye_tracking data
        - check tracker.trackerTime in trial-data can it be matched
  --> sanity check of trial data especially variables - see dataset 123_2022-04-14-1548

- implement testmode for ET + trigger sending --> test it on Laptop

##TODO ANNA:

- test timings of trigger sending   --> save timestamp for sent trigger in trial data?
- which triggers are not necessary?
- check different time values - which can be matched with actual eye tracker data

- program visual oddball task
  --> first: response on oddball with fast keypress
    - determine median response time

##NOTES:

- do automatic conversion of visual angle to pixels in script: https://elvers.us/perception/visualAngle/

- rather install psychopy standalone on presentation PC ---
  see: https://www.psychopy.org/recipes/appFromScript.html
  --> run script via standalone from prompt: https://discourse.psychopy.org/t/run-psychopy-experiment-without-opening-builder/9290
    --> path to standalone python install: C:\Users\stimulation\AppData\Local\Programs\PsychoPy\python.exe
    ---> CMD to rund script: C:\Users\stimulation\AppData\Local\Programs\PsychoPy\python.exe C:\Users\stimulation\Desktop\project_py_oddball_280322\auditory_oddball.py

- send parallel port trigger: https://psychopy.org/api/parallel.html
  --> send trigger --> C:\Users\stimulation\AppData\Local\Programs\PsychoPy\python.exe C:\Users\stimulation\Desktop\project_py_oddball_280322\test_parallelport.py
  --> see: https://stackoverflow.com/questions/26762015/psychopy-sending-triggers-on-64bit-os/26889541#26889541
  ---> see also: https://osdoc.cogsci.nl/3.3/manual/devices/parallel/#windows-7-32-and-64-bit

-  port = parallel.ParallelPort(0x03FF8) #dont quote it - CAVE: correct port needs to be identified
  - use standalone "Parallel Port Tester programm"
  - set all pins to low
  - port.setData(0)

- data stored in hdf5 file - when mouse used as eyetracker
    #import h5py
    #acess data: dset1 = f['data_collection/events/eyetracker/MonocularEyeSampleEvent']
