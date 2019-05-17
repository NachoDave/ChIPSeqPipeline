''' Contains classes to run ChIP seq analysis pipeline '''
import subprocess
import os
import sys
import json
import datetime

"""=========================================================================="""
''' Class to run docker container for samtools =============================='''

class runSamtools:

    def __init__(self, inDr, targetFN, logDr = None, ctrlFN = [],  targetFNOut = None, ctrlFNOut = None):
        # Write BAM files to the same directory as the SAM files
        self.inDr = inDr
        self.targetFN = targetFN
        self.ctrlFN = ctrlFN
        if logDr is None:
            logDr = inDr
        if targetFNOut is None:
            targetFNOut = [w.replace('.sam', '.bam') for w in targetFN]
        if ctrlFNOut is None:
            ctrlFNOut = [w.replace('.sam', '.bam') for w in ctrlFN]

        self.targetFNOut = targetFNOut
        self.ctrlFNOut = ctrlFNOut
        self.logDr = logDr
        dt = str(datetime.datetime.now())
        dt = dt[0:10]
        dt = dt.replace('-', '')
        self.dt = dt


    ''' Method to convert sam files to bam files '''
    def sam2Bam(self):
        print(self.targetFNOut)
        print('\n')
        print(self.ctrlFNOut)
        samViewErr = open(self.logDr + '/samView' + self.dt + '.err', 'w+')
        samViewErr.write('Error log for samtools view ' + self.dt)

        for inNm, outNm in zip(self.targetFN + self.ctrlFN, self.targetFNOut + self.ctrlFNOut):
            print(self.inDr, inNm, outNm)
            print('\n')

        samViewErr.close()
    ''' Method to create BAM index '''
    #def indexBam(self):

    ''' Method to sort BAM files '''
    #def sortBam(self):

    ''' Run all 3 methods to convert, index and sort SAM '''
    def run(self):
        self.sam2Bam()
