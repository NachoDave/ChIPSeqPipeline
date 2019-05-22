''' Contains classes to run ChIP seq analysis pipeline '''
import subprocess
import os
import sys
import json
import datetime

""" ======================================================================== """
""" Class to run trimming docker container ================================= """

class runTrimR:

    def __init__(self, inDr, targetFN, logDr = None, outDr = None, outFN = None,
    scriptDr = '/data/ChIPSeqAnalysis/RScripts/preProcessing/',
    scriptNM = 'readPreprocessing.Rmd',
    reportDr = None, nBsN = 1, phredthres = 30, phredN = 5):

        """
        targetFN - names of files to be trimmed
        inDr - location of input Files
        logDr - where output logs to be written
        outDr - location to write files
        reportDr - where to put rmarkdown reports
        nBsN - reads with at least nBsN base pairs to remove
        phredthres - phred score threshold
        phredN - number of base pairs in read below which to keep
        """
        self.inDr = inDr
        self.targetFN = targetFN
        self.nBsN = str(nBsN)
        self.phredthres = str(phredthres)
        self.phredN = str(phredN)
        self.scriptDr = scriptDr
        self.scriptNM = scriptNM

        if logDr is None:
            logDr = inDr
        if outDr is None:
            outDr = inDr
        if reportDr is None:
            reportDr = inDr

        if outFN is None:
            outFN = [w.replace('.fastq', '_trim.fastq') for w in targetFN]

        self.logDr = logDr
        self.outDr = outDr
        self.reportDr = reportDr
        self.outFN = outFN

        dt = str(datetime.datetime.now())
        dt = dt[0:10]
        dt = dt.replace('-', '')
        self.dt = dt

    def run(self):

        dockerArgs = [
        'docker', 'run', '--rm',
        '-v', self.inDr + ':/home/rstudio/data/',
        '-v', self.outDr + ':/home/rstudio/results/',
        '-v', self.reportDr + ':/home/rstudio/reports/',
        '-v', self.scriptDr + ':/home/rstudio/scripts/',
        'rstudiosyspipe_dj',
        'Rscript', '-e'
        ] # docker arguments for all files

        print(dockerArgs)

        errF = open(self.logDr + '/Trim' + self.dt + '.log', 'w+')
        errF.write('Log file for trimming files using readPreprocessing.Rmd from ' + self.inDr + ' ' + self.dt)
        errF.write('\n')

        for inNm, outNm in zip(self.targetFN, self.outFN):
            print(inNm, outNm, '\n')
            rptStr = inNm.replace('.fastq', '').replace('.gz', '') + '_'
            RMDStr = 'rmarkdown::render("/home/rstudio/scripts/readPreprocessing.Rmd", output_file = "/home/rstudio/reports/TrimReport' + rptStr + self.dt + '.html")' # string of R rmarkdown cmds
            #print(RMDStr)

            spInput = dockerArgs + [RMDStr, '/home/rstudio/data/' + inNm,'/home/rstudio/results/' + outNm, self.nBsN, self.phredN, self.phredthres]

            print(spInput)
            print('\n\n')
            p = subprocess.Popen(spInput, shell=False, stdout=subprocess.PIPE,
                 stderr=subprocess.PIPE)

            output, err = p.communicate()

            errF.write('Trimming file' + inNm)
            errF.write('\n')
            errF.write('stdout: ' + output)
            errF.write('\n stderr: ' + err)

        errF.close()


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
