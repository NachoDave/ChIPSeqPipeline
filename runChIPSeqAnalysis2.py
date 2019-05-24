#!/usr/bin/env python
''' Import libraries ======================================================= '''
import subprocess
import os
import sys
import json
import datetime

''' Import user defined functions (mostly to run docker containers) ======== '''

import chipSeqRunContainersAligners as cont
import chipSeqRunContainersSAMtools as samt
import chipSeqRunContainersQC as qc
import chipSeqRunContainersPeakCalls as pc
import chipSeqRunGeneFinder as gf

''' System constants (these should be changed when moving the pipeline to another
 computer) =================================================================='''

dataDir = '/data/ChIPSeqAnalysis/Experiments/' # path to data
RScriptDir = '/data/ChIPSeqAnalysis/RScripts/' # path to R scripts
genomeDir = '/data/genomes/'
''' Date =================================================================== '''
dt = str(datetime.datetime.now())
dt = dt[0:10]
dt = dt.replace('-', '')

''' Select experiment directory and create dir structure =================== '''

go = 1
cnt = 0

print('Files in ' + dataDir +  'are: ', os.listdir(dataDir))

while go:
    expNm = raw_input('What is the name of your experiment directory? ')
    expDir = dataDir + expNm +'/'
    print(expDir)
    if os.path.exists(expDir):
        go = 0
    else:
        cnt += 1
        print('Could not find the directory, please reenter details')
    if cnt > 4:
        print('Five attempts to find the directory, aborting run')
        sys.exit()
expDataDir = expDir + 'data/'
print('Experimental directory:', expDir)
inputParFn = expDir + '/inputParameters.txt' # input parameter path

datDir = expDir + 'data'

try:
    os.path.exists(datDir) # check the results directory is there
except:
    print('Could not find the data directory. Please create a directory called data \
    in your experiment directory and put your data files in it. Exiting')

inputParFn = expDir + 'inputParameters.txt' # input parameter path
print('Looking for ' + inputParFn +  '\n')
datDir = expDir + 'data'

try:
    os.path.exists(datDir) # check the results directory is there
except:
    print('Could not find the data directory. Please create a directory called data \
    in your experiment directory and put your data files in it. Exiting')

try:
    # Create target Directory
    os.mkdir(expDir + 'results')
    print("Directory " , expDir + 'results' ,  " Created ")
except:
    print("Directory " , expDir + 'results' ,  " already exists")

try:
    # Create target reports Directory
    os.mkdir(expDir + 'reports')
    print("Directory " , expDir + 'reports' ,  " Created ")
except:
    print("Directory reports" , expDir + 'reports' ,  " already exists")

try:
    # Create target logs Directory
    os.mkdir(expDir + 'logs')
    print("Directory " , expDir + 'logs' ,  " Created ")
except:
    print("Directory logs" , expDir + 'logs' ,  " already exists")


resDir = expDir + 'results'
repDir = expDir + 'reports'
logDir = expDir + 'logs' # logs directory
tarDir = expDir +'data' # this should be updated after each step is run to point to the directory containing latest Files

''' Read inputParameters.txt file ========================================== '''
# load input parameters
try:
    with open(inputParFn) as json_file:
        inPars = json.load(json_file)
        print('Opened inputParameters json, THANKS!')
except IOError as ex:
    print("I couldn't even find the inputParameters text file, not a good start! \n ")
    print(ex)
    sys.exit()
except Exception as ex:
    print("Something wrong with the inputParameters.txt file formatting. (See below).")
    print(ex)
    sys.exit()


''' Check essential parameters are present '''
# targetFileNames
try:
    inPars['TargetFileNames']
    print('Found targetFileNames')
except:
    print('Could not find the TargetFileNames in inputParameters')
    sys.exit()

tarFN = inPars['TargetFileNames']
#print(tarFN)

#AnalysisSteps
try:
    inPars['AnalysisSteps']
    print('Found AnalysisSteps field ')
    steps = inPars['AnalysisSteps']
except:
    print('Could not find AnalysisSteps field in inputParameters')
    sys.exit()

''' Check if dependent parameters are present (i.e. aligner if align option) '''
# Check that an aligner is specified if alignment step specified
if 'align' in steps:
    try:
        inPars['Aligner']
        print('Aligner: ' + inPars['Aligner'][0])
    except:
        print('Align requested, but no aligner specified')
        sys.exit()

# Check for TargetFileNames2 in pairended
if 'Y' in inPars['PE']:
    try:
        inPars['TargetFileNames2']
        print('Found TargetFileNames2 for pair ended reads')

        try:
            assert(len(tarFN) == len(inPars['TargetFileNames2']))
            print('Length of target files equal to length of pairs')
            tarFN2 = inPars['TargetFileNames2']
        except:
            print('Length of target files not equal to length of pairs')
            sys.exit()
    except:
        print('Could not find TargetFileNames2 for pair ended reads')
        sys.exit()


''' Initialize current directory and current files ------------------------- '''
curDr = datDir # pointer to the current directory (initially */data) (not really a pointer!)
curTarFN = tarFN
if 'TargetFileNames2' in inPars:
    curTarFN2 = tarFN2

if 'ctrlFileNames' in inPars:
    curCtrlFN = inPars['ctrlFileNames']
else:
    curCtrlFN = []



''' Step 1 Filter low quality reads ======================================== '''


# Need to write a code for trim pair ended reads
if 'trim' in steps:

    # Make trimmed reads Directory
    try:
        os.mkdir(resDir + '/trimmedReads')
    except:
        pass

    # Check for user defined trim values
    if "phredCutoff" in inPars:
        phredCO = int(inPars["phredCutoff"][0])
    else:
        phredCO = 30

    if "phredCutoffExceptions" in inPars:
        phredN = int(inPars["phredCutoffExceptions"][0])
    else:
        phredN = 5

    if "removeNs" in inPars:
        rmN = int(inPars["removeNs"][0])
    else:
        rnM = 1

    "Pair ended or not? -------------------------------------------------------"
    if 'N' in inPars['PE']:

        oTarFN = [w.replace('.fastq', '_trim.fastq') for w in curTarFN] # output target file names
        oCtrlFN = [w.replace('.fastq', '_trim.fastq') for w in curCtrlFN] # output control file names

        print('\n' , curTarFN , oTarFN , curCtrlFN , oCtrlFN)

        trm = qc.runTrimR(curDr, curTarFN + curCtrlFN, outDr = resDir + '/trimmedReads/',
        outFN = oTarFN + oCtrlFN, logDr = logDir, reportDr = repDir, nBsN = rmN,
        phredthres = phredCO, phredN = phredN)

        trm.run()


    elif 'Y' in inPars['PE']:
        print('Please write pair ended trim files')
        sys.exit()

    # Update current directory and files
    curDr = resDir + '/trimmedReads/'
    curTarFN = oTarFN
    curCtrlFN = oCtrlFN

''' Step 2 Fastqc report =================================================== '''

if 'preqc' in steps:
    e = qc.runFastQC(curDr, curTarFN + curCtrlFN, logDr = logDir)
    e.run()


''' Step 3 Alignment ======================================================== '''

''' Step 4 Remove Blacklisted regions ====================================== '''

''' Step 5 Post alignment QC =============================================== '''

''' Step 6 Conversion to BAM =============================================== '''

''' Step 7 Peak calling ==================================================== '''

''' Step 8 Gene list ======================================================= '''
