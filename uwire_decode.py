#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  uwire_decode.py  Python 3
#
#  Copyright 2018 Jason 
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
################ DESCRIPTION #############################
# This script takes the data.ols file from the logic sniffer
# and converts the raw signals of the microwire to packets.
# NOTE:
# Not everything is covered yet and the script is currently
# a work in progress. If your main desire is to see what is
# read by a microcontroller, this will work.
#
labels = []

print("Starting Microwire Deocde Script.")
def READ():
    # Read something
    # Bits 110  A9-A0
    pass

def WRITE():
    # Write something
    # Bits 101  A9-A0
    pass

def ERASE():
    # Erase something
    # Bits 111  A9-A0
    pass

def WRAL():
    # Write all
    # Bits 100  + 01
    pass

def ERAL():
    # Erase all
    # Bits 100  + 10
    pass

def EWEN():
    # Write enable
    # Bits 100  + 11
    pass

def EWDS():
    # Write disable
    # Bits 100  + 00
    pass


# Import labels from the channel.labels file.
fh = open('channel.labels')
print ("Channels Found")
print ("==============")
label_num = 0
for line in fh:		# Print channel names and generate list of channels
    channel = line.strip()
    print ("(" + str(label_num) + ") " + channel)
    label_num += 1
    labels.append(channel)
fh.close()
print ("==============")


# Create the "Labels to Channels" dictionary automatically or request user help.
temp_dict = {'CS':'0', 'SK':'1', 'DI':'2', 'DO':'3'}    # default dict values
Labels_to_Channels = {}
print ('\nTrying to match CS, SK, DI, & DO labels for you. If I cannot match,')
print ('use the list above to match the labels to channels')
for label in temp_dict.keys():  # Try to match labels or request help.
    try:
        Labels_to_Channels[label] = labels.index(label) #labels[selection]
    except:
        selection = int(input ("Select which channel is " + label +"? "))
        Labels_to_Channels[label] = selection
print (Labels_to_Channels)


# Open the .ols file and save the raw packets to a txt file.
# This turns our stream of data from the Logic Sniffer into manageable
# chunks to be passed to the next step.
fin  = open('data.ols')
fout = open('1_raw_packets.txt', 'w')
count = 0
repeat = False
clk_val = "LOW"
old_line = "00000000@0"    
DI_chunk = ''
DO_chunk = ''

for line in fin:    # Turn Logic Analyzer traces into binary packets
    if line.startswith(';'):    # Ignore comments
        continue
    hex_val = line.split('@')                       # 000001011 @ 0
    hex_val = bin(int(hex_val[0], 16))[2:].zfill(4) # 1011
    CS = hex_val[3-Labels_to_Channels['CS']]
    SK = hex_val[3-Labels_to_Channels['SK']]
    DI = hex_val[3-Labels_to_Channels['DI']]
    DO = hex_val[3-Labels_to_Channels['DO']]

    if CS == '1':   # CS is high and data 
        if clk_val == "HIGH" and SK == '0' : # Change from high to low
            clk_val = "LOW"
            continue
            #fout.write (line)
        elif clk_val == "LOW" and SK == '1': # Change from low to high.
            clk_val = "HIGH"
            DI_chunk = DI_chunk + DI
            DO_chunk = DO_chunk + DO
            #exit()
    
        #old_line = line
        #print (hex_val)
    else:
        if repeat == False and DI_chunk != '':
            repeat = True
            #print ('DI_chunk = '+DI_chunk)
            #print ('DO_chunk = '+DO_chunk)
            fout.write('DI = ' + DI_chunk + '\n')
            fout.write('DO = ' + DO_chunk + '\n')
            DI_chunk = ''
            DO_chunk = ''
            #print('CS LOW')
            fout.write('CS LOW \n')
        else:
            repeat = False
            continue
fin.close()
fout.close()

# Open the raw packets, determine the opcode, address and data.
# Store the results.
fin  = open('1_raw_packets.txt')
fout = open('2_activity.txt', 'w')
abort = False
action = ''
dout = ''
count = 0
for line in fin:    # Find opcode, addr, data and write it to file.
    line = line.rstrip()
    if line.startswith('CS'):   # Ignore CS LOW
        abort = False
        continue

    elif line.startswith('DI'):
        if line[5:8] == '100':   # EWDS, WRAL, ERAL, EWEN
            abort = True
            if line[9:11] == '00':    # Erase/Write Disable
                fout.write('EWDS: Write Disabled \n')
            elif line[9:11] == '01':  # Write All
                print ('Write All')
            elif line[9:11] == '10':  # Erase All
                print ('Erase All')
            elif line[9:11] == '11':  # Erase/Write Enable
                fout.write('EWEN: Write Enabled \n')
            else:
                print ('OpCode: ERROR')
        elif line[5:8] == '110': # READ
            action = 'Read Addr: 0x' + hex(int(line[8:18], 2))[2:].zfill(3)
        elif line[5:8] == '101': # WRITE
            print ('OpCode: WRITE')
            abort = True
        elif line[5:8] == '110': # ERASE
            print ('OpCode: ERASE')
            abort = True
            

    elif line.startswith('DO') and abort == False:
        dout = '  DATA: 0x' + hex(int(line[18:34], 2))[2:].zfill(4)
        fout.write('\n' + action + dout)
    else:
        continue
fin.close()
fout.close()


# Convert the read activity into a hex output file. Check to make sure 
# locations don't get wrote to twice. Example output below. Need to use
# line.upper to make hex values uppercase.
#
# ADDR    00   01   02   03   04   05   06   07
# ADDR    08   09   0A   0B   0C   0D   0E   0F
# 0001  0000 0066 00CC 0188 1800 B000 6000 6916
# 0008  D03C A419 003B 0077 006C 018F 033E 077C
#
# If the addr is not 

fin  = open('2_activity.txt')
fout = open('3_hex_output.txt', 'w')
count = 0
row = ''
# Write header lines
fout.write('ADDR    00   01   02   03   04   05   06   07\n')
fout.write('ADDR    08   09   0A   0B   0C   0D   0E   0F\n')

for line in fin:
    if not line.startswith('Read'): # Ignore everything except 'Read'
        continue
    addr = int(line[11:16], 16)
    data = line[26:30].upper()
    if count = 0:
        # attache the front part
        row = '0x'+hex(count)[2:].zfill(4)+' '
    if (addr%8) > count: # Pad the empty areas with '0000'
        padding = (addr%8) - count
        row = row + ' 0000'*count
        count = addr
    row = ' '+data
    print (addr)    
    #print (line.upper())


print ("Script complete.")
exit()



while True:
    clk_ch = int(input ("Choose the CLK channel:"))
    if 0 <= clk_ch <= len(labels):
        bit_position = (len(labels) - 1) - clk_ch # flip the order for channel
        break
    else: continue

# Make sure CS is high, if not go back to top.

# If SK is high, sample DI and make sure it's a 1. If not, go back to start.

#
