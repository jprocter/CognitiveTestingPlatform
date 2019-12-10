Required Python Packages to Run:

    pysimplegui
    pygame
    adafruit-circuitpython-motorkit
    adafruit-circuitpython-motor

    These can be installed via the command:
        pip install pysimplegui adafruit-circuitpython-motorkit adafruit-circuitpython-motor pygame --user


Required Hardware to Run:

    Stepper motor interfaced through an adafruit_motorkit supported board
        PiHAT used in our version is listed as 'Adafruit DC & Stepper Motor HAT for Raspberry Pi - Mini Kit' here: https://circuitpython.readthedocs.io/projects/motorkit/en/latest/api.html
        not using an adafruit_motorkit supported board will cause 'game.py' to crash

        *** If another interface is desired for pellet dispensing, will need to get rid of the adafruit motor import statements and change pellet() in 'game.py' ***

    Joystick
        pygame should be able to detect most USB gamepad/joysticks hooked up (https://www.pygame.org/docs/ref/joystick.html)
        joystick not hooked up properly will crash 'game.py'

    Keyboard

    Mouse

    Monitor


Quick Start Guide:

    1. Make sure joystick is plugged in (this will cause 'game.py' to crash)

    2. Run 'menu.py'
        a. Open Terminal and use cd to navigate to main/ directory
        b. run command 'python menu.py' (might need to replace 'python' with 'python3')

    3. In the new window, find 'Use Parameters from File' and click 'Browse'
        to and use 'defaults.txt' or another desired parameters file. Then click 'Load'.

    4. Change any desired parameters using the menu.

    5. (Optional) save current parameters to named file by typing the name in the
        'Save Current Parameters to File' text box. Then click 'Save'.

    6. Click 'Go'. This will run 'game.py'

    7. In the new window, select which Animal ID to use for results. Then click 'Run'

    8. The tasks marked as active in the parameters will now run in a fullscreen window.
        Results can be found in main/results/{ID}Data.txt.

    You can also run 'game.py' by itself, however this requires a 'parameters.txt' to be
        in the main directory already.




Files included in the Cognitive Testing System:

    main/                   -- main directory where everything is

        data/               -- data directory for sound and stimuli
            incorrect.wav   -- negative sound file
            correct.wav     -- positive sound file
            stimuli/        -- directory for stimuli images
                *.png       -- stimuli files are png images (WMF will not work with pygame)

        AnimalIDS.txt       -- text file with subject IDs listed

        defaults.txt        -- text file with default parameters listed

        game.py             -- 1. Displays a pysimplegui window that has the user select an
                                    animal ID from a list in 'AnimalIDS.txt' using a mouse, then 
                                    closes when 'Run' is clicked
                               2. Starts a window that runs all of the tasks listed as active in
                                    'parameters.txt', and uses their values to run the tasks. Tasks
                                    are played by using a joystick. Every trial is logged to a results file
                                    with the same name as the animal ID chosen.

        menu.py             -- Displays a window that has the user load a parameter_file to
                                use as a base. The user can then use the mouse and keyboard to enter
                                the desired parameters for every task to run. The user has the option to
                                save the parameters to a named file. When 'Go' button is clicked, the current
                                parameters from the window are saved to 'parameters.txt' and then 
                                'game.py' is called.


Files created by 'menu.py':

    main/parameters.txt     -- parameters text file used by 'game.py', made by 'menu.py'


Files created by 'game.py':

    main/results/           -- results directory made on first 'game.py' run
        
        {ID}Data.txt        -- results log file written to named from animal ID chosen in 'game.py'


Editing Parameter Values:

    'parameters.txt' should always hold the current desired parameters to be used in 'game.py', there are two ways to change the values there.

        1. 'menu.py' provides an interactive way to load a default/previous parameter file and then modify their values by replacing the text there.
        
        2. Create and write to 'parameters.txt' manually (Warning: there is a certain syntax to all of the parameters that is expected in 'game.py')
            For best results with this method, use 'defaults.txt' as a basis for 'parameters.txt' to ensure the syntax will not cause issues.


Adding New Parameters to the System:

    {task} = task that the parameter will be used for, if it is a general parameter this will just be 'general' (i.e. 'Pursuit')
    {name} = name of new parameter, used to search parameter files for the value (i.e. 'Circle Size')
    {value} = value of parameter (i.e. 'Large')

        1. Add the parameter to 'defaults.txt' somewhere, make sure that {name} and {value} are on their own lines and
            {value} is on the line that is after {name} like this:

                {name}
                {value}

        2. Add the parameter for use in 'game.py'

            a. Create a key for the parameter by adding an entry in the '{task}_parameters_keys' list (i.e. 'CIRCLE_SIZE').
                Name the key something easy to identify the name of the parameter by. We will call this {key}.

            b. In the function 'load_and_check_params()', add a line to load the parameter into the proper task dictionary
                from the parameters file by {name}. This line should look something like this:

                {task}_parameters[ {key} ] = read_parameter( {name} , parameters)

                ( i.e. pursuit_parameters['CIRCLE_SIZE'] = read_parameter('Pursuit Circle Size', parameters) )

                This should search {name} in the parameters file, find {value} and then assign it to the {task}_parameters
                    dictionary to later be accessed by {key}. Sometimes it is neccessary to convert this string into
                    an int or float depending on how we want to use {value}, as you see in the function.

            c. Now you can use the new parameter in code by calling {task}_parameters[ {key} ] anytime we want to access {value}

        3. Add the parameter for use in 'menu.py' (this is optional if you want to be able to change it using the interactive menu)
            
            a. Create a row in options[] to represent the parameter in the window. Usually you will want to have
                the {name} followed by some sort of pysimplegui object to interact with to show/change the value.

                [TextCustom({name}), sg.InputTextCustom(key = {key})],

                ( i.e. [TextCustom('Circle Size'), sg.Combo(('','Small','Medium','Large'), key = 'CIRCLE_P')], )

                Here TextCustom will be the text displayed, then sg.Combo is a pysimplegui ComboBox to display multiple text
                    selections. Lastly, every pysimplegui object will need a {key} in order to reference later to get/change its value.

            b. In the function 'load_parameters()', add a line to load the parameter from the chosen file and update
                the corresponding pysimplegui object with its {value}

                window[{key}].Update(read_parameter({name}), parameters)

                ( i.e. window['CIRCLE_P'].Update(read_parameter('Pursuit Circle Size', parameters)) )

                This should search {name} in the parameters file, find {value} and then update the pysimplegui object in our 
                    window to display this value.

            c. In the function 'save_parameters()', add a line to save the parameter to a chosen file with its value taken
                from our current pysimplegui window

                write_parameter({name}, values[{key}], parameters)

                ( i.e write_parameter('Pursuit Circle Size', values['CIRCLE_P'], parameters) )

                This should search {name} in the target parameters file, and replace {value} with the value from our
                    pysimplegui object reference by {key}

        4. In order for 'game.py' to be able to read this new parameter, you will need to edit 'parameters.txt' using either of the methods
            described in the above section 'Editing Parameter Values'