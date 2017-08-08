####
# Program translates .full and .pos files output from extract.py
# to a PRISM program which models the PCFG.
# ---
# COMMAND LINE ARGUMENTS:
# sys.argv[1] := .full file path
# sys.argv[2] := .pos file path
# sys.argv[3] := PRISM program output file path
#
# Example Usage: 
# python3 translator.py "Parses/wsj0.full" "Parses/wsj0.pos" "pcfg.psm"
####
import sys

###
# Function parses grammar files
###
def parse(productions, nonterminals, path):

	with open(path) as f:
		rules = f.read().split('\n')

	# Process all rules
	for rule in rules[:-1]:

		# Break up the rules into LHS and RHS parts
		if '-->' in rule:
			split = rule.split('-->')

		elif '--->' in rule:
			split = rule.split('--->')

		lhs = split[0].split(' ')[1]  # Remove counts from LHS production rule
		rhs = split[1]                # RHS of production rule

		# Remove extra formatting from .pos file
		if path == sys.argv[2]:
			rhs = rhs[3:-3].replace("'", "\\'")

			# Skip rules which stand for themselves
			if lhs == rhs:
				continue

		# Add LHS to nonterminals
		nonterminals.add(lhs)

		# Add rule to productions
		if lhs in productions:
			
			if path == sys.argv[2]:
				productions[lhs] += ", ['" + rhs + "']"
				
			else:
				productions[lhs] += ", " + rhs + ""

		else:

			if path == sys.argv[2]:
				productions[lhs] = "[['" + rhs + "']"
				
			else:
				productions[lhs] = "[" + rhs

###
# Main
###
productions = {}      # Dictionary of rules indexed by LHS of production
nonterminals = set()  # Set of nonterminal symbols

# Parse the files
parse(productions, nonterminals, sys.argv[1])
parse(productions, nonterminals, sys.argv[2])

# Format header comment section of program
header_sec = '%%%'
header_sec += '\n% PRISM program for Probabilistic Context Free Grammar models.'
header_sec += '\n% The grammar is derived from the WSJ Treebank corpus.'
header_sec += '\n% ---'
header_sec += '\n% The structure of this code was taken from PRISM User\'s Manual (Version 2.2) - Section 10.2'
header_sec += '\n% Source: http://rjida.meijo-u.ac.jp/prism/download/prism22.pdf'
header_sec += '\n%%%'

# Format Declarations section of program
declarations_sec = '\n\n%%------------------------------------'
declarations_sec += '\n%%  Declarations:'
declarations_sec += '\n%%------------------------------------'

# Format values/2 PRISM rules
values_sec = '\n\n%'
values_sec += '\n% Probabilistic production rules'
values_sec += '\n%'

for p in sorted(productions):
	values_sec += '\nvalues(\'' + p + '\', ' + productions[p] + ']).'

# Format nonterminal/1 section and PRISM rules
nonterminals_sec = '\n\n%'
nonterminals_sec += '\n% Nonterminals'
nonterminals_sec += '\n%'

for nt in sorted(nonterminals):
	nonterminals_sec += '\nnonterminal(\'' + nt + '\').'

# Format Modeling section of program
model_sec = '\n\n%%------------------------------------'
model_sec += '\n%%  Modeling part:'
model_sec += '\n%%------------------------------------'
model_sec += '\n\npcfg(L) :- pcfg(\'S\', L-[]).'
model_sec += '\n\npcfg(LHS, L0-L1) :-'
model_sec += '\n    ( nonterminal(LHS) -> msw(LHS, RHS), proj(RHS, L0-L1)'
model_sec += '\n    ; L0 = [LHS|L1]'
model_sec += '\n    ).'
model_sec += '\n\nproj([], L-L).'
model_sec += '\nproj([X|Xs], L0-L1) :- pcfg(X, L0-L2), proj(Xs, L2-L1).'

# Write to PRISM file
f = open(sys.argv[3], 'w+')
f.write(header_sec + declarations_sec + values_sec + nonterminals_sec + model_sec)