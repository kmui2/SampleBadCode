import random

def circularList(lst,seed):
	if not isinstance(lst,list):
		lst = range(lst)
	i = 0
	random.seed(seed)
	while True:
		yield lst[i]
		if (i+1) % len(lst) ==0:
			random.shuffle(lst)
		i = (i + 1)%len(lst)
		
stimuli = {\
'rockets  1  1  1  1' : ['t',111],
'rockets  1  1  1  2' : ['o',111],
'rockets  1  1  2  1' : ['o',111],
'rockets  1  1  2  2' : ['o',222],
'rockets  1  2  1  1' : ['o',111],
'rockets  1  2  1  2' : ['o',111],
'rockets  1  2  2  1' : ['t',121],
'rockets  1  2  2  2' : ['t',122],
'rockets  2  1  1  1' : ['o',111],
'rockets  2  1  1  2' : ['o',222],
'rockets  2  1  2  1' : ['t',222],
'rockets  2  1  2  2' : ['t',222],
'rockets  2  2  1  1' : ['t',211],
'rockets  2  2  1  2' : ['t',212],
'rockets  2  2  2  1' : ['o',222],
'rockets  2  2  2  2' : ['o',222]}

stimuliOriginal = [stims for stims in stimuli.items() if stims[1][0]=='o']
stimuliTransfer = [stims for stims in stimuli.items() if stims[1][0]=='t']
correctCategorys = [[stims, str(stims[1][1])[0]] for stims in stimuli.items() if stims[1][0]=='o']

locations = ['left','right']
mapping = {'G1':{'1':'gek', '2':'talp'}, 'G2':{'1':'talp', '2':'gek'}, 'A1':{'1':'Type A', '2':'Type B'}, 'A2':{'1':'Type B', '2':'Type A'}}
promptList = ['gek','talp']

separator = ","

def generateTrialsVerification(subjCode,seed,mappingType,labelOrder):
	try:
		trialListFile=open(subjCode+'_trialList.csv','w') #open trial list file for writing
	except IOError:
		print "Couldn't open trial list file for writing for some reason. Weird."
		return False
	promptListCircularList = circularList(promptList,seed+1)
	totalBlocks = 35
	generalizationBlocks = [4, 17, 34]
	trials=[[]*totalBlocks]
	random.seed(int(seed))
	header = separator.join(('part','block','trialType','stim','labelPrompt','correctLabel','correctResp','correctCategoryD1','correctCategoryD2','correctCategorySim'))
	curTrial=1
	for curBlock in range(totalBlocks):
		trials.append([])
		if curBlock in generalizationBlocks:
			#generalization trial
			stimList = stimuliTransfer
			trialType="transfer"
		else:
			stimList = stimuliOriginal
			trialType="original"
		random.shuffle(stimList)
		for curStim in stimList:
		
			curPrompt = promptListCircularList.next()
			curFileName = curStim[0]
			if trialType=='original':
				correctCategory = mapping[mappingType][str(curStim[1][1])[0]]
			else:
				correctCategory ='*'
			correctCategoryD1 = mapping[mappingType][str(curStim[1][1])[0]]
			correctCategoryD2 = mapping[mappingType][str(curStim[1][1])[1]]
			correctCategorySim = mapping[mappingType][str(curStim[1][1])[2]]
			if correctCategory == curPrompt:
				correctResponse = 'Yes'
			elif correctCategory!='*' and (correctCategory != curPrompt):
				correctResponse = 'No'
			else:
				correctResponse = '*'
			curTrial+=1
			trials[curBlock].append(','.join(('train',str(curBlock+1),trialType,curStim[0], curPrompt,correctCategory,correctResponse,\
			correctCategoryD1,correctCategoryD2,correctCategorySim)))
				
	trialListFile.write(header+'\n')
	for curBlock in range(totalBlocks): #shuffle within each block, but not between blocks
		random.seed(int(seed)+(curBlock+1))
		random.shuffle(trials[curBlock])
		for curTrial in trials[curBlock]:
			trialListFile.write(curTrial+'\n')
	return True

				

	
if __name__ == "__main__":
	#for testing; executed when you run generateTrials.py from the terminal.
	trialList = generateTrials('test',10,'G2','V')
