import json
import subprocess
import os
import re
import psutil
import time
import searchJava

#サーバー実行
def startServer(saved_content):
    returnText = ""
    if saved_content["path"] != "":
        json_open = open("data/java_path.json",'r',encoding="utf-8_sig")
        java_paths = json.load(json_open)
        if not "17" in java_paths and not "18" in java_paths:
            search_path()
            java_paths = json.load(json_open)
        for v in ["18","17","16","15","14","13","12","11","10","9","8"]:
            if v in java_paths:
                returnText = check_bit(java_paths[v]["path"],java_paths[v]["bit"], saved_content)
                return returnText
        # if saved_content["mcVersion"] == "1.12.x-1.16.x" or saved_content["mcVersion"] == "1.11.x以前":
        #     if "8" in java_paths:
        #         returnText = check_bit(java_paths["8"]["path"],java_paths["8"]["bit"], saved_content)
        #     else:
        #         for v in java_paths:
        #             if v in ["8","9","10","11","12","13","14","15"]:
        #                 returnText = check_bit(java_paths[v]["path"],java_paths[v]["bit"],saved_content)
        #         if returnText == "":
        #             returnText = search_path("8", saved_content)
        # elif saved_content["mcVersion"] == "1.17.x":
        #     if "16" in java_paths:
        #         returnText = check_bit(java_paths["16"]["path"],java_paths["16"]["bit"], saved_content)
        #     elif "17" in java_paths:
        #         returnText = check_bit(java_paths["17"]["path"],java_paths["17"]["bit"], saved_content)
        #     elif "18" in java_paths:
        #         returnText = check_bit(java_paths["17"]["path"],java_paths["17"]["bit"], saved_content)
        #     else:
        #         returnText = search_path("16", saved_content)
        # elif saved_content["mcVersion"] == "1.18.x以降":
        #     if "17" in java_paths:
        #         returnText = check_bit(java_paths["17"]["path"],java_paths["17"]["bit"], saved_content)
        #     elif "18" in java_paths:
        #         returnText = check_bit(java_paths["17"]["path"],java_paths["17"]["bit"], saved_content)
        #     else:
        #         returnText = search_path("17", saved_content)
    else:
        print("error - path未設定")
        returnText = "サーバーを指定してください"
    return returnText

def search_path():
    paths = searchJava.search_path()
    json_open = open("data/java_path.json",'r',encoding="utf-8_sig")
    java_paths = json.load(json_open)
    java_paths = searchJava.compound_javaLists(java_paths,paths)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    json_write = open('data/java_path.json','w',encoding="utf-8_sig")
    json.dump(java_paths, json_write, ensure_ascii=False, indent=4)

def check_bit(javaPath, bit, saved_content):
    print("cmd: " + javaPath)
    if bit == "64":
            return use_command(javaPath,saved_content)
    else:
        if int(saved_content["memory"]) > 4096:
            print("memory error : 32bit java cannot use over 4gb")
            return "メモリ割り当てエラー\n32bitJavaに4GB以上を割り当てられません"
        elif int(saved_content["memory"]) > 4 and saved_content["memoryUnit"] == "GB":
            print("memory error : 32bit java cannot use over 4gb")
            return "メモリ割り当てエラー\n32bitJavaに4GB以上を割り当てられません"
        else:
            return use_command(javaPath,saved_content)
            
def use_command(javaPath, saved_content):

    path = saved_content["path"]
    reverse = "".join(reversed(path))
    target = reverse.find("/")
    pathDir = reverse[target:]
    pathDir = "".join(reversed(pathDir))
    path = path[len(path) - target:]

    memory = str(saved_content["memory"])
    unit = "M"
    if saved_content["memoryUnit"] == "GB":
        unit = "G"
    memory = memory + unit

    version = ""
    pid = None
    if os.path.isfile(pathDir + "version.txt"):
        f = open(pathDir + 'version.txt', 'r', encoding='UTF-8')
        version = f.read()
        f.close()
    else:
        print("version.txtを作成")
        version, pid = checkServerVersion(javaPath, pathDir, path)
        print(version)
        f = open(pathDir + 'version.txt', 'w', encoding='UTF-8')
        f.write(version)
        f.close()
        while psutil.pid_exists(pid):
            print(f"process: {psutil.pid_exists(pid)}")
            time.sleep(1)
            print(f"process: {psutil.pid_exists(pid)}")


    log4jON = "18"
    if int(version) == 17:
        log4jON = "17"
    elif int(version) <= 16 and int(version) >= 12:
        log4jON = "16"
    elif int(version) <= 11:
        log4jON = "11"
    if saved_content["log4j2"] == 0:
        log4jON = "0"


    print(pathDir)

    others = ""
    if saved_content["gui"] == "0":
        others = others + " nogui"

    command = ['data\openStarter.bat',f"{javaPath}",f"{pathDir}",f"{path}",memory,log4jON,f"{others}"]
    cmdRun = subprocess.run(command, stdout = subprocess.PIPE)
    print(cmdRun)
    if cmdRun.returncode == 0:
        return ""
    else:
        return "サーバーの実行中にエラーが発生しました\nサーバーファイルを指定し直してみてください"


def checkServerVersion(javaPath, pathDir, path):
    version = ""
    pid = ""

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    proc = subprocess.Popen(["data\checkServerVer.bat", f"{javaPath}",f"{pathDir}",f"{path}"], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    while True:
        line = proc.stdout.readline()
        if line:
            print(str(line))
            if re.match(".*\.[0-9]+\.[0-9]+", str(line)):
                version = re.match(".*\.[0-9]+\.[0-9]+", str(line)).group()

                reverse = "".join(reversed(str(version)))
                target = reverse.find(".")
                removed = reverse[target+1:]
                target = removed.find(".")
                removed = removed[:target]
                version = "".join(reversed(removed))

                pid = proc.pid

                proc.stdin.write(b'stop')
                proc.terminate()
                break
                
        if not line and proc.poll() is not None:
            break

    return str(version), pid