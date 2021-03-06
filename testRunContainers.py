#!/usr/bin/env python
# ChIP seq scripts

#from chipSeqRunContainers import runBowtie2Paired as bwt2UP
# import chipSeqRunContainers as cont
import chipSeqRunContainersAligners as cont
import chipSeqRunContainersSAMtools as samt
import chipSeqRunContainersQC as qc
import chipSeqRunContainersPeakCalls as pc
import chipSeqRunGeneFinder as gf
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


#b = cont.runBowtie2Unpaired(inDr, tarFN, genPth, genome, ctrlFN = ctrlFN, outDr = resDr, args = args, logDr = logDr)
#print(b.inDr,  b.targetFN,  b.genomePth,  b.targetFNOut, b.ctrlFN, b.outDr, b.logDr)
#print(b.targetFN)
#print('\n')
#print(b.ctrlFN)
#print('\n')
#b.run()
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

''' Test Samtools ==========================================================='''

#tarFN = ['SRR6730206_shrt_RndSamp_bowtie2.sam', 'SRR6730206_shrt_RndSampCopy_bowtie2.sam']
#ctrlFN = ['SRR6730208_1000bpRnd_bowtie2.sam']
#d = samt.runSamtools(resDr, tarFN, ctrlFN = ctrlFN, logDr = logDr, bamFiles = ['SRR6730206_shrt_RndSamp_bowtie2.bam', 'SRR6730206_shrt_RndSampCopy_bowtie2.bam', 'SRR6730208_1000bpRnd_bowtie2.bam'])
#d.run()
#d.sortBam()
#d.indexBam()


''' Test FastQC ============================================================ '''
#e = qc.runFastQC(inDr, tarFN + ctrlFN)
#e.run()

''' Test MACS ============================================================== '''
inDr = '/data/ChIPSeqAnalysis/Experiments/e/results/alignments/'
outDr = '/data/ChIPSeqAnalysis/Experiments/e/results/peakCalls/'
tarFN = ['SRR6730206_shrt_RndSamp_trim_bowtie2.bam',
'SRR6730206_shrt_RndSampCopy_trim_bowtie2.bam',
]

#f = pc.runMACS(inDr, tarFN, ctrlFN = ctrlFN, outDr = outDr)
#f.run()

''' Test remove blacklist bedtools =========================================
'''
#tarFN = ['SRR6730206_shrt_RndSamp_trim_bowtie2.sorted.bam',
#'SRR6730206_shrt_RndSampCopy_trim_bowtie2.sorted.bam',
#]

#inDr = '/data/DaveJames/ChIPSeqAnalysis/Experiments/CurryExample/results/'
#tarFN = ['SRR6730206.sorted.bam']
#g = qc.runBedToolsRmBL(inDr, tarFN, '/data/ChIPSeqAnalysis/DAC_BlackList/','hg38.blacklist.bed')
#g.run()

''' Test Gene list ========================================================= '''
inDr = '/data/DaveJames/ChIPSeqAnalysis/Experiments/CurryExample/results/'
targetFN = ['SRR6730206_SRR6730208ctrl_PstdMACS14_peaks.xls', 'SRR6730206_SRR6730208ctrl_PstdMACS14_Copy_peaks.xls']
logDr = '/data/DaveJames/ChIPSeqAnalysis/Experiments/CurryExample/results/RTestResults/'
outDr = '/data/DaveJames/ChIPSeqAnalysis/Experiments/CurryExample/results/'

#h = gf.runGeneFinderR(inDr, targetFN, logDr = logDr,
#outDr = outDr, geneLstNm = 'GeneCoordinates_ENSEMBL_Biomart150319sorted.txt')
#h.run()

''' Test Trim function ===================================================== '''
inDr = '/data/ChIPSeqAnalysis/Experiments/e/data/'
targetFN = ['SRR6730206_shrt_RndSamp.fastq','SRR6730206_shrt_RndSamp2.fastq']
outDr = '/data/ChIPSeqAnalysis/Experiments/e/results/'
reportDr = '/data/ChIPSeqAnalysis/Experiments/e/reports/'
logDr = '/data/ChIPSeqAnalysis/Experiments/e/logs/'


#k = qc.runTrimR(inDr = inDr, targetFN = targetFN, outDr = outDr, reportDr = reportDr, logDr = logDr,  nBsN = 1, phredthres = 30, phredN = 5)
#k.run()

''' Test phantom peaks QC ================================================== '''
inDr = '/data/ChIPSeqAnalysis/Experiments/WT1_300519/results/alignments/'
targetFN = ['2_fertile_WT1_i6_filteredhg38_trim_bowtie2UPBlkLstRm.sorted.bam', '5_2093Swan_PCOS_AR_i78_filteredhg38_trim_bowtie2UPBlkLstRm.sorted.bam']
repDr = '/data/ChIPSeqAnalysis/Experiments/WT1_300519/reports/'
logDr= '/data/ChIPSeqAnalysis/Experiments/WT1_300519/logs/'
j = qc.runPhantomPeak(inDr, targetFN, reportDr = repDr, logDr = logDr)
j.run()
