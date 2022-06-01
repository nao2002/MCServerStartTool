import json
import subprocess
import searchJava

#サーバー実行
def startServer(saved_content):
    returnText = ""
    if saved_content["path"] != "":
        json_open = open("data/java_path.json",'r',encoding="utf-8_sig")
        java_paths = json.load(json_open)
        if saved_content["mcVersion"] == "1.16.x以前":
            if "8" in java_paths:
                returnText = check_bit(java_paths["8"]["path"],java_paths["8"]["bit"], saved_content)
            else:
                returnText = search_path("8", saved_content)
        elif saved_content["mcVersion"] == "1.17.x":
            if "16" in java_paths:
                returnText = check_bit(java_paths["16"]["path"],java_paths["16"]["bit"], saved_content)
            elif "17" in java_paths:
                returnText = check_bit(java_paths["17"]["path"],java_paths["17"]["bit"], saved_content)
            elif "18" in java_paths:
                returnText = check_bit(java_paths["17"]["path"],java_paths["17"]["bit"], saved_content)
            else:
                returnText = search_path("16", saved_content)
        elif saved_content["mcVersion"] == "1.18.x":
            if "17" in java_paths:
                returnText = check_bit(java_paths["17"]["path"],java_paths["17"]["bit"], saved_content)
            elif "18" in java_paths:
                returnText = check_bit(java_paths["17"]["path"],java_paths["17"]["bit"], saved_content)
            else:
                returnText = search_path("17", saved_content)
    else:
        print("error - path未設定")
        returnText = "サーバーを指定してください"
    return returnText

def search_path(ver, saved_content):
    searchJava.search_path("C:\\Program Files*\\**\\bin\\java.exe")
    json_open = open("data/java_path.json",'r',encoding="utf-8_sig")
    java_paths = json.load(json_open)
    if ver in java_paths:
        return check_bit(java_paths[ver]["path"],java_paths[ver]["bit"],saved_content)
    elif ver == "16" and "17" in java_paths:
        return check_bit(java_paths["17"]["path"],java_paths["17"]["bit"],saved_content)
    elif ver == "16" and "18" in java_paths:
        return check_bit(java_paths["18"]["path"],java_paths["18"]["bit"],saved_content)
    elif ver == "17" and "18" in java_paths:
        return check_bit(java_paths["18"]["path"],java_paths["18"]["bit"],saved_content)
    else:
        javaV = "8"
        if ver == "16":
            javaV = "16以上"
        elif ver == "17":
            javaV = "17以上"
        return f"Java{javaV}を自動検出できませんでした\nJava設定ウィンドウで設定をしてください"

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

    mcVer = "16"
    if saved_content["mcVersion"] == "1.17.x":
        mcVer = "17"
    elif saved_content["mcVersion"] == "1.18.x":
        mcVer = "18"
    if saved_content["log4j2"] == 0 or saved_content["vanila"] == 0:
        mcVer = "18"

    print(pathDir)

    others = ""
    if saved_content["gui"] == "0":
        others = others + " nogui"

    command = ['data\openStarter.bat',f"{javaPath}",f"{pathDir}",f"{path}",memory,mcVer,f"{others}"]
    cmdRun = subprocess.run(command, stdout = subprocess.PIPE)
    print(cmdRun)
    if cmdRun.returncode == 0:
        return ""
    else:
        return "サーバーの実行中にエラーが発生しました\nサーバーファイルを指定し直してみてください"