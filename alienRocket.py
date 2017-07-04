#!/usr/bin/env python
############################
#  Import various modules  #
############################
import socket
import time
import webbrowser as web
import json
from optionList import optionList

from baseDefsPsychoPy import *
from generateTrials import *
from generateTrialsVerification import *
from stimPresPsychoPy import *


class Exp:
    def __init__(self):

        optionsReceived = False
        fileOpened = False        
        while not fileOpened:
            [optionsReceived, self.subjVariables] = enterSubjInfo('same-gekTalp-noDelay-question-HTEST', optionList) 
            if not optionsReceived:
                popupError(self.subjVariables)
            elif os.path.isfile(self.subjVariables['subjCode'] + '_test.txt'):
                    popupError('Error: That subject code already exists')
            else:
                self.outputFile = open(self.subjVariables['subjCode'] + '_test.txt', 'w')
                fileOpened = True
            # print 'options received: ', optionsReceived, self.subjVariables

        if (
        self.subjVariables['locationMapping'] != 'V' and generateTrials(
            self.subjVariables['subjCode'], 
            self.subjVariables['seed'], 
            self.subjVariables['mapping'], 
            self.subjVariables['locationMapping'], 
            self.subjVariables['categoryStructure']
        )
        ) or generateTrialsVerification(
            self.subjVariables['subjCode'], 
            self.subjVariables['seed'], 
            self.subjVariables['mapping'], 
            self.subjVariables['locationMapping']
        ):
             print "Trials generated"
        else:
            print "Trials not generated - error"
            core.quit()

        if self.subjVariables['responseDevice'] == 'gamepad':
            try:
                self.stick = initGamepad()
                pygame.init()
                self.validResponses = {7: 'right', 6: 'left'}
                self.validResponsesVerification = {7: 'No', 6: 'Yes'}
                self.inputDevice = "gamepad"
                responseInfo = " You will use the gamepad to respond. The experimenter will tell you which keys to use."
            except SystemExit:
                self.subjVariables['responseDevice'] = 'keyboard'
                print "No joystick; using keyboard"
                self.inputDevice = "keyboard"
                self.validResponses = {'z': 'left', 'slash': 'right'}
                self.validResponsesVerification = {'z': 'Yes', 'slash': 'No'}
                responseInfo = " You will use the keyboard keys to respond (z for left and / for right. Place your right index finger on the / key and your left middle finger on the z key."

        else:
            print "Using keyboard"
            self.inputDevice = "keyboard"
            self.validResponses = {'z': 'left', 'slash': 'right'}
            self.validResponsesVerification = {'z': 'Yes', 'slash': 'No'}
            responseInfo = " You will use the keyboard keys to respond (z for left and / for right. Place your right index finger on the / key and your left middle finger on the z key."

        self.win = visual.Window(fullscr=True, pos=[
                                 0, 0], color="white", allowGUI=False, monitor='testingRoom', units='pix', winType='pyglet')
        #self.win = visual.Window([1280,1024], pos=[0,0],color="white", allowGUI=False, monitor='officeMonitor',units='pix',winType='pyglet')

        self.surveyURL = 'https://uwmadison.qualtrics.com/SE/?' + \
            'SID=SV_8GoDUWHh9892NBH'

    # populate survey URL with subject code and experiment room
        self.subjVariables['room'] = socket.gethostname()
        self.surveyURL += '&subjCode=%s&room=%s&mapping=%s&locationMapping=%s' % (
            self.subjVariables['subjCode'], self.subjVariables['room'], self.subjVariables['mapping'], self.subjVariables['locationMapping'])

        self.preFixationDelay = 0.250
        self.ITI = .40
        self.preLabelDelay = 0  # 1.2 #.700 #0
        self.postResponseDelay = .200
        self.numPracticeTrials = 5
        self.takeBreakEveryXTrials = 70

        self.instructionsGekTalp = \
            """In this task you will see schematic pictures of various rockets.  There are two types of rockets - gek rockets, and talp rockets. Your goal is to figure out which ones are which. On each trial of this experiment you will see a picture of one of the rockets and then the two options (gek and talp) will appear to the left and right of the picture. You should respond with the appropriate (left or right) key to choose the kind of rocket you think it is. After you make a choice you will hear a buzzing sound if you made a mistake, and a bleeping sound if you responded correctly. In the beginning you will just be guessing, but you'll soon find yourself improving. Note that on some trials there won't be any feedback (buzz or bleep) sounds. This is normal.
		
		Try to do your best, and don't spend too much time on any one trial. Please let the experimenter know if you have any questions. We'll start with some practice trials.
		\n\n"""

        self.instructionsGekTalpHypothesis = \
            """In this task you will see schematic pictures of various rockets.  There are two types of rockets: gek rockets, and talp rockets. Your goal is to figure out which ones are which by testing hypotheses. On each trial of this experiment you will see a picture of one of the rockets and then the two options (gek and talp) will appear to the left and right of the picture. You should respond with the appropriate (left or right) key to choose the kind of rocket you think it is. After you make a choice you will hear a buzzing sound if you made a mistake, and a bleeping sound if you responded correctly. In the beginning you will just be guessing, but you'll soon find yourself improving. On each trial you should ask yourself questions like "is it the shape of the wings? Is it the shape of the tail? YOU WILL NEED TO CONSIDER MORE THAN ONE FEATURE AT A TIME".  Note that on some trials there won't be any feedback (buzz or bleep) sounds. This is normal.
		
		Try to do your best, and don't spend too much time on any one trial. Please let the experimenter know if you have any questions. We'll start with some practice trials.
		\n\n"""

        self.instructionsGekTalpVerify = \
            """In this task you will see schematic pictures of various rockets.  There are two types of rockets - gek rockets, and talp rockets. Your goal is to figure out which ones are which. On each trial of this experiment you will see a picture of one of the rockets and a prompt 'Is this a gek rocket' or 'Is this a talp rocket'. You should respond 'Yes' or 'No' depending on what you think the answer is. Press the left key to respond 'Yes' and the right key to respond 'No. The experimenter will let you know which specific buttons to use. After you make a choice you will hear a buzzing sound if you made a mistake, and a bleeping sound if you responded correctly. In the beginning you will just be guessing, but you'll soon find yourself improving. **Note that on some trials there won't be any feedback (buzz or bleep) sounds. This is normal.**
		
		Try to do your best, and don't spend too much time on any one trial. Please let the experimenter know if you have any questions. We'll start with some practice trials.
		\n\n"""

        self.instructionsTypeAB = \
            """In this task you will see schematic pictures of various rockets.  There are two types of rockets - gek rockets, and talp rockets. Your goal is to figure out which ones are which. On each trial of this experiment you will see a picture of one of the rockets and then the two options (Type A and Type B) will appear to the left and right of the picture. You should respond with the appropriate (left or right) key to choose the kind of rocket you think it is (Type A or Type B). After you make a choice you will hear a buzzing sound if you made a mistake, and a bleeping sound if you responded correctly. In the beginning you will just be guessing, but you'll soon find yourself improving. *Note that on some trials there won't be any feedback (buzz or bleep) sounds. This is normal.*
		
		Try to do your best, and don't spend too much time on any one trial. Please let the experimenter know if you have any questions. We'll start with some practice trials.
		\n\n"""

        self.instructionsGekTalp += responseInfo
        self.instructionsTypeAB += responseInfo

        if self.subjVariables['mapping'] == 'A1' or self.subjVariables['mapping'] == 'A2':
            self.instructions = self.instructionsTypeAB
        elif self.subjVariables['locationMapping'] == 'V':
            self.validResponses = self.validResponsesVerification
            self.instructions = self.instructionsGekTalpVerify
        else:
            # self.instructions=self.instructionsGekTalp
            self.instructions = self.instructionsGekTalpHypothesis

        self.takeBreak = "Please take a short break.\nPress a key when you are ready to continue."
        self.finalText = "Thank you for participating. We will now ask you some questions about the task. Press enter. A web page should come up. If it doesn't, please alert the experimenter"

        self.practiceTrials = "The next part is practice"
        self.realTrials = "Now for the real trials."


class ExpPresentation():
    def __init__(self, experiment):
        self.experiment = experiment

    def initializeExperiment(self):
        """This loads all the stimili and initializes the trial sequence"""
        self.fixSpot = visual.PatchStim(
            self.experiment.win, tex="none", mask="gauss", size=15, color='white')
        (self.trialListMatrix, self.fieldNames) = importTrials(
            self.experiment.subjVariables["subjCode"] + '_trialList.csv', method="sequential")

        self.centerRectOuter = newRect(self.experiment.win, size=(
            292, 292), pos=(0, 0), color=(0, 0, 0))
        self.centerRectInner = newRect(self.experiment.win, size=(
            288, 288), pos=(0, 0), color=(1, 1, 1))

        showText(self.experiment.win, "Loading Images...",
                 color="gray", waitForKey=False)

        print 'SOUND PREFS: ', prefs.general['audioLib'], prefs.general['audioLib'][0], prefs.general['audioLib'][0] == "pygame"
        if prefs.general['audioLib'] == ['pygame'] or prefs.general['audioLib'][0] == 'pygame':
            print 'loading winsounds'
            self.soundMatrix = loadFiles('stimuli', ['wav'], 'winSound')
        else:
            self.soundMatrix = loadFiles('stimuli', ['wav'], 'sound')
        #self.soundMatrix = loadFiles('stimuli','wav','pyo')
        self.pictureMatrix = loadFiles(
            'stimuli', ['gif', 'png'], 'image', self.experiment.win)
        self.locations = {
            'left': (-270, 0), 'right': (270, 0), 'center': (0, 0)}

    def presentExperimentTrial(self, trialIndex, whichPart, curTrial):
        if self.experiment.subjVariables['locationMapping'] == 'V':
            prompt = newText(self.experiment.win, text="Is this rocket a " +
                             curTrial['labelPrompt'] + '?', color="black", scale=1.5, pos=[0, 400])
            labelReversalMap = {'gek': 'talp', 'talp': 'gek'}
            sideToLabelMap = {
                'Yes': curTrial['labelPrompt'], 'No': labelReversalMap[curTrial['labelPrompt']]}
        else:
            labelLeft = newText(
                self.experiment.win, text=curTrial['labelLeft'], pos=self.locations['left'], color="black", scale=2.0)
            labelRight = newText(
                self.experiment.win, text=curTrial['labelRight'], pos=self.locations['right'], color="black", scale=2.0)
            sideToLabelMap = {
                'left': curTrial['labelLeft'], 'right': curTrial['labelRight']}
        yes = newText(self.experiment.win, text='Yes',
                      pos=self.locations['left'], color="black", scale=1.0)
        no = newText(self.experiment.win, text='No',
                     pos=self.locations['right'], color="black", scale=1.0)

        self.experiment.win.flip()
        core.wait(self.experiment.ITI)
        self.pictureMatrix[curTrial['stim']][0].setPos([0, 0])
        setAndPresentStimulus(self.experiment.win, [
                              self.pictureMatrix[curTrial['stim']][0]], self.experiment.preLabelDelay)
        if self.experiment.subjVariables['locationMapping'] == 'V':
            setAndPresentStimulus(self.experiment.win, [
                                  self.pictureMatrix[curTrial['stim']][0], prompt, yes, no])
        else:
            setAndPresentStimulus(self.experiment.win, [
                                  self.pictureMatrix[curTrial['stim']][0], labelLeft, labelRight])

        if self.experiment.inputDevice == 'keyboard':
            (resp, rt) = getKeyboardResponse(
                self.experiment.validResponses.keys())
        elif self.experiment.inputDevice == 'gamepad':
            (resp, rt) = getGamepadResponse(
                self.experiment.stick, self.experiment.validResponses.keys())
        resp = self.experiment.validResponses[resp]

        if curTrial['trialType'] == "transfer":
            isRight = '*'
        else:
            isRight = int(resp == curTrial['correctResp'])
            if isRight:
                playAndWait(self.soundMatrix['bleep'])
            else:
                playAndWait(self.soundMatrix['buzz'])
        core.wait(self.experiment.postResponseDelay)
        self.experiment.win.flip()

        if self.experiment.subjVariables['categoryStructure'] == "5-4":
            strategy1 = int(sideToLabelMap[resp]
                            == curTrial['correctCategoryD1']),
            strategy2 = int(sideToLabelMap[resp]
                            == curTrial['correctCategoryD2']),
            strategy3 = int(sideToLabelMap[resp]
                            == curTrial['correctCategorySim']),
            strategy4 = '*'
        else:
            strategy1 = int(sideToLabelMap[resp]
                            == curTrial['correctCategoryCC']),
            strategy2 = int(sideToLabelMap[resp]
                            == curTrial['correctCategoryR1']),
            strategy3 = int(sideToLabelMap[resp]
                            == curTrial['correctCategoryR2']),
            strategy4 = int(sideToLabelMap[resp]
                            == curTrial['correctCategoryKP']),

        fieldVars = []
        for curField in self.fieldNames:
            fieldVars.append(curTrial[curField])
        curLine = createResp(self.experiment.optionList, self.experiment.subjVariables, fieldVars,
                             a_whichPart=whichPart,
                             b_trialIndex=trialIndex,
                             d_responseSide=resp,
                             e_responseLabel=sideToLabelMap[resp],
                             f_s1=strategy1,
                             g_s2=strategy2,
                             h_s3=strategy3,
                             i_s4=strategy4,
                             k_isRight=isRight,
                             l_rt=rt * 1000)
        writeToFile(self.experiment.outputFile, curLine)

    def cycleThroughExperimentTrials(self, whichPart):
        self.prevTestType = 'none'

        if whichPart == "practice":
            numTrials = self.experiment.numPracticeTrials
            numBlocks = 1
            trialIndices = random.sample(
                range(1, 30), self.experiment.numPracticeTrials)
            for curPracticeTrialIndex in trialIndices:
                curTrial = self.trialListMatrix.getFutureTrial(
                    curPracticeTrialIndex)
                self.presentExperimentTrial(0, whichPart, curTrial)
        elif whichPart == "real":
            curTrialIndex = 0
            prevBlock = 'none'
            for curTrial in self.trialListMatrix:
                    # take break every X trials (for blocks that have lots of trials; otherwise can set it to break every X blocks)
                if curTrialIndex > 0 and curTrialIndex % self.experiment.takeBreakEveryXTrials == 0:
                    showText(self.experiment.win, self.experiment.takeBreak, color=(
                        0, 0, 0), inputDevice=self.experiment.inputDevice)  # take a break

                """This is what's shown on every trial"""
                self.presentExperimentTrial(curTrialIndex, whichPart, curTrial)

                curTrialIndex += 1


currentExp = Exp()
currentPresentation = ExpPresentation(currentExp)
currentPresentation.initializeExperiment()
showText(currentExp.win, currentExp.instructions,
         color=(-1, -1, -1), inputDevice=currentExp.inputDevice)
showText(currentExp.win, currentExp.practiceTrials,
         color=(-1, -1, -1), inputDevice=currentExp.inputDevice)
currentPresentation.cycleThroughExperimentTrials("practice")
showText(currentExp.win, currentExp.realTrials, color=(
    0, 0, 0), inputDevice=currentExp.inputDevice)
currentPresentation.cycleThroughExperimentTrials("real")
showText(currentExp.win, currentExp.finalText, color=(0, 0, 0),
         inputDevice=currentExp.inputDevice)  # thank the subject
web.open(currentExp.surveyURL)
