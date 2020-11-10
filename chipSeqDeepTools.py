''' Contains classes to run ChIP seq analysis pipeline '''
import subprocess
import os
import sys
import json
import datetime

""" ======================================================================== """
""" Class to run trimming docker container ================================= """

class makeBigWig:

    def __init__(self, inDr, targetFN, outDr, outFN, logDr, extend = 150, bs = 50, args = []):
        self.inDr = inDr
        self.targetFN = targetFN
        self.outDr = outDr
        self.outFN = outFN
        self.extend = extend
        self.bs = bs
        self.args = args
        self.logDr = logDr

        dt = str(datetime.datetime.now())
        dt = dt[0:10]
        dt = dt.replace('-', '')
        self.dt = dt

    def runBamCoverage(self):
        bamCovErr = open(self.logDr  + '/bamCov' + self.dt + '.err', 'w+')
        # Make docker input
        dockerArgs = [
        'docker', 'run', '--rm',
        '-v', self.inDr + ':/dataIn/',
        '-v', self.outDr + ':/dataOut/',
        'quay.io/biocontainers/deeptools:3.3.1--py_0', 'bamCoverage',
        '-p', '10',
        '-v', '--extendReads', str(self.extend),
        '-bs', str(self.bs)
        ] # docker arguments for all files

        #print(dockerArgs)

        # loop through BAM Files
        for ix, ox in zip(self.targetFN, self.outFN):
            bamCovErr.write("Sample: " + ix + "\n")

            dockerInput = dockerArgs + ['--bam',  '/dataIn/' +  ix, '-o', '/dataOut/' + ox]

            print(dockerInput)

            p = subprocess.Popen(dockerInput,
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            output, err = p.communicate()
            bamCovErr.write('stdout: ' + output)
            bamCovErr.write('stderr: ' + err)

        bamCovErr.close()
