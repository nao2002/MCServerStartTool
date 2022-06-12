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

def search_path(way = "quick", priority = "new", current = {}, bit = "all"):
    if way == "quick":
        search_main("C:\\Program Files*\\**\\bin\\java.exe", priority, current, bit)
    elif way == "full":
        for d in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if os.path.exists(f'{d}:'):
                search_main(f"{d}:\\**\\bin\\java.exe", priority, current, bit)
    else:
        search_main(str(way), priority, current, bit)

def search_main(path, priority, current, bit):
    #json_open = open("data/java_path.json",'r',encoding="utf-8_sig")
    #javaPaths = json.load(json_open)
    paths = {}
    if current != {}:
        for v in current:
            if v in ["7","8","9","10","11","12","13","14","15","16","17","18"]:
                if v in paths:
                    if "path" in current[v] and os.path.exists(current[v]["path"]):
                        returnText = change_by_priority(paths[v], current[v])
                        if returnText == "current" or returnText == "error":
                            pass
                        elif returnText == "check":
                            paths[v] = current[v]
                elif "path" in current[v] and os.path.exists(current[v]["path"]):
                    
                    paths.append(v)
                    paths[v].append(current[v])
                
    #指定された条件でjava.exeを検索(デフォルト起動は"C:\\Program Files*\\**\\bin\\java.exe")
    for p in glob.glob(path, recursive=True):
        if os.path.isfile(p):
            reverse = "".join(reversed(p))
            target = reverse.find("\\")
            pathDir = reverse[target:]
            pathDir = "".join(reversed(pathDir))

            command = ['data\checkJavaVer.bat',f"{pathDir}"]
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
                    print("64Bit")
                    javaDetail[str(mainVersion)]["bit"] = "64"
                else:
                    print("32Bit")
                    javaDetail[str(mainVersion)]["bit"] = "32"

                #既に登録されているjavaよりも新しいかを確認
                if str(mainVersion) in javaPaths:
                    if javaPaths[str(mainVersion)]["bit"] == "64":
                        if javaDetail[str(mainVersion)]["bit"] == "64":
                            if "_" in detailVersion:
                                target = detailVersion.find("_")
                                mainDetail = detailVersion[:target]
                                target2 = str(javaPaths[str(mainVersion)]["detail"]).find("_")
                                alreadyDetail = str(javaPaths[str(mainVersion)]["detail"])[:target2]
                                if float(mainDetail) >= float(alreadyDetail):
                                    mainDetail = detailVersion[target+1:]
                                    alreadyDetail = str(javaPaths[str(mainVersion)]["detail"])[target2+1:]
                                    if float(mainDetail) > float(alreadyDetail):
                                        javaPaths[str(mainVersion)] = javaDetail[str(mainVersion)]
                            elif float(javaDetail[str(mainVersion)]["detail"]) > float(javaPaths[str(mainVersion)]["detail"]):
                                javaPaths[str(mainVersion)] = javaDetail[str(mainVersion)]
                    else:
                        if javaDetail[str(mainVersion)]["bit"] == "64":
                            javaPaths[str(mainVersion)] = javaDetail[str(mainVersion)]
                        else:
                            if "_" in detailVersion:
                                target = detailVersion.find("_")
                                mainDetail = detailVersion[:target]
                                target2 = str(javaPaths[str(mainVersion)]["detail"]).find("_")
                                alreadyDetail = str(javaPaths[str(mainVersion)]["detail"])[:target2]
                                if float(mainDetail) >= float(alreadyDetail):
                                    mainDetail = detailVersion[target+1:]
                                    alreadyDetail = str(javaPaths[str(mainVersion)]["detail"])[target2+1:]
                                    if float(mainDetail) > float(alreadyDetail):
                                        javaPaths[str(mainVersion)] = javaDetail[str(mainVersion)]
                            elif float(javaDetail[str(mainVersion)]["detail"]) > float(javaPaths[str(mainVersion)]["detail"]):
                                javaPaths[str(mainVersion)] = javaDetail[str(mainVersion)]
                else:
                    javaPaths[str(mainVersion)] = javaDetail[str(mainVersion)]
                #登録確認ここまで
                    

            else:
                "error"
    print(javaPaths)
    json_write = open("data/java_path.json",'w',encoding="utf-8_sig")
    json.dump(javaPaths, json_write, ensure_ascii=False, indent=4)

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
    else:
        return "error"


#詳細バージョン比較でどちらを使用するかを変更 -> return "current" or "check" or "error"
def change_by_priority(current, check):
    #詳細バージョン存在確認&変更
    currentDetail = ""
    checkDetail = ""
    if "detail" in current:
        currentDetail = current["detail"]
    else:
        if "path" in current:
            currentDetail = check_details(current["path"])
        else:
            return "error"
    if "detail" in check:
        checkDetail = check["detail"]
    else:
        if "path" in check:
            checkDetail = check_details(check["path"])
        else:
            return "error"
    if currentDetail == "error" or checkDetail == "error":
        return "error"
    if "_" in checkDetail:
        target = checkDetail.find("_")
        mainDetail = checkDetail[:target]
        target2 = currentDetail.find("_")
        alreadyDetail = currentDetail[:target2]
        if float(mainDetail) >= float(alreadyDetail):
            mainDetail = checkDetail[target+1:]
            alreadyDetail = currentDetail[target2+1:]
            if float(mainDetail) > float(alreadyDetail):
                return "check"
            else:
                return "current"
        else:
            return "current"
    elif float(checkDetail) > float(currentDetail):
        return "check"
    else:
        return "current"

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