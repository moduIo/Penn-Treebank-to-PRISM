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

#
# Format Declarations section of program
#
declarations = '\n%%------------------------------------'
declarations += '\n%%  Declarations:'
declarations += '\n%%------------------------------------'
declarations += '\n\n%'
declarations += '\n% Probabilistic production rules'
declarations += '\n%'

print(declarations)

#
# Format Modeling section of program
#
model = '\n%%------------------------------------'
model += '\n%%  Modeling part:'
model += '\n%%------------------------------------'
model += '\n\npcfg(L) :- pcfg(\'S\', L-[]).'
model += '\n\npcfg(LHS,L0-L1) :-'
model += '\n    ( nonterminal(LHS) -> msw(LHS, RHS), proj(RHS, L0-L1)'
model += '\n    ; L0 = [LHS|L1]'
model += '\n    ).'
model += '\n\nproj([], L-L).'
model += '\nproj([X|Xs], L0-L1) :- pcfg(X, L0-L2), proj(Xs, L2-L1).'

print(model)