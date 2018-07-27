# Ask the user for the file name that they want to look at and then
# ask for the string that they want to look at

print ("The script opens a file and searches through the file for the string")
print ("you're looking for. Each line that contains the string is then displayed")
print ("on the screen.\n")

while True:
    
    fin = input("Enter the filename that you want to search: ")
    if fin == 'q' or fin == 'Q':
        print ("Quitting!")
        exit()
    if fin == '':
        continue #exit()
    else:
        try:
            fin = open(fin)
            #break
        except FileNotFoundError:
            print ("\nError: FILE NOT FOUND \n")
            continue
    
    while True:
        str_in_file = input("Enter the word or phrase you want to find: ")
        if str_in_file == '':
            continue
        print ("\n\n")
        break
    
    for line in fin:
        if str_in_file in line:
            print (line.strip())
    
    print ("\n\nFinished looking through the file. Press Q to quit or enter a new filename")

