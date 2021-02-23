#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  RPi-Controller.py
#  
#  Copyright 2021 E199416 <E199416@AZ75LTJDCS3M2>
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
#  /home/pi/RPi-Controller.py
#######################################################################
### Run "pinout" in the terminal to see what GPIO is designated to  ###
### each pin. The TDU can be commanded to display one of eight      ###
### colors (white, black, primary & secondary colors) and a test    ###
### pattern. There will be a toggle to cycle the brightness. There  ###
### will also be a toggle for displaying the test pattern.          ###
###                                                                 ###
### [BIT7] [BIT6] [BIT5] [TEST]   [BRT_CYC] [RED] [GREEN] [BLUE]    ###
#######################################################################

''' Setup INSTRUCTIONS
ENTER THE FOLLOWING COMMANDS:
sudo su
crontab -e

Inside the crontab file, go to the bottom and paste the following:
@reboot pigpiod
@reboot python /home/pi/RPi-Controller.py

Save the file and reboot
'''
import os, pigpio, serial
from time import sleep

# Variables
OldInputlist = [0,0,0,0, 0,0,0,0]
pwm_range = 25
RCpin = 7
ShtDn = 17
RGB   = [0,1,4]	# Red, Green, Blue wired to 3, 5, 7 resp. HI is off and LOW is on.
Input = [23,22,24,10,  25,9,8,11]

# Initialize hardware
pi = pigpio.pi()
for i in RGB:			# Set up LEDs so that they remain off.
	pi.set_mode(i, pigpio.OUTPUT)
	pi.write(i,1)
	# Set PWM frequency and range
	pi.set_PWM_frequency(i,1000)
	pi.set_PWM_range(i,pwm_range)
for i in Input:			# Set up Inputs for switches and pull up internally.
	pi.set_mode(i, pigpio.INPUT)
	pi.set_pull_up_down(i, pigpio.PUD_UP)
pi.set_mode(ShtDn, pigpio.INPUT)
pi.set_pull_up_down(ShtDn, pigpio.PUD_UP)
#sleep(10)

""" Is the Daughter board attached? Check_RC() determines if the 
	identifcation RC circuit is installed and working. There's a 
	44uF cap and 100k resistor installed. It takes about 640 loops
	before the logic level goes back high.

https://learn.adafruit.com/basic-resistor-sensor-reading-on-raspberry-pi?view=all
 
3V3 --|100kOhm|--.--+|{44uF}(--. 
                 |             | 
IO(7)<-----------'            GND 
"""
def Check_RC():					# Check if the daughter board exists.
	pi.set_mode(RCpin, pigpio.OUTPUT)
	pi.write(RCpin, 0)
	sleep(1)
	pi.set_mode(RCpin, pigpio.INPUT)
	
	reading = 0
	while True:					# Loop until val goes HI
		val = pi.read(RCpin)
		if val == 1:
			break
		reading += 1
		if val > 1000:			# Timeout after 1k loops
			print ("Resistor ID not found, Check if daughter board is")
			quit()
	print(reading)
	if reading < 400:			# Failure. Value less than expexted.
		child = False
		for i in range(20):		# Blink the red LED
			set_LEDs([0,1,1], 16)	# Red
			sleep(.2)
			set_LEDs([1,1,1], 16)	# Black
			sleep(.2)
		#quit()
	elif 400 < reading < 700:	# Pass. Daughter board is attached.
		for i in range(20):
			set_LEDs([1,0,1], 16)	# Green
			sleep(.1)
			set_LEDs([1,1,1], 16)	# Black
			sleep(.1)
	

def read_inputs():				# Read all eight inputs & of the switches.
	Inputval = [0,0,0,0, 0,0,0,0]
	count = 0
	for i in Input:
		Inputval[count] = pi.read(i)
		count += 1
	#print(Inputval)
	return Inputval
		

def set_LEDs(RGBval, bright):	# Set RGB LED color and the brightness.
	for i in RGB:		# Break before making new LED connections.
		pi.write(i,1)
	count = 0
	for i in RGB:		# Set new connections. 
		bit = RGBval[count]
		if bit == 1:	# Turn off LED
			pi.set_PWM_dutycycle(i,pwm_range)
		else:			# Turn on LED at defined brightness.
			pi.set_PWM_dutycycle(i,bright)
		count += 1
	SerVal = str(RGBval[0])+str(RGBval[1])+str(RGBval[2])
	set_Serial(SerVal)


def brightness_cycle():			# Get dimmer, then brighter. RGB-aware.
	level = 17
	off = pwm_range - level
	up = 0		# 0 gets dimm, 1 gets bright
	while True:
		Inputlist = read_inputs()
		RGBstate = [Inputlist[5], Inputlist[6], Inputlist[7]]
		if Inputlist[3] == 1:	# Max brightness & exit func
			ser.write('>>>>>>>> >>>>>>>> >>>>> '.encode('utf-8'))
			break
		if Inputlist[4] == 0:	# Max brightness & exit func
			ser.write('>>>>>>>> >>>>>>>> >>>>> '.encode('utf-8'))
			break
		# Crude down & up loop. I'd like a better method.
		if up == 0:	# Going down.
			if level < 1:
				up = 1
			else:
				level -= 1
				set_Serial('down')
		else:		# Going up.
			if level > 16:
				up = 0
			else:
				level += 1
				set_Serial('up')
		if RGBstate == [1,1,1]:		# Turn the LEDs off.
			ser.write('t0'.encode('utf-8'))
			for i in RGB:	# Break LED connections before making new ones.
				pi.write(i,1)
		else:						# Set LEDs & brightness.
			set_LEDs(RGBstate, (level+off))
			sleep(.1)


def cycle_colors():				# Cycle thru 6 colors, Doesn't do test...
	while True:					# pattern or change brightness.
		Inputlist = read_inputs()
		if Inputlist[3] == 0:
			break
		RGBstates = [[1,1,1], [0,1,1], [1,0,1],
					[1,1,0], [0,0,1], [0,1,0],
					[1,0,0], [0,0,0]]
		for i in RGBstates:
			Inputlist = read_inputs()
			if Inputlist[3] == 0:
				break
			bitlist = i
			count = 0
			for i in RGB:
				pi.write(i,bitlist[count])
				count+=1
			SerVal = str(bitlist[0])+str(bitlist[1])+str(bitlist[2])
			set_Serial(SerVal)
			sleep(1)

'''	RGB colors
111 = Black		000 = White
110 = Blue		101 = Green		011 = Red
001 = Yellow	010 = Magenta	100 = Cyan
'''
def set_Serial(val):			# Send a serial value to the LCD display.
	ser_dict = {'111':'t0', '110':'t1', '101':'t2', '100':'t3', '011':'t4', 
				'010':'t5', '001':'t6', '000':'t7', 'up':'>', 'down':'<'}
	if ser_on == True:
		ser.write((ser_dict[val]).encode('utf-8'))
	print(ser_dict[val])


def powerdn(gpio, level, tick):
	print("Shutting down the Pi!!!")
	for i in range(10):		# Blink the red LED
		set_LEDs([1,1,0], 16)	# Blue
		sleep(.3)
		set_LEDs([1,1,1], 16)	# Black
		sleep(.3)
		set_LEDs([0,1,1], 16)	# Red
		sleep(.2)
		set_LEDs([1,1,1], 16)	# Black
		sleep(.2)
		set_LEDs([1,0,1], 16)	# Green
		sleep(.1)
		set_LEDs([1,1,1], 16)	# Black
		sleep(.1)
	os.system("sudo halt")


try:	# Is the USB serial connected?
	ser = serial.Serial("/dev/ttyUSB0", 19200)
	ser.write('\n\r'.encode('utf-8'))
	ser_on = True
	print("Serial Cable connected. Yay!!!")
	for i in range(5):		# Blink the magenta LED
		set_LEDs([0,1,0], 16)
		sleep(.1)
		set_LEDs([1,1,1], 16)	# Black
		sleep(.1)
except:	# Nope, it's not connected.
	print("Serial cable not connected.")
	ser_on = False
	for i in range(5):		# Blink the blue LED
		pi.write(RGB[2],0)
		sleep(.1)
		pi.write(RGB[2],1)
		sleep(.1)

# Main program loop.
# Check_RC() Cannot consistently get this test to pass.
call = pi.callback(ShtDn, pigpio.FALLING_EDGE, powerdn)
while True:
	Inputlist = read_inputs()
	RGBstate = [Inputlist[5], Inputlist[6], Inputlist[7]]
	if Inputlist[2] == 1:	# Test pattern
		while True:
			Inputlist = read_inputs()
			RGBstate = [Inputlist[5], Inputlist[6], Inputlist[7]]
			if Inputlist[2] == 0:
				set_LEDs(RGBstate, 16)
				break
			ser.write('t8'.encode('utf-8'))
			sleep(.1)
	if Inputlist[3] == 1:	# Cycle Colors
		cycle_colors()
	if Inputlist[4] == 1:	# Brightness.
		brightness_cycle()
	if Inputlist != OldInputlist: # This eliminates flickering.
		set_LEDs(RGBstate, 16)
		OldInputlist = Inputlist
	else:	# Do nothing.
		pass
	sleep(.1)
