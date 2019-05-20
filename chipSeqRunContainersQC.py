''' Contains classes to run ChIP seq analysis pipeline '''
import subprocess
import os
import sys
import json
import datetime

""" ======================================================================== """
""" Class to run fastQC docker container =================================== """

class runFastQC:

    def __init__(self, inDr, targetFN, logDr = None):
        self.inDr = inDr
        self.targetFN = targetFN

        if logDr is None:
            logDr = inDr

        self.logDr = logDr

        dt = str(datetime.datetime.now())
        dt = dt[0:10]
        dt = dt.replace('-', '')
        self.dt = dt

    def run(self):

        fastQCErr = open(self.logDr + '/runFastQC' + self.dt + '.err', 'w+')
        fastQCErr.write('Error log for samtools Index ' + self.dt)

        dockerArgs= [
        'docker', 'run', '-v', self.inDr + ':/data/', '--rm',
         'biocontainers/fastqc:v0.11.5_cv3', 'fastqc'] + self.targetFN


        print(dockerArgs)

        p = subprocess.Popen(dockerArgs,
        shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE) # run process

        output, err = p.communicate()
        #print('out:' + output)
        #print('err:' + err)

        fastQCErr.write('fastQC report: ' +  self.inDr + ' ' + ''.join(self.targetFN))
        fastQCErr.write('\n' + err)

        fastQCErr.close()

""" ======================================================================== """
""" Class to use bedtools to remove blacklisted regions ==================== """

class runBedToolsRmBL:

    def __init__(self, inDr, targetFN, blkLstPth, blkLstFN, outFN = None, logDr = None):

        self.inDr = inDr
        self.targetFN = targetFN
        self.blkLstPth = blkLstPth
        self.blkLstFN = blkLstFN

        dt = str(datetime.datetime.now())
        dt = dt[0:10]
        dt = dt.replace('-', '')
        self.dt = dt

        if outFN is None:
            outFN = [w.replace('.sorted.bam', 'BLstRm.sorted.bam') for w in targetFN]
        print(outFN)
        self.outFN = outFN

        if logDr is None:
            logDr = inDr

        self.logDr = logDr


    def run(self):
        bedtoolsBLRmErr = open(self.logDr + 'bedtoolsBLRm' + self.dt + '.err', 'w+')
        for inFNDx, outFNDx in zip(self.targetFN, self.outFN):

            dockerArgs = ['docker', 'run', '--rm',
            '-v', self.inDr + ':/input/',
            '-v', self.blkLstPth + ':/blPth',
            'biocontainers/bedtools:v2.28.0_cv1',  'intersect', '-v', '-abam',
            '/input/' + inFNDx, '-b', '/blPth/' + self.blkLstFN
            ]

            print(dockerArgs)

            p = subprocess.Popen(dockerArgs,
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE) # run Preprocess

            output, err = p.communicate()

            print(self.inDr, outFNDx)
            with open(self.inDr + outFNDx, 'w+b') as f:
                f.write(output)

            bedtoolsBLRmErr.write('Input file: ' + self.inDr + inFNDx)
            bedtoolsBLRmErr.write('\n')
            bedtoolsBLRmErr.write(err)
        bedtoolsBLRmErr.close()
