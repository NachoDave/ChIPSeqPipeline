#!/usr/bin/env python
''' Import libraries ======================================================= '''
import subprocess
import os
import sys
import json
import datetime

''' Import user defined functions (mostly to run docker containers) ======== '''

import chipSeqRunContainersAligners as algn
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

#print('Files in ' + dataDir +  'are: ', os.listdir(dataDir))
allExpDr = [drNm for drNm in os.listdir(dataDir) if os.path.isdir(os.path.join(dataDir, drNm))]
allExpDr.sort()
for dx in allExpDr:
    print(dx)


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
#print('Experimental directory:', expDir)
inputParFn = expDir + '/inputParameters.txt' # input parameter path

datDir = expDir + 'data/'

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

if 'ExperimentName' in inPars:
    dirSuffix = '_' + inPars['ExperimentName'][0]
else:
    dirSuffix = ''

resDir = expDir + 'results' + dirSuffix + '/'
repDir = expDir + 'reports' + dirSuffix + '/'
logDir = expDir + 'logs' + dirSuffix + '/'# logs directory
tarDir = expDir +'data' + '/'# this should be updated after each step is run to point to the directory containing latest Files



''' Check for directories and create if needed '''

try:
    os.path.exists(datDir) # check the results directory is there
except:
    print('Could not find the data directory. Please create a directory called data \
    in your experiment directory and put your data files in it. Exiting')
    sys.exit()

try:
    # Create target Directory
    os.mkdir(resDir)
    print("Directory " , resDir ,  " Created ")
except:
    print("Directory " , expDir + 'results' ,  " already exists")

try:
    # Create target reports Directory
    os.mkdir(repDir)
    print("Directory " , repDir ,  " Created ")
except:
    print("Directory reports" , expDir + 'reports' ,  " already exists")

try:
    # Create target logs Directory
    os.mkdir(logDir)
    print("Directory " , logDir ,  " Created ")
except:
    print("Directory logs" , expDir + 'logs' ,  " already exists")

logFile = open(logDir + 'ChIPAnalysis' + dirSuffix +  dt + '.log', 'w+') # open log file for writing

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
    try: # Check aligner is specified
        inPars['Aligner']
        print('Aligner: ' + inPars['Aligner'][0])
    except:
        print('Align requested, but no aligner specified')
        sys.exit()

    try: # check genome directory is specified
        inPars['genomeDir']
        print('Setting genome directory to ' + inPars['genomeDir'][0])
        genomeDir = inPars['genomeDir'][0]
    except:
        print('align specified in analysis steps, but no genome directory specified')

    try: # check genome is specified
        inPars['genome']
        print('Setting genome directory to ' + inPars['genome'][0])
        genome = inPars['genome'][0]
    except:
        print('align specified in analysis steps, but no genome specified')
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

# Check for ControlFileNames2 in pairended
if 'Y' in inPars['PE'] and 'ctrlFileNames' in inPars:
    try:
        inPars['ctrlFileNames2']
        print('Found ctrlFileNames2 for pair ended reads')

        try:
            assert(len(inPars['ctrlFileNames']) == len(inPars['ctrlFileNames2']))
            print('Length of ctrl files equal to length of pairs')
        except:
            print('Length of ctrl files not equal to length of pairs')
            sys.exit()
    except:
        print('Could not find ctrlFileNames2 for pair ended reads')
        sys.exit()

# Check if removeblacklist in analysis AnalysisSteps
if 'removeblacklist' in steps:
    try:
        blkLstDir = inPars['blackListDir'][0]
        print('Blacklist directory is ' + blkLstDir)
        blkLst = inPars['blackList'][0]
        print('Blacklist is ' + blkLst)
    except:
        print('removeblacklist specified in analysis steps, but no blacklist or blacklist directory specified, exiting')
        sys.exit()



''' Initialize current directory and current files ------------------------- '''
if 'TargetDir' in inPars: # user can define a different directory to start from rather than the defaul data. Useful if starting from a different point
    curDr = inPars['TargetDir'][0]
else:
    curDr = datDir # pointer to the current directory (initially */data) (not really a pointer!)
curTarFN = tarFN
if 'TargetFileNames2' in inPars:
    curTarFN2 = tarFN2
else:
    curTarFN2 = []

if 'ctrlFileNames' in inPars:
    curCtrlFN = inPars['ctrlFileNames']
else:
    curCtrlFN = []

if 'ctrlFileNames2' in inPars:
    curCtrlFN2 = inPars['ctrlFileNames2']
else:
    curCtrlFN2 = []



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
        phredthres = phredCO, phredN = phredN, PE = 'N')

        trm.runSE()


    elif 'Y' in inPars['PE']:
        oTarFN = [w.replace('.fastq', '_trim.fastq') for w in curTarFN] # output target file names
        oCtrlFN = [w.replace('.fastq', '_trim.fastq') for w in curCtrlFN] # output control file names
        oTarFN2 = [w.replace('.fastq', '_trim.fastq') for w in curTarFN2] # output target file names
        oCtrlFN2 = [w.replace('.fastq', '_trim.fastq') for w in curCtrlFN2] # output control file names

        print('\n' , curTarFN , oTarFN , curCtrlFN , oCtrlFN)

        trm = qc.runTrimR(curDr, curTarFN + curCtrlFN, curTarFN2 + curCtrlFN2, outDr = resDir + '/trimmedReads/',
        outFN = oTarFN + oCtrlFN, logDr = logDir, reportDr = repDir, nBsN = rmN,
        phredthres = phredCO, phredN = phredN, PE = 'Y')

        trm.runPE()

        curTarFN2 = oTarFN2
        curCtrlFN2 = oCtrlFN2

    # Update current directory and files
    curDr = resDir + '/trimmedReads/'
    curTarFN = oTarFN
    curCtrlFN = oCtrlFN

''' Step 2 Fastqc report =================================================== '''

if 'preqc' in steps:
    e = qc.runFastQC(curDr, curTarFN + curCtrlFN + curTarFN2 + curCtrlFN2, logDr = logDir, repDr = repDir)
    e.run()

''' Step 3 Alignment ======================================================== '''

if 'align' in steps:
    # Create results directory for alignments
    try:
        os.mkdir(resDir + '/alignments/')
        print("Directory " , resDir + '/alignments/' ,  " Created ")
    except:
        print("Directory " , resDir + '/alignments/' ,  " already exists")

    alignDir = resDir + '/alignments/'
    # Use Bowtie2 aligner
    if 'bowtie2' in inPars['Aligner']:
        print('Aligning using Bowtie2!')

        # Check for bowtie2Args
        if 'bowtie2Args' in inPars:
            bwt2Args = inPars['bowtie2Args']
        else:
            bwt2Args = []

        if 'N' in inPars['PE']: # run non pair ended version
        #print(curDr, curTarFN, curCtrlFN)
        # Make output file names
            oTarFN = [w.replace('.fastq', '_bowtie2UP.sam').replace('.gz', '') for w in curTarFN]
            oCtrlFN = [w.replace('.fastq', '_bowtie2UP.sam').replace('.gz', '') for w in curCtrlFN]


            bwt2Algn = algn.runBowtie2Unpaired(inDr = curDr, targetFN = curTarFN, ctrlFN = curCtrlFN, outDr = alignDir,
            logDr = logDir, targetFNOut = oTarFN, ctrlFNOut = oCtrlFN, genomePth = genomeDir, genome = genome,
            args = bwt2Args) # create object to run bowtie2 container

            bwt2Algn.run() # run containers

            # Update current directories and target FilesblkLst
            curDr = alignDir
            curTarFN = oTarFN
            curCtrlFN = oCtrlFN

        elif 'Y' in inPars['PE']: # run pair ended version

            oTarFN = [w.replace('.fastq', '_bowtie2UP.sam').replace('.gz', '') for w in curTarFN]
            oCtrlFN = [w.replace('.fastq', '_bowtie2UP.sam').replace('.gz', '') for w in curCtrlFN]


            bwt2Algn = algn.runBowtie2Paired(inDr = curDr, targetFN1 = curTarFN, targetFN2 = curTarFN2, ctrlFN1 = curCtrlFN,
            ctrlFN2 = curCtrlFN2, outDr = alignDir, logDr = logDir, targetFNOut = oTarFN, ctrlFNOut = oCtrlFN, genomePth = genomeDir, genome = genome,
            args = bwt2Args) # create object to run bowtie2 container

            bwt2Algn.run() # run containers

            # Update current directories and target FilesblkLst
            curDr = alignDir
            curTarFN = oTarFN
            curCtrlFN = oCtrlFN

        else:
            print("Don't know whether to run bowtie2 single or pair ended. Exiting")
            sys.exit()

    elif 'bwa' in inPars['Aligner']:
        print("You haven't written a bwa docker class yet!")
        sys.exit()

    else:
        print("Aligner " + inPars['Aligner'][0] + " not recognised, exiting")
        sys.exit()

''' Step 4 Conversion to BAM ====================================== '''
''' Step 4b sam 2 bam conversion ========================================= '''
if 'sam2bam' in steps:
    print('Converting sam files to bam files, sorting and indexing')
    #
    bamSrtIdx = samt.runSamtools(inDr = curDr, targetFN = curTarFN, ctrlFN = curCtrlFN, logDr = logDir) # note for pair ended change targetFN = curTarFN + curTarFN2
    bamSrtIdx.sam2Bam() # convert sam to bam file
    curTarFN = [w.replace('.sam', '.bam') for w in curTarFN]
    curCtrlFN = [w.replace('.sam', '.bam') for w in curCtrlFN]

''' Step 4b Sort bam files ========================================= '''
if 'sortBam' in steps:
    bamSrtIdx = samt.runSamtools(inDr = curDr, targetFN = curTarFN, ctrlFN = curCtrlFN, logDr = logDir)
    bamSrtIdx.sortBam() # sort bam file


    curTarFN = [w.replace('.bam', '.sorted.bam') for w in curTarFN]
    curCtrlFN = [w.replace('.bam', '.sorted.bam') for w in curCtrlFN]

    ''' Step 4c Remove DAC blacklisted regions from sorted bam files ======= '''
if 'removeblacklist' in steps: # Remove blacklisted regions

    rmBl = qc.runBedToolsRmBL(inDr = curDr, targetFN = curTarFN + curCtrlFN, blkLstPth = blkLstDir, blkLstFN = blkLst,
        logDr = logDir) # make object to run the blacklist container
    rmBl.run()
        # Update filenames
    if 'sortBam' in steps:
        curTarFN = [w.replace('.sorted.bam', 'BlkLstRm.sorted.bam') for w in curTarFN]
        curCtrlFN = [w.replace('.sorted.bam', 'BlkLstRm.sorted.bam') for w in curCtrlFN]
    else:
        curTarFN = [w.replace('.bam', 'BlkLstRm.bam') for w in curTarFN]
        curCtrlFN = [w.replace('.bam', 'BlkLstRm.bam') for w in curCtrlFN]

''' Step 4d Index bam files ========================================= '''
if 'indexBam' in steps:
    bamSrtIdx = samt.runSamtools(inDr = curDr, targetFN = curTarFN, ctrlFN = curCtrlFN, logDr = logDir) # note for pair ended change targetFN = curTarFN + curTarFN2
    bamSrtIdx.indexBam()


    #curTarFN = []
    #curCtrlFN = oCtrlFN

''' Step 5 Post alignment QC =============================================== '''
if 'postqc' in steps:
    j = qc.runPhantomPeak(inDr = curDr, targetFN = curTarFN + curCtrlFN, reportDr = repDir, logDr = logDir)
    j.run()

''' Step 6 Peak calling ==================================================== '''
if 'peakcall' in steps:
    try:
        os.mkdir(resDir + '/peakCalls/')
        print("Directory " , resDir + '/peakCalls/' ,  " Created ")
    except:
        print("Directory " , resDir + '/peakCalls/' ,  " already exists")

    peakDir = resDir + '/peakCalls/'

    ''' Run MACS peakcaller ================================================ '''
    if "MACS" in inPars['PeakCaller']:

        if "macsArgs" in inPars:
            macsArgs = inPars["macsArgs"]
        else:
            macsArgs = []

        macsPkCl = pc.runMACS(inDr = curDr, targetFN = curTarFN, args = macsArgs,
        logDr = logDir, outDr = peakDir, ctrlFN = curCtrlFN)
        macsPkCl.run()

        curDr = peakDir
        curTarFN = [w.replace('.sorted.bam', '_MACS_peaks.xls') for w in curTarFN]

    ''' RUn MACS2 PeakCaller ============================================== '''
    if "MACS2" in inPars['PeakCaller']:
        if "macs2Args" in inPars:
            macs2Args = inPars["macs2Args"]
        else:
            macs2Args = []

        macs2PkCl = pc.runMACS2(inDr = curDr, targetFN = curTarFN, args = macs2Args,
        logDr = logDir, outDr = peakDir, ctrlFN = curCtrlFN)
        macs2PkCl.run()

        curDr = peakDir
        curTarFN = [w.replace('.sorted.bam', '_MACS2_peaks.xls') for w in curTarFN]
        #print(curTarFN)
''' Step 7 Gene list ======================================================= '''

if 'genelist' in steps:
    try:
        os.mkdir(resDir + '/genes/')
        print("Directory " , resDir + '/genes/' ,  " Created ")
    except:
        print("Directory " , resDir + '/genes/' ,  " already exists")

    # Need to check for distance, pvalue and fdr
    if "geneFindDist" in inPars:
        DIST = inPars["geneFindDist"][0]
    else:
        DIST = None

    if "geneFindPValue" in inPars:
        PVALUE = inPars["geneFindPValue"][0]
    else:
        PVALUE = None

    if "geneFindFDR" in inPars:
        FDR = inPars["geneFindFDR"][0]
    else:
        FDR = None

    geneDir = resDir + '/genes/'
    gnFnd = gf.runGeneFinderR(inDr = curDr, targetFN = curTarFN, geneLstNm = inPars["geneList"][0],
    FDR = FDR, pval = PVALUE, dist = DIST, outDr = geneDir, logDr = logDir)
    gnFnd.run()


logFile.close()
