# Countdown.py is a simple script that becomes really useful when you
# want to create long strings of descending numbers. This becomes very
# useful when numbers are greater than 50. See example below.
#
# EXAMPLE:
# "31,30,29,28,27,26,25,24,23,22,21,20,19,18,17,16,\
#  15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0"

start = int(input('Enter the starting number: '))
end   = int(input('Enter the  ending  number: '))
ROWMAX= int(input('Enter the maximum number of numbers per row: ') or '16') 
print()
rowmax_count = ROWMAX
row   = '"'

while  start >= end:
    row = row + str(start) + ','
    start = start - 1
    rowmax_count = rowmax_count - 1
    if start == end:
        row = row + '"'
        break
    if rowmax_count < 1:
        rowmax_count = ROWMAX
        print (row + '\\')
        row = ''
print (row)

