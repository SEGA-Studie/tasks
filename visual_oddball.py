'''VISUAL ODDBALL TASK'''
# For further information see README.md.

'''LOAD MODULES'''
# PsychoPy modules
from matplotlib.pyplot import draw
from psychopy import visual, core, event, clock, data, gui, monitors, parallel
from psychopy.tools.filetools import fromFile, toFile
# Core libraries
import random, time, sys, numpy
# For controlling eyetracker and eye-tracking SDK
import tobii_research
from psychopy.iohub import launchHubServer
from psychopy.core import getTime, wait
# For getting keyboard input
from psychopy.hardware import keyboard
# Library for managing paths
from pathlib import Path
# Miscellaneous
from os import environ #hide messages in console from pygame
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1' #hide messages in console from pygame

#from auditory_oddball import send_trigger
print("This is visual oddball")

'''SETUP'''
# Path to output data:
path_to_data = Path("Desktop", "tasks", "data", "visual_oddball").resolve()
trials_data_folder = Path(path_to_data, 'trialdata')
eyetracking_data_folder = Path(path_to_data, 'eyetracking')

print(trials_data_folder)
print(eyetracking_data_folder)

# Testmode.
# TRUE mimicks an eye-Ttracker by mouse movement, FALSE = eye-tracking hardware is required.
testmode = False

# Experimental settings:
presentation_screen = 0 # stimuli are presented on internal screen 0.
number_of_repetitions = 2
number_of_practice_trials = 25
stimulus_duration_in_seconds = 0.075
standard_ball_color = (128, 0, 128) # purple
size_fixation_cross_in_pixels = 60
standard_ball_size = size_fixation_cross_in_pixels
high_salience_ball_size = round(0.5 * size_fixation_cross_in_pixels)
low_salience_ball_size = round(0.91 * size_fixation_cross_in_pixels)
ISI_interval = [1800, 2000]
gaze_offset_cutoff = 2 * size_fixation_cross_in_pixels
background_color_rgb = (0, 0, 0) # grey
white_slide = 'white'
black_slide = 'black'
baseline_duration = 1
#  After 500ms the no data detection warning should be displayed on screen.
no_data_warning_cutoff = 0.5
# One baseline assessment (black and white screen) at the beginning of the experiment.
baseline_calibration_repetition = 1
# Settings are stored automatically for each trial.
settings = {}

#EEG trigger variables
pulse_duration = 0.01 #10ms duration of trigger signal
#dont quote it - CAVE: correct port needs to be identified - use standalone "Parallel Port Tester programm" to identify it
parallel_port_adress = 0x03FF8

# Presenting a dialog box. Infos are added to "settings".
# id = 123 is used as default testing value.
settings['id'] = 123
settings['group'] = ['ASD', 'TD']
dlg = gui.DlgFromDict(settings,title='visual oddball')
if dlg.OK:
    print('EXPERIMENT IS STARTED')
else:
    core.quit()  # the user hit cancel so exit

# Name for output data.
fileName = str(settings['id']) + '_' + data.getDateStr(format="%Y-%m-%d-%H%M")

# Experiment handler saves experiment data automatically.
exp = data.ExperimentHandler(
    name="visual_oddball",
    version='0.1',
    extraInfo = settings, #experiment info
    dataFileName = str(trials_data_folder / fileName), # where to save the data
    )
str(trials_data_folder / fileName),

# Monitor parameter are adapted to presentation PC.
# Name is saved with psychopy monitor manager.
# Distance is from screen in cm.
mon = monitors.Monitor(
    name = 'eizo_eyetracker',
    width = 29.6,
    distance = 65) 

# Create display window.
# Unit was changed to pixel so that eye tracker outputs pixel on presentation screen.
mywin = visual.Window(
    size=[1920,1080],
    fullscr=True,
    monitor=mon,
    color = background_color_rgb,
    screen=presentation_screen,
    units="pix") 

# Get monitor refresh rate in seconds:
refresh_rate = mywin.monitorFramePeriod 
print('monitor refresh rate: ' + str(round(refresh_rate, 3)) + ' seconds')

# SETUP EYETRACKING
# Difference to psychopy documentation required: - define name as tracker - define presentation window before.
# Output gazeposition is alwys centered, i.e. screen center = [0,0].
if testmode:
    print('mouse is used to mimic eyetracker...')
    iohub_config = {'eyetracker.hw.mouse.EyeTracker': {'name': 'tracker'}}
if not testmode:
    # Search for eye tracker:
    found_eyetrackers = tobii_research.find_all_eyetrackers()
    my_eyetracker = found_eyetrackers[0]
    print("Address: " + my_eyetracker.address)
    print("Model: " + my_eyetracker.model)
    print("Name (It's OK if this is empty): " + my_eyetracker.device_name)
    print("Serial number: " + my_eyetracker.serial_number)

    # Define a config that allows iohub to connect to the eye-tracker:
    iohub_config = {'eyetracker.hw.tobii.EyeTracker':
        {'name': 'tracker', 'runtime_settings': {'sampling_rate': 300, }}}

# IOHUB creates a different instance that records eye tracking data in hdf5 file saved in datastore_name:
io = launchHubServer(**iohub_config,
                        experiment_code = str(eyetracking_data_folder),
                        session_code = fileName,
                        datastore_name = str(eyetracking_data_folder / fileName), #where data is stored
                        window = mywin)

# Call the eyetracker device and start recording:
tracker = io.devices.tracker
tracker.setRecordingState(True)

#SETUP PARALLEL PORT TRIGGER
# List position defines trigger value that is sent, see function send_trigger(),
# i.e. list position 2 will send a trigger with value "S2".
trigger_name_list = ['PLACEHOLDER', #0
                     'trial', #1 -
                     'stimulus', #2 -
                     'ISI', #3 -
                     'baseline', #4 -
                     #'manipulation_squeeze', #5 -
                     #'manipulation_relax', #6 -
                     'experiment_start', #7 -
                     'experiment_end', #8 -
                     'pause_initiated', #9 -
                     'pause_ended', #10 -
                     'experiment_aborted', #11 -
                     'baseline_calibration', #12 -
                     'baseline_whiteslide', #13 -
                     'baseline_blackslide', #14 -
                     'oddball_block', #15 -
                     'manipulation_block'
                     ] #16 -

print(trigger_name_list)

# Find a parallel port:
if not testmode:
    # Don't quote it. Correct port needs to be identified. Use standalone "Parallel Port Tester programm".
    port = parallel.ParallelPort(parallel_port_adress) 
    # Set all pins to low, otherwise no triggers will be sent.
    port.setData(0)

# SETUP KEYBOARD
kb = keyboard.Keyboard()

'''FUNCTIONS'''
# Send a trigger to EEG recording PC via parallel port:
def send_trigger(trigger_name):
    trigger_name_found = False
    for i in trigger_name_list:
        if i == trigger_name:
            trigger_value = trigger_name_list.index(trigger_name)
            trigger_byte = f'{trigger_value:08b}'
            if not testmode:
                port.setPin(2, int(trigger_byte[7]))
                port.setPin(3, int(trigger_byte[6]))
                port.setPin(4, int(trigger_byte[5]))
                port.setPin(5, int(trigger_byte[4]))
                port.setPin(6, int(trigger_byte[3]))
                port.setPin(7, int(trigger_byte[2]))
                port.setPin(8, int(trigger_byte[1]))
                port.setPin(9, int(trigger_byte[0]))
                #wait for pulse duration
                time.sleep(pulse_duration)
                port.setData(0)
            if testmode:
                print('sent DUMMY trigger S' + str(trigger_value))
            trigger_name_found = True
    if not trigger_name_found:
         print('trigger name is not defined: ' + trigger_name)

# Draw instruction slide 1:
def draw_instruction1(background_color = background_color_rgb):
    if background_color is not background_color_rgb:
        background_rect = visual.Rect(win=mywin, size=mywin.size, fillColor= background_color)
        background_rect.draw()

    instruction1 = visual.TextStim(
        win = mywin,
        text = "Das Experiment beginnt jetzt.\nBitte bleibe still sitzen und\nschaue auf das Kreuz in der Mitte.\n\n Weiter mit der Leertaste.",
        color = 'black',
        units = 'pix',
        wrapWidth = 900,
        height = size_fixation_cross_in_pixels)
    instruction1.draw()

# Draw instruction slide 2:
def draw_instruction2(background_color = background_color_rgb):
    if background_color is not background_color_rgb:
        background_rect = visual.Rect(win=mywin, size=mywin.size, fillColor= background_color)
        background_rect.draw()

    instruction2 = visual.TextStim(
        win = mywin,
        text = "Gleich startet die Übung.\nEs werden Kreise auf dem Bildschirm erscheinen. Bitte drücke bei auffälligen Kreisen so schnell wie möglich die Leertase.",
        color = 'black',
        units = 'pix',
        wrapWidth = 900,
        height = size_fixation_cross_in_pixels)
    instruction2.draw()

# Draw instruction slide 3:
def draw_instruction3(background_color = background_color_rgb):
    if background_color is not background_color_rgb:
        background_rect = visual.Rect(win=mywin, size=mywin.size, fillColor= background_color)
        background_rect.draw()

    instruction2 = visual.TextStim(
        win = mywin,
        text = "Die Übung ist jetzt beendet.\nBitte bleibe weiterhin still sitzen. Gleich geht es mit der Aufgabe los.",
        color = 'black',
        units = 'pix',
        wrapWidth = 900,
        height = size_fixation_cross_in_pixels)
    instruction2.draw()

# Draw fixation cross from lines:
def draw_fixcross(background_color=background_color_rgb):

    if background_color is not background_color_rgb:
        background_rect = visual.Rect(win=mywin, size=mywin.size, fillColor= background_color)
        background_rect.draw()

    line1 = visual.Line(win=mywin, units='pix', lineColor='black') #define line object
    line1.start = [-(size_fixation_cross_in_pixels/2), 0]
    line1.end = [+(size_fixation_cross_in_pixels/2), 0]
    line2 = visual.Line(win=mywin, units='pix', lineColor='black') #define line object
    line2.start = [0, -(size_fixation_cross_in_pixels/2)]
    line2.end = [0, +(size_fixation_cross_in_pixels/2)]
    line1.draw()
    line2.draw()

# Draw figure - when gaze is offset - for gaze contincency:
def draw_gazedirect(background_color=background_color_rgb):
        # Adapt background according to privuded "background color"
    if background_color is not background_color_rgb:
        background_rect = visual.Rect(win=mywin, size=mywin.size, fillColor= background_color)
        background_rect.draw()
    # Parameters:
    function_color = 'red'
    arrow_size_pix = size_fixation_cross_in_pixels
    arrow_pos_offset = 5
    width = 3

    rect1 = visual.Rect(
        win=mywin,
        units='pix',
        lineColor=function_color,
        fillColor = background_color_rgb,
        lineWidth=width,
        size = size_fixation_cross_in_pixels*6)

    # Arrow left:
    al_line1 = visual.Line(win=mywin, units='pix', lineColor=function_color, lineWidth=width)
    al_line1.start = [-(arrow_size_pix*arrow_pos_offset), 0]
    al_line1.end = [-(arrow_size_pix*arrow_pos_offset-arrow_size_pix), 0]
    al_line2 = visual.Line(win=mywin, units='pix', lineColor=function_color, lineWidth=width)
    al_line2.start = [-(arrow_size_pix*arrow_pos_offset-(arrow_size_pix/2)), -arrow_size_pix/2]
    al_line2.end = [-(arrow_size_pix*arrow_pos_offset-arrow_size_pix), 0]
    al_line3 = visual.Line(win=mywin, units='pix', lineColor=function_color, lineWidth=width)
    al_line3.start = [-(arrow_size_pix*arrow_pos_offset-(arrow_size_pix/2)), +arrow_size_pix/2]
    al_line3.end = [-(arrow_size_pix*arrow_pos_offset-arrow_size_pix), 0]

    # Arrow right:
    ar_line1 = visual.Line(win=mywin, units='pix', lineColor=function_color, lineWidth=width)
    ar_line1.start = [+(arrow_size_pix*arrow_pos_offset), 0]
    ar_line1.end = [+(arrow_size_pix*arrow_pos_offset-arrow_size_pix), 0]
    ar_line2 = visual.Line(win=mywin, units='pix', lineColor=function_color, lineWidth=width)
    ar_line2.start = [+(arrow_size_pix*arrow_pos_offset-(arrow_size_pix/2)), -arrow_size_pix/2]
    ar_line2.end = [+(arrow_size_pix*arrow_pos_offset-arrow_size_pix), 0]
    ar_line3 = visual.Line(win=mywin, units='pix', lineColor=function_color, lineWidth=width)
    ar_line3.start = [+(arrow_size_pix*arrow_pos_offset-(arrow_size_pix/2)), +arrow_size_pix/2]
    ar_line3.end = [+(arrow_size_pix*arrow_pos_offset-arrow_size_pix), 0]

    # Arrow top:
    at_line1 = visual.Line(win=mywin, units='pix', lineColor=function_color, lineWidth=width)
    at_line1.start = [0, +(arrow_size_pix*arrow_pos_offset)]
    at_line1.end = [0, +(arrow_size_pix*arrow_pos_offset-arrow_size_pix)]
    at_line2 = visual.Line(win=mywin, units='pix', lineColor=function_color, lineWidth=width)
    at_line2.start = [-arrow_size_pix/2, +(arrow_size_pix*arrow_pos_offset-(arrow_size_pix/2))]
    at_line2.end = [0, +(arrow_size_pix*arrow_pos_offset-arrow_size_pix)]
    at_line3 = visual.Line(win=mywin, units='pix', lineColor=function_color, lineWidth=width)
    at_line3.start = [+arrow_size_pix/2, +(arrow_size_pix*arrow_pos_offset-(arrow_size_pix/2))]
    at_line3.end = [0, +(arrow_size_pix*arrow_pos_offset-arrow_size_pix)]

    # Arrow bottom:
    ab_line1 = visual.Line(win=mywin, units='pix', lineColor=function_color, lineWidth=width)
    ab_line1.start = [0, -(arrow_size_pix*arrow_pos_offset)]
    ab_line1.end = [0, -(arrow_size_pix*arrow_pos_offset-arrow_size_pix)]
    ab_line2 = visual.Line(win=mywin, units='pix', lineColor=function_color, lineWidth=width)
    ab_line2.start = [+arrow_size_pix/2, -(arrow_size_pix*arrow_pos_offset-(arrow_size_pix/2))]
    ab_line2.end = [0, -(arrow_size_pix*arrow_pos_offset-arrow_size_pix)]
    ab_line3 = visual.Line(win=mywin, units='pix', lineColor=function_color, lineWidth=width)
    ab_line3.start = [-arrow_size_pix/2, -(arrow_size_pix*arrow_pos_offset-(arrow_size_pix/2))]
    ab_line3.end = [0, -(arrow_size_pix*arrow_pos_offset-arrow_size_pix)]

    # Draw all:
    al_line1.draw()
    al_line2.draw()
    al_line3.draw()

    ar_line1.draw()
    ar_line2.draw()
    ar_line3.draw()

    at_line1.draw()
    at_line2.draw()
    at_line3.draw()

    ab_line1.draw()
    ab_line2.draw()
    ab_line3.draw()

    rect1.draw()

# Feedback indicating that no eyes are currently detected thus eye tracking data is NA:
def draw_nodata_info(background_color=background_color_rgb):
    # Adapt background according to privuded "background color":
    if background_color is not background_color_rgb:
        background_rect = visual.Rect(win=mywin, size=mywin.size, fillColor= background_color)
        background_rect.draw()

    no_data_warning = visual.TextStim(
        win=mywin,
        text='NO EYES DETECTED!',
        color = 'red',
        units = 'pix',
        height = size_fixation_cross_in_pixels)
    no_data_warning.draw()

# Check for keypresses - used to pause and quit experiment:
def check_keypress():
    keys = kb.getKeys(['p','escape'], waitRelease=True)
    timestamp_keypress = clock.getTime()

    if 'escape' in keys:
        send_trigger('pause_initiated')
        dlg = gui.Dlg(title='Quit?', labelButtonOK=' OK ', labelButtonCancel=' Cancel ')
        dlg.addText('Do you really want to quit? - Then press OK')
        ok_data = dlg.show()  # show dialog and wait for OK or Cancel
        if dlg.OK:  # or if ok_data is not None
            send_trigger('experiment_absorded')
            print('EXPERIMENT ABORTED!')
            core.quit()
        else:
            send_trigger('pause_ended')
            print('Experiment continues...')
        pause_time = clock.getTime() - timestamp_keypress
    elif 'p' in keys:
        send_trigger('pause_initiated')
        dlg = gui.Dlg(title='Pause', labelButtonOK='Continue')
        dlg.addText('Experiment is paused - Press Continue, when ready')
        ok_data = dlg.show()  # show dialog and wait for OK
        pause_time = clock.getTime() - timestamp_keypress
        send_trigger('pause ended')
    else:
        pause_time = 0

    pause_time = round(pause_time,3)
    return pause_time

def check_nodata(gaze_position):
    if gaze_position == None:
        nodata_boolean = True
    else:
        nodata_boolean = False
    return nodata_boolean

# Get gaze position and offset cutoff.
# Then check for the offset of gaze from the center screen.
def check_gaze_offset(gaze_position):
    gaze_position = tracker.getPosition()
    gaze_center_offset = numpy.sqrt((gaze_position[0])**2 + (gaze_position[1])**2) #pythagoras theorem

    if gaze_center_offset >= gaze_offset_cutoff:
        offset_boolean = True
    else:
        offset_boolean = False
    return offset_boolean

# Fixation cross: Check for data availability and screen center gaze:
def fixcross_gazecontingent(duration_in_seconds, background_color=background_color_rgb):
    # Translate duration to number of frames:
    number_of_frames = round(duration_in_seconds/refresh_rate)
    timestamp = getTime()
    gaze_offset_duration = 0
    pause_duration = 0
    nodata_duration = 0 
    # Present cross for number of frames:
    for frameN in range(number_of_frames):
        # Check for keypress
        pause_duration += check_keypress()
        gaze_position = tracker.getPosition
        # Check for eyetracking data:
        if check_nodata(gaze_position):
            print('warning:no eyes detected')
            # Reset duration for loop, restart ISI:
            frameN = 1 
            nodata_current_duration = 0
            while check_nodata(gaze_position):
                if nodata_current_duration > no_data_warning_cutoff:
                    draw_nodata_info(background_color)
                mywin.flip()
                nodata_duration += refresh_rate
                nodata_current_duration += refresh_rate
                gaze_position = tracker.getPosition() # get new gaze data
        # Check for gaze
        elif check_gaze_offset(gaze_position):
            print('warning: gaze offset')
            # Reset duration of for loop - resart ISI:
            frameN = 1 
            while not check_nodata(gaze_position) and check_gaze_offset(gaze_position):
                # Listen for keypress:
                pause_duration += check_keypress()
                # Redirect attention to fixation cross area:
                draw_gazedirect(background_color)
                # Wait for monitor refresh time:
                mywin.flip()
                gaze_offset_duration += refresh_rate
                # Get new gaze data:
                gaze_position = tracker.getPosition() 
        # Draw fixation cross:
        draw_fixcross(background_color)
        mywin.flip()

    # Generate output info:
    actual_fixcross_duration = round(getTime()-timestamp,3)
    gaze_offset_duration = round(gaze_offset_duration,3)
    nodata_duration = round(nodata_duration,3)

    # Testing:
    print('number of frames: ' + str(number_of_frames))
    print('no data duration: ' + str(nodata_duration))
    print('gaze offset duration: ' + str(gaze_offset_duration))
    print('pause duration: ' + str(pause_duration))
    print('actual fixcross duration: ' + str(actual_fixcross_duration))
    print("timing offset:",duration_in_seconds-(clock.getTime()-timestamp)) #test timing offset

    return [actual_fixcross_duration, gaze_offset_duration, pause_duration, nodata_duration]

# Stimulus for manipulation:
def draw_ball(size):
    circle1 = visual.Circle(
        win = mywin,
        radius = size,
        units = 'pix',
        fillColor = standard_ball_color,
        interpolate = True)
    circle1.draw()

# Stimulus presentation
def present_ball(duration, trial, salience):
    if trial == 'standard':
        size = standard_ball_size
    elif trial == 'oddball':
        if salience == '+':
            size = high_salience_ball_size
        elif salience == '-':
            size = low_salience_ball_size
    
    number_of_frames = round(duration/refresh_rate) 

    # Present fixation cross for number of frames:
    timestamp = clock.getTime()
    print('presenting ball: {} {} {}'.format(duration, trial, salience))
    for frameN in range(number_of_frames):
        # central fixation cross
        draw_ball(size = size) # draw fixcross during stimulus presentation
        mywin.flip()
    print('presented ball')
    # Translate duration to number of frames:
    #return salience and utility
    actual_stimulus_duration = round(clock.getTime()-timestamp,3)
    print(trial + " duration:",actual_stimulus_duration)
    return actual_stimulus_duration

# Random interstimulus interval (ISI):
def define_ISI_interval():
    ISI = random.randint(ISI_interval[0], ISI_interval[1])
    ISI = ISI/1000 # get to second format
    return ISI

'''EXPERIMENTAL DESIGN'''
# The trial handler calls the sequence and displays it randomized.
# Loop of block is added to experiment handler.
# Any data that is collected  will be transfered to experiment handler automatically.
oddballs = ['oddball_++', 'oddball_+-', 'oddball_-+', 'oddball_--'] # oddballs are defined as strings. first place is u, second is s.
random.shuffle(oddballs)
phase_sequence = [
    'instruction1',
    'baseline_calibration',
    'instruction2',
    # 'practice_trials',
    'baseline',
    'instruction3',
    oddballs[0],
    'baseline', 
    oddballs[1],
    'baseline',
    oddballs[2],
    'baseline',
    oddballs[3]
    ]


phase_handler = data.TrialHandler(phase_sequence,nReps = 1, method='sequential')
exp.addLoop(phase_handler)

# Define global variables:
block_counter = 0
oddball_trial_counter = 1
manipulation_trial_counter = 1
baseline_trial_counter = 1

# Send trigger:
send_trigger('experiment_start')

for phase in phase_handler:
    block_counter += 1

    if phase == 'instruction1':
        draw_instruction1()
        mywin.flip()
        keys = event.waitKeys(keyList = ["space"])
        exp.nextEntry
    
    if phase == 'instruction2':
        draw_instruction2()
        mywin.flip()
        keys = event.waitKeys(keyList = ["space"])
        exp.nextEntry

    if phase == 'instruction3':
        draw_instruction2()
        mywin.flip()
        keys = event.waitKeys(keyList = ["space"])
        exp.nextEntry

    if phase.startswith('oddball_'):
        # common oddball setup.
        oddball_parameters = phase.split('_')[1] # remove the 'oddball_' portion of the phase name
        (u, s) = oddball_parameters

        # Setup oddball trials. Sequence for trial handler with 1/5 chance for an oddball.
        stimulus_sequence = ['standard','standard','standard','standard','oddball']

        # Trial handler calls the sequence and displays it randomized:
        trials = data.TrialHandler(stimulus_sequence,nReps = number_of_repetitions, method='random')
        # Add loop of block to experiment handler. Any collected data will be transfered to experiment handler automatically.
        exp.addLoop(trials)
        # Onset of oddball block:
        send_trigger('oddball_block')
        print('START OF ODDBALL BLOCK')

        for trial in trials:
            send_trigger('trial')
            ISI = define_ISI_interval() # for each trial separately
            timestamp = time.time() # epoch
            timestamp_exp = getTime() # time since start of experiment - also recorded by eyetracker
            timestamp_tracker = tracker.trackerTime()
            print('NEW TRIAL')
            print("ISI: ", ISI)
            print("gaze position: ", tracker.getPosition())
            # stimulus presentation
            send_trigger('stimulus')
            actual_stimulus_duration = present_ball(duration = stimulus_duration_in_seconds, trial = trial, salience = u)
            send_trigger('ISI')
            [fixcross_duration, offset_duration, pause_duration, nodata_duration] = fixcross_gazecontingent(ISI)
        exp.nextEntry()


        # all oddball trials have 160 'frequent' trials and 40 'oddball' trials. Let's add those
        # trials = ['std' for x in range(160)] + ['oddball' for x in range(40)]
        # random.shuffle(trials)

        # for trial in trials:
        #     # draw ball of size matching the trial specification (standard for std, high or low for oddball depending on s)
        #     if trial == 'std':
        #         draw_ball(size = standard_ball_size)
        #     if trial == 'oddball':
        #         if s == '+':
        #             draw_ball(size = high_salience_ball_size)
        #         elif s == '-':
        #             draw_ball(size = low_salience_ball_size)

        #     # clean up our balls...
        #     if u == '+':
        #         show_high_util_slide()


    if phase == 'baseline':
        send_trigger('baseline')
        print('START OF BASELINE PHASE')
        # create data
        timestamp = time.time() # epoch
        timestamp_exp = getTime() # time since start of experiment - also recorded by eyetracker
        # present baseline
        [stimulus_duration, offset_duration, pause_duration, nodata_duration] = fixcross_gazecontingent(baseline_duration)
        # collect global data --> saved to csv
        phase_handler.addData('phase', phase)
        phase_handler.addData('block_counter', block_counter)

        phase_handler.addData('stimulus_duration', stimulus_duration)
        phase_handler.addData('gaze_offset_duration', offset_duration)
        phase_handler.addData('trial_pause_duration', pause_duration)
        phase_handler.addData('trial_nodata_duration', nodata_duration)

        phase_handler.addData('baseline_trial_counter',baseline_trial_counter)
        phase_handler.addData('trial', phase)
        phase_handler.addData('timestamp', timestamp)
        phase_handler.addData('timestamp_exp', timestamp_exp)

        baseline_trial_counter += 1
        exp.nextEntry()


    if phase == 'practice_trials':
        # Define a sequence for trial handler with 1/5 chance for an oddball.
        practice_sequence = ['standard','standard','standard','standard','oddball']
        number_of_repetitions = round(number_of_practice_trials/len(practice_sequence))
        # Trial handler calls the sequence and displays it randomized:
        practice_trials = data.TrialHandler(practice_sequence,nReps = number_of_repetitions, method='random')
        # Add loop of block to experiment handler. Any collected data by trials will be transfered to experiment handler automaticall.
        exp.addLoop(practice_trials) 
        # Onset of practice_trials:
        send_trigger('practice_trials')
        print('START OF PRACTICE TRIAL BLOCK')

        for practice_trial in practice_trials:
            # Send eeg trigger:
            send_trigger('practice_trial')
            ISI = define_ISI_interval()
            timestamp = time.time() #epoch
            # Time since start of experiment, is also recorded by eyetracker:
            timestamp_exp = getTime()
            timestamp_tracker = tracker.trackerTime()
            print('NEW TRIAL')
            print("ISI: ",ISI)
            print("gaze position: ",tracker.getPosition())
            # Stimulus presentation:
            send_trigger('stimulus')
            actual_stimulus_duration = present_ball(duration = stimulus_duration_in_seconds, trial = practice_trial, salience = '-')
            send_trigger('ISI')
            [fixcross_duration, offset_duration, pause_duration, nodata_duration] = fixcross_gazecontingent(ISI)
            # Collect global data, saved to csv:
            phase_handler.addData('phase', phase)
            phase_handler.addData('block_counter', block_counter)
            # Collect trial data, saved to csv:
            practice_trials.addData('oddball_trial_counter',oddball_trial_counter) #trial number
            practice_trials.addData('practice_trial', practice_trial) #oddball or standard
            practice_trials.addData('timestamp', timestamp) #seconds since 01.01.1970 (epoch)
            practice_trials.addData('timestamp_exp', timestamp_exp) #time since start of experiment
            practice_trials.addData('timestamp_tracker', timestamp_tracker) #time of eye tracker (same as epoch?)
            practice_trials.addData('stimulus_duration', actual_stimulus_duration)
            practice_trials.addData('ISI_expected', ISI)
            practice_trials.addData('ISI_duration', fixcross_duration)
            practice_trials.addData('gaze_offset_duration', offset_duration)
            practice_trials.addData('trial_pause_duration', pause_duration)
            practice_trials.addData('trial_nodata_duration', nodata_duration)
            oddball_trial_counter += 1
            # Experiment handler moves to next trial. All data is collected for this trial.
        exp.nextEntry() 
    
    # if phase == 'oddball_block':
    #     # Setup oddball trials. Sequence for trial handler with 1/5 chance for an oddball.
    #     stimulus_sequence = ['standard','standard','standard','standard','oddball']
    #     number_of_repetitions = round(number_of_trials/len(stimulus_sequence))
    #     # Trial handler calls the sequence and displays it randomized:
    #     trials = data.TrialHandler(stimulus_sequence,nReps = number_of_repetitions, method='random')
    #     # Add loop of block to experiment handler. Any collected data will be transfered to experiment handler automatically.
    #     exp.addLoop(trials)
    #     # Onset of oddball block:
    #     send_trigger('oddball_block')
    #     print('START OF ODDBALL BLOCK')

    #     for trial in trials:
    #         send_trigger('trial')
    #         ISI = define_ISI_interval() #for each trial separately
    #         timestamp = time.time() #epoch
    #         timestamp_exp = getTime() #time since start of experiment - also recorded by eyetracker
    #         timestamp_tracker = tracker.trackerTime()
    #         print('NEW TRIAL')
    #         print("ISI: ",ISI)
    #         print("gaze position: ",tracker.getPosition())
    #         #stimulus presentation
    #         send_trigger('stimulus')
    #         actual_stimulus_duration = present_ball(stimulus_duration_in_seconds,trial)
    #         send_trigger('ISI')
    #         [fixcross_duration, offset_duration, pause_duration, nodata_duration] = fixcross_gazecontingent(ISI)




# During calibration process, pupil dilation (black slide) and pupil constriction (white slide) are assessed.
    if phase == 'baseline_calibration':
        baseline_sequence = ['baseline','baseline_whiteslide','baseline_blackslide']
        baseline_calibration_repetition = baseline_calibration_repetition
        # Trial handler calls the sequence and displays it randomized:
        exp_baseline_calibration = data.TrialHandler(baseline_sequence,nReps = baseline_calibration_repetition, method='sequential')
        # Add loop of block to experiment handler. Collected data will be transfered to experiment handler automatically:
        exp.addLoop(exp_baseline_calibration)

        send_trigger('baseline_calibration')
        print('START OF BASELINE CALIBRATION PHASE')

        for baseline_trial in baseline_sequence:

            if baseline_trial == 'baseline':

                #create data
                timestamp = time.time() #epoch
                timestamp_exp = getTime() #time since start of experiment - also recorded by eyetracker

                #present baseline
                send_trigger('baseline')
                [stimulus_duration, offset_duration, pause_duration, nodata_duration] = fixcross_gazecontingent(
                    baseline_duration)

                #collect global data --> saved to csv
                phase_handler.addData('phase', phase)
                phase_handler.addData('block_counter', block_counter)
                phase_handler.addData('stimulus_duration', stimulus_duration)
                phase_handler.addData('gaze_offset_duration', offset_duration)
                phase_handler.addData('trial_pause_duration', pause_duration)
                phase_handler.addData('trial_nodata_duration', nodata_duration)
                phase_handler.addData('baseline_trial_counter',baseline_trial_counter)
                phase_handler.addData('trial', baseline_trial)
                phase_handler.addData('timestamp', timestamp)
                phase_handler.addData('timestamp_exp', timestamp_exp)
                baseline_trial_counter += 1
                exp.nextEntry()

            if baseline_trial == 'baseline_whiteslide':
                # create data
                timestamp = time.time() #epoch
                timestamp_exp = getTime() #time since start of experiment - also recorded by eyetracker

                #present baseline - but with white background
                send_trigger('baseline_whiteslide')
                [stimulus_duration, offset_duration, pause_duration, nodata_duration] = fixcross_gazecontingent(
                    baseline_duration, background_color = white_slide)

                #collect global data --> saved to csv
                phase_handler.addData('phase', phase)
                phase_handler.addData('block_counter', block_counter)
                phase_handler.addData('stimulus_duration', stimulus_duration)
                phase_handler.addData('gaze_offset_duration', offset_duration)
                phase_handler.addData('trial_pause_duration', pause_duration)
                phase_handler.addData('trial_nodata_duration', nodata_duration)
                phase_handler.addData('baseline_trial_counter',baseline_trial_counter)
                phase_handler.addData('trial', baseline_trial)
                phase_handler.addData('timestamp', timestamp)
                phase_handler.addData('timestamp_exp', timestamp_exp)
                #baseline_trial_counter += 1
                exp.nextEntry()
            
            if baseline_trial == 'baseline_blackslide':
                #create data
                timestamp = time.time() #epoch
                timestamp_exp = getTime() #time since start of experiment - also recorded by eyetracker
                #present baseline - but with black background
                send_trigger('baseline_blackslide')
                [stimulus_duration, offset_duration, pause_duration, nodata_duration] = fixcross_gazecontingent(
                    baseline_duration, background_color = black_slide)

                #collect global data --> saved to csv
                phase_handler.addData('phase', phase)
                phase_handler.addData('block_counter', block_counter)
                phase_handler.addData('stimulus_duration', stimulus_duration)
                phase_handler.addData('gaze_offset_duration', offset_duration)
                phase_handler.addData('trial_pause_duration', pause_duration)
                phase_handler.addData('trial_nodata_duration', nodata_duration)
                phase_handler.addData('baseline_trial_counter',baseline_trial_counter)
                phase_handler.addData('trial', baseline_trial)
                phase_handler.addData('timestamp', timestamp)
                phase_handler.addData('timestamp_exp', timestamp_exp)
                #baseline_trial_counter += 1
                exp.nextEntry()


'''WRAP UP AND CLOSE'''
# Send trigger that experiment has ended:
send_trigger('experiment_end')
# Close reading from eyetracker:
tracker.setRecordingState(False) 
# Close iohub instance:
io.quit() 
# Close window:
mywin.close()
core.quit()