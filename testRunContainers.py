#!/usr/bin/env python
# ChIP seq scripts

#from chipSeqRunContainers import runBowtie2Paired as bwt2UP
import chipSeqRunContainers as cont
""" ========================================================================="""
""" Bowtie2 unpaired aligner ------------------------------------------------"""

tarFN = ['SRR6730206_shrt_RndSamp.fastq', 'SRR6730206_shrt_RndSampCopy.fastq']
tarFN2 = ['SRR6730206_shrt_RndSamp2.fastq', 'SRR6730206_shrt_RndSampCopy2.fastq']
ctrlFN = ['SRR6730208_1000bpRnd.fastq']
ctrlFN2 = ['SRR6730208_1000bpRnd2.fastq']
inDr = '/data/ChIPSeqAnalysis/Experiments/e/data/'
genPth = '/data/genomes/'
resDr = '/data/ChIPSeqAnalysis/Experiments/e/results/test'
genome = 'hg19bowtie2'
args = ["-p4", "-t"]
logDr = resDr + '/logs'


b = cont.runBowtie2Unpaired(inDr, tarFN, genPth, genome, ctrlFN = ctrlFN, outDr = resDr, args = args, logDr = logDr)
#print(b.inDr,  b.targetFN,  b.genomePth,  b.targetFNOut, b.ctrlFN, b.outDr, b.logDr)
#print(b.targetFN)
#print('\n')
#print(b.ctrlFN)
#print('\n')
b.run()
'''
c = cont.runBowtie2Paired(inDr, tarFN, tarFN2, genPth, genome, ctrlFN1 = ctrlFN, ctrlFN2 = ctrlFN2,outDr = resDr, args = args)
print(c.inDr,  c.targetFN1,  c.targetFN2,c.genomePth,  c.targetFNOut, c.ctrlFN1, c.ctrlFN2,c.outDr, c.logDr)
print('\n')
print(c.targetFN1)
print('\n')
print(c.ctrlFN1)
print('\n')
c.run()
'''
