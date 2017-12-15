# Script for cleaning up .ols files from the open logic sniffer program
# so that the clock sampling is better.

import math

# Have the user input the clock channel. 
while True:
	clk_bit = int(input('Which channel is the clock bit on? Choose 0-3: '))
	if clk_bit > 7 or clk_bit < 0: continue
	clk_bit = int(math.pow(2, clk_bit))		#power of 2
	break
		

fname = 'data.ols'
fhand = open(fname)
#str_data = open(fname).read()
count = 0
first_hi = True
hex_var_low = 0
for line in fhand:
	if line.startswith(';'): continue	# Ignore the lines with ';' at the beginning.
	#if count > 50: break				# For Debug purposes
	count += 1
	pieces = line.split('@')			# 000000f9@244
	hex_var = pieces[0]					# 000000f9
	hex_var = (int(hex_var[7:8], 16))	# f9 --> 249
	
	if hex_var & clk_bit and first_hi == True:	# clk_bit is HIGH
		first_hi = False
		print (bin(hex_var_low))		# Low  clk
		print (bin(hex_var))			# High clk
	elif hex_var & clk_bit == 0:				# clk_bit is LOw
		hex_var_low = hex_var
		first_hi = True
