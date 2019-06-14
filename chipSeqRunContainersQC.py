''' Contains classes to run ChIP seq analysis pipeline '''
import subprocess
import os
import sys
import json
import datetime

""" ======================================================================== """
""" Class to run trimming docker container ================================= """

class runTrimR:

    def __init__(self, inDr, targetFN, targetFN2 = None, logDr = None, outDr = None, outFN = None, outFN2 = None,
    scriptDr = '/data/ChIPSeqAnalysis/RScripts/preProcessing/',
    scriptNM = 'readPreprocessing.Rmd', reportDr = None, nBsN = 1, phredthres = 30, phredN = 5, PE = 'N'):

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
        self.targetFN2 = targetFN2
        self.nBsN = str(nBsN)
        self.phredthres = str(phredthres)
        self.phredN = str(phredN)
        self.scriptDr = scriptDr
        self.scriptNM = scriptNM
        self.PE = PE

        if logDr is None:
            logDr = inDr
        if outDr is None:
            outDr = inDr
        if reportDr is None:
            reportDr = inDr

        if outFN is None:
            outFN = [w.replace('.fastq', '_trim.fastq') for w in targetFN]

        if outFN2 is None and targetFN2 is not None:
            outFN2 = [w.replace('.fastq', '_trim.fastq') for w in targetFN2]

        self.logDr = logDr
        self.outDr = outDr
        self.reportDr = reportDr
        self.outFN = outFN
        self.outFN2 = outFN2

        dt = str(datetime.datetime.now())
        dt = dt[0:10]
        dt = dt.replace('-', '')
        self.dt = dt

    def runSE(self):

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

            spInput = dockerArgs + [RMDStr, self.PE,'/home/rstudio/data/' + inNm,'/home/rstudio/results/' + outNm, self.nBsN, self.phredN, self.phredthres]

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

    def runPE(self):

        if self.targetFN2 is None:
            print("You've selected pairended trimming, but only one target directory provided. Exiting")
            sys.exit()

        # Main part
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

        for inNm, outNm, inNm2, outNm2, in zip(self.targetFN,  self.outFN, self.targetFN2, self.outFN2):
            print(inNm, outNm, '\n')
            rptStr = inNm.replace('.fastq', '').replace('.gz', '') + '_'
            RMDStr = 'rmarkdown::render("/home/rstudio/scripts/readPreprocessing.Rmd", output_file = "/home/rstudio/reports/TrimReport' + rptStr + self.dt + '.html")' # string of R rmarkdown cmds
            #print(RMDStr)

            spInput = dockerArgs + [RMDStr, self.PE,'/home/rstudio/data/' + inNm,'/home/rstudio/data/' + inNm2,
            '/home/rstudio/results/' + outNm,
            '/home/rstudio/results/' + outNm2,
            self.nBsN, self.phredN, self.phredthres]

            print(spInput)
            print('\n\n')
            p = subprocess.Popen(spInput, shell=False, stdout=subprocess.PIPE,
                 stderr=subprocess.PIPE)

            output, err = p.communicate()

            errF.write('Trimming files' + inNm + ', ' + inNm2)
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
            outFN = [w.replace('.sorted.bam', 'BlkLstRm.sorted.bam') for w in targetFN]
        print(outFN)
        self.outFN = outFN

        if logDr is None:
            logDr = inDr

        self.logDr = logDr


    def run(self):
        bedtoolsBLRmErr = open(self.logDr + '/bedtoolsBLRm' + self.dt + '.err', 'w+')
        for inFNDx, outFNDx in zip(self.targetFN, self.outFN):

            dockerArgs = ['docker', 'run', '--rm',
            '-v', self.inDr + ':/input/',
            '-v', self.blkLstPth + ':/blPth',
            'biocontainers/bedtools:v2.28.0_cv1',  'intersect', '-v', '-abam',
            '/input/' + inFNDx, '-b', '/blPth/' + self.blkLstFN
            ]

            #print(dockerArgs)

            p = subprocess.Popen(dockerArgs,
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE) # run Preprocess

            output, err = p.communicate()

            print(self.inDr, outFNDx)
            with open(self.inDr + outFNDx, 'w+b') as f:
                f.write(output)
            f.close()

            bedtoolsBLRmErr.write('Input file: ' + self.inDr + inFNDx)
            bedtoolsBLRmErr.write('\n')
            bedtoolsBLRmErr.write(err)
        bedtoolsBLRmErr.close()

""" ======================================================================== """
""" Class to use phantompeakqualtools container ============================ """

class runPhantomPeak:

    def __init__(self, inDr, targetFN, logDr = None, reportDr = None, maxppsize = 10000, tmp = '/tmp/'):
        self.inDr = inDr
        self.targetFN = targetFN
        self.maxppsize = str(maxppsize)
        self.tmp = tmp

        if logDr is None:
            logDr = inDr

        if reportDr is None:
            reportDr = inDr

        self.logDr = logDr
        self.reportDr = reportDr

        dt = str(datetime.datetime.now())
        dt = dt[0:10]
        dt = dt.replace('-', '')
        self.dt = dt

        self.outFN = [w.replace('.sorted.bam', '').replace('.bam', '') for w in targetFN]
        print(self.outFN)

    def run(self):

        pQCErr = open(self.logDr + '/runPhantomPeak' + self.dt + '.err', 'w+')
        pQCErr.write('Error log for phantompeakqualtools ' + self.dt)

        for fnDx, outFN in zip(self.targetFN, self.outFN):

            pdfNm = 'CrosCor_' + outFN + '.pdf'
            #print(pdfNm)
            outSPPNm = 'CrosCor_' + outFN + '.spp_out'
            #print(outSPPNm)

            dockerArgs = ['docker', 'run', '--rm',
            '-v', self.inDr + ':/sinput',
            '-v', self.reportDr + ':/output/',
            '-v', self.tmp + ':/temp/',
            'quay.io/biocontainers/phantompeakqualtools:1.2--0'] # docker specific arguments
            print(dockerArgs)
            phntPkArgs = ['Rscript', '--verbose',
            '--max-ppsize=' + self.maxppsize,
            '/usr/local/bin/run_spp.R',
            '-tmpdir=' + self.tmp,
            '-c=/sinput/' + fnDx,
            '-savp=/output/' + pdfNm,
            '-out=/output/' + outSPPNm] # phantompeak arguments
            print(phntPkArgs)

            p = subprocess.Popen(dockerArgs + phntPkArgs,
                shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE) # run Preprocess

            output, err = p.communicate()
            print(output)
            print(err)

            pQCErr.write('Input file: ' + self.inDr + fnDx)
            pQCErr.write('\n')
            pQCErr.write('Stdout:\n')
            pQCErr.write(output)
            pQCErr.write('\nStder:\n ')
            pQCErr.write('err')
            pQCErr.write('\n')

        pQCErr.close()
