""" game.py
        1. Displays a pysimplegui window that has the user select an
            animal ID from a list in animal_ids_file using a mouse, then 
            closes when 'Run' is clicked

        2. Starts a pygame window that runs all of the tasks listed as active in
            the parameters_file, and uses their values to run the tasks. Tasks
            are played by using a joystick. Every trial is logged to a results file
            with the same name as the animal ID chosen.
"""

import os, pygame, re, sys, datetime, time, random

# pip install pysimplegui
import PySimpleGUI as sg

# pip install pygame --user
from pygame.locals import *
from pygame.compat import geterror

# try to initialize adafruit motorkit
try:
    # pip install adafruit-circuitpython-motorkit
    from adafruit_motorkit import MotorKit

# if PiHAT board is not connected
except NotImplementedError:
    # error popup and exit program
    sg.Popup('Error:', 'PiHAT board not setup properly')
    sys.exit()

# pip install adafruit-circuitpython-motor
from adafruit_motor import stepper

kit = MotorKit() # initialize stepper motor
motor_dir = 1 # direction motor is going in, 1 - forward, 0 - backward
dir_num = 0 # number of times motor has gone in this direction

# Animal IDS file to use for ID selection menu
animal_ids_file = 'AnimalIDs.txt'

# parameters file to use for running the game
parameters_file = 'parameters.txt'

main_dir = os.path.split(os.path.abspath(__file__))[0] # current starting directory, should be main/
data_dir = os.path.join(main_dir, 'data') # main/data
stimuli_dir = os.path.join(data_dir, 'stimuli') # main/data/stimuli

# keys to lookup the parameter values for each task
# *** Note Titration parameter currently does NOTHING and is not used at all ***
# TASKORDER is Series or Random
# ACTIVE and TITRATION are boolean True/False
# CIRCLE_SIZE is Small, Medium, or Large
# TRIALS, START_LEVEL, TRIALS_PER_PROB, NUM_PROBS are int numbers
# RESPONSE, TIMEOUT, PURSUIT_TIME, PERCENT are float numbers
general_parameters_keys = ['TASKORDER']
side_parameters_keys = ['ACTIVE', 'TRIALS', 'START_LEVEL', 'RESPONSE', 'TIMEOUT', 'TITRATION']
chase_parameters_keys = ['ACTIVE', 'TRIALS', 'CIRCLE_SIZE', 'RESPONSE', 'TIMEOUT', 'TITRATION']
pursuit_parameters_keys = ['ACTIVE', 'TRIALS', 'CIRCLE_SIZE', 'PURSUIT_TIME', 'RESPONSE', 'TIMEOUT', 'TITRATION']
mts_parameters_keys = ['ACTIVE', 'TRIALS', 'PERCENT', 'RESPONSE', 'TIMEOUT', 'TITRATION']
dmts_parameters_keys = ['ACTIVE', 'TRIALS', 'PERCENT', 'DELAY', 'RESPONSE', 'TIMEOUT', 'TITRATION']
ls_parameters_keys = ['ACTIVE', 'TRIALS_PER_PROB', 'NUM_PROBS', 'PERCENT', 'RESPONSE', 'TIMEOUT', 'TITRATION']

# generate the parameters dictionary for each task
general_parameters = dict.fromkeys(general_parameters_keys)
side_parameters = dict.fromkeys(side_parameters_keys)
chase_parameters = dict.fromkeys(chase_parameters_keys)
pursuit_parameters = dict.fromkeys(pursuit_parameters_keys)
mts_parameters = dict.fromkeys(mts_parameters_keys)
dmts_parameters = dict.fromkeys(dmts_parameters_keys)
ls_parameters = dict.fromkeys(ls_parameters_keys)

# list of tasks to run
task_list = ['']

RED = (255,0,0)
GREEN = (0,255,0)
BACKGROUND_COLOR = (250,250,250)

""" Function that dispenses 1 pellet using the stepper motor """
def pellet():
    # need to declare as global otherwise won't interpret properly
    global motor_dir
    global dir_num

    # 30 steps for one pellet dispensed
    for j in range(30):
      # pause inbetween the steps
        time.sleep(0.01)

        # motor direction of 1 is FORWARD, 0 is BACKWARD
        if motor_dir == 1:
            kit.stepper1.onestep(style=stepper.DOUBLE, direction=stepper.FORWARD)
        else:
            kit.stepper1.onestep(style=stepper.DOUBLE, direction=stepper.BACKWARD)
    
    # every 5 pellets dispensed, switch motor directions
    dir_num += 1
    if dir_num > 5:
        dir_num = 0
        motor_dir = motor_dir * -1

""" Function to read a parameter from a given array of text and return its value
    @param name of the parameter to search for
    @param parameters array of text to search 
    @return the value of the parameter found """
def read_parameter(name, parameters):
    # loop through every text line in parameters
    for i in range(0, len(parameters)):
        # search for the name and ignore upper/lower case
        if re.search(name, parameters[i], re.IGNORECASE):
            # return the value of the parameter which is on the next line after our found name
            return parameters[i + 1].rstrip('\n')

    # if not found, return an error popup and exit program
    sg.Popup('Error:', '\"' + name + '\" parameter does not exist in input file \"' + parameters_file + '\"')
    sys.exit()

""" Function to load all of the task parameter dictionaries from the file passed in
    @param filename of the parameter file to use """
def load_and_check_params(filename):
    # make sure file exists in main/ directory
    if os.path.exists(filename) is False:
        # error popup and exit program
        sg.Popup('Error:', 'There must be a parameters file named ' + filename + ' in the current directory')
        sys.exit()

    # open the parameter file and get the array of text
    parameter_file = open(filename, 'r')
    parameters = parameter_file.readlines()
    parameter_file.close()

    # read general parameters
    general_parameters['TASKORDER'] = read_parameter('Task Order', parameters)

    # read side task parameters and load into side dictionary
    side_parameters['ACTIVE'] = re.search('Yes', read_parameter('Side Task Active', parameters), re.IGNORECASE)
    if side_parameters['ACTIVE']: # if task is active in parameters
        side_parameters['TRIALS'] = int(read_parameter('Side Task Trials to Criterion', parameters))
        side_parameters['START_LEVEL'] = int(read_parameter('Side Start Level', parameters))
        side_parameters['RESPONSE'] = float(read_parameter('Side Task Response Time', parameters))
        side_parameters['TIMEOUT'] = float(read_parameter('Side Task Timeout Time', parameters))
        side_parameters['TITRATION'] = re.search('Yes', read_parameter('Side Task Titration', parameters), re.IGNORECASE)
        task_list.append('Side') # add task to task list to run

    # read chase task parameters and load into chase dictionary
    chase_parameters['ACTIVE'] = re.search('Yes', read_parameter('Chase Task Active', parameters), re.IGNORECASE)
    if chase_parameters['ACTIVE']: # if task is active in parameters
        chase_parameters['TRIALS'] = int(read_parameter('Chase Task Trials to Criterion', parameters))
        chase_parameters['CIRCLE_SIZE'] = read_parameter('Chase Circle Size', parameters)
        chase_parameters['RESPONSE'] = float(read_parameter('Chase Task Response Time', parameters))
        chase_parameters['TIMEOUT'] = float(read_parameter('Chase Task Timeout Time', parameters))
        chase_parameters['TITRATION'] = re.search('Yes', read_parameter('Chase Task Titration', parameters), re.IGNORECASE)
        task_list.append('Chase') # add task to task list to run

    # read pursuit task parameters and load into pursuit dictionary
    pursuit_parameters['ACTIVE'] = re.search('Yes', read_parameter('Pursuit Task Active', parameters), re.IGNORECASE)
    if pursuit_parameters['ACTIVE']: # if task is active in parameters
        pursuit_parameters['TRIALS'] = int(read_parameter('Pursuit Task Trials to Criterion', parameters))
        pursuit_parameters['CIRCLE_SIZE'] = read_parameter('Pursuit Circle Size', parameters)
        pursuit_parameters['PURSUIT_TIME'] = float(read_parameter('Pursuit Task Pursuit Time', parameters))
        pursuit_parameters['RESPONSE'] = float(read_parameter('Pursuit Task Response Time', parameters))
        pursuit_parameters['TIMEOUT'] = float(read_parameter('Pursuit Task Timeout Time', parameters))
        pursuit_parameters['TITRATION'] = re.search('Yes', read_parameter('Pursuit Task Titration', parameters), re.IGNORECASE)
        task_list.append('Pursuit') # add task to task list to run

    # read side mts parameters and load into mts dictionary
    mts_parameters['ACTIVE'] = re.search('Yes', read_parameter('MTS Task Active', parameters), re.IGNORECASE)
    if mts_parameters['ACTIVE']: # if task is active in parameters
        mts_parameters['TRIALS'] = float(read_parameter('MTS Task Trials for Criterion', parameters))
        mts_parameters['PERCENT'] = float(read_parameter('MTS Task % Correct for Criterion', parameters))
        mts_parameters['RESPONSE'] = float(read_parameter('MTS Task Response Time', parameters))
        mts_parameters['TIMEOUT'] = float(read_parameter('MTS Task Timeout Time', parameters))
        mts_parameters['TITRATION'] = re.search('Yes', read_parameter('MTS Task Titration', parameters), re.IGNORECASE)
        task_list.append('MTS') # add task to task list to run

    # read dmts task parameters and load into dmts dictionary
    dmts_parameters['ACTIVE'] = re.search('Yes', read_parameter('DMTS Task Active', parameters), re.IGNORECASE)
    if dmts_parameters['ACTIVE']: # if task is active in parameters
        dmts_parameters['TRIALS'] = int(read_parameter('DMTS Task Trials for Criterion', parameters))
        dmts_parameters['PERCENT'] = float(read_parameter('DMTS Task % Correct for Criterion', parameters))
        dmts_parameters['DELAY'] = float(read_parameter('DMTS Delay Time', parameters))
        dmts_parameters['RESPONSE'] = float(read_parameter('DMTS Task Response Time', parameters))
        dmts_parameters['TIMEOUT'] = float(read_parameter('DMTS Task Timeout Time', parameters))
        dmts_parameters['TITRATION'] = re.search('Yes', read_parameter('DMTS Task Titration', parameters), re.IGNORECASE)
        task_list.append('DMTS') # add task to task list to run

    # read learning set task parameters and load into learning set task dictionary
    ls_parameters['ACTIVE'] = re.search('Yes', read_parameter('Learning Set Task Active', parameters), re.IGNORECASE)
    if ls_parameters['ACTIVE']: # if task is active in parameters
        ls_parameters['TRIALS_PER_PROB'] = int(read_parameter('Learning Set Trials Per Problem', parameters))
        ls_parameters['NUM_PROBS'] = int(read_parameter('Learning Set Number of Problems', parameters))
        ls_parameters['PERCENT'] = float(read_parameter('Learning Set % Correct for Criterion', parameters))
        ls_parameters['RESPONSE'] = float(read_parameter('Learning Set Response Time', parameters))
        ls_parameters['TIMEOUT'] = float(read_parameter('Learning Set Timeout Time', parameters))
        ls_parameters['TITRATION'] = re.search('Yes', read_parameter('Learning Set Titration', parameters), re.IGNORECASE)
        task_list.append('LS') # add task to task list to run

""" Function to write event from task into results file
    @param file to write to
    @param task currently running
    @param value string from task to write """
def write_event(file, task, value):
    # get current time
    time = datetime.datetime.now()
    file.write(time.strftime('%m-%d-%Y %H:%M:%S  ') + task + '  ' + value + '\n')

""" Function to return a randomly generated list
    @param start value for list
    @param end value for list
    @param length of list to return
    @return random list generated """
def random_list(start, end, length):
    # make empty list
    rlist = [] 
  
    # loop until rlist is of desired length
    while len(rlist) != length:
        # generate random int in desired range
        r = random.randint(start, end)

        # only add if random int is not already in rlist
        if r not in rlist:
            rlist.append(r)
  
    return rlist

""" Function to load images for pygame
    @param filename of the image to load
    @param colorkey
    @return pygame image and rect loaded from file """
def load_image(filename, colorkey=None):
    # get full path main/data/stimuli/filename
    image_path = os.path.join(stimuli_dir, filename)

    try:
        # load file as pygame image
        image = pygame.image.load(image_path)

        # scale image so that it will fit nicely in screen (650 width x 300 height)
        while (image.get_width() > 650 or image.get_height() > 300):
            # scale down image by 0.9, keep widthxlength ratio
            image = pygame.transform.rotozoom(image, 0, 0.9)

    # if it doesn't load properly
    except pygame.error:
        # error popup and exit program
        sg.Popup('Error:', 'Cannot load image:' + image_path)
        sys.exit()

    # convert pygame image into pygame object and return
    image = image.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)

    return image, image.get_rect()

""" Function to load sound for pygame
    @param filename of sound file
    @return pygame sound object """
def load_sound(filename):
    # make empty sound class for pygame sound with play function
    class NoneSound:
        def play(self): pass

    # if sound is disabled, return an object sound object
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()

    # generate full sound file path main/data/filename
    sound_path = os.path.join(data_dir, filename)

    try:
        # try to load pygame sound from file
        sound = pygame.mixer.Sound(sound_path)

    # if sound does not properly open
    except pygame.error:
        # error popup and exit program
        sg.Popup('Error:', 'Cannot load sound:' + sound_path)
        sys.exit()

    return sound

""" Class for Stimuli inside of our pygame setup for MTS, DMTS, LS """
class Stimuli(pygame.sprite.Sprite):
    """ Stimuli Constructor
        @param self
        @param stimuli filename to use for self.image
        @param x position to place stimuli
        @param y position to place stimuli """
    def __init__(self, stimuli, x, y):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image, self.rect = load_image(stimuli, -1) # load stimuli image pygame object
        self.rect = self.image.get_rect(center=(x,y)) # place Stimuli on passed in x,y

""" Class for Target circle for Chase, Pursuit """
class Target(pygame.sprite.Sprite):
    """ Target Constructor
        @param self
        @param background from pygame
        @param current_task that is running
        @param diameter for the circle """
    def __init__(self, background, current_task, diameter):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer

        self.diameter = int(diameter) # set desired diameter
        self.current_task = current_task # set current_task
        self.velX = random.choice((-5, 5)) # random X initial vel 5 left or 5 right
        self.velY = random.choice((-5, 5)) # random Y initial vel 5 up or 5 down

        # set Target object to a green circle of desired diameter with background color filled in
        self.image = pygame.Surface([self.diameter,self.diameter])
        self.image.fill((BACKGROUND_COLOR))
        self.rect = pygame.draw.circle(self.image, GREEN, (int(self.diameter/2),int(self.diameter/2)), int(self.diameter/2), 2)

        # set initial x and y to be randomly somewhere on the screen atleast diameter distance away from the edges
        self.rect.x = random.randint(0, background.get_width() - self.diameter)
        self.rect.y = random.randint(0, background.get_height() - self.diameter)

        # Set joystick for Target to activate on during Chase
        # Count the joysticks the computer has
        self.joystick_count = pygame.joystick.get_count()
        if self.joystick_count == 0:
            # No joysticks!
            sg.Popup("Error:", "No joystick detected")
            sys.exit()
        else:
            # Use joystick #0 and initialize it
            self.my_joystick = pygame.joystick.Joystick(0)
            self.my_joystick.init()

    """ Function to change Target's color during Pursuit
        @param self
        @param color to set the circle to """
    def change_color(self, color):
        # save x, y coords
        x = self.rect.x
        y = self.rect.y

        # redraw circle with same x, y and diameter but change color to passed in color
        self.rect = pygame.draw.circle(self.image, color, (int(self.diameter/2),int(self.diameter/2)), int(self.diameter/2), 2)

        # reassign x, y coords
        self.rect.x = x
        self.rect.y = y

    """ Update function for Target movement
        @param self
        @param background from pygame """
    def update(self, background):
        joystick_moved = False

        # if Chase task
        if self.current_task == 'Chase':
            # move based on joystick as long as there is a joystick
            if self.joystick_count != 0:
                # check if joystick has moved in x axis atleast 0.1
                horiz_axis_pos = self.my_joystick.get_axis(0)
                if abs(horiz_axis_pos) < 0.1:
                    horiz_axis_pos = 0

                # check if joystick has move in y axis atleast 0.1
                vert_axis_pos = self.my_joystick.get_axis(1)
                if abs(vert_axis_pos) < 0.1:
                    vert_axis_pos = 0
    
                # if joystick has moved atleast 0.1, 
                if (horiz_axis_pos != 0 or vert_axis_pos != 0):
                    joystick_moved = True
        
        # if Pursuit task, or if in Chase task and joystick has moved
        if (joystick_moved or self.current_task == 'Pursuit'):
            # update x,y based on velocities
            self.rect.x = self.rect.x + self.velX;
            self.rect.y = self.rect.y + self.velY;

        # if Target hits any screen border, reverse directions and 
        # make sure it does not go through the border
        if self.rect.x >= background.get_width() - (self.diameter + 1):
            self.rect.x = background.get_width() - (self.diameter + 1)
            self.velX *= -1
        if self.rect.x < 0:
            self.rect.x = 0
            self.velX *= -1
        if self.rect.y >= background.get_height() - (self.diameter + 1):
            self.rect.y = background.get_height() - (self.diameter + 1)
            self.velY *= -1
        if self.rect.y < 0:
            self.rect.y = 0
            self.velY *= -1

""" Class for Pointer that follows joystick """
class Pointer(pygame.sprite.Sprite):
    """ Pointer Constructor
        @param self
        @param diameter for the Pointer """
    def __init__(self, diameter):
        pygame.sprite.Sprite.__init__(self) # call Sprite initializer

        # make pygame object of a RED filled in circle of desired diameter
        self.diameter = int(diameter) # set diameter of circle
        self.image = pygame.Surface([self.diameter,self.diameter])
        self.image.fill(BACKGROUND_COLOR)
        self.rect = pygame.draw.circle(self.image, RED, (int(self.diameter/2),int(self.diameter/2)), int(self.diameter/2))

        # Initiliaze joystick for the Pointer
        # Count the joysticks the computer has
        self.joystick_count = pygame.joystick.get_count()
        if self.joystick_count == 0:
            # No joysticks!
            sg.Popup("Error:", "No joystick detected")
            sys.exit()
        else:
            # Use joystick #0 and initialize it
            self.my_joystick = pygame.joystick.Joystick(0)
            self.my_joystick.init()

    """ Function to reset Pointer to desired location
        @param self
        @param x position
        @param y position """
    def reset(self, x, y):
        self.rect.x = x
        self.rect.y = y

    """ Function to update the Pointer on screen
        @param self
        @param background from pygame """
    def update(self, background):
        # move based on joystick as long as there is a joystick
        if self.joystick_count != 0:
 
            # if joystick has not moved atleast 0.1, set x movement to 0
            horiz_axis_pos = self.my_joystick.get_axis(0)
            if abs(horiz_axis_pos) < 0.1:
                horiz_axis_pos = 0

            # if joystick has not moved atleast 0.1, set y movement to 0
            vert_axis_pos = self.my_joystick.get_axis(1)
            if abs(vert_axis_pos) < 0.1:
                vert_axis_pos = 0
 
            # move x,y according to the joystick axes with a velocity of 10
            self.rect.x = self.rect.x + horiz_axis_pos * 10
            self.rect.y = self.rect.y + vert_axis_pos * 10

            # if Pointer reaches a screen border, make sure it doesnt go past it
            if self.rect.x >= background.get_width() - (self.diameter+1):
                self.rect.x = background.get_width() - (self.diameter+1)
            if self.rect.x < 0:
                self.rect.x = 0
            if self.rect.y >= background.get_height() - (self.diameter+1):
                self.rect.y = background.get_height() - (self.diameter+1)
            if self.rect.y < 0:
                self.rect.y = 0


""" Main function called when the program starts. Runs inital menu
        for animal ID selection, reads parameters from parameter_file, 
        and then starts the pygame loop running every task in task_list """
def main():
    # check if animal_ids_file in in main/
    animal_ids_path = os.path.join(main_dir, animal_ids_file)
    if os.path.exists(animal_ids_path) is False:
        sg.Popup('Error:', animal_ids_path + ' does not exist')
        sys.exit()

    # read animal IDs from file
    animal_ids = open(animal_ids_path, 'r')
    ids = animal_ids.read().splitlines()
    animal_ids.close()

    # load parameters from main/parameter_file
    load_and_check_params(os.path.join(main_dir, parameters_file))

    # establish layout for animal ID selection menu
    layout = [
                [sg.T(' '  * 10)], # Blank space
                [sg.Text('Subject', font = ('Arial', 15, 'bold')), sg.Combo([''] + ids, key = 'SUBJECT')], # Combo box with animal IDs listed
                [sg.T(' '  * 10)], # Blank space
                [sg.T(' '  * 10), sg.Button('Run', font = ('Arial', 15, 'bold'), button_color = ('white', 'green'))], # Button to Run tasks
                [sg.T(' '  * 10)] # Blank space
             ]

    # Create the PySimpleGui Window with menu
    window = sg.Window('Cognitive Testing System', layout)

    # Loop until user makes an animal ID selection or exits
    while True:
        # update current pysimplegui values
        event, values = window.read()

        # if user closes window
        if event in ([None]):
            window.close()
            sys.exit()

        # if user clicks Run button
        if event in (['Run']):
            # if user did not make a subject ID selection
            if values['SUBJECT'] in ('', None):
                # Popup error and continue selection menu
                sg.Popup('Error:', 'Subject field cannot be blank')
            else:
                # Close window
                break

    # set subject ID for results file logging from user selection in previous menu
    subject = values['SUBJECT']

    # check if main/results exists, if not make it
    results_path = os.path.join(main_dir, 'results')
    if not os.path.exists(results_path):
        os.makedirs(results_path)
    # make or append to results file main/results/{subject}Data.txt
    results_file = open(os.path.join(results_path, subject + 'Data.txt'), 'a+')

    # initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN) # fullscreen
    pygame.mouse.set_visible(0) # make mouse dissapear

    # create pygame background based on screen size
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((BACKGROUND_COLOR)) # grey by default

    # display the background
    screen.blit(background, (0, 0))
    pygame.display.flip() # display first frame

    # initialize pygame objects
    clock = pygame.time.Clock()
    incorrect_sound = load_sound('incorrect.wav') # sound to play for incorrect response
    correct_sound = load_sound('correct.wav') # sound to play for correct response
    
    pointer = Pointer(24) # construct pointer circle with 24 diameter
    pointer.reset(background.get_width()/2, background.get_height()/2) # set pointer to be in center of screen 

    # make list of sprites to render during tasks, initially just the pointer
    allsprites = pygame.sprite.RenderPlain((pointer))

    # general variables
    current_task = ''
    task_over = True
    setup = False

    correct_trials = 0
    trials = 0
    total_trials = 0

    # task ending variables
    correct = False
    timeout = False
    chosen = False

    # side variables
    side_level = side_parameters['START_LEVEL']

    side_walls = [ # list of all the possible walls for side, first 4 are full length, last 4 are partial
                    pygame.Rect(0,0,background.get_width(),200),
                    pygame.Rect(0,background.get_height() - 200,background.get_width(),200),
                    pygame.Rect(0,0,200,background.get_height()),
                    pygame.Rect(background.get_width()-200,0,200,background.get_height()),
                    pygame.Rect(0,0,background.get_width()/4,200),
                    pygame.Rect(0,background.get_height() - 200,background.get_width()/4,200),
                    pygame.Rect(0,0,200,background.get_height()/4),
                    pygame.Rect(background.get_width()-200,0,200,background.get_height()/4)
                 ]

    # pursuit variables
    inside = False

    # dmts variables
    delay_over = False

    # learning set variables
    new_stimuli = True
    problem_trials = 0
    problems = 1

    # main loop to run pygame
    going = True
    while going:

        # if task is over
        if task_over:
            # remove whatever task was currently running
            task_list.remove(current_task)

            # if task_list is empty, end program
            if len(task_list) == 0:
                pygame.quit()
                results_file.close()
                sys.exit()

            # if task order is Random, get random task
            if re.search('Random', general_parameters['TASKORDER'], re.IGNORECASE):
                current_task = random.choice(task_list)
            # if task order is Series, get next task
            else:
                current_task = task_list[0]

            # reset task variables
            trials = 0
            correct_trials = 0
            task_over = False

        # 60 fps, update and draw every 1/60 sec
        clock.tick(60)

        # handle input, escape key = exit
        for event in pygame.event.get():
            if event.type == QUIT:
                going = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                going = False

        # update all current sprites
        allsprites.update(background)
        pygame.display.update()

        # draw background and all current sprites in list
        screen.blit(background, (0, 0))
        allsprites.draw(screen)

        # Side task
        if current_task == 'Side':
            # if already setup
            if setup:
                # if no response in Reponse Time seconds, timeout
                if (time.time() - start_time > side_parameters['RESPONSE']):
                    timeout = True

                elif side_level == 1: # side level 1
                    # draw random green walls from setup selection
                    for i in side_wall_list:
                        screen.fill(GREEN, side_walls[i])

                    # every joystick event, check if Pointer was moved
                    # if Pointer was moved, correct criterion
                    for event in pygame.event.get():
                        if pointer.rect.x != background.get_width()/2 or pointer.rect.y != background.get_height()/2:
                            correct = True

                elif side_level in (2, 3, 4, 5, 6): # side level > 1
                    # draw random green walls from setup selection
                    for i in side_wall_list:
                        screen.fill(GREEN, side_walls[i])

                        # if Pointer collides with a wall, correct criterion
                        if side_walls[i].colliderect(pointer):
                            correct = True

            # need to setup
            else:
                # based on current side_level, generate a random list of indices for the side_wall array
                if side_level in (1, 2):
                    side_wall_list = (0, 1, 2, 3)
                elif side_level == 3:
                    side_wall_list = random_list(0, 3, 3)
                elif side_level == 4:
                    side_wall_list = random_list(0, 3, 2)
                elif side_level == 5:
                    side_wall_list = random_list(0, 3, 1)
                elif side_level == 6:
                    side_wall_list = random_list(4, 7, 1)

                # reset pointer to the center of the screen
                pointer.reset(background.get_width() / 2, background.get_height() / 2)
                allsprites = pygame.sprite.RenderPlain((pointer))

                # reset task variables
                setup = True
                start_time = time.time()

            # trial over
            if correct or timeout:
                trials += 1
                total_trials += 1

                # generate side log string for which walls are up
                # T - top, R - right, B - bottom, L - left
                side_walls_str = ''
                if 0 in side_wall_list or 4 in side_wall_list:
                    side_walls_str += 'T'
                if 3 in side_wall_list or 7 in side_wall_list:
                    side_walls_str +='R'
                if 1 in side_wall_list or 5 in side_wall_list:
                    side_walls_str += 'B'
                if 2 in side_wall_list or 6 in side_wall_list:
                    side_walls_str += 'L'

                # if correct criterion update correct_trials
                if correct:
                    correct_trials += 1

                # set timeout time for incorrect response
                timeout_time = side_parameters['TIMEOUT']

                # set log value with relevant side information
                value = "{}  {}  {}  {}  {}".format(total_trials, trials, side_level, side_walls_str, round(time.time() - start_time, 2))

                # if enough correct trials have been completed, go to next side level
                if correct_trials >= side_parameters['TRIALS']:
                    correct_trials = 0
                    side_level += 1

                    # if level 6 has been completed, go to next task
                    if side_level > 6:
                        side_level = side_parameters['START_LEVEL']
                        task_over = True



        # Chase task
        elif current_task == 'Chase':
            # if already setup
            if setup:
                # if no response in Reponse Time seconds, timeout
                if (time.time() - start_time > chase_parameters['RESPONSE']):
                    timeout = True
                # check if Pointer has reached Target circle
                elif target.rect.contains(pointer):
                    correct = True

            # need to set up
            else:
                # decide circle size of target from parameters
                if re.search('Small', chase_parameters['CIRCLE_SIZE'], re.IGNORECASE):
                    target_size = 100
                elif re.search('Medium', chase_parameters['CIRCLE_SIZE'], re.IGNORECASE):
                    target_size = 200
                elif re.search('Large', chase_parameters['CIRCLE_SIZE'], re.IGNORECASE):
                    target_size = 300

                # construct Target circle for Chase
                target = Target(background, 'Chase', target_size)

                # loop until Pointer is placed somewhere not colliding with Target
                while(target.rect.colliderect(pointer)):
                    newX = random.randInt(0, background.get_width() - pointer.diameter)
                    newY = random.randInt(0, background.get_height() - pointer.diameter)
                    pointer.reset(newX, newY)

                # add Target to list of sprites to maintain
                allsprites = pygame.sprite.RenderPlain((target, pointer))

                # reset task variables
                setup = True
                start_time = time.time()

            # trial ended
            if correct or timeout:
                trials += 1
                total_trials += 1

                # if correct criterion update correct_trials
                if correct:
                    correct_trials += 1

                # set timeout time for incorrect response
                timeout_time = chase_parameters['TIMEOUT']

                # set log value with relevant chase information
                value = "{}  {}  {}  {}".format(total_trials, trials, chase_parameters['CIRCLE_SIZE'], round(time.time() - start_time, 2))

                # if enough correct trials have been completed, go to next task
                if correct_trials >= chase_parameters['TRIALS']:
                    task_over = True



        # Pursuit task
        elif current_task == 'Pursuit':
            # if already set
            if setup:
                # if no response in Reponse Time seconds, timeout
                if (time.time() - start_time > pursuit_parameters['RESPONSE']):
                    timeout = True

                # if Pointer is inside of Target
                elif target.rect.contains(pointer):
                    # if it was already inside
                    if inside:
                        target.change_color(GREEN) # change target color to green
                        # if its been Pursuit Time, correct criterion
                        if (time.time() - start_contains_time >= pursuit_parameters['PURSUIT_TIME']):
                            correct = True

                    # if Pointer has not been inside Target yet
                    else:
                        inside = True
                        start_contains_time = time.time() # reset timer

                # if Pointer is not inside of Target, change circle color to red
                else:
                    target.change_color(RED)
                    inside = False

            # need to setup
            else:
                # decide circle size of target from parameters
                if re.search('Small', pursuit_parameters['CIRCLE_SIZE'], re.IGNORECASE):
                    target_size = 100
                elif re.search('Medium', pursuit_parameters['CIRCLE_SIZE'], re.IGNORECASE):
                    target_size = 200
                elif re.search('Large', pursuit_parameters['CIRCLE_SIZE'], re.IGNORECASE):
                    target_size = 300

                # construct Target circle for Pursuit
                target = Target(background, 'Pursuit', target_size)

                # loop until Pointer is placed somewhere not colliding with Target
                while(target.rect.colliderect(pointer)):
                    newX = random.randint(0, background.get_width() - pointer.diameter)
                    newY = random.randint(0, background.get_height() - pointer.diameter)
                    pointer.reset(newX, newY)

                # add Target to list of sprites to maintain
                allsprites = pygame.sprite.RenderPlain((target, pointer))

                # reset task variables
                inside = False
                setup = True
                start_time = time.time()

            # trial ended
            if correct or timeout:
                trials += 1
                total_trials += 1

                # if correct criterion update correct_trials
                if correct:
                    correct_trials += 1

                # set timeout time for incorrect response
                timeout_time = pursuit_parameters['TIMEOUT']

                # set log value with relevant pursuit information
                value = "{}  {}  {}  {}".format(total_trials, trials, pursuit_parameters['CIRCLE_SIZE'], round(time.time() - start_time, 2))
                
                # if enough correct trials have been completed, go to next task
                if correct_trials >= pursuit_parameters['TRIALS']:
                    task_over = True



        # Match-to-Sample task
        elif current_task == 'MTS':
            # if already set up
            if setup:
                # if no response in Reponse Time seconds, timeout
                if (time.time() - start_time > mts_parameters['RESPONSE']):
                    timeout = True

                # if Pointer collides with correct stimuli, correct criterion
                elif stimuli_correct.rect.contains(pointer):
                    correct = True
                    chosen = True

                # if Pointer collides with incorrect stimuli, incorrect criterion
                elif stimuli_wrong.rect.contains(pointer):
                    correct = False
                    chosen = True

            # need to set up
            else:
                # randomly select stimuli files from main/data/stimuli/
                correct_stimuli = random.choice(os.listdir(stimuli_dir))
                wrong_stimuli = random.choice(os.listdir(stimuli_dir))

                # loop until the two stimuli are different
                while (correct_stimuli == wrong_stimuli):
                    wrong_stimuli = random.choice(os.listdir(stimuli_dir))

                # randomly decide whether the correct will be on the left or right
                correct_position = random.choice([0.15, 0.85])

                # assign stimuli_correct_str for logging
                if correct_position == 0.15:
                    stimuli_correct_str = 'Left'
                    left_stimuli = correct_stimuli
                    right_stimuli = wrong_stimuli
                else:
                    stimuli_correct_str = 'Right'
                    right_stimuli = correct_stimuli
                    left_stimuli = wrong_stimuli

                # construct Stimuli objects for pygame
                stimuli_correct = Stimuli(correct_stimuli, background.get_width() * correct_position, background.get_height()/4)
                stimuli_wrong = Stimuli(wrong_stimuli, background.get_width() * (1 - correct_position), background.get_height()/4)
                stimuli_bottom = Stimuli(correct_stimuli, background.get_width()/2, background.get_height()*.8)
                
                # add stimuli to list of sprites
                allsprites = pygame.sprite.RenderPlain((stimuli_correct, stimuli_wrong, stimuli_bottom, pointer))

                # reset Pointer to center of screen
                pointer.reset(background.get_width()/2, background.get_height()/2)
                
                # reset task variables
                setup = True
                start_time = time.time()

            if chosen or timeout:
                trials += 1
                total_trials += 1

                # if correct criterion, update correct_trials
                if correct:
                    correct_trials += 1

                    # set log value with relevant mts information
                    value = "{}  {}  {}  {}  {}  {}  {}  Correct".format(total_trials, trials, round(mts_parameters['PERCENT'],2), os.path.splitext(os.path.basename(left_stimuli))[0], stimuli_correct_str, os.path.splitext(os.path.basename(right_stimuli))[0], round(time.time() - start_time, 2))
                
                # if incorrect criterion or timeout
                else:
                    # set log value with relevant mts information
                    value = "{}  {}  {}  {}  {}  {}  {}  Incorrect".format(total_trials, trials, round(mts_parameters['PERCENT'],2), os.path.splitext(os.path.basename(left_stimuli))[0], stimuli_correct_str, os.path.splitext(os.path.basename(right_stimuli))[0], round(time.time() - start_time, 2))
                
                # set timeout time for incorrect response
                timeout_time = mts_parameters['TIMEOUT']

                # if enough correct trials have been completed
                if correct_trials >= mts_parameters['TRIALS']:
                    # if accuracy of trials is > parameters percent, go to next task
                    if (correct_trials / trials) >= (mts_parameters['PERCENT'] / 100):
                        task_over = True



        # Delayed-Match-to-Sample Task
        elif current_task == 'DMTS':
            # if already set up
            if setup:
                # if delay is over
                if delay_over:
                    # if no response in Reponse Time seconds, timeout
                    if (time.time() - start_time > dmts_parameters['RESPONSE']):
                        timeout = True

                    # if Pointer collides with correct stimuli, correct criterion
                    elif stimuli_correct.rect.contains(pointer):
                        correct = True
                        chosen = True

                    # if Pointer collides with incorrect stimuli, incorrect criterion
                    elif stimuli_wrong.rect.contains(pointer):
                        correct = False
                        chosen = True

                # delay needs to happen
                else:
                    # start delay when Pointer collides bottom stimuli
                    if stimuli_bottom.rect.contains(pointer):
                        # blank screen
                        screen.blit(background, (0, 0))
                        pygame.display.update()
                        time.sleep(dmts_parameters['DELAY']) # delay

                        # add wrong and correct stimuli to sprites, remove bottom one
                        allsprites = pygame.sprite.RenderPlain((stimuli_wrong, stimuli_correct, pointer))

                        delay_over = True
                        start_time = time.time() # reset timer

            # need to setup
            else:
                # randomly select stimuli files from main/data/stimuli/
                correct_stimuli = random.choice(os.listdir(stimuli_dir))
                wrong_stimuli = random.choice(os.listdir(stimuli_dir))

                # loop until the two stimuli are different
                while (correct_stimuli == wrong_stimuli):
                    wrong_stimuli = random.choice(os.listdir(stimuli_dir))

                # randomly decide whether the correct will be on the left or right
                correct_position = random.choice([0.15, 0.85])

                # assign stimuli_correct_str for logging
                if correct_position == 0.15:
                    stimuli_correct_str = 'Left'
                    left_stimuli = correct_stimuli
                    right_stimuli = wrong_stimuli
                else:
                    stimuli_correct_str = 'Right'
                    right_stimuli = correct_stimuli
                    left_stimuli = wrong_stimuli

                # construct Stimuli objects for pygame
                stimuli_correct = Stimuli(correct_stimuli, background.get_width() * correct_position, background.get_height()/4)
                stimuli_wrong = Stimuli(wrong_stimuli, background.get_width() * (1 - correct_position), background.get_height()/4)
                stimuli_bottom = Stimuli(correct_stimuli, background.get_width()/2, background.get_height()*.8)

                # add only bottom stimuli to sprite list
                allsprites = pygame.sprite.RenderPlain((stimuli_bottom, pointer))

                # reset pointer to center of screen
                pointer.reset(background.get_width()/2, background.get_height()/2)
                
                # reset task variables
                delay_over = False
                setup = True

            # trial over
            if chosen or timeout:
                trials += 1
                total_trials += 1

                # if correct criterion, update correct_trials
                if correct:
                    correct_trials += 1

                    # set log value with relevant dmts information
                    value = "{}  {}  {}  {}  {}  {}  {}  Correct".format(total_trials, trials, round(dmts_parameters['PERCENT'],2), os.path.splitext(os.path.basename(left_stimuli))[0], stimuli_correct_str, os.path.splitext(os.path.basename(right_stimuli))[0], round(time.time() - start_time, 2))
                else:
                    # set log value with relevant dmts information
                    value = "{}  {}  {}  {}  {}  {}  {}  Incorrect".format(total_trials, trials, round(dmts_parameters['PERCENT'],2), os.path.splitext(os.path.basename(left_stimuli))[0], stimuli_correct_str, os.path.splitext(os.path.basename(right_stimuli))[0], round(time.time() - start_time, 2))

                # set timeout time for incorrect response
                timeout_time = dmts_parameters['TIMEOUT']

                # if enough correct trials have been completed
                if correct_trials >= dmts_parameters['TRIALS']:
                    # if accuracy of trials is > parameters percent, go to next task
                    if (correct_trials / trials) >= (dmts_parameters['PERCENT'] / 100):
                        task_over = True


      
        # Learning Set task
        elif current_task == 'LS':
            # if already set up
            if setup:
                # if no response in Reponse Time seconds, timeout
                if (time.time() - start_time > ls_parameters['RESPONSE']):
                    timeout = True

                # if Pointer collides with correct stimuli, correct criterion
                elif stimuli_correct.rect.contains(pointer):
                    correct = True
                    chosen = True

                # if Pointer collides with incorrect stimuli, incorrect criterion
                elif stimuli_wrong.rect.contains(pointer):
                    correct = False
                    chosen = True

            # need to set up
            else:
                # if we're at the start of a problem, we need a new correct stimuli
                if new_stimuli:
                    new_stimuli = False

                    # randomly select stimuli files from main/data/stimuli/
                    correct_stimuli = random.choice(os.listdir(stimuli_dir))

                wrong_stimuli = random.choice(os.listdir(stimuli_dir))

                # loop until the two stimuli are different
                while (correct_stimuli == wrong_stimuli):
                    wrong_stimuli = random.choice(os.listdir(stimuli_dir))

                # randomly decide whether the correct will be on the left or right
                correct_position = random.choice([0.15, 0.85])

                # assign stimuli_correct_str for logging
                if correct_position == 0.15:
                    stimuli_correct_str = 'Left'
                    left_stimuli = correct_stimuli
                    right_stimuli = wrong_stimuli
                else:
                    stimuli_correct_str = 'Right'
                    right_stimuli = correct_stimuli
                    left_stimuli = wrong_stimuli

                # construct Stimuli objects for pygame
                stimuli_correct = Stimuli(correct_stimuli, background.get_width() * correct_position, background.get_height()/2)
                stimuli_wrong = Stimuli(wrong_stimuli, background.get_width() * (1 - correct_position), background.get_height()/2)

                # add stimuli to sprite list
                allsprites = pygame.sprite.RenderPlain((stimuli_correct, stimuli_wrong, pointer))

                # reset pointer to center of screen
                pointer.reset(background.get_width()/2, background.get_height()/2)
                
                # reset task variables
                setup = True
                start_time = time.time() # reset timer

            # trial over
            if chosen or timeout:
                trials += 1
                total_trials += 1
                problem_trials += 1

                # if correct criterion, update correct_trials
                if correct:
                    correct_trials += 1

                    # set log value with relevant ls information
                    value = "{}  {}  {}  {}  {}  {}  {}  {}  Correct".format(total_trials, problems, trials, round(ls_parameters['PERCENT'],2), os.path.splitext(os.path.basename(left_stimuli))[0], stimuli_correct_str, os.path.splitext(os.path.basename(right_stimuli))[0], round(time.time() - start_time, 2))
                else:
                    # set log value with relevant ls information
                    value = "{}  {}  {}  {}  {}  {}  {}  {}  Incorrect".format(total_trials, problems, trials, round(ls_parameters['PERCENT'],2), os.path.splitext(os.path.basename(left_stimuli))[0], stimuli_correct_str, os.path.splitext(os.path.basename(right_stimuli))[0], round(time.time() - start_time, 2))
                
                # set timeout time for incorrect response
                timeout_time = ls_parameters['TIMEOUT']

                # if enough problem trials have been completed
                if problem_trials >= ls_parameters['TRIALS_PER_PROB']:
                    problem_trials = 0
                    problems += 1 # increment number of problems
                    new_stimuli = True # new problem

                    # if enough problems have been completed
                    if (problems > ls_parameters['NUM_PROBS']):
                        # if accuracy of all ls trials is > parameters percent, go to next task
                        if (correct_trials / trials) >= (ls_parameters['PERCENT'] / 100):
                            task_over = True



        # any time a trial ends (correct criterion OR no response in Reponse Time OR a choice was made)
        if correct or timeout or chosen:
            if correct:
                correct_sound.play()
                pellet()
                time.sleep(4) # wait for sound to play and pellet to dispense
            else:
                incorrect_sound.play()

                # make screen blank for timeout_time
                screen.blit(background, (0, 0))
                pygame.display.update()
                time.sleep(timeout_time)

            # write log for task to results file
            write_event(results_file, current_task, value)

            # reset trial ending variables
            correct = False
            timeout = False
            chosen = False

            # reset the next trial
            setup = False


""" this calls the 'main' function when this script is executed """
if __name__ == '__main__':
    main()
