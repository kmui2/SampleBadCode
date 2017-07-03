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

stimuliCC = {\
'rockets  1  1  1  1' : ['o',1111],
'rockets  1  1  1  2' : ['t',2112],
'rockets  1  1  2  1' : ['t',2111],
'rockets  1  1  2  2' : ['o',1111],
'rockets  1  2  1  1' : ['t',1121],
'rockets  1  2  1  2' : ['o',2222],
'rockets  1  2  2  1' : ['t',2121],
'rockets  1  2  2  2' : ['o',1111],
'rockets  2  1  1  1' : ['o',1111],
'rockets  2  1  1  2' : ['t',2212],
'rockets  2  1  2  1' : ['o',2222],
'rockets  2  1  2  2' : ['t',1212],
'rockets  2  2  1  1' : ['t',1221],
'rockets  2  2  1  2' : ['o',2222],
'rockets  2  2  2  1' : ['o',2222],
'rockets  2  2  2  2' : ['t',1222]}



locations = ['left','right']
mapping = {'G1':{'1':'gek', '2':'talp'}, 'G2':{'1':'talp', '2':'gek'}, 'A1':{'1':'Type A', '2':'Type B'}, 'A2':{'1':'Type B', '2':'Type A'}}
labelOrderMapping = {'GL':['gek', 'talp'], 'GR':['talp','gek'],'AL':['Type A', 'Type B'],'AR':['Type B', 'Type A']}

separator = ","

def generateTrials(subjCode,seed,mappingType,labelOrder,categoryStructure):
	if categoryStructure=='5-4':
		stimuliOriginal = [stims for stims in stimuli.items() if stims[1][0]=='o']
		stimuliTransfer = [stims for stims in stimuli.items() if stims[1][0]=='t']
		correctCategorys = [[stims, str(stims[1][1])[0]] for stims in stimuli.items() if stims[1][0]=='o']
	else:
		stimuliOriginal = [stims for stims in stimuliCC.items() if stims[1][0]=='o']
		stimuliTransfer = [stims for stims in stimuliCC.items() if stims[1][0]=='t']
		correctCategorys = [[stims, str(stims[1][1])[0]] for stims in stimuliCC.items() if stims[1][0]=='o']
	try:
		trialListFile=open(subjCode+'_trialList.csv','w') #open trial list file for writing
	except IOError:
		print "Couldn't open trial list file for writing for some reason. Weird."
		return False
	if labelOrder == 'R':
		labelOrderMappingCircularList = circularList(labelOrderMapping.keys(),seed+1)
	else:
		curLabelOrder = labelOrder
	totalBlocks = 35
	generalizationBlocks = [4, 17, 34]
	trials=[[]*totalBlocks]
	random.seed(int(seed))
	if categoryStructure=="5-4":
		header = separator.join(('part','block','trialType','stim','labelLeft','labelRight','correctLabel','correctResp','correctCategoryD1','correctCategoryD2','correctCategorySim'))
	else:
		header = separator.join(('part','block','trialType','stim','labelLeft','labelRight','correctLabel','correctResp','correctCategoryCC','correctCategoryR1','correctCategoryR2','correctCategoryKP'))
	
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
		
			if labelOrder == 'R':
				curLabelOrder = labelOrderMappingCircularList.next()

			curFileName = curStim[0]
			if trialType=='original':
				correctCategory = mapping[mappingType][str(curStim[1][1])[0]]
			else:
				correctCategory ='*'

			if correctCategory == labelOrderMapping[curLabelOrder][0]:
				correctResponse = 'left'
			elif correctCategory == labelOrderMapping[curLabelOrder][1]:
				correctResponse = 'right'
			else:
				correctResponse = '*'
			curTrial+=1
			if categoryStructure=="5-4":
				correctCategoryD1 = mapping[mappingType][str(curStim[1][1])[0]]
				correctCategoryD2 = mapping[mappingType][str(curStim[1][1])[1]]
				correctCategorySim = mapping[mappingType][str(curStim[1][1])[2]]
				trials[curBlock].append(','.join(('train',str(curBlock+1),trialType,curStim[0], labelOrderMapping[curLabelOrder][0],labelOrderMapping[curLabelOrder][1],correctCategory,correctResponse,\
				correctCategoryD1,correctCategoryD2,correctCategorySim)))
			else: #cc category structure
				correctCategoryCC = mapping[mappingType][str(curStim[1][1])[0]]
				correctCategoryR1 = mapping[mappingType][str(curStim[1][1])[1]]
				correctCategoryR2 = mapping[mappingType][str(curStim[1][1])[2]]
				correctCategoryKP = mapping[mappingType][str(curStim[1][1])[3]]
				trials[curBlock].append(','.join(('train',str(curBlock+1),trialType,curStim[0], labelOrderMapping[curLabelOrder][0],labelOrderMapping[curLabelOrder][1],correctCategory,correctResponse,\
				correctCategoryCC, correctCategoryR1,correctCategoryR2,correctCategoryKP)))

				
	trialListFile.write(header+'\n')
	for curBlock in range(totalBlocks): #shuffle within each block, but not between blocks
		random.seed(int(seed)+(curBlock+1))
		random.shuffle(trials[curBlock])
		for curTrial in trials[curBlock]:
			trialListFile.write(curTrial+'\n')
	return True

				

	
if __name__ == "__main__":
	#for testing; executed when you run generateTrials.py from the terminal.
	trialList = generateTrials('test',10,'G1','GL','CC')
