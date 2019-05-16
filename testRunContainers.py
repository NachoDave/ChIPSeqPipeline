#!/usr/bin/env python
# ChIP seq scripts

#from chipSeqRunContainers import runBowtie2Paired as bwt2UP
import chipSeqRunContainers as cont
""" ========================================================================="""
""" Bowtie2 unpaired aligner ------------------------------------------------"""

tarFN = ['SRR6730206_shrt_RndSamp.fastq', 'SRR6730206_shrt_RndSampCopy.fastq']
ctrlFN = ['SRR6730208_1000bpRnd.fastq', 'xxx']
inDr = '/data/ChIPSeqAnalysis/Experiments/e/data/'
genPth = '/data/genomes/'
resDr = '/data/ChIPSeqAnalysis/Experiments/e/results/test'
genome = 'hg19bowtie2'

#b = bwt2UP(inDr, tarFN, genPth, 'x')
b = cont.runBowtie2Unpaired(inDr, tarFN, genPth, genome, ctrlFN = ctrlFN, outDr = resDr)
#print(b.inDr,  b.targetFN,  b.genomePth,  b.targetFNOut, b.ctrlFN, b.outDr, b.logDr)
print(b.targetFN)
print('\n')
print(b.ctrlFN)
print('\n')
b.run()
