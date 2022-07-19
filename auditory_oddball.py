
'''AUDITORY ODDBALL TASK'''
# For further information see README.md.

'''LOAD MODULES'''
# Core libraries:
from psychopy import visual, core, event, clock, data, gui, monitors, parallel
import random, time, numpy
# For controlling eye tracker and eye-tracking SDK:
import tobii_research
from psychopy.iohub import launchHubServer
from psychopy.core import getTime, wait
# For getting keyboard input:
from psychopy.hardware import keyboard
# For playing sound:
from psychopy import prefs
prefs.hardware['audioLib'] = ['PTB'] #PTB described as highest accuracy sound class
from psychopy import sound
import psychtoolbox as ptb #sound processing via ptb
# For managing paths:
from pathlib import Path
# Miscellaneous: Hide messages in console from pygame:
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

'''SETUP'''
# Path to output data:
path_to_data = Path("Desktop", "tasks", "data", "auditory_oddball").resolve()
trials_data_folder = Path(path_to_data, 'trialdata')
eyetracking_data_folder = Path(path_to_data, 'eyetracking')

print(trials_data_folder)
print(eyetracking_data_folder)

# Testmode.
# TRUE mimics an eye-tracker by mouse movement, FALSE = eye-tracking hardware is required.
testmode = True

# Experimental settings:
# Input dialgue boxes are presented on external screen 1.
dialog_screen = 1
# Stimuli are presented on internal screen 0.
presentation_screen = 0
number_of_trials = 10 #should be multiplier of 5 - target 100
stimulus_duration_in_seconds = 0.1
# If oddball or standrad stimulus is defined below.
sound_one_in_Hz = 500
sound_two_in_Hz = 750
size_fixation_cross_in_pixels = 60
# Inter Stimulus Interval (ISI) randomly varies between value0 and value1.
ISI_interval = [1800, 2000]
# Sensitivity: Warning of gaze offset from the center.
gaze_offset_cutoff = 3 * size_fixation_cross_in_pixels
# [0, 0 , 0] is gray as float [-1, 1]
background_color_rgb = (0, 0, 0)
white_slide = 'white'
black_slide = 'black'
manipulation_repetition = 1 # TARGET: 5
# Presentation duration of baseline screen, in seconds.
baseline_duration = 5 # TARGET: 10
# The two parameter of manipulatin:
squeeze_phase_duration = 6 # TARGET: 18
relax_phase_duration = 10 # TARGET: 60
squeeze_ball_color = (50, 25, 0) # yellow
relax_ball_color = (0, 0, 255) # blue
baseline_calibration_repetition = 1 # TARGET: 1
# After 500 ms the no_data detection warning should be displayed on the screen.
no_data_warning_cutoff = 0.5
# Setings are stored automatically for each trial.
settings = {}

# EEG trigger variables. 10 ms duration of trigger signal.
pulse_duration = 0.01

# Don't quote it! Correct port needs to be identified.
# Use standalone "Parallel Port Tester programm" to identify it.
parallel_port_adress = 0x03FF8

# Presenting a dialog box. Infos are added to settings.
settings['id'] = 123 #default testing value
settings['group'] = ['ASD', 'TD']

dlg = gui.DlgFromDict(settings,title='auditory oddball')
if dlg.OK:
    print('EXPERIMENT IS STARTED')
    #core.wait(5)
else:
    core.quit()  # the user hit cancel so exit

# Name for output data.
fileName = str(settings['id']) + '_' + data.getDateStr(format="%Y-%m-%d-%H%M")

# Expriment handler saves experiment data automatically.
exp = data.ExperimentHandler(
    name="auditory_oddball",
    version='0.1',
    extraInfo = settings,
    dataFileName = str(trials_data_folder / fileName),
    )

# Two different sound frequencies (conditions) are balanced across groups and
# saved in the setings dictionary.
random_number = random.random()
if random_number < 0.5:
    standard_sound = sound.Sound(sound_one_in_Hz)
    oddball_sound = sound.Sound(sound_two_in_Hz)
    print('oddball sound is',sound_two_in_Hz,'Hz')
    settings['standard_frequency'] = sound_one_in_Hz
    settings['oddball_frequency'] = sound_two_in_Hz
    # exp.addData('oddball_frequency',sound_two_in_Hz)
if random_number >= 0.5:
    standard_sound = sound.Sound(sound_two_in_Hz)
    oddball_sound = sound.Sound(sound_one_in_Hz)
    print('oddball sound is',sound_one_in_Hz,'Hz')
    settings['standard_frequency'] = sound_two_in_Hz
    settings['oddball_frequency'] = sound_one_in_Hz
    # exp.addData('oddball_frequency',sound_one_in_Hz)

# Monitor parameters are adapted to presentation PC.
# Name is saved with PsychoPy monitor manager.
# Distance is from screenin cm.
mon = monitors.Monitor(
    name = 'eizo_eyetracker',
    width = 29.6,
    distance = 65)

# Create display window.
# Unit was changed to pixel so that eye trcker outputs pixel on presentation screen.
# Screen resolution is 1920/1080.
mywin = visual.Window(
    size = [1920,1080],
    fullscr=True,
    monitor = mon,
    color = background_color_rgb,
    screen = presentation_screen,
    units = "pix")

refresh_rate = mywin.monitorFramePeriod #get monitor refresh rate in seconds
print('monitor refresh rate: ' + str(round(refresh_rate, 3)) + ' seconds')

#start timer for experiment - this is also the timestamp recorded by the eyetracker - note: no dedicated clock needed, just call getTime() without clock see below
#exp_timer = core.Clock()

#SETUP EYETRACKING:
    #CAVE: difference to psychopy documentation required: - define name as tracker - define presentation window before
    #NOTE: output gazeposition is alwys centered, i.e. screen center = [0,0]

if testmode:
    print('mouse is used to mimick eyetracker...')
    iohub_config = {'eyetracker.hw.mouse.EyeTracker': {'name': 'tracker'}} #use mouse as eyetracker

if not testmode:
    #search for eye tracker
    found_eyetrackers = tobii_research.find_all_eyetrackers()
    my_eyetracker = found_eyetrackers[0]
    print("Address: " + my_eyetracker.address)
    print("Model: " + my_eyetracker.model)
    print("Name (It's OK if this is empty): " + my_eyetracker.device_name)
    print("Serial number: " + my_eyetracker.serial_number)

    #deifne a config that allow iohub to connect to the eye-tracker
    iohub_config = {'eyetracker.hw.tobii.EyeTracker':
        {'name': 'tracker', 'runtime_settings': {'sampling_rate': 300, }}}


#use IOHUB to create a different instance that records eye tracking data in hdf5 file  - saved in datastore_name
io = launchHubServer(**iohub_config,
                        experiment_code = str(eyetracking_data_folder),
                        session_code = fileName,
                        datastore_name = str(eyetracking_data_folder / fileName), #where data is stored
                        window = mywin)

#calls the eyetracker device
tracker = io.devices.tracker
#---> start recording
tracker.setRecordingState(True)

#SETUP Parallel port trigger
    #list position defines trigger value that is sent - see function send_trigger()
    # i.e. list position 2 will send a trigger with value "S2"
trigger_name_list = ['PLACEHOLDER', #0
                     'trial', #1 -
                     'standard', #2 -
                     'standard_rev', #3 -
                     'oddball', #4 -
                     'oddball_rev', #5 -
                     'ISI', #6 -
                     'baseline', #7 -
                     'manipulation_squeeze', #8 -
                     'manipulation_relax', #9 -
                     'experiment_start', #10 -
                     'experiment_end', #11 -
                     'pause_initiated', #12 -
                     'pause_ended', #13 -
                     'experiment_aborted', #14 -
                     'baseline_calibration', #15 -
                     'baseline_whiteslide', #16 -
                     'baseline_blackslide', #17 -
                     'oddball_block', #18 -
                     'manipulation_block'] #19 -

print(trigger_name_list)

#find a parallel port
if not testmode:
    port = parallel.ParallelPort(parallel_port_adress) #dont quote it - CAVE: correct port needs to be identified - use standalone "Parallel Port Tester programm"
    port.setData(0) #set all pins to low - otherwise no triggers will be sent

##SETUP keyboard --> check for keypresses
kb = keyboard.Keyboard()

""" FUNCTIONS """

#send a trigger to EEG recording PC via parallel port
def send_trigger(trigger_name):

    #INFO
    ##tested definition - brian vision recorder - other triggers are created by addition of pins
    ##pin 2 - S1
    ##pin 3 - S2
    ##pin 4 - S4
    ##pin 5 - S8
    ##pin 6 - S16
    ##pin 7 - S32
    ##pin 8 - S64
    ##pin 9 - S128

    #triggers defined for current experiment - Onset Trigger für Trial/Stimulus Präsentation und ISI machen auch fürs EEG Sinn.
    #S1 - onset_trial
    #S2 - stimulus
    #S3 - ISI
    #S4 - baseline
    #S5 - manipulation_squeeze
    #S6 - manipulation_relax
    #S7 - experiment_start
    #S8 - experiment_end
    #S9 - pause_initiated
    #S10 - pause_ended
    #S11 - experiment_aborted
    #S12 - baseline_calibration
    #S13 -

    trigger_name_found = False

    for i in trigger_name_list:

        if i == trigger_name:

            #look up position in list
            trigger_value = trigger_name_list.index(trigger_name)

            #translates trigger integer value to byte value (binary of length 8 = able to represent values 1-256)
            #e.g. list position 3 --> trigger value "3" --> trigger_byte "00000011"
            trigger_byte = f'{trigger_value:08b}'

            #set pins according to trigger byte
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

                #testing
                #print('sent trigger S' + str(trigger_value))

                #set all pins back to zero
                port.setData(0)

            if testmode:

                #testing
                print('sent DUMMY trigger S' + str(trigger_value))


            trigger_name_found = True

    if not trigger_name_found:
        print('trigger name is not defined: ' + trigger_name)

# Draw instruction slides:
def draw_instruction(text, background_color = background_color_rgb):
    if background_color is not background_color_rgb:
        background_rect = visual.Rect(win=mywin, size=mywin.size, fillColor= background_color)
        background_rect.draw()

    instruction_slide = visual.TextStim(
        win = mywin,
        text = text,
        color = 'black',
        units = 'pix',
        wrapWidth = 900,
        height = size_fixation_cross_in_pixels)
    instruction_slide.draw()

# draw a fixation cross from lines
def draw_fixcross(background_color=background_color_rgb, cross_color = 'black'):

    if background_color is not background_color_rgb:
        background_rect = visual.Rect(win=mywin, size=mywin.size, fillColor= background_color)
        background_rect.draw()

    line1 = visual.Line(win=mywin, units='pix', lineColor = cross_color) #define line object
    line1.start = [-(size_fixation_cross_in_pixels/2), 0]
    line1.end = [+(size_fixation_cross_in_pixels/2), 0]
    line2 = visual.Line(win=mywin, units='pix', lineColor = cross_color) #define line object
    line2.start = [0, -(size_fixation_cross_in_pixels/2)]
    line2.end = [0, +(size_fixation_cross_in_pixels/2)]
    line1.draw()
    line2.draw()

#draw figure - when gaze is offset - for gaze contincency
def draw_gazedirect(background_color=background_color_rgb):

    #adapt background according to privuded "background color"
    if background_color is not background_color_rgb:
        background_rect = visual.Rect(win=mywin, size=mywin.size, fillColor= background_color)
        background_rect.draw()

    #parameters
    function_color = 'red'
    arrow_size_pix = size_fixation_cross_in_pixels
    arrow_pos_offset = 5
    width = 3

    rect1 = visual.Rect(win=mywin, units='pix', lineColor=function_color, fillColor = background_color, lineWidth=width, size = size_fixation_cross_in_pixels*6)

    #arrow left
    al_line1 = visual.Line(win=mywin, units='pix', lineColor=function_color, lineWidth=width)
    al_line1.start = [-(arrow_size_pix*arrow_pos_offset), 0]
    al_line1.end = [-(arrow_size_pix*arrow_pos_offset-arrow_size_pix), 0]
    al_line2 = visual.Line(win=mywin, units='pix', lineColor=function_color, lineWidth=width)
    al_line2.start = [-(arrow_size_pix*arrow_pos_offset-(arrow_size_pix/2)), -arrow_size_pix/2]
    al_line2.end = [-(arrow_size_pix*arrow_pos_offset-arrow_size_pix), 0]
    al_line3 = visual.Line(win=mywin, units='pix', lineColor=function_color, lineWidth=width)
    al_line3.start = [-(arrow_size_pix*arrow_pos_offset-(arrow_size_pix/2)), +arrow_size_pix/2]
    al_line3.end = [-(arrow_size_pix*arrow_pos_offset-arrow_size_pix), 0]

    #arrow right
    ar_line1 = visual.Line(win=mywin, units='pix', lineColor=function_color, lineWidth=width)
    ar_line1.start = [+(arrow_size_pix*arrow_pos_offset), 0]
    ar_line1.end = [+(arrow_size_pix*arrow_pos_offset-arrow_size_pix), 0]
    ar_line2 = visual.Line(win=mywin, units='pix', lineColor=function_color, lineWidth=width)
    ar_line2.start = [+(arrow_size_pix*arrow_pos_offset-(arrow_size_pix/2)), -arrow_size_pix/2]
    ar_line2.end = [+(arrow_size_pix*arrow_pos_offset-arrow_size_pix), 0]
    ar_line3 = visual.Line(win=mywin, units='pix', lineColor=function_color, lineWidth=width)
    ar_line3.start = [+(arrow_size_pix*arrow_pos_offset-(arrow_size_pix/2)), +arrow_size_pix/2]
    ar_line3.end = [+(arrow_size_pix*arrow_pos_offset-arrow_size_pix), 0]

    #arrow top
    at_line1 = visual.Line(win=mywin, units='pix', lineColor=function_color, lineWidth=width)
    at_line1.start = [0, +(arrow_size_pix*arrow_pos_offset)]
    at_line1.end = [0, +(arrow_size_pix*arrow_pos_offset-arrow_size_pix)]
    at_line2 = visual.Line(win=mywin, units='pix', lineColor=function_color, lineWidth=width)
    at_line2.start = [-arrow_size_pix/2, +(arrow_size_pix*arrow_pos_offset-(arrow_size_pix/2))]
    at_line2.end = [0, +(arrow_size_pix*arrow_pos_offset-arrow_size_pix)]
    at_line3 = visual.Line(win=mywin, units='pix', lineColor=function_color, lineWidth=width)
    at_line3.start = [+arrow_size_pix/2, +(arrow_size_pix*arrow_pos_offset-(arrow_size_pix/2))]
    at_line3.end = [0, +(arrow_size_pix*arrow_pos_offset-arrow_size_pix)]

    #arrow bottom
    ab_line1 = visual.Line(win=mywin, units='pix', lineColor=function_color, lineWidth=width)
    ab_line1.start = [0, -(arrow_size_pix*arrow_pos_offset)]
    ab_line1.end = [0, -(arrow_size_pix*arrow_pos_offset-arrow_size_pix)]
    ab_line2 = visual.Line(win=mywin, units='pix', lineColor=function_color, lineWidth=width)
    ab_line2.start = [+arrow_size_pix/2, -(arrow_size_pix*arrow_pos_offset-(arrow_size_pix/2))]
    ab_line2.end = [0, -(arrow_size_pix*arrow_pos_offset-arrow_size_pix)]
    ab_line3 = visual.Line(win=mywin, units='pix', lineColor=function_color, lineWidth=width)
    ab_line3.start = [-arrow_size_pix/2, -(arrow_size_pix*arrow_pos_offset-(arrow_size_pix/2))]
    ab_line3.end = [0, -(arrow_size_pix*arrow_pos_offset-arrow_size_pix)]

    #draw all
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

#draw a feedback that no eyes are currently detected thus eye tracking data is NA
def draw_nodata_info(background_color=background_color_rgb):

    #adapt background according to privuded "background color"
    if background_color is not background_color_rgb:
        background_rect = visual.Rect(win=mywin, size=mywin.size, fillColor= background_color)
        background_rect.draw()

    no_data_warning = visual.TextStim(win=mywin, text='NO EYES DETECTED!', color = 'red', units = 'pix', height = size_fixation_cross_in_pixels)
    no_data_warning.draw()

#stimulus for manipulation
def draw_ball(ball_color):
    circle1 = visual.Circle(win=mywin,
                            radius=size_fixation_cross_in_pixels,
                            units = 'pix',
                            fillColor =ball_color,
                            interpolate=True)
    circle1.draw()

#check for keypresses - used to pause and quit experiment
def check_keypress():
    #these keys are allowed
    keys = kb.getKeys(['p','escape'], waitRelease=True)
    timestamp_keypress = clock.getTime()

    if 'escape' in keys:

        send_trigger('pause_initiated')
        dlg = gui.Dlg(title='Quit?', labelButtonOK=' OK ', labelButtonCancel=' Cancel ')
        dlg.addText('Do you really want to quit? - Then press OK')
        ok_data = dlg.show()  # show dialog and wait for OK or Cancel

        if dlg.OK:  # or if ok_data is not None
            send_trigger('experiment_aborted')
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
        send_trigger('pause_ended')

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


#check for the offset of gaze from the center screen
def check_gaze_offset(gaze_position):

    gaze_center_offset = numpy.sqrt((gaze_position[0])**2 + (gaze_position[1])**2) #pythagoras theorem

    if gaze_center_offset >= gaze_offset_cutoff:
        offset_boolean = True
        #print('center offset:' + str(gaze_center_offset)) #testing
    else:
        offset_boolean = False
    return offset_boolean

#fixation cross - and check for "data available" and "screen center gaze"
def fixcross_gazecontingent(duration_in_seconds, background_color=background_color_rgb, cross_color = 'black'):
    #translate duration to number of frames
    number_of_frames = round(duration_in_seconds/refresh_rate)
    timestamp = getTime()
    gaze_offset_duration = 0
    pause_duration = 0
    nodata_duration = 0
    #present cross for number of frames
    for frameN in range(number_of_frames):

        #check for keypress
        pause_duration += check_keypress()

        #check for eye tracking data - only call once per flip
        gaze_position = tracker.getPosition()

        #check for eye tracking data
        if check_nodata(gaze_position):
            print('warning: no eyes detected')
            frameN = 1 #reset duration of for loop - resart ISI
            nodata_current_duration = 0

            while check_nodata(gaze_position):
                if nodata_current_duration > no_data_warning_cutoff: #ensure that warning is not presented after every eye blink
                    draw_nodata_info(background_color)
                mywin.flip() #wait for monitor refresh time
                nodata_duration += refresh_rate
                nodata_current_duration += refresh_rate
                gaze_position = tracker.getPosition() #get new gaze data

        #check for gaze
        elif check_gaze_offset(gaze_position):
            print('warning: gaze offset')
            frameN = 1 #reset duration of for loop - resart ISI

            while not check_nodata(gaze_position) and check_gaze_offset(gaze_position):

                #listen for keypress
                pause_duration += check_keypress()

                draw_gazedirect(background_color) #redirect attention to fixation cross area
                mywin.flip() #wait for monitor refresh time
                gaze_offset_duration += refresh_rate
                gaze_position = tracker.getPosition() #get new gaze data

        #draw fixation cross -
        draw_fixcross(background_color, cross_color)
        mywin.flip()

    #generate output info
    actual_fixcross_duration = round(getTime()-timestamp,3)
    gaze_offset_duration = round(gaze_offset_duration,3)
    nodata_duration = round(nodata_duration,3)

    #testing:
    print('numberof frames: ' + str(number_of_frames))
    print('no data duration: ' + str(nodata_duration))
    print('gaze offset duration: ' + str(gaze_offset_duration))
    print('pause duration: ' + str(pause_duration))
    print('actual fixcross duration: ' + str(actual_fixcross_duration))
    #print("timing offset:",duration_in_seconds-(clock.getTime()-timestamp)) #test timing offset

    return [actual_fixcross_duration, gaze_offset_duration, pause_duration, nodata_duration]

#stimulus presentation
def present_stimulus(duration_in_seconds,trial):

    nextFlip = mywin.getFutureFlipTime(clock='ptb') # sync sound start with next screen refresh
    if trial == 'oddball':
        oddball_sound.play(when=nextFlip)
    if trial == 'standard':
        standard_sound.play(when=nextFlip)
    if trial == 'oddball_rev':
        standard_sound.play(when=nextFlip)
    if trial == 'standard_rev':
        oddball_sound.play(when=nextFlip)
    number_of_frames = round(duration_in_seconds/refresh_rate) #translate duration to number of frames

    #present cross for number of frames
    timestamp = clock.getTime()
    for frameN in range(number_of_frames):
        #central fixation cross
        draw_fixcross() #draw fixcross during stimulus presentation
        mywin.flip()

        #bugfixing
        #print(tracker.getPosition())

    #stop replay
    if trial == 'oddball':
        oddball_sound.stop()
    if trial == 'standard':
        standard_sound.stop()
    if trial == 'oddball_rev':
        standard_sound.stop()
    if trial == 'standard_rev':
        oddball_sound.stop()


    #function output
    actual_stimulus_duration = round(clock.getTime()-timestamp,3)
    print(trial + " duration:",actual_stimulus_duration)
    return actual_stimulus_duration

#random interstimulus interval
def define_ISI_interval():
    ISI = random.randint(ISI_interval[0], ISI_interval[1])
    ISI = ISI/1000 #get to second format
    return ISI

#present a ball indicative
def present_ball(which_phase):

    if which_phase == 'squeeze':
        number_of_frames = round(squeeze_phase_duration/refresh_rate) #translate duration to number of frames
        #present ball for number of frames
        for frameN in range(number_of_frames):
            if frameN == 1:
                timestamp = clock.getTime()
            #central fixation cross
            draw_ball(squeeze_ball_color) #draw fixcross during stimulus presentation
            mywin.flip()

    if which_phase == 'relax':
        number_of_frames = round(relax_phase_duration/refresh_rate) #translate duration to number of frames
        #present ball for number of frames
        for frameN in range(number_of_frames):
            if frameN == 1:
                timestamp = clock.getTime()
            #central fixation cross
            draw_ball(relax_ball_color) #draw fixcross during stimulus presentation
            mywin.flip()

    actual_manipulation_duration = round(clock.getTime()-timestamp,3)
    print(which_phase + " duration:",actual_manipulation_duration)
    return actual_manipulation_duration

"""EXPERIMENTAL DESIGN """

phase_sequence = ['instruction1','baseline_calibration','oddball_block','baseline','oddball_block_rev','baseline','instruction2','manipulation_block','baseline','oddball_block','baseline','oddball_block_rev','baseline', 'instruction3']
phase_handler = data.TrialHandler(phase_sequence,nReps = 1, method='sequential') #trial handler calls the sequence and displays it randomized
exp.addLoop(phase_handler) #add loop of block to experiment handler - any data that is collected  will be transfered to experiment handler automatically

#define global variables
block_counter = 0
oddball_trial_counter = 1
manipulation_trial_counter = 1
baseline_trial_counter = 1

#send trigger
send_trigger('experiment_start')

for phase in phase_handler:

    block_counter += 1

    if phase == 'instruction1':
        text_1 = "Das Experiment beginnt jetzt.\nBitte bleibe still sitzen und\nschaue auf das Kreuz in der Mitte.\n\n Weiter mit der Leertaste."
        print('SHOW INSTRUCTIONS SLIDE 1')
        draw_instruction(text = text_1)
        mywin.flip()
        keys = event.waitKeys(keyList = ["space"])
        exp.nextEntry()

    if phase == 'instruction2':
        text_2 = "Gleich wirst du einen gelben Kreis sehen.\nBitte drücke dann fest das Kraftmessgerät.\n\nMit der Leertaste geht es weiter."
        print('SHOW INSTRUCTIONS SLIDE 2')
        draw_instruction(text = text_2)
        mywin.flip()
        keys = event.waitKeys(keyList = ["space"])
        exp.nextEntry

    if phase == 'instruction3':
        text_3 = "Das Experiment ist jetzt beendet.\nBitte bleibe still noch sitzen."
        print('SHOW INSTRUCTIONS SLIDE 3')
        draw_instruction(text = text_3)
        mywin.flip()
        keys = event.waitKeys(keyList = ["space"])
        exp.nextEntry

    if phase == 'oddball_block':

        #setup oddbal trials
        stimulus_sequence = ['standard','standard','standard','standard','oddball'] #define a sequence for trial handler - 1/5 chance for an oddball
        number_of_repetitions = round(number_of_trials/len(stimulus_sequence))
        trials = data.TrialHandler(stimulus_sequence,nReps = number_of_repetitions, method='random') #trial handler calls the sequence and displays it randomized
        exp.addLoop(trials) #add loop of block to experiment handler - any data that is collected  by trials will be transfered to experiment handler automatically

        # Inform the ioHub server about the TrialHandler - could not get this to work
        #io.createTrialHandlerRecordTable(trials)

        #onset of oddball block
        send_trigger('oddball_block')
        print('START OF ODDBALL BLOCK')

        for trial in trials:

            #new trail - send to hdf5 file - does it do anything?
            #io.sendMessageEvent(trial, category='test')
            send_trigger('trial')

            #create data
            ISI = define_ISI_interval() #for each trial separately
            timestamp = time.time() #epoch
            timestamp_exp = getTime() #time since start of experiment - also recorded by eyetracker

            timestamp_tracker = tracker.trackerTime()

            #print for testing
            print('NEW TRIAL')
            print("ISI: ",ISI)
            print("gaze position: ",tracker.getPosition())

            #stimulus presentation
            send_trigger(trial)
            actual_stimulus_duration = present_stimulus(stimulus_duration_in_seconds,trial)

            #ISI
            #fixcross(ISI)
            send_trigger('ISI')
            [fixcross_duration, offset_duration, pause_duration, nodata_duration] = fixcross_gazecontingent(ISI)
            #print('trial was paused:' + str(trial_paused))

            #collect global data --> saved to csv
            phase_handler.addData('phase', phase)
            phase_handler.addData('block_counter', block_counter)

            #collect trial data --> saved to csv
            trials.addData('oddball_trial_counter',oddball_trial_counter) #trial number
            trials.addData('trial', trial) #oddball or standard
            trials.addData('timestamp', timestamp) #seconds since 01.01.1970 (epoch)
            trials.addData('timestamp_exp', timestamp_exp) #time since start of experiment
            trials.addData('timestamp_tracker', timestamp_tracker) #time of eye tracker (same as epoch?)
            trials.addData('stimulus_duration', actual_stimulus_duration)
            trials.addData('ISI_expected', ISI)
            trials.addData('ISI_duration', fixcross_duration)
            trials.addData('gaze_offset_duration', offset_duration)
            trials.addData('trial_pause_duration', pause_duration)
            trials.addData('trial_nodata_duration', nodata_duration)

            oddball_trial_counter += 1

            #collect all data in trials --> also stored in hdf5 (eye tracking file)
            #io.addTrialHandlerRecord(trial)
            #io.addTrialHandlerRecord(trial)

            exp.nextEntry() #experiment handler - move to next trial - all data is collected for this trial

    if phase == 'oddball_block_rev':

        #setup oddbal trials
        stimulus_sequence = ['standard_rev','standard_rev','standard_rev','standard_rev','oddball_rev'] #define a sequence for trial handler - 1/5 chance for an oddball
        number_of_repetitions = round(number_of_trials/len(stimulus_sequence))
        trials = data.TrialHandler(stimulus_sequence,nReps = number_of_repetitions, method='random') #trial handler calls the sequence and displays it randomized
        exp.addLoop(trials) #add loop of block to experiment handler - any data that is collected  by trials will be transfered to experiment handler automatically

        # Inform the ioHub server about the TrialHandler - could not get this to work
        #io.createTrialHandlerRecordTable(trials)

        #onset of oddball block
        send_trigger('oddball_block_rev')
        print('START OF ODDBALL BLOCK REVERSAL')

        for trial in trials:

            #new trail - send to hdf5 file - does it do anything?
            #io.sendMessageEvent(trial, category='test')
            send_trigger('trial')

            #create data
            ISI = define_ISI_interval() #for each trial separately
            timestamp = time.time() #epoch
            timestamp_exp = getTime() #time since start of experiment - also recorded by eyetracker

            timestamp_tracker = tracker.trackerTime()

            #print for testing
            print('NEW TRIAL')
            print("ISI: ",ISI)
            print("gaze position: ",tracker.getPosition())

            #stimulus presentation
            send_trigger(trial)
            actual_stimulus_duration = present_stimulus(stimulus_duration_in_seconds,trial)

            #ISI
            #fixcross(ISI)
            send_trigger('ISI')
            [fixcross_duration, offset_duration, pause_duration, nodata_duration] = fixcross_gazecontingent(ISI)
            #print('trial was paused:' + str(trial_paused))

            #collect global data --> saved to csv
            phase_handler.addData('phase', phase)
            phase_handler.addData('block_counter', block_counter)

            #collect trial data --> saved to csv
            trials.addData('oddball_trial_counter',oddball_trial_counter) #trial number
            trials.addData('trial', trial) #oddball or standard
            trials.addData('timestamp', timestamp) #seconds since 01.01.1970 (epoch)
            trials.addData('timestamp_exp', timestamp_exp) #time since start of experiment
            trials.addData('timestamp_tracker', timestamp_tracker) #time of eye tracker (same as epoch?)
            trials.addData('stimulus_duration', actual_stimulus_duration)
            trials.addData('ISI_expected', ISI)
            trials.addData('ISI_duration', fixcross_duration)
            trials.addData('gaze_offset_duration', offset_duration)
            trials.addData('trial_pause_duration', pause_duration)
            trials.addData('trial_nodata_duration', nodata_duration)

            oddball_trial_counter += 1

            #collect all data in trials --> also stored in hdf5 (eye tracking file)
            #io.addTrialHandlerRecord(trial)
            #io.addTrialHandlerRecord(trial)

            exp.nextEntry() #experiment handler - move to next trial - all data is collected for this trial


    if phase == 'manipulation_block':

        #setup experimental manipulation
        manipulation_sequence = ['baseline','squeeze','baseline','relax']
        manipulation_repetition = manipulation_repetition
        exp_manipulations = data.TrialHandler(manipulation_sequence,nReps = manipulation_repetition, method='sequential') #trial handler calls the sequence and displays it randomized
        exp.addLoop(exp_manipulations) #add loop of block to experiment handler - any data that is collected  will be transfered to experiment handler automatically

        send_trigger('manipulation_block')
        print('START OF MANIPULATION PHASE')
        #wait for instructions, then keypress

        for manipulation in exp_manipulations:

            #print for testing
            print('NEW MANIPULATION:' + manipulation)

            #create data
            timestamp = time.time() #epoch
            timestamp_exp = getTime() #time since start of experiment - also recorded by eyetracker

            #fixation_cross for 10 seconds to determine tonic pupil size
            if manipulation == 'baseline':
                send_trigger('baseline')
                [stimulus_duration, offset_duration, pause_duration, nodata_duration] = fixcross_gazecontingent(baseline_duration)

                #save data
                exp_manipulations.addData('stimulus_duration', stimulus_duration)
                exp_manipulations.addData('gaze_offset_duration', offset_duration)
                exp_manipulations.addData('trial_pause_duration', pause_duration)
                exp_manipulations.addData('trial_nodata_duration', nodata_duration)

            #manipulation presentation
            if manipulation == 'squeeze' or manipulation == 'relax':

                if manipulation == 'squeeze':
                    send_trigger('manipulation_squeeze')
                if manipulation == 'relax':
                    send_trigger('manipulation_relax')

                #present ball that indicates squeeze or relax (based on manipultion variable)
                actual_manipulation_duration = present_ball(manipulation)

                #save data
                exp_manipulations.addData('stimulus_duration', actual_manipulation_duration)


            if manipulation == 'squeeze':

                grip_info = {}
                grip_info['effort_rating'] = ['high','low']
                grip_info['grip_strength'] = int(0)

                #present dialgue box to enter hand grip strength data
                dlg = gui.DlgFromDict(grip_info,title='hand grip strength', screen=dialog_screen)
                dlg.addText('Fast input! - do not delay experiment')

                exp_manipulations.addData('effort_rating', grip_info['effort_rating'])
                exp_manipulations.addData('grip_strength', grip_info['grip_strength'])


            #collect global data --> saved to csv
            phase_handler.addData('phase', phase)
            phase_handler.addData('block_counter', block_counter)

            #collect data --> saved to csv
            exp_manipulations.addData('manipulation_trial_counter',manipulation_trial_counter)
            exp_manipulations.addData('trial', manipulation)
            exp_manipulations.addData('timestamp', timestamp)
            exp_manipulations.addData('timestamp_exp', timestamp_exp)

            manipulation_trial_counter += 1

            exp.nextEntry() #experiment handler - move to next trial - all data is collected for this trial

    #checks pupil size for a duration:
    if phase == 'baseline':

        send_trigger('baseline')
        print('START OF BASELINE PHASE')

        #create data
        timestamp = time.time() #epoch
        timestamp_exp = getTime() #time since start of experiment - also recorded by eyetracker

        #present baseline
        [stimulus_duration, offset_duration, pause_duration, nodata_duration] = fixcross_gazecontingent(baseline_duration)

        #collect global data --> saved to csv
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

    #checks pupil size for a duration + max dilation furing black slide and max constriction during white slide
    if phase == 'baseline_calibration':

        #setup experimental manipulation
        baseline_sequence = ['baseline','baseline_whiteslide','baseline_blackslide']
        baseline_calibration_repetition = baseline_calibration_repetition
        exp_baseline_calibration = data.TrialHandler(baseline_sequence,nReps = baseline_calibration_repetition, method='sequential') #trial handler calls the sequence and displays it randomized
        exp.addLoop(exp_baseline_calibration) #add loop of block to experiment handler - any data that is collected  will be transfered to experiment handler automatically

        send_trigger('baseline_calibration')
        print('START OF BASELINE CALIBRATION PHASE')

        for baseline_trial in baseline_sequence:

            if baseline_trial == 'baseline':

                #create data
                timestamp = time.time() #epoch
                timestamp_exp = getTime() #time since start of experiment - also recorded by eyetracker

                #present baseline
                send_trigger('baseline')
                [stimulus_duration, offset_duration, pause_duration, nodata_duration] = fixcross_gazecontingent(baseline_duration)

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

                #create data
                timestamp = time.time() #epoch
                timestamp_exp = getTime() #time since start of experiment - also recorded by eyetracker

                #present baseline - but with white background
                send_trigger('baseline_whiteslide')
                [stimulus_duration, offset_duration, pause_duration, nodata_duration] = fixcross_gazecontingent(baseline_duration, background_color = white_slide)

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
                [stimulus_duration, offset_duration, pause_duration, nodata_duration] = fixcross_gazecontingent(baseline_duration, background_color = black_slide, cross_color = 'grey')

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


""" wrap-up and close """

#send trigger that experiment has ended
send_trigger('experiment_end')

tracker.setRecordingState(False) #close reading from eyetracker
io.quit() #close iohub instance


# dataFile.close() #close file
mywin.close()
core.quit()


#draw the stimuli and update the window
# stimulus_frames = round(stimulus_duration_in_seconds/refresh_rate)
# for frameN in range(stimulus_frames):   # For exactly 30 frames on a 60Hz display ~ 500ms
#     grating.setPhase(0.05, '+')#advance phase by 0.05 of a cycle
#     grating.draw()
#     fixation.draw()
#     mywin.flip()
#
#     if len(event.getKeys())>0:
#         break
#     event.clearEvents()

#pause, so you get a chance to see it!
#core.wait(5.0)
