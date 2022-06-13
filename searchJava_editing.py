import glob
import os
import subprocess
import json
import enum

class SearchJava(enum):
    #way
    FULL = "full"
    QUICK = "quick"
    #priority
    NEW = "new"
    OLD = "old"
    #bit
    ALL = "all"

#list形式で、{"ver":{"path":"(path)","detail":("detail"),"bit":(64 or 32)}}で出力予定

def search_path(way = "quick", priority = "new", bit = "all"):
    if way == "quick":
        search_main("C:\\Program Files*\\**\\bin\\java.exe", priority, bit)
    elif way == "full":
        for d in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if os.path.exists(f'{d}:'):
                search_main(f"{d}:\\**\\bin\\java.exe", priority, bit)
    else:
        search_main(str(way), priority, bit)

def search_main(path, priority, bit):
    #json_open = open("data/java_path.json",'r',encoding="utf-8_sig")
    #javaPaths = json.load(json_open)
    paths = {}
                
    #指定された条件でjava.exeを検索
    for p in glob.glob(path, recursive=True):
        if os.path.isfile(p):
            reverse = "".join(reversed(p))
            target = reverse.find("\\")
            pathDir = reverse[target:]
            pathDir = "".join(reversed(pathDir))

            new_details,ver = check_details(pathDir)
            

def check_details(path):
    print("check details of java version")
    #詳細バージョン確認 -> return 詳細バージョン(string)
    reverse = "".join(reversed(path))
    target = reverse.find("\\")
    pathDir = reverse[target:]
    pathDir = "".join(reversed(pathDir))
    
    os.chdir(pathDir)

    command = ['java',"-version"]
    cmdRun = subprocess.run(command, capture_output=True)
    if cmdRun.returncode == 0:
        javaDetail = {}
        output = str(cmdRun.stderr)
        print(output)
        target = output.find('"')
        version = output[target+1:]
        target = version.find('"')
        version = version[:target]
        print(version)

        if version.startswith("1."):
            version = version[2:]
        target = version.find(".")
        mainVersion = version[:target]
        print(mainVersion)

        javaDetail[str(mainVersion)] = {}
        javaDetail[str(mainVersion)]["path"] = pathDir

        detailVersion = version[target+1:]
        print(detailVersion)

        javaDetail[str(mainVersion)]["detail"] = detailVersion

        if "64-Bit" in output:
            javaDetail[str(mainVersion)]["bit"] = "64"
        else:
            javaDetail[str(mainVersion)]["bit"] = "32"

        return javaDetail,mainVersion
    else:
        return "error"


#詳細バージョン比較でどちらを使用するかを変更 current & new を渡す(例:currentにpaths["7"]、newにjavaDetail["7"]を渡す) -> currentとnewのどちらかを返す
def change_by_priority(current, new):
    #詳細バージョン存在確認&変更
    currentDetail = ""
    newDetail = ""
    if not "detail" in current or not "detail" in new:
        currentDetail = current["detail"]
    else:
        currentDetail = current["detail"]
        newDetail = new["detail"]
    if "_" in newDetail:
        target = newDetail.find("_")
        mainDetail = newDetail[:target]
        target2 = currentDetail.find("_")
        alreadyDetail = currentDetail[:target2]
        if float(mainDetail) >= float(alreadyDetail):
            mainDetail = newDetail[target+1:]
            alreadyDetail = currentDetail[target2+1:]
            if float(mainDetail) > float(alreadyDetail):
                return new
            else:
                return current
        else:
            return current
    elif float(newDetail) > float(currentDetail):
        return new
    else:
        return current

#指定されたファイルに指定する
def change_java(path):
    json_open = open("data/java_path.json",'r',encoding="utf-8_sig")
    javaPaths = json.load(json_open)
    if os.path.isfile(path):
            reverse = "".join(reversed(path))
            target = reverse.find("/")
            pathDir = reverse[target:]
            pathDir = "".join(reversed(pathDir))

            command = ['data\checkJavaVer.bat',f"{pathDir}"]
            cmdRun = subprocess.run(command, capture_output=True)

            if cmdRun.returncode == 0:
                output = str(cmdRun.stderr)
                print(output)
                target = output.find('"')
                version = output[target+1:]
                target = version.find('"')
                version = version[:target]
                print(version)

                if version.startswith("1."):
                    version = version[2:]
                target = version.find(".")
                mainVersion = version[:target]
                print(mainVersion)
                
                javaPaths[str(mainVersion)] = {}
                javaPaths[str(mainVersion)]["path"] = pathDir

                detailVersion = version[target+1:]
                print(detailVersion)

                javaPaths[str(mainVersion)]["detail"] = detailVersion

                if "64-Bit" in output:
                    print("64Bit")
                    javaPaths[str(mainVersion)]["bit"] = "64"
                else:
                    print("32Bit")
                    javaPaths[str(mainVersion)]["bit"] = "32"                    

            else:
                "error"
    print(javaPaths)
    json_write = open("data/java_path.json",'w',encoding="utf-8_sig")
    json.dump(javaPaths, json_write, ensure_ascii=False, indent=4)