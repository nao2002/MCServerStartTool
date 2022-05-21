import os
from tkinter import *
from tkinter import filedialog
import searchJava

def openFiledialog(defaultDir, currentPath):
    print("openFile")
    fTyp = [("jar File", ".jar")]
    iFile = os.path.abspath(os.path.dirname(__file__))
    if not defaultDir == "":
        iFile = defaultDir
    iFilePath = filedialog.askopenfilename(filetype = fTyp, initialdir = iFile)
    if iFilePath == "":
        iFilePath = currentPath
    return iFilePath

def openDirdialog(defaultDir):
    print("openDir")
    iDir = os.path.abspath(os.path.dirname(__file__))
    if not defaultDir == "":
        iDir = defaultDir
    iDirPath = filedialog.askdirectory(initialdir = iDir)
    if iDirPath == "":
        iDirPath = defaultDir
    return iDirPath

def selectCustomJava(defaultDir):
    print("selectJava")
    fTyp = [("java file", "java.exe")]
    iFile = os.path.abspath(os.path.dirname(__file__))
    if not defaultDir == "":
        iFile = defaultDir
    iFilePath = filedialog.askopenfilename(filetype = fTyp, initialdir = iFile)
    if iFilePath == "":
        return "error"
    searchJava.change_java(iFilePath)
    return "changed"