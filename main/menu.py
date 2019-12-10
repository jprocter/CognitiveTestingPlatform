""" menu.py
        Displays a pysimplegui window that has the user load a parameter_file to
        use as a base. The user can then use the mouse and keyboard to enter
        the desired parameters for every task to run. The user has the option to
        save the parameters to a named file. When 'Go' is clicked, the current
        parameters from the window are saved to parameters_file and then 
        game.py is called.
"""

import os, sys, re

# pip install pysimplegui
import PySimpleGUI as sg

main_dir = os.path.split(os.path.abspath(__file__))[0] # directory where this file is, should be main/
os.chdir(main_dir) # make sure we are in this directory

# parameters file to use for running the game
parameters_file = 'parameters.txt'

# lambda function overloading pysimplegui Text and Input so that they are all the same size/font
# basically just a macro to make code look nicer and save text
TextCustom = lambda text, font = ('Arial', 11):sg.Text(text = text, font = font, size = (30, 1))
InputTextCustom = lambda key, text = '':sg.InputText(text, size = (15, 1), key = key)

# layout of the rows of options in start menu
# keys are assigned pysimplegui objects is used to index the values array for their current value later
options = [ 
            [TextCustom('Use Parameters from File', font = ('Arial', 11, 'bold')), InputTextCustom('IN_FILE'), sg.FileBrowse()], # file browser for loading parameters file
            [TextCustom(' '), sg.Button('Load')], # Load button
            [TextCustom('Task Order'), sg.Radio('Series', 'RADIO_TASKORDER', key = 'TASKORDER_SERIES'), sg.Radio('Random', 'RADIO_TASKORDER', key = 'TASKORDER_RAND')], # Yes/No button for Taskorder

            [sg.T(' '  * 10)], # Blank space

            [TextCustom('Side Task Active', font = ('Arial', 11, 'bold')), sg.Radio('Yes', 'RADIO_S', key = 'S_YES'), sg.Radio('No', 'RADIO_S', key = 'S_NO')], # Yes/No button for Side Active
            [TextCustom('Trials to Criterion'), InputTextCustom('TRIALS_S')], # Input text for number of trials
            [TextCustom('Start Level'), sg.Combo(('','1','2','3','4','5','6'), key = 'LEVEL_S')], # Drop down box for side start level
            [TextCustom('Response Time (seconds)'), InputTextCustom('RESPONSE_S')], # Input text for response time
            [TextCustom('Timeout Time (seconds)'), InputTextCustom('TIMEOUT_S')], # Input text for timeout time
            [TextCustom('Titration'), sg.Radio('Yes', 'RADIO_STIT', key = 'TIT_S_YES'), sg.Radio('No', 'RADIO_STIT', key = 'TIT_S_NO')], # Yes/No button for Titration

            [sg.T(' '  * 10)], # Blank space

            [TextCustom('Chase Task Active', font = ('Arial', 11, 'bold')), sg.Radio('Yes', 'RADIO_C', key = 'C_YES'), sg.Radio('No', 'RADIO_C', key = 'C_NO')], # Yes/No button for Chase Active
            [TextCustom('Trials to Criterion'), InputTextCustom('TRIALS_C')], # Input text for number of trials
            [TextCustom('Circle Size'), sg.Combo(('','Small', 'Medium', 'Large'), key = 'CIRCLE_C')], # Input text for circle size
            [TextCustom('Response Time (seconds)'), InputTextCustom('RESPONSE_C')], # Input text for response time
            [TextCustom('Timeout Time (seconds)'), InputTextCustom('TIMEOUT_C')], # Input text for timeout time
            [TextCustom('Titration'), sg.Radio('Yes', 'RADIO_CTIT', key = 'TIT_C_YES'), sg.Radio('No', 'RADIO_CTIT', key = 'TIT_C_NO')], # Yes/No button for Titration

            [sg.T(' '  * 10)], # Blank space

            [TextCustom('Pursuit Task Active', font = ('Arial', 11, 'bold')), sg.Radio('Yes', 'RADIO_P', key = 'P_YES'), sg.Radio('No', 'RADIO_P', key = 'P_NO')], # Yes/No button for Pursuit Active
            [TextCustom('Trials to Criterion'), InputTextCustom('TRIALS_P')], # Input text for number of trials
            [TextCustom('Circle Size'), sg.Combo(('','Small','Medium','Large'), key = 'CIRCLE_P')], # Input text for circle size
            [TextCustom('Pursuit Time (seconds)'), InputTextCustom('PURSUIT_P')], # Input text for pursuit time
            [TextCustom('Response Time (seconds)'), InputTextCustom('RESPONSE_P')], # Input text for response time
            [TextCustom('Timeout Time (seconds)'), InputTextCustom('TIMEOUT_P')], # Input text for timeout time
            [TextCustom('Titration'), sg.Radio('Yes', 'RADIO_PTIT', key = 'TIT_P_YES'), sg.Radio('No', 'RADIO_PTIT', key = 'TIT_P_NO')], # Yes/No button for Titration

            [sg.T(' '  * 10)], # Blank space

            [TextCustom('MTS Task Active', font = ('Arial', 11, 'bold')), sg.Radio('Yes', 'RADIO_MTS', key = 'MTS_YES'), sg.Radio('No', 'RADIO_MTS', key = 'MTS_NO')], # Yes/No button for MTS Active
            [TextCustom('Trials to Criterion'), InputTextCustom('TRIALS_MTS')], # Input text for number of trials
            [TextCustom('% Correct for Criterion'), InputTextCustom('PERCENT_MTS')], # Input text for percent correct
            [TextCustom('Response Time (seconds)'), InputTextCustom('RESPONSE_MTS')], # Input text for response time
            [TextCustom('Timeout Time (seconds)'), InputTextCustom('TIMEOUT_MTS')], # Input text for timeout time
            [TextCustom('Titration'), sg.Radio('Yes', 'RADIO_MTSTIT', key = 'TIT_MTS_YES'), sg.Radio('No', 'RADIO_MTSTIT', key = 'TIT_MTS_NO')], # Yes/No button for Titration

            [sg.T(' '  * 10)], # Blank space

            [TextCustom('DMTS Task Active', font = ('Arial', 11, 'bold')), sg.Radio('Yes', 'RADIO_DMTS', key = 'DMTS_YES'), sg.Radio('No', 'RADIO_DMTS', key = 'DMTS_NO')], # Yes/No button for DMTS Active
            [TextCustom('Trials to Criterion'), InputTextCustom('TRIALS_DMTS')], # Input text for number of trials
            [TextCustom('% Correct for Criterion'), InputTextCustom('PERCENT_DMTS')], # Input text for percent correct
            [TextCustom('Delay Time (seconds)'), InputTextCustom('DELAY_DMTS')], # Input text for delay time
            [TextCustom('Response Time (seconds)'), InputTextCustom('RESPONSE_DMTS')], # Input text for response time
            [TextCustom('Timeout Time (seconds)'), InputTextCustom('TIMEOUT_DMTS')], # Input text for timeout time
            [TextCustom('Titration'), sg.Radio('Yes', 'RADIO_DMTSTIT', key = 'TIT_DMTS_YES'), sg.Radio('No', 'RADIO_DMTSTIT', key = 'TIT_DMTS_NO')], # Yes/No button for Titration

            [sg.T(' '  * 10)], # Blank space

            [TextCustom('Learning Set Task Active', font = ('Arial', 11, 'bold')), sg.Radio('Yes', 'RADIO_LS', key = 'L_YES'), sg.Radio('No', 'RADIO_LS', key = 'L_NO')], # Yes/No button for LS Active
            [TextCustom('Trials Per Problem'), InputTextCustom('TRIALSPERPROB_LS')], # Input text for number of trials per problem
            [TextCustom('Number of Problems'), InputTextCustom('NUMPROBS_LS')], # Input text for number of problems
            [TextCustom('% Correct for Criterion'), InputTextCustom('PERCENT_LS')], # Input text for percent correct
            [TextCustom('Response Time (seconds)'), InputTextCustom('RESPONSE_LS')], # Input text for response time
            [TextCustom('Timeout Time (seconds)'), InputTextCustom('TIMEOUT_LS')], # Input text for timeout time
            [TextCustom('Titration'), sg.Radio('Yes', 'RADIO_LSTIT', key = 'TIT_LS_YES'), sg.Radio('No', 'RADIO_LSTIT', key = 'TIT_LS_NO')], # Yes/No button for Titration
         ]

column = [
            [TextCustom('Save Current Parameters to File', font = ('Arial', 11, 'bold'))],
            [InputTextCustom('OUT_FILE'), sg.FileBrowse()], # File browser for parameter file to save to
            [sg.Button('Save')] # Save button
         ]

# layout of main menu window, then Run button on bottom
layout = [
            [sg.Column(options, scrollable = True)], # options[] on top to scroll through as only column
            [sg.Column(column), sg.Button('Go', font = ('Arial', 25, 'bold'), button_color = ('white','green'))] # bottom - save parameter file menu as left column, Run button as right column
         ]


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

    # if parameter not found, make value in menu blank
    return ''

""" Function to write a parameter to a given array of text by name
    @param name of parameter to search for
    @param value of parameter to write
    @param parameters array of text to search """
def write_parameter(name, value, parameters):
    # only write parameters that have filled out fields
    if value not in ('', None):
        # loop through every text line in parameters
        for i in range(0, len(parameters)):
            # search for the name and ignore upper/lower case
            if re.search(name, parameters[i], re.IGNORECASE):
                # write the value of the parameter which is on the next line after our found name
                parameters[i + 1] = value + '\n'
                return

    # if parameter not found, give warning popup
    sg.Popup('Warning:', name + ' not found in input parameter format, so not saved to output file')

""" Function to update all of the window parameter values from the file passed in
    @param filename of the parameter file to use
    @param window from pysimplegui to update with values
    @return parameters array of text from file """
def load_parameters(filename, window):
    # check if filename exists in main/ directory
    if os.path.exists(filename) is False:
        sg.Popup('Error:', filename + ' does not exist')
        return None

    # read array of text from passed in file
    parameter_file = open(filename, 'r')
    parameters = parameter_file.readlines()
    parameter_file.close()

    # the keys of pysimplegui objects established in layout[] is used to index the window to update their values

    # udpate general parameters on window
    window['TASKORDER_SERIES'].Update(re.search('Series', read_parameter('Task Order', parameters), re.IGNORECASE))
    window['TASKORDER_RAND'].Update(re.search('Random', read_parameter('Task Order', parameters), re.IGNORECASE))

    # update side task parameters on window
    window['S_YES'].Update(re.search('Yes', read_parameter('Side Task Active', parameters), re.IGNORECASE))
    window['S_NO'].Update(re.search('No', read_parameter('Side Task Active', parameters), re.IGNORECASE))
    window['TRIALS_S'].Update(read_parameter('Side Task Trials to Criterion', parameters))
    window['LEVEL_S'].Update(read_parameter('Side Start Level', parameters))
    window['RESPONSE_S'].Update(read_parameter('Side Task Response Time', parameters))
    window['TIMEOUT_S'].Update(read_parameter('Side Task Timeout Time', parameters))
    window['TIT_S_YES'].Update(re.search('Yes', read_parameter('Side Task Titration', parameters), re.IGNORECASE))
    window['TIT_S_NO'].Update(re.search('No', read_parameter('Side Task Titration', parameters), re.IGNORECASE))

    # update chase task parameters on window
    window['C_YES'].Update(re.search('Yes', read_parameter('Chase Task Active', parameters), re.IGNORECASE))
    window['C_NO'].Update(re.search('No', read_parameter('Chase Task Active', parameters), re.IGNORECASE))
    window['TRIALS_C'].Update(read_parameter('Chase Task Trials to Criterion', parameters))
    window['CIRCLE_C'].Update(read_parameter('Chase Circle Size', parameters))
    window['RESPONSE_C'].Update(read_parameter('Chase Task Response Time', parameters))
    window['TIMEOUT_C'].Update(read_parameter('Chase Task Timeout Time', parameters))
    window['TIT_C_YES'].Update(re.search('Yes', read_parameter('Chase Task Titration', parameters), re.IGNORECASE))
    window['TIT_C_NO'].Update(re.search('No', read_parameter('Chase Task Titration', parameters), re.IGNORECASE))

    # update pursuit task parameters on window
    window['P_YES'].Update(re.search('Yes', read_parameter('Pursuit Task Active', parameters), re.IGNORECASE))
    window['P_NO'].Update(re.search('No', read_parameter('Pursuit Task Active', parameters), re.IGNORECASE))
    window['TRIALS_P'].Update(read_parameter('Pursuit Task Trials to Criterion', parameters))
    window['CIRCLE_P'].Update(read_parameter('Pursuit Circle Size', parameters))
    window['PURSUIT_P'].Update(read_parameter('Pursuit Task Pursuit Time', parameters))
    window['RESPONSE_P'].Update(read_parameter('Pursuit Task Response Time', parameters))
    window['TIMEOUT_P'].Update(read_parameter('Pursuit Task Timeout Time', parameters))
    window['TIT_P_YES'].Update(re.search('Yes', read_parameter('Pursuit Task Titration', parameters), re.IGNORECASE))
    window['TIT_P_NO'].Update(re.search('No', read_parameter('Pursuit Task Titration', parameters), re.IGNORECASE))

    # update mts task parameters on window
    window['MTS_YES'].Update(re.search('Yes', read_parameter('MTS Task Active', parameters), re.IGNORECASE))
    window['MTS_NO'].Update(re.search('No', read_parameter('MTS Task Active', parameters), re.IGNORECASE))
    window['TRIALS_MTS'].Update(read_parameter('MTS Task Trials for Criterion', parameters))
    window['PERCENT_MTS'].Update(read_parameter('MTS Task % Correct for Criterion', parameters))
    window['RESPONSE_MTS'].Update(read_parameter('MTS Task Response Time', parameters))
    window['TIMEOUT_MTS'].Update(read_parameter('MTS Task Timeout Time', parameters))
    window['TIT_MTS_YES'].Update(re.search('Yes', read_parameter('MTS Task Titration', parameters), re.IGNORECASE))
    window['TIT_MTS_NO'].Update(re.search('No', read_parameter('MTS Task Titration', parameters), re.IGNORECASE))

    # update dmts task parameters on window
    window['DMTS_YES'].Update(re.search('Yes', read_parameter('DMTS Task Active', parameters), re.IGNORECASE))
    window['DMTS_NO'].Update(re.search('No', read_parameter('DMTS Task Active', parameters), re.IGNORECASE))
    window['TRIALS_DMTS'].Update(read_parameter('DMTS Task Trials for Criterion', parameters))
    window['PERCENT_DMTS'].Update(read_parameter('DMTS Task % Correct for Criterion', parameters))
    window['DELAY_DMTS'].Update(read_parameter('DMTS Delay Time', parameters))
    window['RESPONSE_DMTS'].Update(read_parameter('DMTS Task Response Time', parameters))
    window['TIMEOUT_DMTS'].Update(read_parameter('DMTS Task Timeout Time', parameters))
    window['TIT_DMTS_YES'].Update(re.search('Yes', read_parameter('DMTS Task Titration', parameters), re.IGNORECASE))
    window['TIT_DMTS_NO'].Update(re.search('No', read_parameter('DMTS Task Titration', parameters), re.IGNORECASE))

    # update learning set task parameters on window
    window['L_YES'].Update(re.search('Yes', read_parameter('Learning Set Task Active', parameters), re.IGNORECASE))
    window['L_NO'].Update(re.search('No', read_parameter('Learning Set Task Active', parameters), re.IGNORECASE))
    window['TRIALSPERPROB_LS'].Update(read_parameter('Learning Set Trials Per Problem', parameters))
    window['NUMPROBS_LS'].Update(read_parameter('Learning Set Number of Problems', parameters))
    window['PERCENT_LS'].Update(read_parameter('Learning Set % Correct for Criterion', parameters))
    window['RESPONSE_LS'].Update(read_parameter('Learning Set Response Time', parameters))
    window['TIMEOUT_LS'].Update(read_parameter('Learning Set Timeout Time', parameters))
    window['TIT_LS_YES'].Update(re.search('Yes', read_parameter('Learning Set Titration', parameters), re.IGNORECASE))
    window['TIT_LS_NO'].Update(re.search('No', read_parameter('Learning Set Titration', parameters), re.IGNORECASE))


    return parameters

""" Function to write all of the current window parameter values to a file
    @param filename of the parameter file to write to
    @param values pysimplegui array to take parameters from
    @param parameters array of text to use as file base """
def save_parameters(filename, values, parameters):
    # the keys of pysimplegui objects established in layoutr[] is used to index the values array for their current value

    # save general parameters
    write_parameter('Task Order', ('Random','Series')[values['TASKORDER_SERIES']], parameters)

    # save side task parameters from window
    write_parameter('Side Task Active', ('No','Yes')[values['S_YES']], parameters)
    write_parameter('Side Task Trials to Criterion', values['TRIALS_S'], parameters)
    write_parameter('Side Start Level', values['LEVEL_S'], parameters)
    write_parameter('Side Task Response Time', values['RESPONSE_S'], parameters)
    write_parameter('Side Task Timeout Time', values['TIMEOUT_S'], parameters)
    write_parameter('Side Task Titration', ('No','Yes')[values['TIT_S_YES']], parameters)

    # save chase task parameters from window
    write_parameter('Chase Task Active', ('No','Yes')[values['C_YES']], parameters)
    write_parameter('Chase Task Trials to Criterion', values['TRIALS_C'], parameters)
    write_parameter('Chase Circle Size', values['CIRCLE_C'], parameters)
    write_parameter('Chase Task Response Time', values['RESPONSE_C'], parameters)
    write_parameter('Chase Task Timeout Time', values['TIMEOUT_C'], parameters)
    write_parameter('Chase Task Titration', ('No','Yes')[values['TIT_C_YES']], parameters)

    # save pursuit task parameters from window
    write_parameter('Pursuit Task Active', ('No','Yes')[values['P_YES']], parameters)
    write_parameter('Pursuit Task Trials to Criterion', values['TRIALS_P'], parameters)
    write_parameter('Pursuit Circle Size', values['CIRCLE_P'], parameters)
    write_parameter('Pursuit Task Pursuit Time', values['PURSUIT_P'], parameters)
    write_parameter('Pursuit Task Response Time', values['RESPONSE_P'], parameters)
    write_parameter('Pursuit Task Timeout Time', values['TIMEOUT_P'], parameters)
    write_parameter('Pursuit Task Titration', ('No','Yes')[values['TIT_P_YES']], parameters)

    # save mts task parameters from window
    write_parameter('MTS Task Active', ('No','Yes')[values['MTS_YES']], parameters)
    write_parameter('MTS Task Trials for Criterion', values['TRIALS_MTS'], parameters)
    write_parameter('MTS Task % Correct for Criterion', values['PERCENT_MTS'], parameters)
    write_parameter('MTS Task Response Time', values['RESPONSE_MTS'], parameters)
    write_parameter('MTS Task Timeout Time', values['TIMEOUT_MTS'], parameters)
    write_parameter('MTS Task Titration', ('No','Yes')[values['TIT_MTS_YES']], parameters)

    # save dmts task parameters from window
    write_parameter('DMTS Task Active', ('No','Yes')[values['DMTS_YES']], parameters)
    write_parameter('DMTS Task Trials for Criterion', values['TRIALS_DMTS'], parameters)
    write_parameter('DMTS Task % Correct for Criterion', values['PERCENT_DMTS'], parameters)
    write_parameter('DMTS Delay Time', values['DELAY_DMTS'], parameters)
    write_parameter('DMTS Task Response Time', values['RESPONSE_DMTS'], parameters)
    write_parameter('DMTS Task Timeout Time', values['TIMEOUT_DMTS'], parameters)
    write_parameter('DMTS Task Titration', ('No','Yes')[values['TIT_DMTS_YES']], parameters)

    # save learning set task parameters from window
    write_parameter('Learning Set Task Active', ('No','Yes')[values['L_YES']], parameters)
    write_parameter('Learning Set Trials Per Problem', values['TRIALSPERPROB_LS'], parameters)
    write_parameter('Learning Set Number of Problems', values['NUMPROBS_LS'], parameters)
    write_parameter('Learning Set % Correct for Criterion', values['PERCENT_LS'], parameters)
    write_parameter('Learning Set Response Time', values['RESPONSE_LS'], parameters)
    write_parameter('Learning Set Timeout Time', values['TIMEOUT_LS'], parameters)
    write_parameter('Learning Set Titration', ('No','Yes')[values['TIT_LS_YES']], parameters)

    # write array of text to file passed in
    parameter_file = open(filename, 'w')
    parameter_file.writelines(parameters)
    parameter_file.close()

""" Main function called at runtime, starts the pysimplegui window and
        handles user input for loading/saving/writing parameters, ends
        when user hits 'Go' and a parameter file was loaded atleast once. """
def main():
    loaded = False

    # start the pysimplegui window based on the layout we defined
    window = sg.Window('Cognitive Testing System', layout)

    # event loop to process 'events' and get the 'values' of the inputs
    while True:             
        event, values = window.read() # update pysimplegui values

        # if user closes Window
        if event in ([None]):
            window.close()
            sys.exit()

        # if user clicks 'Load' button
        if event in (['Load']):
            # if there is a filename in load parameters file selection
            if (values['IN_FILE'] not in ('', None)):
                # get array of text from parameter file
                parameters = load_parameters(values['IN_FILE'], window)

                # if array of text is not empty, we have successfully loaded our parameters
                if parameters is not None:
                    loaded = True

            # if user did not select a file to load but clicked Load button
            else:
                sg.Popup('Error:', 'No filename to load parameters from')

        # if user clicks 'Save' button
        if event in (['Save']):
            # if there is a filename in save parameters file selection
            if (values['OUT_FILE'] not in ('', None)):
                # make sure we have loaded atleast once before saving file
                if loaded is True:
                    save_parameters(values['OUT_FILE'], values, parameters)
                else:
                    sg.Popup('Error:', 'Need to load parameters from file once first to get format')

            # if user did not select a file to save but clicked Save button
            else:
                sg.Popup('Error:', 'No filename to save parameters to')

        # if user clicks 'Go' button
        if event in (['Go']):
            # if we have loaded a parameters file atleast once, then we can end
            if loaded is False:
                sg.Popup('Error:', 'Must load parameters from file first')
            else:
                break

    # close pysimplegui window
    window.close()

    # write our current window parameters to parmeters_file that is used by game.py
    save_parameters(os.path.join(main_dir, parameters_file), values, parameters)

    # call game.py to run the tasks with out parameters
    os.system('python3 {}'.format(os.path.join(main_dir, 'game.py')))

# this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()
