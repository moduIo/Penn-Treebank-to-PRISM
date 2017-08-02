###
# Program translates .full and .pos files output from extract.py
# to a PRISM program which models the PCFG.
###
import sys

#
# Format header comment section of program
#
header = '%%%'
header += '\n% PRISM program for Probabilistic Context Free Grammar models.'
header += '\n% The grammar is derived from the WSJ Treebank corpus.'
header += '\n% ---'
header += '\n% The structure of this code was taken from PRISM User\'s Manual (Version 2.2) - Section 10.2'
header += '\n% Source: http://rjida.meijo-u.ac.jp/prism/download/prism22.pdf'
header += '\n%%%'

print(header)