import glob
import os
import subprocess
from enum import Enum

class SearchJava(Enum):
    #way
    FULL = "full"
    QUICK = "quick"
    #priority
    NEW = "new"
    OLD = "old"
    #bit
    ALLBIT = "all"

#list形式で、{"ver":{"path":"(path)","detail":("detail"),"bit":(64 or 32)}}で出力予定

def search_path(way = SearchJava.QUICK, priority = SearchJava.NEW, bit = SearchJava.ALLBIT):
    if priority != SearchJava.NEW and priority != SearchJava.OLD:
        raise Exception('Error argument "priority" needs only SearchJava.NEW or SearchJava.OLD')
    if bit != SearchJava.ALLBIT and bit != 32 and bit != 64:
        raise Exception('Error argument "bit" needs only SearchJava.ALLBIT or 32 (int) or 64 (int)')
    if way == SearchJava.NEW or way == SearchJava.OLD or way == SearchJava.ALLBIT:
        raise Exception('Error argument "way" can use SearchJava.QUICK or SearchJava.FULL or file path (str, example: "C:\\Program Files*\\**\\java.exe")')

    if way == SearchJava.QUICK:
        return __search_main("C:\\Program Files*\\**\\bin\\java.exe", priority, bit)
    elif way == SearchJava.FULL:
        for d in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if os.path.exists(f'{d}:'):
                return __search_main(f"{d}:\\**\\bin\\java.exe", priority, bit)
    else:
        return __search_main(str(way), priority, bit)

#指定された条件でjava.exeを検索、その後check_detailsとchange_by_priorityを呼び出し結果のパスのリストを返す
#リストの形式 -> {"ver":{"path":"(path)","detail":("detail"),"bit":(64 or 32)}}
def __search_main(path, priority, bit):
    paths = {}

    for p in glob.glob(path, recursive=True):
        if os.path.isfile(p):
            reverse = "".join(reversed(p))
            target = reverse.find("\\")
            pathDir = reverse[target:]
            pathDir = "".join(reversed(pathDir))

            new_details,ver = __check_details(pathDir)
            if bit == 32 and new_details[ver]["bit"] != "32":
                continue
            if bit == 64 and new_details[ver]["bit"] != "64":
                continue

            if ver in paths:
                returnMsg = __change_by_priority(current=paths[ver], new=new_details[ver], priority=priority, bit=bit)
                if returnMsg == "current":
                    new_details[ver] = paths[ver]
                elif returnMsg == "new":
                    pass
                elif returnMsg == "error":
                    continue
            else:
                paths[ver] = {}
            paths[ver] = new_details[ver]
    return paths
            

def __check_details(path):
    #詳細バージョン確認 -> return 詳細バージョン(string),メインバージョン
    os.chdir(path)

    command = ['java',"-version"]
    cmdRun = subprocess.run(command, capture_output=True)
    if cmdRun.returncode == 0:
        javaDetail = {}
        output = str(cmdRun.stderr)
        target = output.find('"')
        version = output[target+1:]
        target = version.find('"')
        version = version[:target]

        if version.startswith("1."):
            version = version[2:]
        target = version.find(".")
        mainVersion = version[:target]

        javaDetail[str(mainVersion)] = {}
        javaDetail[str(mainVersion)]["path"] = path

        detailVersion = version[target+1:]

        javaDetail[str(mainVersion)]["detail"] = detailVersion

        if "64-Bit" in output:
            javaDetail[str(mainVersion)]["bit"] = "64"
        else:
            javaDetail[str(mainVersion)]["bit"] = "32"

        return javaDetail,str(mainVersion)
    else:
        return "error"


#詳細バージョン比較でどちらを使用するかを変更 current & new を渡す(例:currentにpaths["7"]、newにjavaDetail["7"]を渡す) -> "current"と"new"のどちらかを返す
def __change_by_priority(current, new, priority=SearchJava.NEW, bit=SearchJava.ALLBIT):
    #詳細バージョン存在確認&変更

    trueMessage = "new"
    falseMessage = "current"
    if priority == SearchJava.OLD:
        trueMessage = "current"
        falseMessage = "new"

    currentDetail = ""
    newDetail = ""
    if not "detail" in current and not "detail" in new:
        return "error"
    elif not "detail" in current:
        return "new"
    elif not "detail" in new:
        return "current"
    else:
        currentDetail = current["detail"]
        newDetail = new["detail"]

    if bit == 32 and current["bit"] != "32" and new["bit"] == "32":
        return "true"
    if (bit == 64 or bit == SearchJava.ALLBIT) and current["bit"] != "64" and new["bit"] == "64":
        return "true"
    if bit == SearchJava.ALLBIT and current["bit"] == "64" and new["bit"] == "32":
        return "current"

    if "_" in newDetail:
        target = newDetail.find("_")
        mainDetail = newDetail[:target]
        target2 = currentDetail.find("_")
        alreadyDetail = currentDetail[:target2]
        if float(mainDetail) >= float(alreadyDetail):
            mainDetail = newDetail[target+1:]
            alreadyDetail = currentDetail[target2+1:]
            if float(mainDetail) > float(alreadyDetail):
                return trueMessage
            else:
                return falseMessage
        else:
            return falseMessage
    elif float(newDetail) > float(currentDetail):
        return trueMessage
    else:
        return falseMessage

#2つのjavaListを合成 -> priorityとbitの優先を処理した後の合成後Listを出力
def compound_javaLists(paths1, paths2, priority=SearchJava.NEW, bit=SearchJava.ALLBIT):
    compound_list = {}

    if type(paths1) != dict or type(paths2) != dict:
        raise Exception('Error not collect arguments: the method "compound_javaLists" must needs 2 dict type arguments')
    if priority != SearchJava.NEW and priority != SearchJava.OLD:
        raise Exception('Error argument "priority" needs only SearchJava.NEW or SearchJava.OLD')
    if bit != SearchJava.ALLBIT and bit != 32 and bit != 64:
        raise Exception('Error argument "bit" needs only SearchJava.ALLBIT or 32 (int) or 64 (int)')
    
    for v in paths1:
        if v in paths2:
            returnMsg = __change_by_priority(current=paths1[v], new=paths2[v], priority=priority, bit=bit)

            if not returnMsg == "error" and not v in compound_list:
                compound_list[v] = {}

            if returnMsg == "current":
                compound_list[v] = paths1[v]
            elif returnMsg == "new":
                compound_list[v] = paths2[v]
            elif returnMsg == "error":
                paths2.pop(v)
                continue
            
            paths2.pop(v)
        else:
            if "detail" in paths1[v]:
                if not v in compound_list:
                    compound_list[v] = {}
                compound_list[v] = paths1[v]
            else:
                continue
    
    for v in paths2:
        if "detail" in paths2[v]:
            if not v in compound_list:
                compound_list[v] = {}
            compound_list[v] = paths2[v]
        else:
            continue

    return compound_list