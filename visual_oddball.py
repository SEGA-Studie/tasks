'''VISUAL ODDBALL TASK'''
# For further information see README.md.

'''LOAD MODULES'''
# Core libraries
from matplotlib.pyplot import draw
from psychopy import visual, core, event, clock, data, gui, monitors, parallel
from psychopy.tools.filetools import fromFile, toFile
import random, time, numpy
# For controlling eyetracker and eye-tracking SDK
import tobii_research
from psychopy.iohub import launchHubServer
# For getting keyboard input
from psychopy.hardware import keyboard
# Library for managing paths
from pathlib import Path
# Miscellaneous: Hide messages in console from pygame:
from os import environ 
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1' 
import statistics

print("THIS IS VISUAL ODDBALL.")

'''SETUP'''
# Path to output data:
path_to_data = Path("Desktop", "tasks", "data", "visual_oddball").resolve()
trials_data_folder = Path(path_to_data, 'trialdata')
eyetracking_data_folder = Path(path_to_data, 'eyetracking')
print(trials_data_folder)
print(eyetracking_data_folder)

# Testmode.
# TRUE mimicks an eye-Ttracker by mouse movement, FALSE = eye-tracking hardware is required.
testmode = True

# Experimental settings:
presentation_screen = 0 # stimuli are presented on internal screen 0.
number_of_repetitions = 2
number_of_practice_trials = 10
stimulus_duration_in_seconds = 0.075
standard_ball_color = (128, 0, 128)
size_fixation_cross_in_pixels = 60
standard_ball_size = size_fixation_cross_in_pixels
high_salience_ball_size = round(0.5 * size_fixation_cross_in_pixels)
low_salience_ball_size = round(0.75 * size_fixation_cross_in_pixels)
ISI_interval = [2250, 2500]
gaze_offset_cutoff = 3 * size_fixation_cross_in_pixels
background_color_rgb = (0, 0, 0) # grey
white_slide = 'white'
black_slide = 'black'
baseline_duration = 5 # in seconds, duration of baseline screen, target: 10.
#  After 500ms the no data detection warning should be displayed on screen.
no_data_warning_cutoff = 0.5
# One baseline assessment (black and white screen) at the beginning of the experiment.
baseline_calibration_repetition = 1
# Settings are stored automatically for each trial.
settings = {}

# EEG trigger variables. 10ms duration of trigger signal:
pulse_duration = 0.01 
parallel_port_adress = 0x03FF8

# Presenting a dialog box. Infos are added to "settings".
# id = 123 is used as default testing value.
settings['id'] = 123
settings['group'] = ['ASD', 'TD']
dlg = gui.DlgFromDict(settings, title = 'Visual Oddball')
if dlg.OK:
    print('EXPERIMENT IS STARTED')
else:
    core.quit()  # the user hit cancel to exit

# Name for output data.
fileName = str(settings['id']) + '_' + data.getDateStr(format="%Y-%m-%d-%H%M")

# Experiment handler saves experiment data automatically.
exp = data.ExperimentHandler(
    name = "visual_oddball",
    version = '0.1',
    extraInfo = settings,
    dataFileName = str(trials_data_folder / fileName),
    )
str(trials_data_folder / fileName),

# Monitor seettings: Distance is from screen in cm.
mon = monitors.Monitor(
    name = 'eizo_eyetracker',
    width = 29.6,
    distance = 65) 

# Create display window.
# Unit is changed to pixel so that eye tracker outputs pixel on presentation screen.
mywin = visual.Window(
    size = [1920,1080],
    fullscr = True,
    monitor = mon,
    color = background_color_rgb,
    screen = presentation_screen,
    units = "pix") 

# Get monitor refresh rate in seconds:
refresh_rate = mywin.monitorFramePeriod 
print('monitor refresh rate: ' + str(round(refresh_rate, 3)) + ' seconds')

# SETUP EYETRACKING
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
                        datastore_name = str(eyetracking_data_folder / fileName),
                        window = mywin)

# Call the eyetracker device and start recording:
tracker = io.devices.tracker
tracker.setRecordingState(True)

#SETUP PARALLEL PORT TRIGGER
# List position defines trigger value that is sent, see function send_trigger(),
# i.e. list position 2 will send a trigger with value "S2".
trigger_name_list = ['PLACEHOLDER', #0
                     'trial', #1 -
                     'standard', #2 -
                     'oddball', #3 -
                     'ISI', #4-
                     'baseline', #5 -
                     'experiment_start', #6 -
                     'experiment_end', #7 -
                     'pause_initiated', #8 -
                     'pause_ended', #9 -
                     'experiment_aborted', #10 -
                     'baseline_calibration', #11 -
                     'baseline_whiteslide', #12 -
                     'baseline_blackslide', #13 -
                     'oddball_block', #14 -
                     'practice_trial', #15 -
                     'practice_trials' #16 -
                     ]

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
                # Wait for pulse duration:
                time.sleep(pulse_duration)
                port.setData(0)
            if testmode:
                print('sent DUMMY trigger S' + str(trigger_value))
            trigger_name_found = True
    if not trigger_name_found:
         print('trigger name is not defined: ' + trigger_name)

# Draw instruction slides:
def draw_instruction(text, background_color = background_color_rgb):
    if background_color is not background_color_rgb:
        background_rect = visual.Rect(
            win = mywin,
            size = mywin.size,
            fillColor = background_color)
        background_rect.draw()

    instruction_slide = visual.TextStim(
        win = mywin,
        text = text,
        color = 'black',
        units = 'pix',
        wrapWidth = 900,
        height = size_fixation_cross_in_pixels)
    instruction_slide.draw()

# Draw fixation cross from lines:
def draw_fixcross(
    background_color = background_color_rgb,
    cross_color = 'black'):
    if background_color is not background_color_rgb:
        background_rect = visual.Rect(
            win = mywin,
            size = mywin.size,
            fillColor = background_color)
        background_rect.draw()
    line1 = visual.Line(win = mywin, units = 'pix', lineColor = cross_color) 
    line1.start = [-(size_fixation_cross_in_pixels/2), 0]
    line1.end = [+(size_fixation_cross_in_pixels/2), 0]
    line2 = visual.Line(win = mywin, units = 'pix', lineColor = cross_color) 
    line2.start = [0, -(size_fixation_cross_in_pixels/2)]
    line2.end = [0, +(size_fixation_cross_in_pixels/2)]
    line1.draw()
    line2.draw()

# Draw figure when gaze is offset for gaze contincency:
def draw_gazedirect(background_color = background_color_rgb):
        # Adapt background according to privuded "background color"
    if background_color is not background_color_rgb:
        background_rect = visual.Rect(
            win = mywin,
            size = mywin.size,
            fillColor = background_color)
        background_rect.draw()
    # Parameters:
    function_color = 'red'
    arrow_size_pix = size_fixation_cross_in_pixels
    arrow_pos_offset = 5
    width = 3

    rect1 = visual.Rect(
        win = mywin,
        units = 'pix',
        lineColor = function_color,
        fillColor = background_color,
        lineWidth = width,
        size = size_fixation_cross_in_pixels*6)

    # Arrow left:
    al_line1 = visual.Line(win = mywin, units = 'pix', lineColor=function_color, lineWidth=width)
    al_line1.start = [-(arrow_size_pix*arrow_pos_offset), 0]
    al_line1.end = [-(arrow_size_pix*arrow_pos_offset-arrow_size_pix), 0]
    al_line2 = visual.Line(win = mywin, units = 'pix', lineColor = function_color, lineWidth=width)
    al_line2.start = [-(arrow_size_pix*arrow_pos_offset-(arrow_size_pix/2)), -arrow_size_pix/2]
    al_line2.end = [-(arrow_size_pix*arrow_pos_offset-arrow_size_pix), 0]
    al_line3 = visual.Line(win = mywin, units = 'pix', lineColor=function_color, lineWidth=width)
    al_line3.start = [-(arrow_size_pix*arrow_pos_offset-(arrow_size_pix/2)), +arrow_size_pix/2]
    al_line3.end = [-(arrow_size_pix*arrow_pos_offset-arrow_size_pix), 0]

    # Arrow right:
    ar_line1 = visual.Line(win = mywin, units = 'pix', lineColor = function_color, lineWidth = width)
    ar_line1.start = [+(arrow_size_pix*arrow_pos_offset), 0]
    ar_line1.end = [+(arrow_size_pix*arrow_pos_offset-arrow_size_pix), 0]
    ar_line2 = visual.Line(win = mywin, units='pix', lineColor = function_color, lineWidth = width)
    ar_line2.start = [+(arrow_size_pix*arrow_pos_offset-(arrow_size_pix/2)), -arrow_size_pix/2]
    ar_line2.end = [+(arrow_size_pix*arrow_pos_offset-arrow_size_pix), 0]
    ar_line3 = visual.Line(win = mywin, units = 'pix', lineColor = function_color, lineWidth = width)
    ar_line3.start = [+(arrow_size_pix*arrow_pos_offset-(arrow_size_pix/2)), +arrow_size_pix/2]
    ar_line3.end = [+(arrow_size_pix*arrow_pos_offset-arrow_size_pix), 0]

    # Arrow top:
    at_line1 = visual.Line(win = mywin, units='pix', lineColor = function_color, lineWidth = width)
    at_line1.start = [0, +(arrow_size_pix*arrow_pos_offset)]
    at_line1.end = [0, +(arrow_size_pix*arrow_pos_offset-arrow_size_pix)]
    at_line2 = visual.Line(win = mywin, units = 'pix', lineColor = function_color, lineWidth = width)
    at_line2.start = [-arrow_size_pix/2, +(arrow_size_pix*arrow_pos_offset-(arrow_size_pix/2))]
    at_line2.end = [0, +(arrow_size_pix*arrow_pos_offset-arrow_size_pix)]
    at_line3 = visual.Line(win = mywin, units = 'pix', lineColor = function_color, lineWidth = width)
    at_line3.start = [+arrow_size_pix/2, +(arrow_size_pix*arrow_pos_offset-(arrow_size_pix/2))]
    at_line3.end = [0, +(arrow_size_pix*arrow_pos_offset-arrow_size_pix)]

    # Arrow bottom:
    ab_line1 = visual.Line(win = mywin, units = 'pix', lineColor = function_color, lineWidth=width)
    ab_line1.start = [0, -(arrow_size_pix*arrow_pos_offset)]
    ab_line1.end = [0, -(arrow_size_pix*arrow_pos_offset-arrow_size_pix)]
    ab_line2 = visual.Line(win = mywin, units = 'pix', lineColor = function_color, lineWidth = width)
    ab_line2.start = [+arrow_size_pix/2, -(arrow_size_pix*arrow_pos_offset-(arrow_size_pix/2))]
    ab_line2.end = [0, -(arrow_size_pix*arrow_pos_offset-arrow_size_pix)]
    ab_line3 = visual.Line(win = mywin, units = 'pix', lineColor = function_color, lineWidth = width)
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
def draw_nodata_info(background_color = background_color_rgb):
    # Adapt background according to privuded "background color":
    if background_color is not background_color_rgb:
        background_rect = visual.Rect(
            win = mywin,
            size = mywin.size,
            fillColor = background_color)
        background_rect.draw()

    no_data_warning = visual.TextStim(
        win = mywin,
        text = 'NO EYES DETECTED!',
        color = 'red',
        units = 'pix',
        height = size_fixation_cross_in_pixels)
    no_data_warning.draw()

# Check for keypresses, used to pause and quit experiment:
def check_keypress():
    keys = kb.getKeys(['p','escape'], waitRelease = True)
    timestamp_keypress = clock.getTime()

    if 'escape' in keys:
        send_trigger('pause_initiated')
        dlg = gui.Dlg(title = 'Quit?', labelButtonOK = ' OK ', labelButtonCancel = ' Cancel ')
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
        dlg = gui.Dlg(title = 'Pause', labelButtonOK = 'Continue')
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
    gaze_center_offset = numpy.sqrt((gaze_position[0])**2 + (gaze_position[1])**2) # Pythagoras theorem

    if gaze_center_offset >= gaze_offset_cutoff:
        offset_boolean = True
    else:
        offset_boolean = False
    return offset_boolean

# Fixation cross: Check for data availability and screen center gaze.
def fixcross_gazecontingent(duration_in_seconds, background_color = background_color_rgb, cross_color = 'black'):
    # Translate duration to number of frames:
    number_of_frames = round(duration_in_seconds/refresh_rate)
    timestamp = core.getTime()
    gaze_offset_duration = 0
    pause_duration = 0
    nodata_duration = 0 
    # Variables contain all space bar presses in a single trial.
    responses_timestamp = list() # since experiment start
    responses_rt = list() # since trial start
    # Present cross for number of frames:
    for frameN in range(number_of_frames):
        # Check for space bar presses during practice trials and oddball blocks:
        # In the end of the practice trials the median of all reaction times is calculated for each subject individually.
        responses = kb.getKeys([' '], waitRelease = True)
        response_timestamp = core.getTime()
        if ' ' in responses:
            for response in responses:
                responses_timestamp.append(response_timestamp)
                responses_rt.append(response.rt)
                print('RESPONSE: [{}] [{}] ({})'.format(response_timestamp, response.name, response.rt))

        # Check for keypress
        pause_duration += check_keypress()
        gaze_position = tracker.getPosition()
        # Check for eyetracking data:
        if check_nodata(gaze_position):
            print('warning: no eyes detected')
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
        draw_fixcross(background_color, cross_color)
        mywin.flip()

    # Generate output info:
    actual_fixcross_duration = round(core.getTime()-timestamp,3)
    gaze_offset_duration = round(gaze_offset_duration,3)
    nodata_duration = round(nodata_duration,3)

    # Testing:
    print('number of frames: ' + str(number_of_frames))
    print('no data duration: ' + str(nodata_duration))
    print('gaze offset duration: ' + str(gaze_offset_duration))
    print('pause duration: ' + str(pause_duration))
    print('actual fixcross duration: ' + str(actual_fixcross_duration))
    print("timing offset:",duration_in_seconds-(clock.getTime()-timestamp)) # test timing offset

    return [actual_fixcross_duration, gaze_offset_duration, pause_duration, nodata_duration, responses_timestamp, responses_rt]

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
    timestamp = clock.getTime()
    print('presenting ball: {} {} {}'.format(duration, trial, salience))
    for frameN in range(number_of_frames):
        draw_ball(size = size)
        mywin.flip()
    print('presented ball')
    # Calculate actual stimulus duration and return salience and utility:
    actual_stimulus_duration = round(clock.getTime()-timestamp,3)
    print(trial + " duration:",actual_stimulus_duration)
    return actual_stimulus_duration

# Random Interstimulus Interval (ISI):
def define_ISI_interval():
    ISI = random.randint(ISI_interval[0], ISI_interval[1])
    ISI = ISI/1000 # ms -> s
    return ISI

'''EXPERIMENTAL DESIGN'''
# The trial handler calls the sequence and displays it randomized.
# Loop of block is added to experiment handler.
# Any data that is collected  will be transfered to experiment handler automatically.
# Oddballs are defined as strings. 1st place is u, 2nd is s:
oddballs = ['oddball_++', 'oddball_+-', 'oddball_-+', 'oddball_--']
practoddballs = ['practoddball_++', 'practoddball_+-', 'practoddball_-+', 'practoddball_--']

random.shuffle(oddballs)
random.shuffle(practoddballs)
print(practoddballs)

phase_sequence = [
    'instruction1',
    'baseline_calibration',
    'instruction2',
    'baseline',
    practoddballs[0],
    'baseline',
    practoddballs[1],
    'baseline',
    practoddballs[2],
    'baseline',
    practoddballs[3],
    'instruction3',
    'baseline',
    oddballs[0],
    'baseline', 
    oddballs[1],
    'baseline',
    oddballs[2],
    'baseline',
    oddballs[3],
    'instruction4'
    ]

phase_handler = data.TrialHandler(phase_sequence,nReps = 1, method = 'sequential')
exp.addLoop(phase_handler)

# Define global variables:
block_counter = 0
oddball_trial_counter = 1
manipulation_trial_counter = 1
baseline_trial_counter = 1
practice_trial_counter = 1
all_responses = list()

# Send trigger:
send_trigger('experiment_start')

for phase in phase_handler:
    block_counter += 1

    if phase == 'instruction1':
        text_1 = "Das Experiment beginnt jetzt.\nBitte bleibe still sitzen und\nschaue auf das Kreuz in der Mitte.\n\n Weiter mit der Leertaste."
        print('SHOW INSTRUCTION SLIDE 1')
        draw_instruction(text = text_1)
        mywin.flip()
        keys = event.waitKeys(keyList = ["space"])
        exp.nextEntry
    
    if phase == 'instruction2':
        text_2 = "Gleich startet die Übung.\nDrücke bei auffälligen Kreisen\nmöglichst schnell die Leertaste.\n\nWeiter geht es mit der Leertaste."
        print('SHOW INSTRUCTIONS SLIDE 2')
        draw_instruction(text = text_2)
        mywin.flip()
        keys = event.waitKeys(keyList = ["space"])
        exp.nextEntry

    if phase == 'instruction3':
        # Calculating median of reaction times in practice trials for each subject individually: 
        responses_median = statistics.median(all_responses)
        print('MEDIAN = ' , responses_median)
        # Showing instruction slide:
        text_3 = "Die Übung ist beendet.\nBitte bleibe still sitzen.\n\nGleich beginnt die Aufgabe."
        print('SHOW INSTRUCTION SLIDE 3')
        draw_instruction(text = text_3)
        mywin.flip()
        keys = event.waitKeys(keyList = ["space"])
        exp.nextEntry
    
    if phase == 'instruction4':
        text_4 = "Das Experiment ist jetzt beendet.\nBitte bleibe noch still sitzen."
        print('SHOW INSTRUCTION SLIDE 4')
        draw_instruction(text = text_4)
        mywin.flip()
        keys = event.waitKeys(keyList = ["space"])
        exp.nextEntry

    if phase.startswith('oddball_'):
        # Common oddball setup.
        oddball_parameters = phase.split('_')[1] # remove the 'oddball_' portion of the phase name
        (u, s) = oddball_parameters # u = utility; s = slience
        
        # Sequence for trial handler with 1/5 chance for an oddball.
        stimulus_sequence = ['standard','standard','standard','standard','oddball']

        # Trial handler calls the sequence and displays it randomized:
        trials = data.TrialHandler(stimulus_sequence,nReps = number_of_repetitions, method = 'random')
        # Add loop of block to experiment handler. Any collected data will be transfered to experiment handler automatically.
        exp.addLoop(trials)
        # Onset of oddball block:
        send_trigger('oddball_block')
        print('START OF ODDBALL BLOCK')

        if u == '+':
            text_high_utility = "Im folgenden Block kannst du\n für jede schnelle Reaktion\n10 Cent gewinnen."
            print('SHOW HIGH TILITY SLIDE')
            draw_instruction(text = text_high_utility)
            mywin.flip()
            core.wait(7)
        
        if u == '-':
            text_low_utility = "Jetzt kannst du nicht gewinnen.\n Drücke trotzdem so schnell zu kannst!"
            print('SHOW LOW UTILITY SLIDE')
            draw_instruction(text = text_low_utility)
            mywin.flip()
            core.wait(7)

        for trial in trials:
            send_trigger('trial')
            ISI = define_ISI_interval() # jittery ISI for each trial separately
            timestamp = time.time() # epoch
            timestamp_exp = core.getTime() # time since start of experiment - also recorded by eyetracker
            timestamp_tracker = tracker.trackerTime()
            print('NEW TRIAL')
            print("ISI: ", ISI)
            print("gaze position: ", tracker.getPosition())
            # Reset keyboard clock to get reaction times relative to each trial start.
            kb.clock.reset()
            # stimulus presentation
            send_trigger('trial')
            actual_stimulus_duration = present_ball(duration = stimulus_duration_in_seconds, trial = trial, salience = s)
            send_trigger('ISI')
            [fixcross_duration, offset_duration, pause_duration, nodata_duration, responses_timestamp, responses_rt] = fixcross_gazecontingent(ISI)

            # In high utility oddball blocks: Feedback for subject:
            feedback = " "
            if trial == 'oddball' and u == '+':
                text_feedback_pos = "Gut gemacht!\nDu hast 10 Cent gewonnen!"
                text_feedback_neg = "Leider keine Belohnung."
                if not responses_rt:
                    feedback = 'no response given'
                    print('SHOW FEEDBACK SLIDE: NEGATIVE FEEDBACK')
                    draw_instruction(text = text_feedback_neg)
                    mywin.flip()
                    core.wait(3)
                elif responses_rt[0] <= responses_median:
                    feedback = 'correct response'
                    print('SHOW FEEDBACK SLIDE: POSITIVE FEEDBACK')
                    draw_instruction(text = text_feedback_pos)
                    mywin.flip()
                    core.wait(3)
                elif responses_rt[0] > responses_median:
                    feedback = 'response too slow'
                    print('SHOW FEEDBACK SLIDE: NEGATIVE FEEDBACK')
                    draw_instruction(text = text_feedback_neg)
                    mywin.flip()
                    core.wait(3)
               
            # Save data in .csv file:
            # Information about each phase:
            phase_handler.addData('phase', phase)
            phase_handler.addData('block_counter', block_counter)
            phase_handler.addData('responses_median', responses_median)
            #  Information about each trial in an oddball phase:
            trials.addData('trial', trial)
            trials.addData('oddball_trial_counter', oddball_trial_counter)
            trials.addData('stimulus_duration', actual_stimulus_duration)
            trials.addData('ISI_expected', ISI)
            trials.addData('ISI_duration',fixcross_duration)
            trials.addData('gaze_offset_duration', offset_duration)
            trials.addData('trial_pause_duration', pause_duration)
            trials.addData('trial_nodata_duration', nodata_duration)
            trials.addData('responses_timestamp', responses_timestamp)
            trials.addData('responses_rt', responses_rt)
            trials.addData('timestamp', timestamp)
            trials.addData('timestamp_exp', timestamp_exp)
            trials.addData('timestamp_tracker', timestamp_tracker)
            trials.addData('feedback', feedback)
           
            
            oddball_trial_counter += 1
            exp.nextEntry()

    if phase == 'baseline':
        send_trigger('baseline')
        print('START OF BASELINE PHASE')
        # create data
        timestamp = time.time() # epoch
        # Time since start of experiment, is also recorded by eyetracker.
        timestamp_exp = core.getTime() 
        # present baseline
        [stimulus_duration, offset_duration, pause_duration, nodata_duration, responses_timestamp, responses_rt] = fixcross_gazecontingent(baseline_duration)
        # Collected global data is savd to output file:
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

    if phase.startswith('practoddball_'):
        practice_parameters = phase.split('_')[1]
        (u, s) = practice_parameters
        correct_responses = list()
        
        # Define a sequence for trial handler with 1/5 chance for an oddball.
        practice_sequence = ['standard','standard','standard','standard','oddball']
        number_of_repetitions = round(number_of_practice_trials/len(practice_sequence))

        # Trial handler calls the sequence and displays it randomized:
        practice_trials = data.TrialHandler(practice_sequence, nReps = number_of_repetitions, method = 'random')
        # Add loop of block to experiment handler. Any collected data by trials will be transfered to experiment handler automaticall.
        exp.addLoop(practice_trials) 
        # Onset of practice_trials:
        send_trigger('practice_trials')
        print('START OF PRACTICE TRIAL BLOCK')

        if u == '+':
            print('SHOW UTILITY SLIDE')
            text_high_utility = "Im folgenden Block kannst du\n für jede schnelle Reaktion\n10 Cent gewinnen."
            draw_instruction(text = text_high_utility)
            mywin.flip()
            core.wait(7)
        
        if u == '-':
            text_low_utility = "Jetzt kannst du nicht gewinnen.\n Drücke trotzdem so schnell zu kannst!"
            print('SHOW LOW UTILITY SLIDE')
            draw_instruction(text = text_low_utility)
            mywin.flip()
            core.wait(7)
        
        for practice_trial in practice_trials:
            # Send eeg trigger:
            send_trigger('practice_trial')
            ISI = define_ISI_interval()
            timestamp = time.time() #epoch
            # Time since start of experiment, is also recorded by eyetracker:
            timestamp_exp = core.getTime()
            timestamp_tracker = tracker.trackerTime()
            print('NEW PRACTICE TRIAL')
            print("ISI: ",ISI)
            print("gaze position: ",tracker.getPosition())
            # Reset keyboard clock to get reaction times relative to each trial start.
            kb.clock.reset()
            # In each trial, the stimulus (standard or oddball) and the fixcross ist presented:
            send_trigger('trial')
            actual_stimulus_duration = present_ball(duration = stimulus_duration_in_seconds, trial = practice_trial, salience = s)
            send_trigger('ISI')
            [fixcross_duration, offset_duration, pause_duration, nodata_duration, responses_timestamp, responses_rt] = fixcross_gazecontingent(ISI)
            if practice_trial == 'oddball' and len(responses_rt) != 0:
                for response_rt in responses_rt:
                    correct_responses.append(response_rt)

            # Save data in .csv file:
            # Information about each phase:
            phase_handler.addData('phase', phase)
            phase_handler.addData('block_counter', block_counter)
            # Information about each trial in phase:
            practice_trials.addData('practice_trial', practice_trial)
            practice_trials.addData('practice_trial_counter', practice_trial_counter) 
            practice_trials.addData('stimulus_duration', actual_stimulus_duration)
            practice_trials.addData('ISI_expected', ISI)
            practice_trials.addData('ISI_duration', fixcross_duration)
            practice_trials.addData('gaze_offset_duration', offset_duration)
            practice_trials.addData('trial_pause_duration', pause_duration)
            practice_trials.addData('trial_nodata_duration', nodata_duration)
            practice_trials.addData('responses_timestamp', responses_timestamp)
            practice_trials.addData('responses_rt', responses_rt)
            practice_trials.addData('timestamp', timestamp) 
            practice_trials.addData('timestamp_exp', timestamp_exp) 
            practice_trials.addData('timestamp_tracker', timestamp_tracker) 

            practice_trial_counter += 1
            exp.nextEntry() 

        for correct_response in correct_responses:
            all_responses.append(correct_response)
            print('CORRECT PRACTICE RESPONSES SO FAR: ', all_responses)
        
# During calibration process, pupil dilation (black slide) and
# pupil constriction (white slide) are assessed.
    if phase == 'baseline_calibration':
        baseline_sequence = ['baseline','baseline_whiteslide','baseline_blackslide']
        baseline_calibration_repetition = baseline_calibration_repetition
        exp_baseline_calibration = data.TrialHandler(baseline_sequence,nReps = baseline_calibration_repetition, method='sequential')
        # Baseline calibration block is added to loop.
        # Collected data will be transfered to experiment handler automatically:
        exp.addLoop(exp_baseline_calibration)

        send_trigger('baseline_calibration')
        print('START OF BASELINE CALIBRATION PHASE')

        for baseline_trial in baseline_sequence:
            if baseline_trial == 'baseline':
                timestamp = time.time() # Epoch
                # Time since start of experiment, is also recorded by eyetracker.
                timestamp_exp = core.getTime() 
                # Present baseline
                send_trigger('baseline')
                [stimulus_duration, offset_duration, pause_duration, nodata_duration, responses_timestamp, responses_rt] = fixcross_gazecontingent(baseline_duration)
                # Global data is saved to output file:
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
                timestamp = time.time() # Epoch
                # Time since start of experiment, is also recorded by eyetracker.
                timestamp_exp = core.getTime() 
                # Present baseline with white background:
                send_trigger('baseline_whiteslide')
                [stimulus_duration, offset_duration, pause_duration, nodata_duration, responses_timestamp, responses_rt] = fixcross_gazecontingent(
                    baseline_duration, background_color = white_slide)
                # Global data is saved to output file:
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
                exp.nextEntry()
            
            if baseline_trial == 'baseline_blackslide':
                timestamp = time.time() # Epoch
                # Time since start of experiment, is also recorded by eyetracker.
                timestamp_exp = core.getTime() 
                # Present baseline with black background:
                send_trigger('baseline_blackslide')
                [stimulus_duration, offset_duration, pause_duration, nodata_duration, responses_timestamp, responses_rt] = fixcross_gazecontingent(
                    baseline_duration, background_color = black_slide, cross_color = 'grey')

                # Global data is saved to output file:
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
                exp.nextEntry()

'''WRAP UP AND CLOSE'''
# Send trigger that experiment has ended:
send_trigger('experiment_end')
print('EXPERIMENT ENDED')
# Close reading from eyetracker:
tracker.setRecordingState(False) 
# Close iohub instance:
io.quit() 
# Close window:
mywin.close()
core.quit()