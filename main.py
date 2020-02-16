import os
import time

class FileExample:      # main class, it creates an object with all the parameters of the file you want to find
    def __init__(this):
        this.path = None
        this.name = None
        this.dateTime = None
        this.dateTime_unit = None
        this.size = None
        this.size_unit = None

    def choosePath(this):       # adds the path of the location you want to scan - required
        while True:
            path = input("Enter the path of the scanned directory: ") # for example "C:/Users"
            if os.path.exists(path):
                this.path = path
                break
            print("Path doesn't exist!")

    def changeName(this):       # adds the full name (with suffix) of the wanted file - optional
        while True:
            fileName = input("Enter a name of the file: ").strip() # for example "Hello_world.txt"
            if fileName:    #if EMPTYSTRING: >> False
                this.name = fileName
                break
            print("Invalid name of a file!")

    def changeDateTime(this):       # adds the date/time (last modified time) of the wanted file, you can choose between 3 formats (day, hour, minute) depending on how specifically you want to search the files - optional
        while True:
            try:
                string = input("Enter a date in one of the following formats: DD MM YYYY, DD MM YYYY HH, DD MM YYYY HH MM: ")
                seconds = time.strptime(string, "%d %m %Y")
                this.dateTime_unit = "d" #d -> day 24 h - files modified this day
                break
            except ValueError:
                try:
                    seconds = time.strptime(string, "%d %m %Y %H")
                    this.dateTime_unit = "h" #h -> hour 60 min - files modified this hour
                    break
                except ValueError:
                    try:
                        seconds = time.strptime(string, "%d %m %Y %H %M")
                        this.dateTime_unit = "m" #m -> minute 60 sec - files modified this minute
                        break
                    except ValueError:
                        print("Invalid format of a date!")
        this.dateTime = time.mktime(seconds)

    def changeSize(this):       # adds the size of the wanted file with a unit - optional
        while True:
            try:
                size_specs = input("Enter a size (integer) with a unit (B, kB, MB or GB): ").split() # for example "10 kb" (you must use the space otherwise you'll receive "Invalid input!" message)
                this.size = int(size_specs[0])
                if size_specs[1].upper() == "B":
                    this.size_unit = "B"
                    break
                elif size_specs[1].upper() == "kB".upper():
                    this.size *= 1024
                    this.size_unit = "kB"
                    break
                elif size_specs[1].upper() == "MB":
                    this.size *= (1024 ** 2)
                    this.size_unit = "MB"
                    break
                elif size_specs[1].upper() == "GB":
                    this.size *= (1024 ** 3)
                    this.size_unit = "GB"
                    break
                print("Invalid unit of size!")
            except ValueError:
                print("Invalid input!")
            except IndexError:
                print("Invalid input!")

def getDirectory(path):     # scans the given location and puts all the files and directories as DirEntry (https://docs.python.org/3/library/os.html#os.DirEntry) objects in a list
    directoryList = []
    try:
        with os.scandir(path) as directory:
            for object in directory:
                directoryList.append(object)
    except PermissionError:     # for some reason, you don't have permission to scan through certain directories
        with open("data.txt", "a", encoding="utf-8") as f:
            line = f'{path} - Access is denied'     # but you can at least see the paths of these directories
            print(line)
            f.write(line + "\n")
    return directoryList

def switch(i, object):      # substitution of the switch statement (which is not included in Python), helps to choose which parameter you want to change
    options = {1:object.changeName, 2:object.changeDateTime, 3:object.changeSize}
    f = options.get(i, lambda: print("Invalid choice!"))
    return f()  # returns a function of the created fileExample object

def setup(object):      # this is a setup function for defining the parameters of the fileExample object
    object.choosePath()
    while True:
        try:
            option = input("Define parameters (at least one) of your file. Choose: (1)name (2)date/time (3)size. Press ENTER to start scanning. ")
            switch(int(option), object)
        except ValueError:
            if option == "" and object.name != None or object.dateTime != None or object.size != None:
                break
            elif option == "":      # defining at least one of the parameters (name, date/time, size) is required
                print("You have to define at least one parameter in order to start scanning!")
            else:
                print("Invalid input!")

def checkParameters(file, fileExample):                                 # this function compares the given parameters of the fileExample object with a real file from the scanned location
    if fileExample.name != None and file.name.lower() != fileExample.name.lower():  # if the Name is not defined or it matches the Name of the real file, function continues
        return False                                                                # if the Name is defined, but doesn't match the Name of the real file, function returns False

    if fileExample.dateTime != None:
        time_interval = (24 * 3600) - 1 #dateTime_unit == "d" - day is default (24 h)
        if fileExample.dateTime_unit == "h": #hour 60 min
            time_interval = 3600 - 1
        elif fileExample.dateTime_unit == "m": #minute 60 sec
            time_interval = 60 - 1
        if file.stat().st_mtime < fileExample.dateTime or file.stat().st_mtime > fileExample.dateTime + time_interval:
            return False                        # if the date/time is defined, but is not within the same day/hour/minute (depending on the chosen time format), function returns False

    if fileExample.size != None:                # if the size of the real file is within 0.9 to 1.1 amount of the chosen size, it's considered as the same size
        if file.stat().st_size < fileExample.size * 0.9 or file.stat().st_size > fileExample.size * 1.1: # rounding: 0.9x -> 1.1x = 1x
            return False

    return True     # if the defined parameters match, function returns True

def scan(object, path, duplicate_files=[], fileFoundInThisDir=False):       # this function goes through a list of files and directories given from the getDirectory function
    directory = getDirectory(path)
    for element in directory:
        if element.is_dir():        # if the element in the list is a directory, function recursively goes into that directory and scans files/directories there
            path = element.path
            scan(object,path)
        else:
            if object.name != None:     # you can't have 2 files with the same name in the same directory, so if you search by the name and one file had already been found in that directory,
                if fileFoundInThisDir:  # there can't be another file you're looking for - so it just skips the checkParameters
                    continue
            if checkParameters(element, object):        # if the element in the list is a file, function checkParameters checks if it matches your wanted file
                duplicate_files.append(element)         # if it does match, it's added into a list of duplicate files
                fileFoundInThisDir = True
    return duplicate_files

def printFiles(listOfFiles):        # prints the duplicate files with additional information
    count = 1
    with open("data.txt", "a", encoding="utf-8") as f:      # the information can be so long that they can't be displayed in the console, that's why everything is saved into a text file
        for entry in listOfFiles:
            firstLine = f'{count}) {entry.name}'
            secondLine = f'    Path: {entry.path}'
            size = (entry.stat().st_size / 1024)
            thirdLine = f'        Last Modified: {time.ctime(entry.stat().st_mtime)}    Size: {size} kB'
            print(firstLine, secondLine, thirdLine, sep="\n")
            f.writelines([firstLine + "\n", secondLine + "\n", thirdLine + "\n"])
            count += 1

def main():     # main function
    open("data.txt", "w").close() # open+close to erase the text
    fileExample = FileExample()
    setup(fileExample)
    duplicate_files = scan(fileExample, fileExample.path)
    printFiles(duplicate_files)

if __name__ == "__main__":
    main()