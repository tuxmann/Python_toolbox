import glob
from shutil import copyfile

print('Getting the list of files\n')
all_files = glob.glob('./*.*')

print('Copying the files into Home directory.\n')
for file in all_files:
	dest_file = file.strip('.')
	copyfile(file, '/home/pi'+dest_file)

print('Finished!')
