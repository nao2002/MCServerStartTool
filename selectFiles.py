import os
from tkinter import *
from tkinter import filedialog
from findDataFile import find_data_file as finddata
import searchJava

def openFiledialog(defaultDir, currentPath):
    print("openFile")
    fTyp = [("jar File", ".jar")]
    iFile = os.path.abspath(finddata())
    if not defaultDir == "":
        iFile = defaultDir
    iFilePath = filedialog.askopenfilename(filetype = fTyp, initialdir = iFile)
    if iFilePath == "":
        iFilePath = currentPath
    return iFilePath

def openDirdialog(defaultDir):
    print("openDir")
    iDir = os.path.abspath(finddata())
    if not defaultDir == "":
        iDir = defaultDir
    iDirPath = filedialog.askdirectory(initialdir = iDir)
    if iDirPath == "":
        iDirPath = defaultDir
    return iDirPath

def selectCustomJava(defaultDir):
    print("selectJava")
    fTyp = [("java file", "java.exe")]
    iFile = os.path.abspath(finddata())
    if not defaultDir == "":
        iFile = defaultDir
    iFilePath = filedialog.askopenfilename(filetype = fTyp, initialdir = iFile)
    if iFilePath == "":
        return "error"
    ret = searchJava.search_path(way=str(iFilePath))
    return ret