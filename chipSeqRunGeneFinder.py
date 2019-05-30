''' Contains classes to run ChIP seq analysis pipeline '''
import subprocess
import os
import sys
import json
import datetime

""" Class to run gene finder rscript ======================================= """

class runGeneFinderR:

    def __init__(self, inDr, targetFN, geneLstNm,
    geneLstPth = '/data/ChIPSeqAnalysis/RScripts/geneTable/',
    scriptDr = '/data/ChIPSeqAnalysis/RScripts/geneFindR/',
    scriptNM = 'runFindGenes.Rmd' , dist = [],
    FDR = [], pval = [], outFN = None, outDr = None, logDr = None,
    peakCaller = 'MACS'):

        self.inDr = inDr # directory containng MACS xlsx
        self.targetFN = targetFN # files to look for genelist
        self.scriptDr = scriptDr
        self.geneLstPth = geneLstPth
        self.scriptNM = scriptNM
        self.peakCaller = peakCaller
        self.geneLstNm = geneLstNm

        if logDr is None:
            logDr = inDr

        if outDr is None:
            outDr = inDr

        self.logDr = logDr
        self.outDr = outDr

        if outFN is None:
            outFN = [w.replace('_peaks.xls', '') for w in targetFN]

        self.outFN = outFN
        dt = str(datetime.datetime.now())
        dt = dt[0:10]
        dt = dt.replace('-', '')
        self.dt = dt

    def run(self):

        dockerArgs = ['docker', 'run', '--rm',
         '-v', self.scriptDr +':/home/rstudio/scripts',
          '-v', self.inDr + ':/home/rstudio/data',
          '-v', self.geneLstPth + ':/home/rstudio/genetable',
          '-v', self.logDr + ':/home/rstudio/logDr',
          '-v', self.outDr + ':/home/rstudio/output',
           'rstudionsyspipe_dj:version2', 'Rscript', '-e']

        print(dockerArgs)

        rOutPut = open(self.logDr +  'Genefinder' + self.dt + '.log', 'w+')

        for infndx, outfndx in zip(self.targetFN, self.outFN):

            RMDStr = 'rmarkdown::render("/home/rstudio/scripts/' + self.scriptNM + '", output_file = "/home/rstudio/logDr' + outfndx + '.html")'
            inputPth = '/home/rstudio/data/' + infndx
            pkCler = self.peakCaller
            gnStr = '/home/rstudio/genetable/' + self.geneLstNm
            outputPth = '/home/rstudio/output/' + outfndx

            #print(RMDStr)
            #print('\n')
            #print(inputPth)
            #print('\n')
            #print(gnStr)
            #print('\n')
            #print(outputPth)
            #print('\n')

            dockerInput = dockerArgs + [RMDStr, inputPth, pkCler , gnStr, outputPth]
            print(dockerInput)

            p = subprocess.Popen(dockerInput, shell=False, stdout=subprocess.PIPE,
                 stderr=subprocess.PIPE)

            output, err = p.communicate()

            rOutPut.write('GeneFinder from' + self.inDr + infndx)#
            rOutPut.write('\n')
            rOutPut.write('stdout: ')
            rOutPut.write(output)
            print('\n')
            rOutPut.write('stderr: ')
            rOutPut.write(err)
            rOutPut.write('\n\n')

        rOutPut.close()
