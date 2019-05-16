''' Contains classes to run ChIP seq analysis pipeline '''
import subprocess
import os
import sys
import json
import datetime

''' Class to run docker container for unpaired bowtie2 ======================'''
class runBowtie2Unpaired:

    '''Methods =============================================================='''
    ''' Constructor ---------------------------------------------------------'''
    def __init__(self, tpDr, targetFn, args = [], logDr = None, ctrlFn = None, outDr =  None, targetFnOut = None, ctrlFnOut = None):
        if outDr is None:
            outDr = tpDr # if no output directory provided, use input directory
        if outNm is None:
            print('Sort out output name')
        if ctrl is not None:
            targets = targetFn + ctrlFn # combine target filenames and control
            # file names

        ''' try/catch to check all inputs ok --------------------------------'''

    ''' main function to run container --------------------------------------'''
    def run():









''' Class to run docker container for paired bowtie2 ========================'''
class runBowtie2Paired:

''' Constructor ============================================================='''
    def __init__(self, tpDr, targetFn1, targetFn2, ctrlFn, outDir =  None, outNm = None):
        if outDir is None:
            outDir = tpDr
        if outNm is None:
            print('Sort out output name')#
