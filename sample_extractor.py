####
# Program extracts original sentences from corpus using
# .tagged input files and writes in sentences in PRISM
# format for learning.
# ---
# COMMAND LINE ARGUMENTS:
# sys.argv[1] := .tagged file path
# sys.argv[2] := PRISM program output file path
#
# Example Usage: 
# python3 sample_extractor.py "Parses/wsj0.tagged" "sentences.dat"
####
import sys

###
# Function parses sentences from .tagged file
###
def parse(samples, path):

	with open(path) as f:
		sentences = f.read().split('\n')

	for sentence in sentences[:-1]:

		# PRISM pcfg/1 example format
		sample = "pcfg(["

		# Remove POS annotation from each word
		for word in sentence.split(' ')[:-1]:
			cleaned = word.split('/')[1][1:-1].replace("'", "\\'")
			sample += "'" + cleaned + "'" + ', '

		sample = sample[:-2]  # Remove extra ', '
		sample += "])."
		samples.append(sample)

###
# Main
###
samples = []
parse(samples, sys.argv[1])

# Write to PRISM data file
f = open(sys.argv[2], 'w+')

for sample in samples:
	f.write(sample + '\n')