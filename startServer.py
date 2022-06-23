import json
import subprocess
import os
import re
import psutil
import time
import searchJava
from findDataFile import find_data_file as finddata
import asyncio
from tkinter import simpledialog

#サーバー実行
def startServer(saved_content):
    os.chdir(finddata())
    returnText = ""
    if saved_content["path"] != "":
        json_open = open("data/java_path.json",'r',encoding="utf-8_sig")
        java_paths = json.load(json_open)
        json_open.close()
        if not "17" in java_paths and not "18" in java_paths:
            search_path()
            json_open = open("data/java_path.json","r",encoding="utf-8_sig")
            java_paths = json.load(json_open)
        for v in ["18","17","16","15","14","13","12","11","10","9","8"]:
            if v in java_paths:
                returnText = check_bit(java_paths[v]["path"],java_paths[v]["bit"], saved_content)
                return returnText
        return "javaが見つかりませんでした\njavaをインストールするか、詳細設定画面から検出してください\njava17以上のインストールを推奨します"
    else:
        print("error - path未設定")
        returnText = "サーバーを指定してください"
    return returnText

def search_path():
    paths = searchJava.search_path()
    os.chdir(finddata())
    json_open = open("data/java_path.json",'r',encoding="utf-8_sig")
    java_paths = json.load(json_open)
    java_paths = searchJava.compound_javaLists(java_paths,paths)
    os.chdir(finddata())
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
    error = None
    if os.path.isfile(pathDir + "version.txt"):
        f = open(pathDir + 'version.txt', 'r', encoding='UTF-8')
        version = f.read()
        f.close()
        print(version)
        if not isint(version) and not version == "Exception":
            if saved_content["vCheck"] == "1":
                version, pid, error = asyncio.run(asyncio.wait_for(checkServerVersion("data\checkServerVer.bat",[f"{javaPath}",f"{pathDir}",f"{path}"]),60))
                if error != None:
                    if error == "java_error":
                        return "サーバーの起動に失敗しました\n\n必要なバージョンのjavaが存在しない可能性が高いです\njava17以上であれば全てのバージョンを起動できるため\njava17以上のインストールを推奨しております\n\n既にインストール済みの場合は詳細設定のjava設定から検出を試してください"
                    elif error == "error":
                        return "サーバーの起動に失敗しました\n\n何らかのエラーが発生しました"
                f = open(pathDir + 'version.txt', 'w', encoding='UTF-8')
                f.write(version)
                f.close()
            else:
                version = ""
    else:
        if saved_content["vCheck"] == "1":
            print("version.txtを作成")
            version, pid, error = asyncio.run(asyncio.wait_for(checkServerVersion("data\checkServerVer.bat",[f"{javaPath}",f"{pathDir}",f"{path}"]),60))
            if error != None:
                if error == "java_error":
                    return "サーバーの起動に失敗しました\n\n必要なバージョンのjavaが存在しない可能性が高いです\njava17以上であれば全てのバージョンを起動できるため\njava17以上のインストールを推奨しております\n\n既にインストール済みの場合は詳細設定のjava設定から検出を試してください"
                elif error == "error":
                    return "サーバーの起動に失敗しました\n\n何らかのエラーが発生しました"
            print(version)
            f = open(pathDir + 'version.txt', 'w', encoding='UTF-8')
            f.write(version)
            f.close()
        else:
            version = ""

    if pid != None:
        while psutil.pid_exists(pid):
            print(f"process: {psutil.pid_exists(pid)}")
            time.sleep(1)
            print(f"process: {psutil.pid_exists(pid)}")

    if checkEULA(pathDir) == False:
        return "eula.txtに同意していないため起動できません\n規約に同意する場合\neula=false を eula=true\nに書き換え再実行してください"

    if version == "Exception" or version == "":
        version = askVersion(vCheck=saved_content["vCheck"])
        if version == "cancel":
            return "cancel"
        else:
            f = open(pathDir + "version.txt","w",encoding="UTF-8")
            f.write(str(version))
            f.close()

    log4jON = "18"
    if version == "Exception":
        log4jON = "0"
    elif int(version) == 17:
        log4jON = "17"
    elif int(version) <= 16 and int(version) >= 12:
        log4jON = "16"
    elif int(version) <= 11:
        log4jON = "11"
    if saved_content["log4j2"] == 0:
        log4jON = "0"

    others = ""
    if saved_content["gui"] == "0":
        others = others + " nogui"

    command = ['data\openStarter.bat',f"{javaPath}",f"{pathDir}",f"{path}",memory,log4jON,f"{others}",str(os.getpid())]
    cmdRun = subprocess.run(command, stdout = subprocess.PIPE)
    print(cmdRun)
    if cmdRun.returncode == 0:
        return ""
    else:
        return "サーバーの実行中にエラーが発生しました\nサーバーファイルを指定し直してみてください"

async def checkServerVersion(command, args):
    version = ""
    pid = None
    error = None

    os.chdir(finddata())
    proc = await asyncio.create_subprocess_exec(command, *args, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)

    while True:
        if proc.returncode != None:
            error = "error"
            break
            
        try:
            line =  await asyncio.wait_for(proc.stdout.readline(), 20)
        except:
            print("timeout")
            version = "Exception"
            pid = proc.pid

            await proc.communicate(b'stop')
            break
        if line:
            print(str(line))
            if re.search("[0-9]\.[0-9]+(\.[0-9]+)?", str(line)):
                version = re.search("[0-9]\.[0-9]+(\.[0-9]+)?", str(line)).group()

                print(f"version:{version}")
                target = version.find(".")
                removed = "".join(reversed(version[target+1:]))
                if version.count(".") != 1:
                    target = removed.find(".")
                    removed = removed[target+1:]
                version = "".join(reversed(removed))

                pid = proc.pid

                await proc.communicate(b'stop')
                break

            if version == "" and ("Done" in str(line) or "done" in str(line)):
                version = "Exception"
                pid = proc.pid

                await proc.communicate(b'stop')
                break

            if "UnsupportedClassVersion" in str(line):
                version = ""
                pid = proc.pid
                error = "java_error"

                break

    return str(version), pid, error

def isint(s):  # 整数値を表しているかどうかを判定
    try:
        int(s, 10)  # 文字列を実際にint関数で変換してみる
    except ValueError:
        return False
    else:
        return True

def askVersion(second = False, vCheck = "1"):
    if second == False:
        txt = "バージョンの自動検知に失敗しました\nバージョンを半角数字で入力してください\n*1.18.1 -> 18 のみを入力"
        if vCheck != "1":
            txt = "バージョンを半角数字で入力してください\n*1.18.1 -> 18 のみを入力"
        ret = simpledialog.askstring("手動設定", txt)
        if ret == None:
            return "cancel"
        elif isint(ret):
            return ret
        else:
            return askVersion(second=True)
    elif second == True:
        ret = simpledialog.askstring("エラー", "バージョンを半角数字のみで入力してください\n*1.18.1 -> 18 のみを入力")
        if ret == None:
            return "cancel"
        elif isint(ret):
            return ret
        else:
            return askVersion(second=True)

def checkEULA(pathDir):
    if os.path.exists(pathDir+"eula.txt"):
        os.chdir(pathDir)
        f = open('eula.txt', 'r', encoding='UTF-8')
        eula = f.read()
        eula = eula.lower()
        f.close()
        if "eula=true" in eula:
            os.chdir(finddata())
            return True
        else:
            os.chdir(finddata())
            return False
    else:
        os.chdir(finddata())
        return False