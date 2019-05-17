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
