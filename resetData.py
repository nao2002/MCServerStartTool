import json
import os

def resetData():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    json_write = open("data/data.json",'w',encoding="utf-8_sig")
    content = {
        "path": "",
        "dirPath": "",
        "mcVersion": "1.18.x以降",
        "memory": "2048",
        "memoryUnit": "MB",
        "gui": "1",
        "log4j2": "1",
        "x": -1.0,
        "y": -1.0
    }
    json.dump(content, json_write, ensure_ascii=False, indent=4)

    json_write = open("data/java_path.json",'w',encoding="utf-8_sig")
    content = {}
    json.dump(content, json_write, ensure_ascii=False, indent=4)
    print("reset done.")