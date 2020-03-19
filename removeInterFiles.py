# Deletes files


import os

def rmIntFiles(pth, filenames, checkStr):

    for dx in filenames:

        if checkStr in dx:

            os.remove(pth + dx)

        else:
            print("Tried to remove " + checkStr + "file" + "but file name is " + dx)
