# Contains functions to run the peak calling docker biocontainers

import subprocess
import os
import sys
import json
import datetime

""" Class to run MACS docker container ======================================"""
class runMACS:

    def __init__(self, inDr, targetFN, args = [], logDr = None,
    outDr = None, ctrlFN = None, outFN = None):

        self.inDr = inDr
        self.targetFN = targetFN
        self.args = args

        if logDr is None:
            logDr = inDr

        if outDr is None:
            outDr = inDr

        self.logDr = logDr
        self.outDr = outDr

        if outFN is None:
            outFN = [w.replace('.sorted.bam', '_MACS') for w in targetFN]

        if not ctrlFN:
            ctrlFN = None

        self.ctrlFN = ctrlFN
        self.outFN = outFN
        dt = str(datetime.datetime.now())
        dt = dt[0:10]
        dt = dt.replace('-', '')
        self.dt = dt
    ''' run function ------------------------------------------------------- '''

    def run(self):

        ''' Docker arguments for all cases '''
        dockerArgs = ['docker', 'run', '--rm', # docker run args
        '-v',  self.inDr + ':/data/inputFiles', # shared volume for input data
        '-v', self.outDr +  ':/data/outputFiles', # shared volume for outputdata
        'kathrinklee/macs1', # container
        'macs14', # call program
        '--gsize=hs', # genome size
        '--format=BAM' # output file format
        ]

        macsErr = open(self.logDr + '/macs' + self.dt + '.err', 'w+')
        macsErr.write('Error log for MACS ' + self.dt) # open err file for writin

        for cx, dx in enumerate(self.targetFN): # loop through input Files

            ''' Check for conrol files '''
            if self.ctrlFN is None:
                    #print('No control file')
                ctrlArgs = []
                ctrlFN = 'No control'
            elif len(self.ctrlFN) == 1:
                ctrlArgs = ['-c', '/data/inputFiles/' + self.ctrlFN[0]]
                #print('1 Control file found: ', ctrlArgs)
                ctrlFN = self.ctrlFN[0]
            else:
                ctrlArgs = ['-c', '/data/inputFiles/' + self.ctrlFN[cx]]
                #print('Control file found: ', ctrlArgs)
                ctrlFN = self.ctrlFN[cx]
            ''' Construct dcker input'''
            print('Target file: ', dx, 'Output file: ', self.outFN[cx])
            tarArgs = ['-t', '/data/inputFiles/' + dx]
            outFNArgs = ['--name', '/data/outputFiles/' + self.outFN[cx]]
            dockerInput = dockerArgs + outFNArgs + tarArgs + ctrlArgs + self.args

            ''' Run subprocess '''
            p = subprocess.Popen(dockerInput, shell=False, stdout=subprocess.PIPE,
                 stderr=subprocess.PIPE)

            output, err = p.communicate()
            macsErr.write('\n' + 'Experiment File: ' + dx +
                 ', Control File: ' + ctrlFN + '\n')
            macsErr.write(err + '\n')

        macsErr.close()
            #print(dockerInput)
""" Class to run MACS docker container ======================================"""
class runMACS2:

    def __init__(self, inDr, targetFN, args = [], logDr = None,
    outDr = None, ctrlFN = None, outFN = None):

        self.inDr = inDr
        self.targetFN = targetFN
        self.args = args

        if logDr is None:
            logDr = inDr

        if outDr is None:
            outDr = inDr

        self.logDr = logDr
        self.outDr = outDr

        if outFN is None:
            outFN = [w.replace('.sorted.bam', '_MACS2') for w in targetFN]

        if not ctrlFN:
            ctrlFN = None

        self.ctrlFN = ctrlFN
        self.outFN = outFN
        dt = str(datetime.datetime.now())
        dt = dt[0:10]
        dt = dt.replace('-', '')
        self.dt = dt


    def run(self):
        ''' Docker args for all cases '''
        dockerArgs = ['docker', 'run', '--rm', # docker run args
            '-v', self.inDr + ':/data/inputFiles', # shared volume for input outputdata
            '-v', self.outDr +  ':/data/outputFiles', # shared volume for outputdata
            'fooliu/macs2', # container
            'callpeak', # program
            '-g', 'hs'
            ]

        macsErr = open(self.logDr + '/macs2' + self.dt + '.err', 'w+')
        macsErr.write('Error log for MACS2 ' + self.dt) # open err file for writin

        for cx, dx in enumerate(self.targetFN): # loop through input Files

            ''' Check for conrol files '''
            if self.ctrlFN is None:
                    #print('No control file')
                ctrlArgs = []
                ctrlFN = 'No control'
            elif len(self.ctrlFN) == 1:
                ctrlArgs = ['-c', '/data/inputFiles/' + self.ctrlFN[0]]
                #print('1 Control file found: ', ctrlArgs)
                ctrlFN = self.ctrlFN[0]
            else:
                ctrlArgs = ['-c', '/data/inputFiles/' + self.ctrlFN[cx]]
                #print('Control file found: ', ctrlArgs)
                ctrlFN = self.ctrlFN[cx]
            ''' Construct dcker input'''
            print('Target file: ', dx, 'Output file: ', self.outFN[cx])
            tarArgs = ['-t', '/data/inputFiles/' + dx]
            outFNArgs = ['--name', self.outFN[cx], '--outdir', '/data/outputFiles/']
            dockerInput = dockerArgs + outFNArgs + tarArgs + ctrlArgs + self.args
            print('\n')
            print(dockerInput)
            ''' Run subprocess '''
            p = subprocess.Popen(dockerInput, shell=False, stdout=subprocess.PIPE,
                 stderr=subprocess.PIPE)

            output, err = p.communicate()
            macsErr.write('\n' + 'Experiment File: ' + dx +
                 ', Control File: ' + ctrlFN + '\n')
            macsErr.write(err + '\n')

        macsErr.close()
