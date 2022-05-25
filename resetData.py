import json

def resetData():
    json_write = open("data/data.json",'w',encoding="utf-8_sig")
    content = {
        "path": "",
        "dirPath": "",
        "mcVersion": "1.16.x以前",
        "vanila": "1",
        "memory": "4096",
        "memoryUnit": "MB",
        "gui": "1",
        "log4j2": "1"
    }
    json.dump(content, json_write, ensure_ascii=False, indent=4)

    json_write = open("data/java_path.json",'w',encoding="utf-8_sig")
    content = {}
    json.dump(content, json_write, ensure_ascii=False, indent=4)
    print("reset done.")