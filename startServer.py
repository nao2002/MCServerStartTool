import json
import subprocess
import os
import re
import searchJava
from findDataFile import find_data_file as finddata
import zipfile

#サーバー実行
def startServer(saved_content, timeout=None):
    os.chdir(finddata())
    returnText = ""
    if saved_content["path"] != "":
        returnText = use_command(saved_content)
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
    json_open.close()
    os.chdir(finddata())
    json_write = open('data/java_path.json','w',encoding="utf-8_sig")
    json.dump(java_paths, json_write, ensure_ascii=False, indent=4)
    json_write.close()

def check_bit(bit, saved_content):
    if bit == "64":
            return ""
    else:
        if int(saved_content["memory"]) > 4096:
            print("memory error : 32bit java cannot use over 4gb")
            return "メモリ割り当てエラー\n32bitJavaに4GB以上を割り当てられません"
        elif int(saved_content["memory"]) > 4 and saved_content["memoryUnit"] == "GB":
            print("memory error : 32bit java cannot use over 4gb")
            return "メモリ割り当てエラー\n32bitJavaに4GB以上を割り当てられません"
        else:
            return ""
            
def use_command(saved_content):

    path = saved_content["path"]
    reverse = "".join(reversed(saved_content["path"]))
    target = reverse.find("/")
    pathDir = reverse[target:]
    pathDir = "".join(reversed(pathDir))
    path = path[len(path) - target:]

    memory = str(saved_content["memory"])
    unit = "M"
    if saved_content["memoryUnit"] == "GB":
        unit = "G"
    memory = memory + unit

    version, java_version = checkServerVersion(saved_content)

    if saved_content["vCheck"] == "1" and (version == "Exception" or version == ""):
        return "バージョンの自動検出に失敗しました\nバージョンを手動で指定してください"
    
    if saved_content["vCheck"] == "0":
        java_version = saved_content["versions_list"][saved_content["version_index"]][1]

    json_open = open("data/java_path.json",'r',encoding="utf-8_sig")
    java_paths = json.load(json_open)
    json_open.close()
    if not java_version in java_paths:
        search_path()
        json_open = open("data/java_path.json","r",encoding="utf-8_sig")
        java_paths = json.load(json_open)
        json_open.close()
        if not java_version in java_paths:
            return f"javaバージョン: {java_version} が見つかりませんでした\nインストールするか、設定画面から検出してみてください"
    javaPath = java_paths[java_version]["path"]

    check = check_bit(java_paths[java_version]["bit"], saved_content)
    if check != "":
        return check
        
    v = version.split(".")
    if checkEULA(pathDir) == False and (int(v[1]) >= 8 or int(v[0]) >= 2):
        return "サーバーの起動に失敗しました\n\neula.txtに同意してください\n規約に同意する場合\neula=false を eula=true\nに書き換え再実行してください"

    log4jON = "18"
    if version == "Exception":
        log4jON = "0"
    elif int(v[0]) == 1 and int(v[1]) == 17:
        log4jON = "17"
    elif int(v[0]) == 1 and int(v[1]) <= 16 and int(v[1]) >= 12:
        log4jON = "16"
    elif int(v[0]) == 1 and int(v[1]) <= 11:
        log4jON = "11"
    if saved_content["log4j2"] == "0":
        log4jON = "0"

    others = ""
    if saved_content["gui"] == "0":
        others = others + " nogui"

    command = ['data\openStarter.bat',f"{javaPath}",f"{pathDir}",f"{path}",memory,log4jON,f"{others}"]
    subprocess.Popen(command, stdout = subprocess.PIPE)
    return ""

def checkServerVersion(saved_content): #jarファイル内を参照してバージョンを特定
    file = zipfile.ZipFile(saved_content["path"])
    list = file.namelist()
    if ("version.json" in list): #version.jsonファイルがある場合(mc1.14以上)
        with zipfile.ZipFile(saved_content["path"]) as z:
            with z.open("version.json") as f:
                base = str(f.read())
                target = base.find("\"id\"")+6
                text = base[target:]
                target = text.find("\\n")
                text = text[:target]
                m = re.search(r'\d+\.\d+', text)
                version = m.group()

                if "\"java_version\"" in base:
                    target = base.find("\"java_version\"")+15
                    text = base[target:]
                    target = text.find("\\n")
                    text = text[:target]
                    m = re.search(r'\d+', text)
                    java_version = m.group()

                    return version, java_version
                else:
                    return version, "8"
    elif ("META-INF/log4j-provider.properties" in list): #versionファイルがなくlog4jのプロパティファイルがある場合(mc1.13以下)
        #メモ Log4jAPIVersion = 2.0.0 だと1.7-1.11.2, Log4jAPIVersion = 2.1.0 だと1.12-1.16.5
        with zipfile.ZipFile(saved_content["path"]) as z:
            with z.open("META-INF/log4j-provider.properties") as f:
                text = str(f.read())
                target = text.find("Log4jAPIVersion = ")+18
                text = text[target:]
                target = text.find("\\n")
                text = text[:target]
                m = re.search(r'\d\.\d\.\d', text)
                text = m.group()
                if text == "2.0.0":
                    return "1.7", "8"
                elif text == "2.1.0":
                    return "1.12", "8"
                else:
                    return "Exception", "8"
    else: #検出できなかった時　プラグイン鯖などの際の処理もこちら
        #META-INF/log4j-provider.propertiesがない場合だが、1.7未満のバージョンもこうなるので、Vanilaか否かのチェックボックスを置くべき
        return "1.6", "8"

def isint(s):  # 整数値を表しているかどうかを判定
    try:
        int(s, 10)  # 文字列を実際にint関数で変換してみる
    except ValueError:
        return False
    else:
        return True

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
        return True