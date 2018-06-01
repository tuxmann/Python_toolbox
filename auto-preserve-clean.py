#! python3
# -*- coding: utf-8 -*-
#
#  auto-preserve-clean.py
#  
#  Copyright 2018 Jason Mann <e199416@AZ75DTGG29382>
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
########################################################################
########################################################################
####                        Script description                      ####
########################################################################
########################################################################
#
#   This Python3 script is meant to be ran on a Windows PC only.
#   No special libraries are requiered. This script automating the 
#   process of saving binary images from avionics modules using 
#   additional command line software.
#
#    PART ONE:
# X0. Use the time feature to record the start and stop time of the 
#     script to quantify how much time is saved.
# X1. Ping the list of IP address available for the module.
# X2. FTP to first IP addr that responds. Get Part# & Run the "dir" 
#     command to know if the module is 486 or PPC.
# X3. Use info about the module to get Maintenance & Flight Code contents
# X4. Decide which version of software is needed to save binaries.
# X5. Dump binary images. 2 images for 486 and 5 for PPC.
# X5a.Ask the user if side B needs to be retrieved. Rename data as Side_A
#
########################################################################
########################################################################

import os, socket, shutil, subprocess, sys, time
from ftplib import FTP
from     io import StringIO

# Constants
time_start = time.time()
SLOTS = 8
DIR_PPC = "d:\PPC_DL_SW"
DIR_486 = "d:\486_DL_SW"
DIR_RETURNS = "d:\\3P1C_Cust_Returns"

SWITCH_486 = ["DUMPFILE1", "DUMPFILE2"]
SWITCH_PPC = ["DUMPFILE1", "DUMPFILE2", "DUMPFILE3", "DUMPFILE4", "DUMPFILE5"]

# Variables
year   = str(time.localtime().tm_year) + "_"
month  = str(time.localtime().tm_mon).zfill(2) + "_"
date   = str(time.localtime().tm_mday).zfill(2) + "_"
hour   = str(time.localtime().tm_hour).zfill(2) + "_"
minute = str(time.localtime().tm_min).zfill(2)
yr_mon_date = year + month + date[:-1]

size = '1'  # Assume that the module is single

# Check slots until you find the first client
# Returns the first found IP address of the client
def ping_slots():   
    Client_IP = 16  # Local variable and first pingable slot
    for i in range(SLOTS):
        print ('trying 192.168.1.' + str(Client_IP))
        response = subprocess.call("ping -n 1 -w 100 192.168.1." + \
                   str(Client_IP), stdout=subprocess.DEVNULL)
        if response == 0:   # Rec'd a response. End of function.
            print ("Found a client at 192.168.1." + str(Client_IP) + '\n')
            return ("192.168.1." + str(Client_IP))
        else:               # No response
            Client_IP += 1
    # No modules were found.
    print ('No client has been found')
    print ('Please troubleshoot manually.')
    question = input('(Q)uit or ENTER to retry: ')
    if question == 'Q' or question == 'q':  # User wants to quit
        exit()
    else:                                   # User wants to try again.
        ping_slots()

# Dump the maintenance Maintenance & Flight Code contents into a folder
# made just for this module.
# Returns part_num, arch, module_dir
def dump_nvm(IP, SN):
    ftp = FTP(IP)
    ftp_welcome = (ftp.login(user='', passwd='')) # Returns a str
    ftp_welcome = ftp_welcome.split()
    for line in ftp_welcome:    # Find the part number of the module
        if not line.startswith('hw-desc'): continue
        pieces = line.split(':')
        part_num = pieces[1]
        pn_end = part_num.find('>')
        part_num = (part_num[1:pn_end])
    
    # We know the part# & ser#. Try to create the full path. Keep going
    # back one directory at a time until the full path is created.
    module_dir = DIR_RETURNS + '\\' + part_num + '\\' + SN + '\\' + yr_mon_date
    try:                        # Make D:\3P1C_Cust_Returns\Part_Num\Ser_Num\Yr_mon_date
        os.mkdir(module_dir)
    except FileNotFoundError:   # Can't find SN folder and maybe other folders too.
        try:
            os.mkdir(DIR_RETURNS + '\\' + part_num + '\\' + SN)
            os.mkdir(module_dir)
        except FileNotFoundError:   # Can't find part_num folder
            try:
                os.mkdir(DIR_RETURNS + '\\' + part_num)
                os.mkdir(DIR_RETURNS + '\\' + part_num + '\\' + SN)
                os.mkdir(module_dir)
            except FileNotFoundError:   # Can't find 3P1C_Cust_Returns folder
                os.mkdir(DIR_RETURNS)
                os.mkdir(DIR_RETURNS + '\\' + part_num)
                os.mkdir(DIR_RETURNS + '\\' + part_num + '\\' + SN)
                os.mkdir(module_dir)
    except FileExistsError:     # Folder found. What next?
        #print ("Found folder")
        found_folder = True
    os.chdir(module_dir)        # Change DIR so that file will fall in automatically.

    # This sends the output of 'dir' command to the variable result_string.
    # We look at the result_string to know if we see a PPC or 486.
    old_stdout = sys.stdout
    result = StringIO()
    sys.stdout = result
    ftp_dir = ftp.dir()
    sys.stdout = old_stdout
    result_string = result.getvalue()
    result_string = result_string.split()
    
    for line in result_string:  # Find the architecture of the module
        if not (line.endswith('.so') or line.endswith('.dll')): continue
        if line.endswith('.so'):    # PPC
            arch = 'PPC'
            break
        else:                       # 486
            arch = '486'
            break
    print ("This client's part number is " + part_num  + ' and it is a ' + arch + '\n')
    print ("Getting file, please wait...")
    
    if arch == 'PPC':   # PPC file
        ftp.retrbinary('RETR /rcs/NVSRAMRO', open('NVSRAMRO', 'wb').write)
    else:               # 486  file
        ftp.retrbinary('RETR /rcs/EEPROM.BIN', open('EEPROM.BIN', 'wb').write)
    print ("The file from the client has been preserved")
    
    return part_num, arch, module_dir

# Dump Flash bin files. Move each file to the new module_dir folder.
def dumpflash(DIR, module_dir, IP, part_num, sw_list):
    os.chdir(DIR)
    for switch in sw_list:  # Dump each binary in the list.
        print ()
        print ("Getting " + switch[4:] + " from the module...")
        time.sleep(15)      # Used to prevent errors when running dumpsw
        file_name = part_num + "_" + switch[4:] + ".bin"
        command = "dumpsw -" + switch + " " + IP + " " + file_name
        subprocess.run(command, shell=True)
        shutil.move(DIR + '\\' + file_name, module_dir + '\\' + file_name)
    time.sleep(1)

def save_module(size, SN, IP):
    if size == '2': # Side B, rename .zip file & check if same slot or not.
        print('\nPower off test fixture. Flip module over.')
        input('Power on test fixture. Wait ten seconds. Press ENTER')
        os.rename(yr_mon_date+'.zip', yr_mon_date+'_side_a.zip')
        response = subprocess.call("ping -n 1 -w 100 " + IP, stdout=subprocess.DEVNULL)
        if response != 0:   # Module changed slot.
            IP = ping_slots()
    
    part_num, arch, module_dir = dump_nvm(IP, SN)
    
    if arch == 'PPC':   # NextGen file Retrieval & Storage
        dumpflash(DIR_PPC, module_dir, IP, part_num, SWITCH_PPC)
    else:               # Legacy  file Retrieval & Storage
        dumpflash(DIR_486, module_dir, IP, part_num, SWITCH_486)
    
    
    # Change to the ser_num directory, zip up binary files. Delete the directory.
    os.chdir(DIR_RETURNS + '\\' + part_num + '\\' + ser_num)
    shutil.make_archive(yr_mon_date, "zip", yr_mon_date)
    shutil.rmtree(yr_mon_date)
    print ('Zipping finished. Files are stored in the directory listed below:')
    print (module_dir[:-10] + '\n') # [:-10] strips the "2018-01-25" off the string

    if size == '2': # Dual Channel actions
        os.rename(yr_mon_date+'.zip', yr_mon_date+'_side_b.zip')
    

if __name__ == '__main__':
    # Ping the slots in order to find which the 
    print ('Auto Preservation script started...\n')
    print ('The process will take up to 12 minutes per side to run...\n')
    print ('Pinging slots in search of a client')
    IP = ping_slots()

    ser_num = input("Please enter the serial number of the module: ")
    if len(ser_num) < 1: # If only ENTER is pressed, set the time as it's name.
        ser_num = 'unk_' + year + month + date + hour + minute
    
    while True: # Continue to 
        try:
            save_module(size, ser_num, IP)
            break
        except: # False positive from ping_slots function. Try again.
            print ("Pinging error, Trying again...")
            IP = ping_slots()
    
    time_total = time.time() - time_start   # Stop timer. Waiting for user input.
    
    while True: # Ask the user if the client is single or dual.
        size = input("Is this a single(1) or dual(2) channel module? ")
        if size == '1':   # Single slot, quit
            break
        elif size == '2':
            time_start = time.time()
            save_module(size, ser_num, IP)
            time_end = time.time()
        else: continue
        break
    
    
    time_total = time_total + (time_end - time_start)
    minutes = str(time_total // 60)[:-2]
    seconds = str(time_total % 60)[:2]
    print ("This script saved " + minutes + " minutes and " + seconds + " seconds.")
