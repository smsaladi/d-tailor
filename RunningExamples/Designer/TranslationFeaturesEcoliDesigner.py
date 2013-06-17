'''
Created on Dec 22, 2012

@author: jcg
'''

import Functions
import sys
from SequenceDesigner import SequenceDesigner
from Features.Structure import Structure,StructureMFE
from Features import CAI,RNADuplex
from DesignOfExperiments.Design import RandomSampling,Optimization,FullFactorial
from Data import project_dir


class TranslationFeaturesEcoliDesigner(SequenceDesigner):
    
    def __init__(self, name, seed, design, dbfile, createDB=True):
        SequenceDesigner.__init__(self, name, seed, design, dbfile, createDB)
        
    def configureSolution(self, solution):
        '''
        Solution configuration
        '''
                
        if solution.sequence == None:
            return 0
        
        #Populate solution with desired features
        solution.mutable_region=range(0,len(solution.sequence)) # whole region
        solution.cds_region = (49,len(solution.sequence))
        solution.keep_aa = True
        
        cai_obj = CAI.CAI(solution=solution,label="cds",args= {  'cai_range' : (49,len(solution.sequence)), 'mutable_region' : range(49,len(solution.sequence)) } )
            
        #Look for RBS
        dup_obj1 = RNADuplex.RNADuplexRibosome(solution1=solution, label="sd16s", args = { 'rnaMolecule1region' : (25,48), 'mutable_region' : range(25,48) })
        dup_mfe = RNADuplex.RNADuplexMFE(dup_obj1)
        dup_obj1.add_subfeature(dup_mfe)
        
        #MFE [-30,30]
        st1_obj = Structure(solution=solution,label="utr",args= { 'structure_range' : (49-30,49+30), 'mutable_region' : range(49-30,49+30) } )
        st_mfe = StructureMFE(st1_obj)
        st1_obj.add_subfeature(st_mfe)
        
        solution.add_feature(cai_obj)
        solution.add_feature(dup_obj1)
        solution.add_feature(st1_obj)                    
    
    def validateSolution(self, solution):
        '''
        Solution validation tests
        '''
        if solution.sequence == None or ('?' in solution.levels.values()):
            sys.stderr.write("SolutionValidator: Level unknown - "+str(solution.levels)+"\n")                        
            solution.valid = False
            return 0
        
        #check if solution is valid
        valid = True
      
        designed_region = solution.sequence
                
        #No internal Promoters
        (score, position, spacer) = Functions.look_for_promoters(designed_region)
        if score >= 15.3990166: #0.95 percentile for Promoter PWM scores
            valid = False
            sys.stderr.write("SolutionValidator: High Promoter score: "+str(score)+"\n")                    
        
        #No internal Terminator
        score = Functions.look_for_terminators(designed_region)
        if score >= 90: #90% confidence from transtermHP
            valid = False
            sys.stderr.write("SolutionValidator: High Terminator score\n")    
            
        #No restriction enzymes
        #if 'ggtctc' in designed_region or 'gagacc' in designed_region:
        #    sys.stderr.write("SolutionValidator: Restriction enzyme found\n")
        #    valid = False        
        
        solution.valid = valid
        
        return valid


if __name__ == '__main__':
    #Seed sequence from which mutants will be derived
    seed1='aacattcttgttaagattatgtgatctttagcgcgggaggaaaatattgatgaaacagcctgcgcccgtttatcagagaattgcgggtcatcaatggcgacatatctggctttctggcgatatacacggttgtcttgagcagttgcgccgcaaattatggcattgtcgttttgatccgtggcgagatttacttatctcagtgggagacgttatcgatcgtgggccgcaaagtttacgttgtctgcagttactggaacaacattgggtttgtgcggtaagaggcaatcatgaacagatggcgatggatgcgctggcatcccagcagatgtctttgtggttgatgaatggcggcgactggtttattgcgctggcagataatcaacagaaacaagcgaaaacggcgctggaaaaatgtcagcatttgccctttattcttgaagtacacagtcgcaccggcaagcatgttattgctcatgccgattatccagatgatgtttatgaatggcaaaaggacgttgatttgcatcaggtcttgtggagccgctcgcgattaggtgaacgccaaaaagggcagggaattacaggtgctgatcatttctggtttggtcatacaccgttgcgacatcgcgtggatattggcaacctgcattatattgataccggtgctgtctttgggggcgaactgactcttgtgcaattgcaataa'
#    seed2='ctgaaatatgaattttaacttttagtcattttataaagaggacattttcatgaatcgtattgaacattatcatgactggttacgtgacgcccacgcaatggaaaagcaagccgaatctatgcttgaatccatggccagccgtatagataattatcctgaactacgcgctcgtattgaacaacatcttagtgaaaccaaaaaccagattgttcaactggaaactattcttgatcgtaatgacatttcacgttcagtcattaaagattccatgagtaaaatggctgcgcttgggcagtcaatcggtggtatattcccttctgatgaaatagtcaaaggctctattagcggatatgtcttcgagcaatttgaaatcgcctgttacacctcactattagcagcagcaaaaaatgccggtgatacagcttcaattccaaccatcgaagcgattttaaatgaggaaaagcaaatggccgactggctgattcagaatattccgcaaacaactgagaaatttttaattcgctctgaaactgatggcgtagaagcgaagaaataa'
#    seed3='cgctggtgatgggcttaagtatcctgctgctgaaaaaacaggagggatgatgcgccatttacgcaatatttttaatctgggtatcaaagagttgcgcagtctgctcggtgataaagcgatgctgacgctgattgtcttctcgtttacggtgtcggtgtattcgtcagcgaccgttacgccaggatcgttgaacctcgcgccgatcgccattgccgatatggatcaatcgcagttatcgaaccggatcgttaacagcttctatcgtccgtggtttttgccaccggagatgatcaccgccgatgagatggatgccggactggacgccggacgctataccttcgcgataaatattccgcctaattttcagcgtgatgtcctcgccggacgccagccggatattcaggtgaacgtcgatgccacgcgcatgagccaggcatttaccggcaatgggtatatccagaatattatcaacggtgaagtgaacagctttgtcgcgcgctaccgtgataacagcgaaccgttggtatcgctggaaacccggatgcgctttaacccgaacctcgatcccgcgtggtttggcggggtgatggcgatcatcaacaacattaccatgctggcgattgtattgaccggatcggcgctgatccgcgagcgtgaacacggcacggtggaacacttactggtgatgccgataacgccgtttgagatcatgatggcgaagatctggtcgatggggctggtggtgctggtggtatcgggattatcgctggtgctgatggtgaaaggtgtactgggcgtaccgattgaaggctcgatcccgctgtttatgctgggcgtggcgctcagtctgtttgccaccacgtcaatcggcatttttatggggacgatagcgcgttcaatgccgcaactggggctgctggtgattctggtgctgctgccgctgcaaatgctttccggtggttccacgccgcgcgaaagtatgccgcagatggtgcaggacattatgctgaccatgccgacgacacactttgttagcctcgcgcaggccatcctctaccggggtgccggattcgaaatcgtctggccgcagtttctgacgctgatggcaattggcggcgcatttttcaccattgcgctgctgcgattcaggaagacgattgggacaatggcgtaa'
#    seed4='ttacaacgataaaaggctgtactttttctttagctcatggattaacacaatgaaattaatcactgcaccatgcagagcattacttgctctgccgttttgctacgccttttctgcggcaggagaagaagcacgtccggcagaacatgacgacacaaaaacacccgcaattacctcgacatcttctccttcatttcgtttttacggcgaattaggggttggtggatatatggatttagagggtgagaataaacataaatacagcgacggtacctatattgaaggtggcctggagatgaagtacggctcctggttcggcctgatttacggcgaaggctggaccgtgcaggccgaccacgacggcaatgcctgggtgccagaccatagctggggtggtttcgagggcggaattaaccgtttctatggcggttatcgtaccaatgatggcaccgaaatcatgctcagtctgcgtcaggattcctcgctggatgacctgcaatggtggggcgatttcacccccgatctgggctacgtcattcccaatacccgcgacattatgactgcgctgaaggtacagaacttaagcggcaactttcgttatagcgtcaccgcgactcctgccggacatcatgatgaaagcaaagcctggctacattttggcaaatacgatcgctatgacgacaaatacacctatccggcaatgatgaacggttacatccagtatgaccttgccgaaggcatcacctggatgaacggtctggaaatcaccgacggcacaggacagctctatctcacgggcctgctaactcctaactttgccgctcgcgcctggcaccataccggacgcgccgacgggctggacgtaccgggaagtgaaagtgggatgatggtgagcgccatgtatgaagcgttaaagggcgtttatctctccaccgcttacacctacgccaaacatcgccctgaccacgctgacgatgaaaccacctctttcatgcagtttggtatctggtacgaatacggcggcggacgtttcgccacggcttttgatagccgcttctacatgaaaaatgcctctcacgatcccagcgaccaaatcttcctgatgcaatatttctactggtaa'    
#    seed5='tgggtcgtcagcaaaagaaagataacgctgactcacggggagaataaccgtgaacagacgtaattttattaaagcagcctcctgcggggcattgctgacgggcgcgctgccgtctgtcagtcatgcggctgctgaaaaccgcccgccaattccgggatcgctggggatgttgtacgactcgaccttgtgcgtaggctgccaggcttgcgtcaccaagtgtcaggatatcaatttccctgaacgtaacccgcaaggggaacagacctggtcgaacaacgacaaactgtcgccgtataccaataacatcattcaggtgtggaccagcggcacaggggtcaacaaagaccaggaggagaacggctacgcgtacattaagaaacagtgtatgcactgcgtcgatccgaactgtgtctctgtgtgcccggtctctgcactgaaaaaagatccgaaaaccggcattgtccattacgacaaagatgtgtgcaccggctgccgttactgcatggtcgcctgtccgtacaacgtgccgaagtacgactacaacaacccgtttggtgcgctgcataagtgcgagctgtgcaaccagaaaggtgtggaacgtctcgataaaggcggtctacctggctgcgtagaagtgtgcccggcgggcgcggtgattttcggtacgcgtgaagagctgatggcggaggcgaaaaaacgtctggcgctgaagcctggcagcgaataccactatccgcgtcagacgctgaaatctggcgacacttacctgcatacggtgccgaaatattatccgcatctgtacggcgagaaagagggcggcggtactcaggttctggtactgacgggtgtgccttatgaaaatctcgacctgccgaaactggacgatctttctaccggtgcgcgttccgaaaatattcaacacaccctgtataaaggcatgatgctaccactggctgtgctggcgggcttaaccgtgctggttcgtcgcaacaccaaaaacgaccatcacgacggaggagacgatcatgagtcatga'
#    seed6='ccagtagcactggctgctggggtgcgttttattcataaagcaaggctgtatgagcgagaaattaaagatagtctatcgcccattacaagaattgtcaccgtatgcgcacaacgccaggacgcacagtactgagcaggtggcacaactggtagaaagtattaagcaattcggctggactaatccggtgctgattgacgaaaagggcgaaattattgcgggtcacggtcgtgttatggcggctgaaatgctcaaaatggattctgttccggtcattgttctgtctggcctgacggatgagcagaagcagcgataa'
#    seed7='gtataaacttgacgctttcaaaataaaaagaaaatcgaagcattcacacatgaataaaaaattaatgtatatattcgcaatttttatagttgcagcaattacctgtattagccaacccaagaaaacgacgttgcgtgataaagccatggtgaattatgcctttgattatttaagctcaccgggcagtcttccattcaccacggcagccacggagctttccgcgattcatggtcactcaacgtcgcaatatcgccttggagaattttatcttcatggtagcgacggtaaaccactggattatacacaggcgagatactggtatgagcaatcagcggaacaggaaaatccacgcgcgcaaagtaaactggggtggatctacctcaaaggtctgggggtcaaacccgacacccgtaaagcaattctctggtataaggaagcagctgaacaagggtatgctcatgctcaatatactttaggtttgatctacagaaatggctcaggtattaatgttaaccattatgaatctcaaaaatggttaaaactgaccgccaaacaacattacaaaaatgcggaaagattacttgccgggcttcccgcacattaa'
#    seed8='tctcctttgttattactgtcgtgctttcacttctcgcaggagtcctcgtatggtaagcaacgcctccgcattaggacgcaatggcgtacatgatttcatcctcgttcgcgctaccgctatcgtcctgacgctctacatcatttatatggtcggttttttcgctaccagtggcgagctgacatatgaagtctggatcggtttcttcgcctctgcgttcaccaaagtgttcaccctgctggcgctgttttctatcttgatccatgcctggatcggcatgtggcaggtgttgaccgactacgttaaaccgctggctttgcgcctgatgctgcaactggtgattgtcgttgcactggtggtttacgtgatttatggattcgttgtggtgtggggtgtgtga'
#    seed9='ggttgttgcagaatatgcaaggatgttgtttttcgttaacggagctgccatgaatctgcctgtaaaaatccgccgtgactggcactactatgcgttcgccattggccttatattcattcttaatggcgtggtggggttactgggatttgaagcaaaaggttggcagacctatgccgtcggtctggtgacgtgggtgattagtttctggctggcggggttgattattcgtcgtcgcgatgaagaaactgaaaacgcccaataa'
#    seed10='caattagcaagacatctttttagaacacgctgaataaattgaggttgctatgtctattgtggtgaaaaataacattcattgggttggtcaacgtgactgggaagtgcgtgattttcacggcacggaatataaaacgctgcgcggcagcagctacaatagctacctcatccgcgaagaaaaaaacgtgctgatcgacaccgtcgaccataaattcagccgcgaatttgtgcagaacctgcgtaatgaaatcgatctggcggatatcgattacatcgtgattaaccatgcagaagaggaccacgctggggcgctgaccgaactgatggcacaaattcccgatacgccgatctactgtacagccaacgctatcgactcgataaatggtcatcaccatcatccggagtggaattttaatgtggtgaaaactggcgacacgctggatatcggcaacggcaaacagctcatttttgtcgaaacaccaatgctgcactggccggacagcatgatgacttacctgacaggcgacgcggtgctgttcagtaacgatgctttcggtcaacactactgcgacgagcatctgttcaacgatgaagtggatcagacggagcttttcgagcagtgccagcgttactacgccaatatcctgacgccgttcagccgcctggtaacaccgaaaattaccgagatcctgggctttaacttaccagtcgatatgatagccacttcccacggcgtggtatggcgcgataacccgacgcaaattgtcgagctgtacctgaaatgggcggctgattatcaggaagacagaatcaccattttctacgacaccatgtcgaataacacccgcatgatggctgacgctatcgcccaggggattgcggaaaccgacccacgcgtggcggtgaaaattttcaacgtcgcccgaagcgataaaaacgaaatcctgactaatgtcttccgctcaaaaggcgtgctggtcggcacttcgacgatgaataacgtgatgatgccgaaaatcgccgggctggtggaggagatgactggtttacgcttccgtaacaaacgcgccagtgctttcggctctcacggctggagcggcggtgcggtggatcgtctttccacgcgcctgcaggatgcgggtttcgaaatgtcgcttagcctgaaagcgaaatggcgaccagaccaggacgctctgaagttatgccgtgaacacggtcgcgaaatcgcccgtcagtgggcgctcgcgccgctgccgcagagcacggtgaatacggtagttaaagaagaaacctctgccaccacgacggctgacctcggcccacggatgcagtgcagcgtctgccagtggatttacgatccggcaaaaggcgagccaatgcaggacgttgcgccaggaacgccgtggagtgaagtcccggataacttcctctgcccggaatgctccctcggcaaagacgtctttgaagaactggcatcggaggcaaaatga'
#    seed11='gaatcaggctgttaatcataaataagaccacgggccacggaggctatcaatgttgagtatttttaaaccagcgccacacaaagcgcgcttacctgccgcggagatcgatccgacttatcgtcgattgcgctggcaaattttcctggggatattctttggctatgcggcttactatttggttcgtaagaactttgcgcttgctatgccttatctggttgagcagggattctcacgcggtgatttaggttttgccctttcggggatctcgattgcttatggattttcgaaattcatcatgggttcggtatcggatcgctcgaatccgcgcgttttcctgcccgcaggtttgattctggcggcggcagtgatgttgtttatgggctttgtgccatgggcgacgtcgagcattgcggtgatgtttgtactgttgttcctctgcggttggttccaggggatggggtggccgccgtgtggtcgtactatggtgcactggtggtcgcagaaagaacgtggcggcattgtgtcagtgtggaactgtgcgcacaacgtcggtggtggtattccgccgctgctgttcctgctggggatggcctggttcaatgactggcatgcggcgctctatatgcctgctttctgcgccattctggtggcattattcgcctttgcgatgatgcgcgataccccgcaatcctgtggcttgccgccgatcgaagagtacaaaaatgattatccggacgactataacgaaaaagcggaacaggagctgacggcgaagcaaatcttcatgcagtacgtactgccgaacaaactgctgtggtatatcgccatcgccaacgtgttcgtttatctgctgcgttacggcatcctcgactggtcaccgacttatctgaaagaggttaagcatttcgcgctagataaatcctcctgggcctacttcctttatgaatatgcaggtattccgggcactctgctgtgcggctggatgtcggataaagtcttccgtggcaaccgtggggcaaccggcgttttctttatgacactggtgaccatcgcgactatcgtttactggatgaacccggcaggtaacccaaccgtcgatatgatttgtatgattgttatcggcttcctgatctacggtcctgtgatgctgatcggtctgcatgcgctggaactggcaccgaaaaaagcggcaggtacggcagcgggctttaccgggctgtttggttacctgggcggttcggtggcggcgagcgcgattgttggctacaccgtggacttcttcggctgggatggcggctttatggtaatgattggcggcagcattctggcggttatcttgttgattgttgtgatgattggcgaaaaacgtcgccatgaacaattactgcaagaacgcaacggaggctaa'
#    seed12='acaattcaagaatagccgcaaaatgttgtcattacaacaaggcggctatatgacgctcgcgcagtttgccatgattttctggcacgacctggcagcaccgatcctggcgggaattattaccgcagcgattgtcagctggtggcgtaaccggaagtaa'
#    seed13='atttataaagattaagtaaacacgcaaacacaacaataacggagccgtgatggctggaaacacaattggacaactctttcgcgtaaccaccttcggcgaatcgcacgggctggcgctcggctgcatcgtcgatggtgttccgccaggcattccgctgacggaagcggacctgcaacatgacctcgaccgtcgtcgccctgggacatcgcgctataccacccagcgccgcgagccggatcaggtcaaaattctctccggtgtttttgaaggcgttactaccggcaccagcattggcttgttgatcgaaaacactgaccagcgctctcaggattacagtgcgattaaggacgttttccgtccaggccatgccgattacacctacgaacaaaaatacggtctgcgcgattatcgcggcggtggacgttcttccgcccgcgaaaccgccatgcgcgtggcggcaggagctattgccaaaaaatatctcgccgagaaatttggtattgaaatccgtggctgcctgacccagatgggcgacattccgctggatatcaaagactggtcgcaggtcgagcaaaatccgtttttttgcccggaccccgacaaaatcgacgcgttagacgagttgatgcgtgcgctgaaaaaagagggcgactccatcggcgctaaagtcaccgttgttgccagtggcgttcctgccggacttggcgagccggtctttgaccgcctggatgctgacatcgcccatgcgctgatgagcatcaacgcggtgaaaggcgtggaaattggcgacggctttgacgtggtggcgctgcgcggcagccagaaccgcgatgaaatcaccaaagacggtttccagagcaaccatgcgggcggcattctcggcggtatcagcagcgggcagcaaatcattgcccatatggcgctgaaaccgacctccagcattaccgtgccgggtcgtaccattaaccgctttggcgaagaagttgagatgatcaccaaaggccgtcacgatccctgtgtcgggatccgcgcagtgccgatcgcagaagcgatgctggcgatcgttttaatggatcacctgttacggcaacgggcgcaaaatgccgatgtgaagactgatattccacgctggtaa'
#    seed14='taaaaacagcgcggtgtattgtgacgtttttatatctaccgtgaatgttatgaacactatcgtatttgtggaagatgatgcggaagtcggttcactgattgccgcgtacctggcaaaacatgatatgcaggttaccgtagagccgcgcggcgaccaggccgaagaaaccattttgcgagaaaatccggatttggtgttactcgacatcatgctaccaggcaaggacggcatgaccatttgtcgtgatttacgcgcaaagtggtctggaccgattgttcttctaacctctctcgatagcgatatgaaccacatcctggcactggaaatgggtgcctgcgactatattctcaaaacgacgccccctgctgttttgctagcgcgtttacgtttgcatttgcgtcagaatgagcaagccacactgaccaaaggtcttcaggaaacgtctctgactccctacaaagccctgcatttcggcacgttgaccatcgatcccatcaaccgcgtagtcaccctggctaacactgaaatctcgctctcgacagctgatttcgaattattgtgggaattagctacccatgccgggcaaatcatggaccgcgatgcattgctgaaaaatttacgcggcgtcagttatgacggactggatcgtagcgtggacgtggctatttcgcggttaagaaaaaaactgctcgataacgccgcagaaccttatcgcattaaaactgtgcgtaacaaaggctatctttttgcgcctcatgcatgggaataa'
#    seed15='cgtcgcactcgatgcttagcaagcgataaacacattgtaaggataacttatgaacaagactcaactgattgatgtaattgcagagaaagcagaactgtccaaaacccaggctaaagctgctctggagtccactctggctgcaattactgagtctctgaaagaaggcgatgctgtacaactggttggtttcggtaccttcaaagtgaaccaccgcgctgagcgtactggccgcaacccgcagaccggtaaagaaatcaaaattgccgcagctaacgtaccggcatttgtttctggcaaggcactgaaagacgcagttaagtaa'
#    seed16='gccgaataatcgtcgttggcgaattttacgactctgacaggaggtggcaatgctggttgccgcaggacagtttgctgttacatctgtgtgggaaaagaacgctgagatttgtgcctcgttgatggcgcaggcggcggaaaacgacgcatcgctgtttgccctgccggaagcattgctggcgcgcgatgatcatgatgcagatctatcggttaaatcagcacagctgctggaaggcgaattcctcggactttacggcgagaaagtaaacgtaacatgatgacgacaattctgacgattcatgttccttcaacgccggggcgcgcatggaatatgctggtggcacttcaggcaggaaacatcgtcgcccgttatgccaaactgcatctctatgatgcatttgccattcaggaatcacgccgtgttgatgctggtaatgaaatcgctccgttactggaggtggaagggatgaaggtcggtctgatgacctgttatgacttacgctttccagagctggcgctggcacaggcattacagggagctgaaatcctggtacttcctgccgcctgggttcgcgggccgctcaaagagcatcactggtcaacgttgcttgccgctcgtgcgctggataccacctgttatatggtggcggcgggggagtgcgggaacaaaaatatcggtcaaagccggattatagatccctttggcgtcaccattgcggcagcgtcagaaatgcctgcactcattatggcggaagtgacgcccgaacgtgtgcgtcaggtgcgcgcgcaactgcccgtcttaaacaaccgtcgctttgcgccgccgcaattattatga'
#    seed17='aacgactgcccatgtcgatttagaaatagttttttgaaaggaaagcagcatgaaaattaaaactctggcaatcgttgttctgtcggctctgtccctcagttctacagcggctctggccgctgccacgacggttaatggtgggaccgttcactttaaaggggaagttgttaacgccgcttgcgcagttgatgcaggctctgttgatcaaaccgttcagttaggacaggttcgtaccgcatcgctggcacaggaaggagcaaccagttctgctgtcggttttaacattcagctgaatgattgcgataccaatgttgcatctaaagccgctgttgcctttttaggtacggcgattgatgcgggtcataccaacgttctggctctgcagagttcagctgcgggtagcgcaacaaacgttggtgtgcagatcctggacagaacgggtgctgcgctgacgctggatggtgcgacatttagttcagaaacaaccctgaataacggaaccaataccattccgttccaggcgcgttattttgcaaccggggccgcaaccccgggtgctgctaatgcggatgcgaccttcaaggttcagtatcaataa'
#    seed18='ttttgcagggatgttgtcgtccctgaaaaagcaaaaatggagaaaaggaatgagtgaatcattacatctgacccgcaatggatcaattctggaaattacccttgatcgtccaaaagcgaatgctattgatgcaaaaaccagctttgaaatgggcgaagtatttctaaatttccgtgacgatccgcaattacgtgtcgccattattaccggtgccggagagaagttcttttccgcgggctgggatttaaaagcggcagcagaaggcgaagcaccggatgctgactttggtccgggtggttttgcgggattaaccgaaattttcaatctcgacaaaccggttatcgcagctgtgaacggctatgcctttggcggcggctttgaactggcgctggcggcagattttattgtttgtgccgataacgccagcttcgccctgccggaagccaaactgggcatcgttcctgacagcggcggtgtgctgcgtctgccgaagatcctgccgcctgccatcgtcaatgaaatggtgatgaccggcagacgaatgggcgcagaagaggcgctgcgttgggggatagtcaaccgcgtggttagccaggcggaactgatggataacgcccgcgaactggctcagcagctggttaacagcgccccgctggcgattgcggcgctgaaagagatctaccgcaccaccagcgaaatgccggtagaagaagcgtatcgctatattcgcagcggcgtgttgaaacactatccatcggttctgcattcggaagatgccattgaagggccgctggcgtttgccgagaagcgcgatccggtgtggaaaggacgttaa'
#    seed19='caaccagtaaactacgcgccagttatgtacacactcaggacaaaaaaacgtgacgattaaattgattgtcggcctggcgaaccccggtgctgaatacgccgcaacgcgacataatgctggtgcctggttcgttgacttactggcagagcgtttgcgcgctccgctgcgcgaagaggctaaattctttggttatacttcgcgagtcactcttggaggcgaagatgtccgcctgttagtcccgactacatttatgaatctcagcggcaaagccgttgcggcgatggccagttttttccgcattaatccggacgaaattctggtggcccacgacgaactggatctgcctcctggcgtcgccaaatttaaattgggcggtggccatggtggtcacaatggactgaaagacatcatcagtaaattgggtaataaccctaactttcaccgtttacgcatcggaatcggtcatccgggcgataaaaataaagttgtcggttttgtgttaggcaaaccgcctgttagtgaacagaagttaattgatgaagccattgacgaagcggcgcgttgtactgaaatgtggtttacagatggcttgaccaaagcaacgaaccgattgcacgcctttaaagcgcaataa'
#    seed20='atcacaaatgttttttgattgtgaagttttgcacggacggggaagatgaatgaaaaagattgcatttggctgtgatcatgtcggtttcattttaaaacatgaaatagtggcacatttagttgagcgtggcgttgaagtgattgataaaggaacctggtcgtcagagcgtactgattatccacattacgccagtcaagtcgcactggctgttgctggcggagaggttgatggcgggattttgatttgtggtactggcgtcggtatttcgatagcggcgaacaagtttgccggaattcgcgcggtcgtctgtagcgaaccttattccgcgcaactttcgcggcagcataacgacaccaacgtgctggcttttggttcacgagtggttggcctcgaactggcaaaaatgattgtggatgcgtggctgggcgcacagtacgaaggcggtcgtcatcaacaacgcgtggaggcgattacggcaatagagcagcggagaaattga'
#    seed21='gccccggcacaggctgcccaggccgttgcgactctataaggacacgataatgacgatttttgataattatgaagtgtggtttgtcattggcagccagcatctgtatggcccggaaaccctgcgtcaggtcacccaacatgccgagcacgtcgttaatgcgctgaatacggaagcgaaactgccctgcaaactggtgttgaaaccgctgggcaccacgccggatgaaatcaccgctatttgccgcgacgcgaattacgacgatcgttgcgctggtctggtggtgtggctgcacaccttctccccggccaaaatgtggatcaacggcctgaccatgctcaacaaaccgttgctgcaattccacacccagttcaacgcggcgctgccgtgggacagtatcgatatggactttatgaacctgaaccagactgcacatggcggtcgcgagttcggcttcattggcgcgcgtatgcgtcagcaacatgccgtggttaccggtcactggcaggataaacaagcccatgagcgtatcggctcctggatgcgtcaggcggtctctaaacaggatacccgtcatctgaaagtctgccgatttggcgataacatgcgtgaagtggcggtcaccgatggcgataaagttgccgcacagatcaagttcggtttctccgtcaatacctgggcggttggcgatctggtgcaggtggtgaactccatcagcgacggcgatgttaacgcgctggtcgatgagtacgaaagctgctacaccatgacgcctgccacacaaatccacggcaaaaaacgacagaacgtgctggaagcggcgcgtattgagctggggatgaagcgtttcctggaacaaggtggcttccacgcgttcaccaccacctttgaagatttgcacggtctgaaacagcttcctggtctggccgtacagcgtctgatgcagcagggttacggctttgcgggcgaaggcgactggaaaactgccgccctgcttcgcatcatgaaggtgatgtcaaccggtctgcagggcggcacctcctttatggaggactacacctatcacttcgagaaaggtaatgacctggtgctcggctcccatatgctggaagtctgcccgtcgatcgccgcagaagagaaaccgatcctcgacgttcagcatctcggtattggtggtaaggacgatcctgcccgcctgatcttcaatacccaaaccggcccagcgattgtcgccagcttgattgatctcggcgatcgttaccgtctactggttaactgcatcgacacggtgaaaacaccgcactccctgccgaaactgccggtggcgaatgcgctgtggaaagcgcaaccggatctgccaactgcttccgaagcgtggatcctcgctggtggcgcgcaccataccgtcttcagccatgcactgaacctcaacgatatgcgccaattcgccgagatgcacgacattgaaatcacggtgattgataacgacacacgcctgccagcgtttaaagacgcgctgcgctggaacgaagtgtattacgggtttcgtcgctaa'
#    seed22='catgatattcatcaggaaaacgccatctatttgatggtgaggagactgcgtgactgacgttttactctgtgttggcaatagcatgatgggcgatgatggcgcaggtccgctgctggcggaaaagtgcgccgccgcgccgaaaggtaactgggtggtgattgacggcggtagcgcaccggaaaacgacatcgtcgctatccgtgaactgcgcccgacacgactgctgattgtcgacgccacggatatggggctaaaccccggcgagatccgcatcatcgacccggatgatatcgccgagatgtttatgatgactacccataacatgccgttgaattaccttatcgaccagttgaaagaagatattggcgaagtgattttcctcggcattcagccggatatcgtcggcttttactacccgatgacccagccgattaaagatgcggtagaaaccgtttatcaacgactggaaggctgggaaggaaatggcggcttcgcgcagttagcggtggaagaagagtag'
#    seed23='ccgacgatgattacggcctcaggcgacaggcacaaatcggagagaaactatgtttgaaccaatggaacttaccaatgacgcggtgattaaagtcatcggcgtcggcggcggcggcggtaatgctgttgaacacatggtgcgcgagcgcattgaaggtgttgaattcttcgcggtaaataccgatgcacaagcgctgcgtaaaacagcggttggacagacgattcaaatcggtagcggtatcaccaaaggactgggcgctggcgctaatccagaagttggccgcaatgcggctgatgaggatcgcgatgcattgcgtgcggcgctggaaggtgcagacatggtctttattgctgcgggtatgggtggtggtaccggtacaggtgcagcaccagtcgtcgctgaagtggcaaaagatttgggtatcctgaccgttgctgtcgtcactaagcctttcaactttgaaggcaagaagcgtatggcattcgcggagcaggggatcactgaactgtccaagcatgtggactctctgatcactatcccgaacgacaaactgctgaaagttctgggccgcggtatctccctgctggatgcgtttggcgcagcgaacgatgtactgaaaggcgctgtgcaaggtatcgctgaactgattactcgtccgggtttgatgaacgtggactttgcagacgtacgcaccgtaatgtctgagatgggctacgcaatgatgggttctggcgtggcgagcggtgaagaccgtgcggaagaagctgctgaaatggctatctcttctccgctgctggaagatatcgacctgtctggcgcgcgcggcgtgctggttaacatcacggcgggcttcgacctgcgtctggatgagttcgaaacggtaggtaacaccatccgtgcatttgcttccgacaacgcgactgtggttatcggtacttctcttgacccggatatgaatgacgagctgcgcgtaaccgttgttgcgacaggtatcggcatggacaaacgtcctgaaatcactctggtgaccaataagcaggttcagcagccagtgatggatcgctaccagcagcatgggatggctccgctgacccaggagcagaagccggttgctaaagtcgtgaatgacaatgcgccgcaaactgcgaaagagccggattatctggatatcccagcattcctgcgtaagcaagctgattaa'
#    seed24='cgggggtgggggtataatgaccattctgttattgcatagagtagttaacatgaagcggagtagaacggaagtggggcgctggcgcatgcagcgtcaggctagccgacgtaaatcgcgttggcttgaggggcaatcgcgccgaaatatgcgtatccacagcatcaggaagtgcattctaaacaaacagcgtaactcgttattgtttgcgatctacaatatctaa'
#    seed25='gatgagttatgtagactggccgccattaattttgaggcacacgtactacatggctgaattcgaaaccacttttgcagatctgggcctgaaggctcctatccttgaagcccttaacgatctgggttacgaaaaaccatctccaattcaggcagagtgtattccacatctgctgaatggccgcgacgttctgggtatggcccagacggggagcggaaaaactgcagcattctctttacctctgttgcagaatcttgatcctgagctgaaagcaccacagattctggtgctggcaccgacccgcgaactggcggtacaggttgctgaagcaatgacggatttctctaaacacatgcgcggcgtaaatgtggttgctctgtacggcggccagcgttatgacgtgcaattacgcgccctgcgtcaggggccgcagatcgttgtcggtactccgggccgtctgctggaccacctgaaacgtggcactctggacctctctaaactgagcggtctggttctggatgaagctgacgaaatgctgcgcatgggcttcatcgaagacgttgaaaccattatggcgcagatcccggaaggtcatcagaccgctctgttctctgcaaccatgccggaagcgattcgtcgcattacccgccgctttatgaaagagccgcaggaagtgcgcattcagtccagcgtgactacccgtcctgacatcagccagagctactggactgtctggggtatgcgcaaaaacgaagcactggtacgtttcctggaagcggaagattttgatgcggcgattatcttcgttcgtaccaaaaacgcgactctggaagtggctgaagctcttgagcgtaacggctacaacagcgccgcgctgaacggtgacatgaaccaggcgctgcgtgaacagacactggaacgcctgaaagatggtcgtctggacatcctgattgcgaccgacgttgcagcccgtggcctggacgttgagcgtatcagcctggtagttaactacgatatcccgatggattctgagtcttacgttcaccgtatcggtcgtaccggtcgtgcgggtcgtgctggccgcgcgctgctgttcgttgagaaccgcgagcgtcgtctgctgcgcaacattgaacgtactatgaagctgactattccggaagtagaactgccgaacgcagaactgctaggcaaacgccgtctggaaaaattcgccgctaaagtacagcagcagctggaaagcagcgatctggatcaataccgcgcactgctgagcaaaattcagccgactgctgaaggtgaagagctggatctcgaaactctggctgcggcactgctgaaaatggcacagggtgaacgtactctgatcgtaccgccagatgcgccgatgcgtccgaaacgtgaattccgtgaccgtgatgaccgtggtccgcgcgatcgtaacgaccgtggcccgcgtggtgaccgtgaagatcgtccgcgtcgtgaacgtcgtgatgttggcgatatgcagctgtaccgcattgaagtgggccgcgatgatggtgttgaagttcgtcatatcgttggtgcgattgctaacgaaggcgacatcagcagccgttacattggtaacatcaagctgtttgcttctcactccaccatcgaactgccgaaaggtatgccgggtgaagtgctgcaacactttacgcgcactcgcattctcaacaagccgatgaacatgcagttactgggcgatgcacagccgcatactggcggtgagcgtcgtggcggtggtcgtggtttcggtggcgaacgtcgtgaaggcggtcgtaacttcagcggtgaacgccgtgaaggtggccgtggtgatggtcgtcgttttagcggcgaacgtcgtgaaggccgcgctccgcgtcgtgatgattctaccggtcgtcgtcgtttcggtggtgatgcgtaa'
#    seed26='ccggggctatgcttatagcgataatcatactgatgagagagggaaggtcatggatcaggcgctactggacgggggttatcgctgttataccggcgaaaagatcgatgtctatttcaacactgcgatatgtcagcattctggcaattgcgtacgtggcaacggcaagttatttaatctcaaacgaaagccgtggatcatgccggatgaagtcgacgtcgccactgtggttaaagtgattgatacgtgcccgagcggcgcgctgaaataccgtcataaataa'
#    seed27='ctggcgagggtttccagatatcatgagttctgattacgcaggagaactcatgatctggataatgctcgccacgctggcggtagtgtttgtggttggttttcgggtgctgacatccggggccagaaaagcgattcgccgtctcagcgatcggctgaacatcgatgtcgtacccgtggagtcgatggtcgatcaaatgggaaagtcagctggtgacgaatttttacgttatttgcatcgtccggatgagtcgcacctgcaaaacgccgcgcaggtgttgctcatctggcaaattgtcattgtcgatggtagcgaacagaacctgctgcaatggcatcggattttacaaaaagctcgcctcgccgcgccgattaccgacgctcaggtcaggctggcgctaggttttctgcgcgaaaccgaacctgaaatgcaggatattaatgcttttcagatgcgctataacgcgttctttcagcctgccgagggcgttcactggttgcattga'
#    seed28='ctgcattatttctggcgtcgaatagctattccttaagcaggagcttgtcatggaattcttaatggacccctcaatttgggcggggctactcacgcttgttgttctcgaaattgtgctgggtatcgataacctggtcttcatcgccattcttgctgacaaactgccgccaaaacaacgcgataaagcgcgtttgctggggttatcactggcgctgattatgcgtctggggctgctgtcgctgatttcatggatggtcacgctgaccaaaccgctatttaccgtcatggatttctccttctccggacgcgacctgattatgttgttcggggggatattcttgctgttcaaagcaacaaccgaactgcatgaacggctggaaaaccgcgatcatgattccggccacggtaaaggctacgccagtttctgggtggtcgtcacacagattgtcatccttgacgccgtcttctcgttggatgcggtaattactgcagtagggatggttaaccatctgccggtgatgatggcggcggtagtgattgcgatggcggttatgttgctggcatccaaaccgctgacgcgattcgttaaccagcaccccacggtggtggtgctctgtctgagcttcctgttaatgattggtctgagtctggtggcagaaggtttcggtttccacattccgaaaggttacctgtatgccgcgattggcttctcgatcatcatcgaagtgtttaaccagattgcgcgtcgcaactttattcgccaccagtcgactttgccgctgcgagcgcgtactgccgatgccatcctgcgtttgatgggcgggaaacgtcaggccaatgttcagcacgatgccgataacccgatgccgatgccgatcccggaaggtgcatttgccgaagaagaacgttacatgattaacggcgtactgacgctggcgtcgcgttctctgcgcgggatcatgacgccgcgcggtgaaataagctgggttgacgctaatctcggggtcgatgaaatccgcgagcaactgctctcttcaccgcacagtctgttcccggtatgtcgcggtgaactggatgaaatcatcggtattgtacgtgctaaagaactgctggtggcgctggaagagggcgttgatgtggcggcgattgcttcggcgtctccggcgattatcgtcccggaaaccctcgatccgatcaacctgttgggcgtgctgcgtcgtgctcgcgggagctttgttatcgtgaccaacgagtttggtgtggtacaaggtctggtcacgccgctggatgtgctggaagccattgcgggtgaattcccggacgctgacgaaacgccggaaatcattactgatggtgacggctggctggtaaaaggcggtacagatttgcatgccttgcagcaggcgcttgatgttgagcaccttgccgatgacgatgatatcgcgacggtcgcgggcctcgtgatctcggcaaatggtcacattccccgtgtgggcgatgtgattgatgtagggccactgcatatcaccatcattgaagccaatgattatcgtgttgatctggttcgcattgttaaagagcaaccggcgcacgatgaagatgagtaa'
#    seed29='ctaacgcatgctagtttaatgacataaggtaggtgaaacggagattggagtgaaaaagtttcgatgggtcgttctggttgtcgtggtgttggcttgcttgctgctttgggcgcaggtattcaacatgatgtgcgatcaggatgtacaatttttcagcggaatttgtgccattaaccagtttatcccgtggtga'
#    seed30='ataaaagttatctcccttctcgttcatcgttccatatttgagaaacagtatgtcttccagagttttgaccccggacgtcgttggtattgacgccctggtacacgatcaccaaaccgttctggcaaaagctgaaggcggtgtggttgccgtatttgctaacaatgccccggcgttttatgccgtcacgcctgcacgcctggctgaactgctggcgctggaagaaaagctggcgcgtccgggaagcgatgtcgctctggacgatcaactctatcaggaaccgcaagccgctcccgttgctgtacccatggggaaattcgccatgtatccggactggcaacccgatgccgattttatccgcctggcggcgctatggggcgtggcgctaagagagccggtgaccaccgaagaactggcctcattcattgcctactggcaggcggaaggtaaagtctttcaccatgtgcagtggcaacaaaaactggcgcgcagcctgcaaatcggtcgtgccagcaacggcggactgccgaaacgagatgtgaatacggtcagcgaacctgacagccaaattccaccaggattcagagggtaa'

    
    #Design Methodology and thresholds
    design_param = {  "sd16sRNADuplexMFE": { 'type' : 'REAL' , 
                                             'thresholds' : { '1': (-12.7,-7.3), '2': (-7.3,-5.8), '3': (-5.8,-5.2), '4': (-5.2,-3.3), '5': (-3.3, 2.0) } },
                      "utrStructureMFE"  : { 'type' : 'REAL' , 
                                             'thresholds' : { '1': (-29.2,-12.2), '2': (-12.2,-9.95), '3': (-9.95,-8.4), '4': (-8.4,-6.73), '5': (-6.73,0.65) } },
                      "cdsCAI"           : { 'type' : 'REAL' , 
                                             'thresholds' : { '1': (0.13,0.29), '2': (0.29,0.33), '3': (0.33,0.37), '4': (0.37,0.42), '5': (0.42,0.86) } }                   
                   
                     }
        
        
    if len(sys.argv)>=2:
        if sys.argv[1] == "optimization":
            design = Optimization(["sd16sRNADuplexMFE","utrStructureMFE","cdsCAI"],design_param, sys.argv[2])
        elif sys.argv[1] == "fullfactorial":
            design = FullFactorial(["sd16sRNADuplexMFE","utrStructureMFE","cdsCAI"],design_param)
        elif sys.argv[1] == "randomsampling":
            design = RandomSampling(["sd16sRNADuplexMFE","utrStructureMFE","cdsCAI"],design_param, int(sys.argv[2]))
        elif sys.argv[1] == "-h":
            print "Please use one of the following options: "
            print "TranslationFeaturesEcoliDesigner.py optimization [target]"
            print "TranslationFeaturesEcoliDesigner.py fullfactorial"
            print "TranslationFeaturesEcoliDesigner.py randomsampling [sample size]"
            sys.exit("")
        else:
            sys.exit("For help use TranslationFeaturesEcoliDesigner.py -h\n")
    else:
        #design = Optimization(["sd16sRNADuplexMFE","utrStructureMFE","cdsCAI"],design_param, '1.4.3')
        design = FullFactorial(["sd16sRNADuplexMFE","utrStructureMFE","cdsCAI"],design_param)
        #design = RandomSampling(["sd16sRNADuplexMFE","utrStructureMFE","cdsCAI"],design_param, 10)
        pass     
    
    tfec_designer = TranslationFeaturesEcoliDesigner("tfec", seed1, design, project_dir+"/testFiles/outputFiles/tfec_test", createDB=True)
    tfec_designer.run(selection="directional")  
