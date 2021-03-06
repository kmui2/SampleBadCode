#from pyglet.media import avbin
import numpy

from psychopy import core, logging, event, visual, data, gui, misc, prefs, sound, core, visual
import glob
import os
import random
import sys
import gc
import time
import hashlib
import subprocess
import math
from scipy import ndimage

# attempting import winsound
try:
    import winsound
except ImportError:
    print "Warning: winsound not found; will try using pyo/pyaudio"

# attempting import pyo
try:
    import pyo
    print "Attempting to use pyo for sounds"
    prefs.general['audioLib'] = ['pyo']
    print 'initializing pyo to 48000'
    sound.init(48000, buffer=128)
    print 'Using %s(with %s) for sounds' % (sound.audioLib, sound.audioDriver)
except:
    print 'could not load pyo'

# attempting import pygame
try:
    import pygame
    from pygame.locals import *
except ImportError:
    print "Warning: pygame not found; will be using pyglet for stim presentation"


def killDropbox():
    try:
        error = os.system('taskkill /f /im Dropbox.exe /t')
        if not error:
            print "Dropbox terminated"
        else:
            print "Dropbox not running, so can't terminate"
    except:
        pass


def startDropbox():
    try:
        subprocess.Popen('start /B %USERPROFILE%/desktop/dropboxShortcut.lnk', shell=True)
        print "Dropbox restarted"
    except:
        print "Could not re-start dropbox"


def getHash(files):
    if not isinstance(files, list):
        files = [files]
    hashes = [(fname, hashlib.md5(file(fname, 'r').read()).hexdigest()) for fname in files]
    return hashes


def circularList(lst, seed):
    if not isinstance(lst, list):
        lst = range(lst)
    i = 0
    random.seed(seed)
    random.shuffle(lst)
    while True:
        yield lst[i]
        if (i + 1) % len(lst) == 0:
            random.shuffle(lst)
        i = (i + 1) % len(lst)


def getRunTimeVars(varsToGet, order, expVersion):
    """Get run time variables, see http://www.psychopy.org/api/gui.html for explanation"""
    infoDlg = gui.DlgFromDict(dictionary=varsToGet, title=expVersion, fixed=[expVersion], order=order)
    order.append('dateStr')
    order.append('expVersion')
    varsToGet['dateStr'] = data.getDateStr()
    varsToGet['expVersion'] = expVersion
    if infoDlg.OK:
        return varsToGet
    else:
        print 'User Cancelled'


def enterSubjInfo(expName, optionList):
    """ Brings up a GUI in which to enter all the subject info."""

    def inputsOK(optionList, expInfo):
        for curOption in sorted(optionList.items()):
            name = curOption[1]['name']
            options = curOption[1]['options']

            if options != 'any' and expInfo[name] not in options:
                return [False, "The option you entered for {name} is not in the allowable list of options: {options})"
                .format(name=name, options=str(options))]
        
        print "inputsOK passed"
        return [True, '']

    try:
        expInfo = misc.fromFile(expName + '_lastParams.pickle')
    except:
        expInfo = {}  # make the kind of dictionary that this gui can understand
        for curOption in sorted(optionList.items()):
            expInfo[curOption[1]['name']] = curOption[1]['default']
    # load the tips
    tips = {}
    for curOption in sorted(optionList.items()):
        tips[curOption[1]['name']] = curOption[1]['prompt']
    expInfo['dateStr'] = data.getDateStr()
    expInfo['expName'] = expName
    dlg = gui.DlgFromDict(expInfo, title=expName, fixed=['dateStr', 'expName'], order=[optionName[1]['name'] for optionName in sorted(optionList.items())], tip=tips)
    if dlg.OK:
        misc.toFile(expName + '_lastParams.pickle', expInfo)
        [success, error] = inputsOK(optionList, expInfo)
        if success:
            return [True, expInfo]
        else:
            return [False, error]
    else:
        core.quit()


def popupError(text):
    errorDlg = gui.Dlg(title="Error", pos=(200, 400))
    errorDlg.addText('Error: ' + text, color='Red')
    errorDlg.show()


def setupSubjectVariables():
    parser = OptionParser()
    parser.add_option("-s", "--subject-id", dest="subjid", help="specify the subject id")

    (options, args) = parser.parse_args()
    self.subjID = options.subjid

    if not self.subjID:
        print "You must provide a Subject ID"
        parser.print_help()
        sys.exit()


def writeHeader(curTrial, headerText, fileName='header'):
    try:
        if curTrial['trialNum'] == 1:
            if os.path.isfile(fileName + '.txt'):  # file already exists
                print 'header file exists'
                return False
            else:
                headerFile = open(fileName + '.txt', 'w')
                writeToFile(headerFile, headerText)
                return True
    except:
        return False


def writeToFile(fileHandle, trial, sync=True):
    """Writes a trial (array of lists) to a fileHandle"""
    line = '\t'.join([str(i) for i in trial])  # TABify
    line += '\n'  # add a newline
    fileHandle.write(line)
    if sync:
        fileHandle.flush()
        os.fsync(fileHandle)


def syncFile(fileHandle):
    """syncs file to prevent buffer loss"""
    fileHandle.flush()
    os.fsync(fileHandle)


def getSubjVariables(allSubjVariables):
    def checkInput(value, options, type):
        """Checks input.  Uses 'any' as an option to check for any <str> or <int>"""
        try:
            # if the user typed something and it's an instance of the correct type and it's in the options list...
            if value and isinstance(value, type) and ('any' in options or value.upper() in options):
                return True
            return False
        except:
            print"Try again..."
    subjVariables = {}
    for curNum, varInfo in sorted(allSubjVariables.items()):
        curValue = ''
        while not checkInput(curValue, varInfo['options'], varInfo['type']):
            curValue = raw_input(varInfo['prompt'])
        if not 'any' in varInfo['options']:
            curValue = str(curValue.upper())
        subjVariables[varInfo['name']] = curValue
    return subjVariables


def loadFiles(directory, extension, fileType, win='', whichFiles='*', stimList=[]):
    """ Load all the pics and sounds"""
    path = os.getcwd()  # set path to current directory
    if isinstance(extension, list):
        fileList = []
        for curExtension in extension:
            fileList.extend(glob.glob(os.path.join(
                path, directory, whichFiles + curExtension)))
    else:
        fileList = glob.glob(os.path.join(
            path, directory, whichFiles + extension))
	
    fileMatrix = {}  # initialize fileMatrix  as a dict because it'll be accessed by picture names, cound names, whatver
    for num, curFile in enumerate(fileList):
        fullPath = curFile
        fullFileName = os.path.basename(fullPath)
        stimFile = os.path.splitext(fullFileName)[0]
        if fileType == "image":
            try:
                # gets height/width of the image
                surface = pygame.image.load(fullPath)
                stim = visual.ImageStim(
                    win, image=fullPath, mask=None, interpolate=True)
                fileMatrix[stimFile] = (
                    (stim, fullFileName, num, surface.get_width(), surface.get_height(), stimFile))
            except:  # no pygame, so don't store the image dims
                stim = visual.ImageStim(
                    win, image=fullPath, mask=None, interpolate=True)
                fileMatrix[stimFile] = (
                    (stim, fullFileName, num, '', '', stimFile))
        elif fileType == "sound":
            soundRef = sound.Sound(fullPath)
            fileMatrix[stimFile] = ((soundRef))
        elif fileType == "winSound":
            soundRef = open(fullPath, "rb").read()
            fileMatrix[stimFile] = ((soundRef))
            # this allows asynchronous playing in winSound.
            fileMatrix[stimFile + '-path'] = fullPath

    # check
    if stimList and set(fileMatrix.keys()).intersection(stimList) != set(stimList):
        popupError(str(set(stimList).difference(fileMatrix.keys())) +
                   " does not exist in " + path + '\\' + directory)
    return fileMatrix


def loadFilesOld(directory, extension, fileType, win='', whichFiles='*', stimList=[]):
    """ Load all the pics and sounds"""
    path = os.getcwd()  # set path to current directory
    if type(extension).__name__ == 'list':
        fileList = []
        for curExtension in extension:
            fileList.extend(glob.glob(os.path.join(
                path, directory, whichFiles + curExtension)))
    else:
        fileList = glob.glob(os.path.join(
            path, directory, whichFiles + extension))
    fileMatrix = {}  # initialize fileMatrix  as a dict because it'll be accessed by picture names, cound names, whatver
    for i in range(len(fileList)):
        fullPath = fileList[i]
        fullFileName = os.path.basename(fullPath)
        # chops off the extension
        stimFile = fullFileName[:len(fullFileName) - 4]
        if fileType == "image":
            try:
                # this is just to get heigh/width of the image
                surface = pygame.image.load(fullPath)
                #stim = visual.PatchStim(win, tex=fullPath)
                stim = visual.SimpleImageStim(win, image=fullPath)
                fileMatrix[stimFile] = (
                    (stim, fullFileName, i, surface.get_width(), surface.get_height(), stimFile))
            except:  # no pygame, so don't store the image dims
                stim = visual.SimpleImageStim(win, image=fullPath)
                fileMatrix[stimFile] = (
                    (stim, fullFileName, i, '', '', stimFile))

        elif fileType == "sound":
            soundRef = sound.Sound(fullPath)
            fileMatrix[stimFile] = ((soundRef))
        elif fileType == "winSound":
            soundRef = highPitch = open(fullPath, "rb").read()
            fileMatrix[stimFile] = ((soundRef))
    # check
    if stimList and set(fileMatrix.keys()).intersection(stimList) != set(stimList):
        # print stimList, fileMatrix.keys(),set(stimList).difference(fileMatrix.keys())
        popupError(str(set(stimList).difference(fileMatrix.keys())) +
                   " does not exist in " + path + '\\' + directory)

    return fileMatrix


def sortDictValues(someDict, returnWhat='values'):
    keys = someDict.keys()
    keys.sort()
    if returnWhat == 'values':
        return map(someDict.get, keys)
    else:
        return keys


def createResp(allSubjVariables, subjVariables, fieldVars, **respVars):
    trial = []  # initalize array
    for curSubjVar, varInfo in sorted(allSubjVariables.items()):
        trial.append(subjVariables[varInfo['name']])

    trial.append(subjVariables['expName'])
    trial.append(subjVariables['dateStr'])
    for curFieldVar in fieldVars:
        trial.append(curFieldVar)
    for curRespVar in sortDictValues(respVars):
        trial.append(str(curRespVar))
    return trial


def createRespNew(allSubjVariables, subjVariables, fieldVarNames, fieldVars, **respVars):
    """Creates  a key and value list of all the variables passed in from various sources (runtime, trial params, dep. vars."""

    def stripUnderscores(keyList):
        return [curKey.split('_')[1] for curKey in keyList]

    trial = []  # initalize array
    header = []
    for curSubjVar, varInfo in sorted(allSubjVariables.items()):
        header.append(allSubjVariables[curSubjVar]['name'])
        trial.append(subjVariables[varInfo['name']])
    for curFieldVar in fieldVars:
        trial.append(curFieldVar)
    for curRespVar in sortDictValues(respVars):
        trial.append(str(curRespVar))
    header.extend(fieldVarNames)
    header.extend(stripUnderscores(sortDictValues(respVars, 'keys')))
    return [header, trial]


def importTrials(fileName, method="sequential", seed=random.randint(1, 100)):
    (stimList, fieldNames) = data.importConditions(
        fileName, returnFieldNames=True)
    # seed is ignored for sequential; used for 'random'
    trials = data.TrialHandler(stimList, 1, method=method, seed=seed)
    return (trials, fieldNames)


def initGamepad():
    pygame.joystick.init()  # init main joystick device system
    try:
        stick = pygame.joystick.Joystick(0)
        stick.init()  # init instance
        return stick
    except pygame.error:
        raise SystemExit(
            "---->No joystick/gamepad found. Make sure one is plugged in<--")


def getKeyboardResponse(validResponses, duration=0):
    event.clearEvents()
    responded = False
    done = False
    rt = '*'
    responseTimer = core.Clock()
    while True:
        if not responded:
            responded = event.getKeys(
                keyList=validResponses, timeStamped=responseTimer)
        if duration > 0:
            if responseTimer.getTime() > duration:
                break
        else:  # end on response
            if responded:
                break
    if not responded:
        return ['*', '*']
    else:
        return responded[0]  # only get the first resp


def getKeyboardResponseEndResp(validResponses, duration=0, endOnResponse=True):
    event.clearEvents()
    responded = False
    done = False
    rt = '*'
    responseTimer = core.Clock()
    while True:
        if not responded:
            responded = event.getKeys(
                keyList=validResponses, timeStamped=responseTimer)
        if duration > 0:
            if responseTimer.getTime() > duration or responded:
                break
        else:  # end on response
            if responded:
                break
    if not responded:
        return ['*', '*']
    else:
        return responded[0]  # only get the first resp


def getMouseResponse(mouse, duration=0):
    event.clearEvents()
    responseTimer = core.Clock()
    numButtons = len(event.mouseButtons)
    response = [0] * numButtons
    timeElapsed = False
    mouse.clickReset()
    responseTimer.reset()
    rt = '*'
    while not any(response) and not timeElapsed:
        (response, rt) = mouse.getPressed(getTime=True)
        if duration > 0 and responseTimer.getTime() > duration:
            timeElapsed = True

    if not any(response):  # if there was no response (would only happen if duration is set)
        return ('*', '*')
    else:
        nonZeroResponses = filter(lambda x: x > 0, rt)
        # only care about the first (earliest) click
        firstResponseButtonIndex = rt.index(min(nonZeroResponses))
        return (firstResponseButtonIndex, rt[firstResponseButtonIndex])


# TO DO: move stick to the last parameter so it's treated as optional - that way we can have a generic response function that either takes or doesn't take a joystick parameter as provided.
def getGamepadResponse(stick, validResponses, duration=0):
    """joystick needs to be initialized (with initGamepad or manually). Only returns the first response. """
    def getJoystickResponses():  # returns buttons. If none are pressed, checks the hat.
        for n in range(stick.get_numbuttons()):
            if stick.get_button(n):  # if this is down
                return n
        for n in range(stick.get_numhats()):
            return stick.get_hat(n)

    responded = False
    timeElapsed = False
    responseTimer = core.Clock()
    response = "*"
    rt = '*'
    pygame.event.clear()  # clear event cue
    responseTimer.reset()
    while not responded and not timeElapsed:
        for event in pygame.event.get():  # iterate over event stack
            if event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYHATMOTION:
                response = getJoystickResponses()
                print 'responded', response
                if response in validResponses:
                    rt = responseTimer.getTime()
                    responded = True
                    break
        if duration > 0 and responseTimer.getTime() > duration:
            timeElapsed = True
    if not responded:
        return ['*', '*']
    else:
        return (response, rt)


def euclidDistance(pointA, pointB):
    return sqrt((pointA[0] - pointB[0])**2 + (pointA[1] - pointB[1])**2)


def pressedSomething(validKeys):
    for event in pygame.event.get():
        if event.type in (QUIT, KEYDOWN, MOUSEBUTTONDOWN):
            if event.key in validKeys:
                return True


def makeBorder(width=128, height=128, borderColor=-1, xborder=10, yborder=10):
    """ creates a bitmap with a border"""
    borderColor = -1
    array = numpy.zeros([height, width])
    array[xborder:-xborder, yborder:-yborder] = 1
    if xborder > 0:
        array[:xborder, :] = array[-xborder:, :] = borderColor
    if yborder > 0:
        array[:, :yborder] = array[:, -yborder:] = borderColor
    return array
