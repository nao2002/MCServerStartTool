import glob
import os
import subprocess
import json

def search_path(path):
    json_open = open("data/java_path.json",'r',encoding="utf-8_sig")
    javaPaths = json.load(json_open)
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