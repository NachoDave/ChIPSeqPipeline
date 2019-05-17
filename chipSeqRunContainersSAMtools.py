''' Contains classes to run ChIP seq analysis pipeline '''
import subprocess
import os
import sys
import json
import datetime

"""=========================================================================="""
''' Class to run docker container for samtools =============================='''

class runSamtools:

    def __init__(self, inDr, targetFN, logDr = None, ctrlFN = [],  targetFNOut = None, ctrlFNOut = None, bamFiles = None, idxBamFiles = None):
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
        self.bamFiles = bamFiles
        self.idxBamFiles = idxBamFiles

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

            # run samtools view to convert .sam to .bam----------------------------#

            samToolsViewPar = ['docker', 'run', '--rm', '-v',
                    self.inDr + ':/data/input/',
                    'biocontainers/samtools:v1.7.0_cv3',
                    'samtools', 'view', '-S', '-b',
                    '/data/input/' + inNm
                    ]

            #print(samToolsViewPar)
            p = subprocess.Popen(samToolsViewPar,
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE) # run process

            output, err = p.communicate()
            samViewErr.write('\n' + inNm)
            samViewErr.write(err + '\n')

            with open(self.inDr + '/' + outNm, 'w+b') as f:
                f.write(output)
            f.close

        samViewErr.close()


    ''' Method to sort BAM files '''
    def sortBam(self):
        samSortErr = open(self.logDr  + '/samSort' + self.dt + '.err', 'w+')
        samSortErr.write('Error log for samtools sort ' + self.dt)

        if self.bamFiles is None: # check if bam file names provide, otherwise use the output file names
            self.bamFiles = self.targetFNOut + self.ctrlFNOut

        for inNm in self.bamFiles:

            outNm = inNm.replace('.bam', '.sorted.bam')
            print('Input file name: ', inNm)
            print('  Output fileName: ', outNm)

            # run samtools sort to convert sort the bam ---------------------------#
            samToolsSortPar = ['docker', 'run', '--rm', '-v',
                        self.inDr + ':/data/input/',
                        'biocontainers/samtools:v1.7.0_cv3',
                        'samtools', 'sort',
                        '/data/input/' + inNm
                    ]

            #print(samToolsSortPar)
            p = subprocess.Popen(samToolsSortPar,
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE) # run process

            output, err = p.communicate()
            samSortErr.write('\n' + inNm)
            samSortErr.write(err + '\n')

            with open(self.inDr + '/' + outNm, 'w+b') as f:
                f.write(output)
            f.close


        samSortErr.close()

    ''' Method to create BAM index '''
    def indexBam(self):

        if self.idxBamFiles is None:
            self.idxBamFiles = [w.replace('.sam', '.sorted.bam') for w in self.targetFN + self.ctrlFN]

        samIdxErr = open(self.logDr + '/samIndex' + self.dt + '.err', 'w+')
        samIdxErr.write('Error log for samtools Index ' + self.dt)

        for inNm in self.idxBamFiles:
            print("Sorted bam file name: ", inNm)
            print('\n')
            # run samtools index to convert .sam to .bam---------------------------#
            samToolsIndexPar = ['docker', 'run', '--rm', '-v',
                self.inDr + ':/data/input/',
                'biocontainers/samtools:v1.7.0_cv3',
                'samtools', 'index',
                '/data/input/' + inNm
                ]

            p = subprocess.Popen(samToolsIndexPar,
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE) # run process

            output, err = p.communicate()
            samIdxErr.write('\n' + inNm)
            samIdxErr.write(err + '\n')


        samIdxErr.close()




    ''' Run all 3 methods to convert, index and sort SAM '''
    def run(self):
        self.sam2Bam()
