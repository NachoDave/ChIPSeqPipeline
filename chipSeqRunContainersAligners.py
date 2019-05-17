''' Contains classes to run ChIP seq analysis pipeline '''
import subprocess
import os
import sys
import json
import datetime

''' Class to run docker container for unpaired bowtie2 ======================'''
class runBowtie2Unpaired:
    ''' Variables:
    inDr - directory where fastq/fastq.gz files are stored
    targetFn - list of target FileNames
    genomePath - path to genomes
    args - additonal user defined bowtie2 arguments
    logDr - directory to write log Files
    ctrlFn - list of control Filenames
    targetFnOut - directory to write output Files
    ctrlFnOut - list of output control file FileNames
    '''

    '''Methods =============================================================='''
    ''' Constructor ---------------------------------------------------------'''
    def __init__(self, inDr, targetFN, genomePth, genome, args = [], logDr = None, outDr =  None, ctrlFN = [],  targetFNOut = None, ctrlFNOut = None):
        self.inDr = inDr
        self.targetFN = targetFN
        self.genomePth = genomePth
        self.args = args
        self.ctrlFN = ctrlFN
        self.genome = genome

        if outDr is None:
            outDr = inDr # if no output directory provided, use input directory
        if targetFNOut is None:
            targetFNOut = [w.replace('.fastq', '_bowtie2UP.sam').replace('.gz', '') for w in targetFN]
        if ctrlFNOut is None:
            if ctrlFN:
                ctrlFNOut = [w.replace('.fastq', '_bowtie2UP.sam').replace('.gz', '') for w in ctrlFN]
            else:
                ctrlFNOut = []
        if logDr is None:
            logDr = outDr

        self.outDr = outDr
        self.targetFNOut = targetFNOut
        self.ctrlFNOut = ctrlFNOut
        self.logDr = logDr

        dt = str(datetime.datetime.now())
        dt = dt[0:10]
        dt = dt.replace('-', '')
        self.dt = dt
        ''' try/catch to check all inputs ok --------------------------------'''

    ''' main function to run container --------------------------------------'''

    def run(self):
        print(self.targetFN + self.ctrlFN)
        print(self.targetFNOut + self.ctrlFNOut)
        print('\n')

        with open(self.logDr + '/' + 'AlignBowtie2Unpaired' + self.dt + '.err', 'w+') as lgf:

            lgf.write('Align stderr ' + str(datetime.datetime.now()) + '\n') # open log file for writing
            for fqFN, fqFNOut in zip(self.targetFN + self.ctrlFN, self.targetFNOut + self.ctrlFNOut): # loop trhough files

                inPth = self.inDr + '/' + fqFN
                outPth = self.outDr + '/' + fqFNOut
                print('\n')
                print('Locating file:', inPth, '\n')
                print('Output path', outPth, '\n')
                print('\n')

                if os.path.exists(inPth):
                    print(inPth, 'exists, attempting alignment')

                    ''' Input to bowtie2 -----------------------------------'''
                    bwt2ParLst = ['docker', 'run','--rm','-v', self.genomePth + ':/data/genomes/',
                            '-v', self.inDr + ':/data/inputFiles',
                            '-v', self.outDr + ':/data/outputFiles',
                            'biocontainers/bowtie2:v2.2.9_cv2',
                            'bowtie2', '-q',
                            '-x', self.genomePth + self.genome,
                            '-U', '/data/inputFiles/' + fqFN,
                            '-S', '/data/outputFiles/' + fqFNOut
                    ]

                    if self.args: # if there are command line args add these in
                        bwt2ParLst[len(bwt2ParLst):len(bwt2ParLst) + len(self.args)] = self.args
                        #print(bwt2ParLst)
                    p = subprocess.Popen(bwt2ParLst,
                    shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE) # run process

                    output, err = p.communicate()
                    print('out:' + output)
                    print('err:' + err)

                    lgf.write('\nFile to align: ' +   inPth + '\nGenome:'
                    + self.genomePth + self.genome + '\nOutput File:' + outPth + '\n'
                    + 'Docker/Bowtie2 arguments: ' + ','.join(bwt2ParLst))
                    if self.args:
                        lgf.write('Cmd line Args: ' + ','.join(self.args) + '\n\n')
                    else:
                        lgf.write('No additional command line args\n\n')
                    lgf.write(err)

                else:
                    print('Could not find file', inPth, 'skipping alignment')

        lgf.close()

"""=========================================================================="""
''' Class to run docker container for Paired bowtie2 ========================'''
class runBowtie2Paired:
    ''' Variables:
    inDr - directory where fastq/fastq.gz files are stored
    targetFn - list of target FileNames
    genomePath - path to genomes
    args - additonal user defined bowtie2 arguments
    logDr - directory to write log Files
    ctrlFn - list of control Filenames
    targetFnOut - directory to write output Files
    ctrlFnOut - list of output control file FileNames
    '''

    '''Methods =============================================================='''
    ''' Constructor ---------------------------------------------------------'''
    def __init__(self, inDr, targetFN1, targetFN2, genomePth, genome, args = [], logDr = None, outDr =  None, ctrlFN1 = [], ctrlFN2 = [],  targetFNOut = None, ctrlFNOut = None):
        self.inDr = inDr
        self.targetFN1 = targetFN1
        self.targetFN2 = targetFN2
        self.genomePth = genomePth
        self.args = args
        self.ctrlFN1 = ctrlFN1
        self.ctrlFN2 = ctrlFN2
        self.genome = genome

        if outDr is None:
            outDr = inDr # if no output directory provided, use input directory
        if targetFNOut is None:
            targetFNOut = [w.replace('.fastq', '_bowtie2P.sam').replace('.gz', '') for w in targetFN1]
        if ctrlFNOut is None:
            if ctrlFN1:
                ctrlFNOut = [w.replace('.fastq', '_bowtie2P.sam').replace('.gz', '') for w in ctrlFN1]
            else:
                ctrlFNOut = []
        if logDr is None:
            logDr = outDr

        self.outDr = outDr
        self.targetFNOut = targetFNOut
        self.ctrlFNOut = ctrlFNOut
        self.logDr = logDr

        dt = str(datetime.datetime.now())
        dt = dt[0:10]
        dt = dt.replace('-', '')
        self.dt = dt
        ''' try/catch to check all inputs ok --------------------------------'''

    ''' main function to run container --------------------------------------'''

    def run(self):
        print(self.targetFN1 + self.ctrlFN1, '\n')
        print(self.targetFN2 + self.ctrlFN2, '\n')
        print(self.targetFNOut + self.ctrlFNOut, '\n')
        print('\n')

        with open(self.logDr + '/' + 'AlignBowtie2Paired' + self.dt + '.err', 'w+') as lgf:

            lgf.write('Align stderr ' + str(datetime.datetime.now()) + '\n') # open log file for writing
            for fqFN, fqFN2, fqFNOut in zip(self.targetFN1 + self.ctrlFN1, self.targetFN2 + self.ctrlFN2,self.targetFNOut + self.ctrlFNOut): # loop trhough files

                inPth = self.inDr + '/' + fqFN
                inPth2 = self.inDr + '/' + fqFN2
                outPth = self.outDr + '/' + fqFNOut
                print('\n')
                print('Locating files:', inPth, 'and', inPth2, '\n')
                print('Output path', outPth, '\n')
                print('\n')

                if os.path.exists(inPth) and os.path.exists(inPth2):
                    print(inPth, 'and', inPth2, 'paired reads exist, attempting alignment')

                    ''' Input to bowtie2 -----------------------------------'''

                    bwt2ParLst = ['docker', 'run','--rm','-v', self.genomePth + ':/data/genomes/',
                            '-v', self.inDr + ':/data/inputFiles',
                            '-v', self.outDr + ':/data/outputFiles',
                            'biocontainers/bowtie2:v2.2.9_cv2',
                            'bowtie2', '-q',
                            '-x', self.genomePth + self.genome,
                            '-1', '/data/inputFiles/' + fqFN,
                            '-2', '/data/inputFiles/' + fqFN2,
                            '-S', '/data/outputFiles/' + fqFNOut
                    ]

                    if self.args: # if there are command line args add these in
                        bwt2ParLst[len(bwt2ParLst):len(bwt2ParLst) + len(self.args)] = self.args
                        #print(bwt2ParLst)
                    p = subprocess.Popen(bwt2ParLst,
                    shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE) # run process

                    output, err = p.communicate()
                    print('out:' + output)
                    print('err:' + err)

                    lgf.write('\nPaired Files to align: ' +   inPth + ' and ' + inPth2 + '\nGenome:'
                    + self.genomePth + self.genome + '\nOutput File:' + outPth + '\n'
                    + 'Docker/Bowtie2 arguments: ' + ','.join(bwt2ParLst))
                    if self.args:
                        lgf.write('Cmd line Args: ' + ','.join(self.args) + '\n\n')
                    else:
                        lgf.write('No additional command line args\n\n')
                    lgf.write(err)

                else:
                    print('Could not find file', inPth, 'skipping alignment')

        lgf.close()


"""=========================================================================="""
''' Class to run docker container for MACS =================================='''
