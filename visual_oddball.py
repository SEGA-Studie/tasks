'''VISUAL ODDBALL TASK'''

"""load modules"""
from psychopy import visual, core, event, clock, data, gui, monitors
from psychopy.tools.filetools import fromFile, toFile #filesystem
#import psychtoolbox as ptb #sound processing via ptb
import random, time, sys, numpy

#import iohub that controls eyetracker
from psychopy.iohub import launchHubServer
from psychopy.core import getTime, wait

#read keyboard
from psychopy.hardware import keyboard

'''setup'''
#path to data
path_to_data = "C:/Users/Nico/PowerFolders/project_py_oddball/data/visual_oddball/"
trials_data_folder = path_to_data + 'trialdata/'
eyetracking_data_folder = path_to_data + 'eyetracking/'

#experimental settings
background_color_rgb = (0, 0, 0) #grey as float [-1,1]
number_of_practice_trials = 15
ISI_interval = [1800, 2000]
stimulus_duration_in_seconds = 2
baseline_duration = 1

standard_ball_color = (128, 0, 128) #purple
size_fixation_cross_in_pixels = 132 #also defines standard stimulus size ~ translates to 3.2 degrees visual angle on 24 inch screen with 25.59 inches screen distance- see https://elvers.us/perception/visualAngle/
gaze_offset_cutoff = 2 * size_fixation_cross_in_pixels

high_salience_ball_size = round(0.5 * size_fixation_cross_in_pixels) #~ translates to 1.6 degrees visual angle on 24 inch screen with 25.59 inches screen distance
low_salience_ball_size = round(0.91 * size_fixation_cross_in_pixels) #~ translates to 2.9 degrees visual angle on 24 inch screen with 25.59 inches screen distance

#define experimental settings as dictonary
settings = {} #create a dictonary - all values added to this dictonary will be stored automatically for each trial
settings['id'] = 123 #default testing value
settings['group'] = ['ASD', 'TD']

# - present a dialogue to change params
dlg = gui.DlgFromDict(settings,title='visual oddball')
if dlg.OK:
    print('EXPERIMENT IS STARTED')
    #core.wait(5)
else:
    core.quit()  # the user hit cancel so exit

# - make a text file to save data
fileName = str(settings['id']) + '_' + data.getDateStr(format="%Y-%m-%d-%H%M")

#define experiment handler - automatically saves experiment data
exp = data.ExperimentHandler(
    name="visual_oddball",
    version='0.1',
    extraInfo = settings, #experiment info
    dataFileName = trials_data_folder + fileName, # where to save the data
    )

#define monitor
mon = monitors.Monitor(name = 'default',
                       width = 70, #in cm
                       distance = 65) #in cm, distance from screen - ~ 25.59 inches

#create display window
#CAVE: Avoid integrated graphics for experiment computers wherever possible as no accurate frame timing
#CAVE: set Windows scaling to 100% - otherwise onscreen units will not get right
#NOTE: experiment screen will be FUllHD, thus testscreen is specified accordingly
mywin = visual.Window(size=[1920,1080],
                      #pos=[0,0],
                      #fullscr=True,
                      monitor=mon,
                      color = background_color_rgb,
                      screen=0,
                      units="pix") #unit changed to pixel so that eye tracker outputs pixel on presentation screen

refresh_rate = mywin.monitorFramePeriod #get monitor refresh rate in seconds
print('monitor refresh rate: ' + str(round(refresh_rate, 3)) + ' seconds')

#setup eyetracking
#CAVE: difference to psychopy documentation required: - define name as tracker - define presentation window before
iohub_config = {'eyetracker.hw.mouse.EyeTracker': {'name': 'tracker'}} #use mouse as eyetracker
io = launchHubServer(**iohub_config, #creates a separate instance that records eye tracking data outside loop
                        experiment_code = eyetracking_data_folder,
                        session_code = fileName,
                        datastore_name = eyetracking_data_folder + fileName, #where data is stored
                        window = mywin)
tracker = io.devices.tracker #calls the eyetracker device
#---> start recording
tracker.setRecordingState(True)

##setup keyboard --> check for keypresses
kb = keyboard.Keyboard()

'''functions'''
# define a fixation cross from lines - alternative definition
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

#draw figure - when gaze is offset - for gaze contincency
def draw_gazedirect():
    #parameters
    function_color = 'red'
    arrow_size_pix = size_fixation_cross_in_pixels
    arrow_pos_offset = 3
    width = 3

    rect1 = visual.Rect(win=mywin, units='pix', lineColor=function_color, fillColor = background_color_rgb, lineWidth=width, size = size_fixation_cross_in_pixels*2)

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

#stimulus for manipulation
def draw_ball(size,ball_color=standard_ball_color):
    circle1 = visual.Circle(win=mywin,
                            radius=size,
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
        dlg = gui.Dlg(title='Quit?', labelButtonOK=' OK ', labelButtonCancel=' Cancel ')
        dlg.addText('Do you really want to quit? - Then press OK')
        ok_data = dlg.show()  # show dialog and wait for OK or Cancel
        if dlg.OK:  # or if ok_data is not None
            print('EXPERIMENT ABORTED!')
            core.quit()
        else:
            print('Experiment continues...')
        pause_time = clock.getTime() - timestamp_keypress

    elif 'p' in keys:
        dlg = gui.Dlg(title='Pause', labelButtonOK='Continue')
        dlg.addText('Experiment is paused - Press Continue, when ready')
        ok_data = dlg.show()  # show dialog and wait for OK
        pause_time = clock.getTime() - timestamp_keypress

    else:
        pause_time = 0

    pause_time = round(pause_time,3)
    return pause_time

#check for the offset of gaze from the center screen
def check_gaze_offset():
    #check gaze
    gaze_position = tracker.getPosition()
    gaze_center_offset = numpy.sqrt((gaze_position[0])**2 + (gaze_position[1])**2) #pythagoras theorem

    if gaze_center_offset >= gaze_offset_cutoff:
        offset_boolean = True
        #print('center offset:' + str(gaze_center_offset)) #testing
    else:
        offset_boolean = False
    return offset_boolean

#fixation cross - and check for screen center gaze
def fixcross_gazecontingent(duration_in_seconds, background_color=background_color_rgb):
    #translate duration to number of frames
    number_of_frames = round(duration_in_seconds/refresh_rate)
    timestamp = getTime()
    gaze_offset_duration = 0
    pause_duration = 0
    #present cross for number of frames
    for frameN in range(number_of_frames):

        #check for keypress
        pause_duration += check_keypress()

        #check for gaze
        if check_gaze_offset():
            print('warning: gaze offset')

            frameN = 1 #reset duration of for loop - resart ISI

            while check_gaze_offset():

                #listen for keypress
                pause_duration += check_keypress()

                draw_gazedirect() #redirect attention to fixation cross area
                mywin.flip() #wait for monitor refresh time
                gaze_offset_duration += refresh_rate


        #draw fixation cross -
        draw_fixcross(background_color)
        mywin.flip()

    #generate output info
    actual_fixcross_duration = round(getTime()-timestamp,3)
    gaze_offset_duration = round(gaze_offset_duration,3)

    #testing:
    print('numberof frames: ' + str(number_of_frames))
    print('gaze offset duration: ' + str(gaze_offset_duration))
    print('actual fixcross duration: ' + str(actual_fixcross_duration))
    print('pause duration: ' + str(pause_duration))
    #print("timing offset:",duration_in_seconds-(clock.getTime()-timestamp)) #test timing offset

    return [actual_fixcross_duration, gaze_offset_duration, pause_duration]

#stimulus presentation
def present_stimulus(duration_in_seconds,trial,utility='low',salience='high'):

    number_of_frames = round(duration_in_seconds/refresh_rate) #translate duration to number of frames

    if trial == 'standard':
        ball_size = size_fixation_cross_in_pixels
    elif trial == 'oddball' and salience == 'low':
        ball_size = low_salience_ball_size
    elif trial == 'oddball' and salience == 'high':
        ball_size = high_salience_ball_size

    #present cross for number of frames
    timestamp = clock.getTime()
    for frameN in range(number_of_frames):
        #central fixation cross
        draw_ball(ball_size) #draw fixcross during stimulus presentation
        mywin.flip()

        #until keypress or maximum_duration
        #feedback

    #function output

    #return salience and utility

    actual_stimulus_duration = round(clock.getTime()-timestamp,3)
    print(trial + " duration:",actual_stimulus_duration)
    return actual_stimulus_duration



#random interstimulus interval
def define_ISI_interval():
    ISI = random.randint(ISI_interval[0], ISI_interval[1])
    ISI = ISI/1000 #get to second format
    return ISI



"""experimental design """

phase_sequence = ['baseline','practice_trials']
phase_handler = data.TrialHandler(phase_sequence,nReps = 1, method='sequential') #trial handler calls the sequence and displays it randomized
exp.addLoop(phase_handler) #add loop of block to experiment handler - any data that is collected  will be transfered to experiment handler automatically

#define global variables
block_counter = 0
oddball_trial_counter = 1
manipulation_trial_counter = 1
baseline_trial_counter = 1

for phase in phase_handler:

    if phase == 'baseline':

        print('START OF BASELINE PHASE')

        #create data
        timestamp = time.time() #epoch
        timestamp_exp = getTime() #time since start of experiment - also recorded by eyetracker

        #present baseline
        [stimulus_duration, offset_duration, pause_duration] = fixcross_gazecontingent(baseline_duration)

        #collect global data --> saved to csv
        phase_handler.addData('phase', phase)
        phase_handler.addData('block_counter', block_counter)

        phase_handler.addData('stimulus_duration', stimulus_duration)
        phase_handler.addData('gaze_offset_duration', offset_duration)
        phase_handler.addData('trial_pause_duration', pause_duration)

        phase_handler.addData('baseline_trial_counter',baseline_trial_counter)
        phase_handler.addData('trial', phase)
        phase_handler.addData('timestamp', timestamp)
        phase_handler.addData('timestamp_exp', timestamp_exp)

        baseline_trial_counter += 1

        exp.nextEntry()

    if phase == 'practice_trials':

        #setup oddbal trials
        practice_sequence = ['standard','standard','oddball'] #define a sequence for trial handler - 1/5 chance for an oddball
        number_of_repetitions = round(number_of_practice_trials/len(practice_sequence))
        practice_trials = data.TrialHandler(practice_sequence,nReps = number_of_repetitions, method='random') #trial handler calls the sequence and displays it randomized
        exp.addLoop(practice_trials) #add loop of block to experiment handler - any data that is collected  by trials will be transfered to experiment handler automatically

        # Inform the ioHub server about the TrialHandler - could not get this to work
        #io.createTrialHandlerRecordTable(trials)

        print('START OF PRACTICE TRIAL BLOCK')

        for practice_trial in practice_trials:

            #create data
            ISI = define_ISI_interval() #for each trial separately
            timestamp = time.time() #epoch
            timestamp_exp = getTime() #time since start of experiment - also recorded by eyetracker

            #print for testing
            print('NEW TRIAL')
            print("ISI: ",ISI)
            print("gaze position: ",tracker.getPosition())

            #stimulus presentation
            #[actual_stimulus_duration] = present_stimulus(stimulus_duration_in_seconds,trial=practice_trial)
            present_stimulus(stimulus_duration_in_seconds,trial=practice_trial)

            #ISI
            #fixcross(ISI)
            [fixcross_duration, offset_duration, pause_duration] = fixcross_gazecontingent(ISI)
            #print('trial was paused:' + str(trial_paused))



""" wrap-up and close """
tracker.setRecordingState(False) #close reading from eyetracker
io.quit() #close iohub instance


# dataFile.close() #close file
mywin.close()
core.quit()
