#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  run_getkasp.py
#  
#  Copyright 2017 Junli Zhang <zhjl86@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

# Just to run all the steps at once for designing KASP primers
# Need to use in MacPro

# change the reference location accordingly.

# example: run_getkasp.py for_polymarker.csv 200 1 1 63 25 0 ~/blast/db/161010_Chinese_Spring_v1.0_pseudomolecules.fasta

#########################
from glob import glob


def main(args):
	polymarker_input = args[1] # SNP input file, same as polymarker input
	price = args[2] # maximum restriction enzyme, e.g. 200 ($200/1000U)
	caps = int(args[3]) # whether to design CAPS primer, 1 is yes, 0 is no
	kasp = int(args[4]) # whether to design KASP primer, 1 is yes, 0 is no
	max_Tm = args[5] # max primer Tm, e.g. 63
	max_size = args[6] # max primer size, e.g. 25
	reference = args[7] # a blastable reference sequence file
	#pick_anyway = args[7] # pick primer anyway even if it violates specific constrains
	#reference = args[8] # a blastable reference sequence file
	pick_anyway = "0" # pick primer anyway even if it violates specific constrains
	
	script_path = os.path.dirname(os.path.realpath(__file__)) + "/bin/" # scripts folder


	# step 1:
	cmd1 = script_path + "parse_polymarker_input.py " + polymarker_input
	print("Step 1: Parse polymarker input command:\n", cmd1)
	call(cmd1, shell=True)
	
	#step 2: blast
	cmd2 = 'blastn -task blastn -db ' + reference + ' -query for_blast.fa -outfmt "6 std qseq sseq slen" -word_size 11 -num_threads 3 -out blast_out.txt'
	print("Step 2: Blast command:\n", cmd2)
	call(cmd2, shell=True)
	
	# Step 3: parse the blast output file and output the homelog contigs and flanking ranges
	cmd3 = script_path + "getflanking.py " + polymarker_input + " blast_out.txt temp_range.txt "
	print("Step 3: Get the flanking range command:\n", cmd3)
	call(cmd3, shell=True)
	
	# step 4: split file for each marker
	# gawk '{ print $2,$3,$4 > "temp_marker_"$1".txt" }' temp_range.txt
	cmd4 = "gawk  '{ print $2,$3,$4 > \"temp_marker_\"$1\".txt\" }' temp_range.txt"
	print("Step 4: Flanking range for each marker command:\n", cmd4)
	filesize = os.path.getsize("temp_range.txt")
	if filesize == 0: # no good SNPs
		cmd0 = 'echo All the SNPs are bad, possibly too many hits. Please check the stdout. | tee Potential_CAPS_primers.tsv Potential_KASP_primers.tsv > All_alignment_raw.fa'
		call(cmd0, shell=True)
		sys.exit()
	else:
		call(cmd4, shell=True)
	
	# step 5: get flanking sequences for each file
	# find . -iname "temp_marker*" | xargs -n1 basename | xargs -I {} sh -c 'blastdbcmd -entry_batch {} -db  reference  > flanking_{}.fa'
	#cmd5 = "find . -iname \"temp_marker*\" | xargs -n1 basename | xargs -I {} sh -c 'blastdbcmd -entry_batch {} -db " + reference + " > flanking_{}.fa'"
	cmd5="for i in temp_marker*; do blastdbcmd -entry_batch $i -db " + reference + " > flanking_$i.fa; done"
	print("Step 5: Get flanking sequences for each marker command:\n", cmd5)
	call(cmd5, shell=True)
	
	# step 6: get kasp
	if kasp:
		cmd6 = script_path + "getkasp3.py " + max_Tm + " " + max_size + " " + pick_anyway # add blast option
		print("Step 6: Get KASP primers for each marker command:\n", cmd6)
		call(cmd6, shell=True)

	# step 7: get CAPS markers
	if caps:
		cmd9 = script_path + "getCAPS.py " + price + " " + max_Tm + " " + max_size + " " + pick_anyway # add blast option and price
		print("Step 9: Get CAPS and dCAPS primers for each marker command:\n", cmd9)
		call(cmd9, shell=True)
	
	# step 8: concatenate output files
	caps_files = glob("CAPS_output/selected_CAPS_primers*")
	kasp_files = glob("KASP_output/selected_KASP_primers*")
	print("all output files are: ", caps_files)
	cmd10 = "cat CAPS_output/selected_CAPS_primers* > Potential_CAPS_primers.tsv"
	cmd11 = "cat KASP_output/selected_KASP_primers* > Potential_KASP_primers.tsv"
	cmd12 = "cat alignment_raw_* > All_alignment_raw.fa"
	print("Concatenate all output files to single files\n", cmd10, "\n", cmd11, "\n", cmd12)
	if caps:
		call(cmd10, shell=True)
	if kasp:
		call(cmd11, shell=True)
	#call(cmd12, shell=True)
	if caps or kasp:
		toglob = "alignment_raw_*"
		alignment_files = glob("alignment_raw_*")
		with open("All_alignment_raw.fa", "w") as outfile:
			for f in alignment_files:
				with open(f) as infile:
					outfile.write(f + "\n")
					outfile.write(infile.read())
					outfile.write("\n\n")
		outfile.close()
	else:
		toglob = "flanking_*"
	# output alignment file if either CAPS or KASP markers were designed
	# else output raw flanking files
	alignment_files = glob(toglob)
	with open("All_alignment_raw.fa", "w") as outfile:
		for f in alignment_files:
			with open(f) as infile:
				outfile.write(f + "\n")
				outfile.write(infile.read())
				outfile.write("\n\n")
	outfile.close()
	print("\n\n\n KASP primers have been designed successfully!\n Check files beginning with 'select_primer' and CAPS_output.txt")
	return 0

if __name__ == '__main__':
	import sys, os
	from subprocess import call
	sys.exit(main(sys.argv))
