import tkinter as tk
from tkinter import ttk
from tkinter import *
from functools import partial
import json
import selectFiles
import startServer
import sys
import os
import searchJava
from searchJava import SearchJava
from findDataFile import find_data_file as finddata
import resetData
import threading

windows = {}
saved_content = {}

def get_json():
    global saved_content
    json_open = open("data/data.json",'r',encoding="utf-8_sig")
    saved_content = json.load(json_open)

def save_json():
    json_write = open('data/data.json','w',encoding="utf-8_sig")
    json.dump(saved_content, json_write, ensure_ascii=False, indent=4)

def mainWindow():

    get_json()

    main_win = tk.Tk()

    # メインウィンドウ
    main_win.title("MC_Server_Starter")
    if saved_content["x"] <= -1.0:
        main_win.geometry("520x145")
    else:
        x = saved_content["x"]
        y = saved_content["y"]
        main_win.geometry(f"520x145+{x}+{y}")
    main_win.resizable(width=False, height=False)

    # メインフレーム
    main_frm = ttk.Frame(main_win)
    main_frm.grid(column=0, row=0, sticky=tk.NSEW, padx=5, pady=10)

    #フォルダパス
    folder_label = ttk.Label(main_frm, text="サーバーファイル")
    pathVar = StringVar(value=str(saved_content["path"]))
    folder_box = ttk.Entry(main_frm, textvariable=pathVar, state="readonly")
    windows["pathVar"] = pathVar
    folder_btn = ttk.Button(main_frm, text="参照", command=select_path)

    #手動バージョン選択
    version_label = ttk.Label(main_frm, text="バージョン")
    version_list = [i[1][0] for i in saved_content["versions_list"].items()]
    if saved_content["version_index"] >= len(version_list):
        saved_content["version_index"] = len(version_list)-1
        save_json()
    version_selector = ttk.Combobox(main_frm, values=version_list, state="readonly")
    version_selector.set(version_list[saved_content["version_index"]])
    version_selector.bind('<<ComboboxSelected>>', versionComboSelect)
    windows["versionSelector"] = version_selector
    windows["versionSelector_label"] = version_label

    #バージョン自動検出するかどうか
    vCheck_var = StringVar(value=str(saved_content["vCheck"]))
    vCheck_toggle = ttk.Checkbutton(
    main_frm, padding=(10), text='バージョンを自動検出する',
    variable=vCheck_var, onvalue='1', offvalue='0',
    command=partial(versionDetectToggle, vCheck_var))

    #バージョン自動検出状態の場合、version_selectorを無効化
    if saved_content["vCheck"] == "1":
        version_selector.state(["disabled"])
        version_label.state(["disabled"])
    else:
        version_selector.state(["!disabled"])
        version_label.state(["!disabled"])

    #実行ボタン
    app_btn = ttk.Button(main_frm, text="起動", command=start_subThread)
    windows["start_btn"] = app_btn

    detail_btn = ttk.Button(main_frm, text="設定", command=toDetailWindow)

    # ウィジェットの配置
    folder_label.place(x=5, y=5)
    folder_box.place(x=85, y=5, width=340, height=23)
    folder_btn.place(x=425, y=4, height=25)
    version_label.place(x=60, y=48)
    version_selector.place(x=125, y=48, width=100)
    vCheck_toggle.place(x=280, y=40)
    app_btn.place(x=85,y=90, width=100, height=25)
    detail_btn.place(x=315,y=90,width=110,height=25)

    # 配置設定
    main_win.columnconfigure(0, weight=1)
    main_win.rowconfigure(0, weight=1)
    main_frm.columnconfigure(1, weight=1)

    windows["now"] = main_win
    windows["frm"] = main_frm
    main_win.protocol("WM_DELETE_WINDOW", click_close)
    main_win.mainloop()

def start_subThread():
    server_task = threading.Thread(target=start)
    server_task.start()

def start():
    windows["now"].wm_state('iconic')
    windows["start_btn"].state(["disabled"])
    errorMessage = startServer.startServer(saved_content=saved_content)
    print(errorMessage)
    if errorMessage != "":
        windows["now"].wm_state('normal')
        if errorMessage != "cancel":
            tk.messagebox.showwarning("エラーが発生しました", errorMessage)
    windows["start_btn"].state(["!disabled"])

def select_path():
    path = selectFiles.openFiledialog(saved_content["dirPath"],saved_content["path"])
    windows["pathVar"].set(path)
    saved_content["path"] = path
    save_json()

def toDetailWindow():
    global windows
    print(windows)
    saved_content["x"] = windows["now"].winfo_x()
    saved_content["y"] = windows["now"].winfo_y()
    save_json()
    windows["now"].destroy()
    detailWindow()
    
def detailWindow():

    detail_win = tk.Tk()

    # メインウィンドウ
    detail_win.title("詳細設定")
    x = saved_content["x"]
    y = saved_content["y"]
    detail_win.geometry(f"400x445+{x}+{y}")
    detail_win.resizable(width=False, height=False)

    # メインフレーム
    main_frm = ttk.Frame(detail_win)
    main_frm.grid(column=0, row=0, sticky=tk.NSEW, padx=5, pady=10)

    #バージョン
    version_label = ttk.Label(main_frm, text="バージョン対応表の設定")
    version_btn = ttk.Button(main_frm, text="開く", command=toVersionWindow)

    #JAVA
    java_label = ttk.Label(main_frm, text="Javaファイルパスの設定")
    java_btn = ttk.Button(main_frm, text="開く", command=toJavaWindow)

    #デフォルトディレクトリ
    directory_label = ttk.Label(main_frm, text="デフォルトディレクトリを指定する")
    dirPathVar = StringVar(value=str(saved_content["dirPath"]))
    directory_box = ttk.Entry(main_frm, textvariable=dirPathVar, state="readonly")
    windows["dirPathVar"] = dirPathVar
    directory_btn = ttk.Button(main_frm, text="参照", command=select_dir)

    #メモリ割り当て
    memory_label = ttk.Label(main_frm, text="割り当てメモリ")
    memoryVar = StringVar(value=str(saved_content["memory"]))
    memory_box = ttk.Entry(main_frm, width=15, textvariable=memoryVar, validate="focusout", validatecommand=memoryChanged)
    memory_box["justify"] = tk.RIGHT
    windows["memoryBox"] = memory_box
    memoryVar.trace_add("write", memoryChanged)
    memoryUnitVar = StringVar(value=str(saved_content["memoryUnit"]))
    memory_comb = ttk.Combobox(main_frm, textvariable=memoryUnitVar, values=["MB", "GB"], width=12, state="readonly")
    memory_comb.bind('<<ComboboxSelected>>', memoryComboSelect)
    windows["memoryComb"] = memory_comb

    #GUI表示チェック
    gui_var = StringVar(value=str(saved_content["gui"]))
    gui_toggle = ttk.Checkbutton(
    main_frm, padding=(10), text='GUIを表示',
    variable=gui_var, onvalue='1', offvalue='0',
    command=partial(toggleButtonSave, gui_var, "gui"))

    #log4j2対応
    log4j2_var = StringVar(value=str(saved_content["log4j2"]))
    log4j2_toggle = ttk.Checkbutton(
    main_frm, padding=(10), text='log4j2対策の自動有効化 (ON推奨)',
    variable=log4j2_var, onvalue='1', offvalue='0',
    command=partial(toggleButtonSave, log4j2_var, "log4j2"))

    #バージョン自動検知
    # vCheck_var = StringVar(value=str(saved_content["vCheck"]))
    # vCheck_toggle = ttk.Checkbutton(
    # main_frm, padding=(10), text='バージョンの自動検知　*起動にかかる時間が増えることがあります',
    # variable=vCheck_var, onvalue='1', offvalue='0',
    # command=partial(toggleButtonSave, vCheck_var, "vCheck"))

    #サーバーエラー確認
    # errorCheck_label = ttk.Label(main_frm, text="サーバーのエラーチェックをする")
    # errorCheck_btn = ttk.Button(main_frm, text="実行",command=errorCheck)

    #リセット
    reset_label = ttk.Label(main_frm, text="初期状態に戻す")
    reset_btn = ttk.Button(main_frm, text="リセット", command=resetAsk)


    # ウィジェット作成（実行ボタン）
    back_btn = ttk.Button(main_frm, text="戻る", command=toMainWindow)

    version_label.place(x=20, y=7)
    version_btn.place(x=270, y=5, width=100,height=25)
    java_label.place(x=20, y=57)
    java_btn.place(x=270, y=55, width=100,height=25)
    directory_label.place(x=20, y=108)
    directory_btn.place(x=270,y=105, width=100,height=25)
    directory_box.place(x=25, y=133,width=345)
    memory_label.place(x=20, y=185)
    memory_box.place(x=200, y=185, width=100)
    memory_comb.place(x=300, y=185, width=70)
    gui_toggle.place(x=13, y=220)
    log4j2_toggle.place(x=13, y=255)
    reset_label.place(x=20, y=325)
    reset_btn.place(x=270, y=325, width=100, height=25)
    back_btn.place(x=150, y=385, width=100)

    # 配置設定
    detail_win.columnconfigure(0, weight=1)
    detail_win.rowconfigure(0, weight=1)
    main_frm.columnconfigure(1, weight=1)

    windows["now"] = detail_win
    windows["frm"] = main_frm
    detail_win.protocol("WM_DELETE_WINDOW", click_close)
    detail_win.mainloop()

def toJavaWindow():
    global windows
    saved_content["x"] = windows["now"].winfo_x()
    saved_content["y"] = windows["now"].winfo_y()
    save_json()
    windows["now"].destroy()
    javaWindow()

def javaWindow():

    java_win = tk.Tk()

    # メインウィンドウ
    java_win.title("JAVAPATH設定")
    x = saved_content["x"]
    y = saved_content["y"]
    java_win.geometry(f"520x300+{x}+{y}")
    java_win.resizable(width=False, height=False)

    # メインフレーム
    main_frm = ttk.Frame(java_win)
    main_frm.grid(column=0, row=0, sticky=tk.NSEW, padx=5, pady=10)

    json_open = open("data/java_path.json",'r',encoding="utf-8_sig")
    java_paths = json.load(json_open)
    listbox = tk.Listbox(main_frm, justify="left")
    for i in java_paths:
        listbox.insert(tk.END ,f"Java{i}." + java_paths[i]["detail"] + " - " + java_paths[i]["bit"] + "bit",java_paths[i]["path"],"")
    windows["listData"] = listbox

    autoScan_btn = ttk.Button(main_frm, text="クイックスキャン", command=partial(askScan, "default"))
    windows["autoScan_btn"] = autoScan_btn

    fullScan_btn = ttk.Button(main_frm, text="フルスキャン", command=partial(askScan, "full"))
    windows["fullScan_btn"] = fullScan_btn

    selfSelect_btn = ttk.Button(main_frm, text="手動選択", command=select_java)
    windows["selfSelect_btn"] = selfSelect_btn

    # ウィジェット作成（実行ボタン）
    back_btn_var = StringVar(value="戻る")
    back_btn = ttk.Button(main_frm, textvariable=back_btn_var, command=toDetailWindow)
    windows["back_btn"] = back_btn
    windows["back_btn_var"] = back_btn_var

    # ウィジェットの配置
    #listbox.grid(column=0,row=0)
    #autoScan_btn.grid(column=0,row=1)
    #fullScan_btn.grid(column=1, row=1)

    #selfSelect_btn.grid(column=2,row=1)

    #back_btn.grid(column=1, row=2, pady=10)

    listbox.place(x=20,y=7,width=470)
    autoScan_btn.place(x=20, y=180, width=100)
    fullScan_btn.place(x=205, y=180,width=100)
    selfSelect_btn.place(x=390, y=180, width=100)

    back_btn.place(x=205,y=240, width=100)

    # 配置設定
    java_win.columnconfigure(0, weight=1)
    java_win.rowconfigure(0, weight=1)
    main_frm.columnconfigure(1, weight=1)

    windows["now"] = java_win
    windows["frm"] = main_frm
    java_win.protocol("WM_DELETE_WINDOW", click_close)
    java_win.mainloop()

def toVersionWindow():
    global windows
    saved_content["x"] = windows["now"].winfo_x()
    saved_content["y"] = windows["now"].winfo_y()
    save_json()
    windows["now"].destroy()
    versionWindow()

def versionWindow():
    version_win = tk.Tk()
    version_win.title("バージョン設定")
    x = saved_content["x"]
    y = saved_content["y"]
    version_win.geometry(f"350x300+{x}+{y}")
    version_win.resizable(width=False, height=False)

    main_frm = ttk.Frame(version_win)
    main_frm.grid(column=0, row=0, sticky=tk.NSEW, padx=5, pady=10)

    title_frame = ttk.Frame(main_frm)
    mc_version_label = ttk.Label(title_frame, text="マイクラバージョン")
    mc_version_label["justify"] = tk.CENTER
    java_version_label = ttk.Label(title_frame, text="javaバージョン")
    java_version_label["justify"] = tk.CENTER
    mc_version_label.pack(side=tk.LEFT, padx=20)
    java_version_label.pack(side=tk.RIGHT, padx=20)
    title_frame.pack()

    scroll_canvas = tk.Canvas(main_frm)
    scroll_frame = tk.Frame(scroll_canvas)
    scrollbar = tk.Scrollbar(
        scroll_canvas, orient=tk.VERTICAL, command=scroll_canvas.yview, 
    )

    version_lists = saved_content["versions_list"]
    version_entries = []
    for i in version_lists:
        key = version_lists[i][0]
        value = version_lists[i][1]
        frame = ttk.Frame(scroll_frame)
        index = len(version_entries)
        mcvar = StringVar(value=str(key))
        mc = ttk.Entry(frame, textvariable=mcvar)
        mc["justify"] = tk.RIGHT
        mc.pack(side=tk.LEFT)
        javavar = StringVar(value=str(value))
        val_cmd = version_win.register(checkDigit)
        java = ttk.Entry(frame, textvariable=javavar, validate="key", validatecommand=(val_cmd, '%S'))
        java["justify"] = tk.RIGHT
        java.pack(side=tk.RIGHT)
        version_entries.append((index, frame, mcvar, javavar))
        frame.pack()

    windows["version_entries"] = version_entries
    windows["version_scroll_frame"] = scroll_frame

    scroll_canvas.configure(scrollregion=(0, 0, 350, 300))
    scroll_canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
    scroll_canvas.pack(expand=True, fill=tk.BOTH)

    scroll_canvas.create_window((0, 0), window=scroll_frame, anchor=tk.NW, width=350, height=300)

    manage_frame = ttk.Frame(main_frm)
    add_btn = ttk.Button(manage_frame, text="追加", command=addVersion)
    remove_btn = ttk.Button(manage_frame, text="削除", command=removeVersion)
    remove_btn.pack(side=tk.RIGHT, padx=20)
    add_btn.pack(side=tk.RIGHT, padx=20)
    manage_frame.pack(pady=10)

    back_btn = ttk.Button(main_frm, text="保存して戻る", command=saveAndReturnFromVersionWindow)

    back_btn.pack(pady=25)

    version_win.columnconfigure(0, weight=1)
    version_win.rowconfigure(0, weight=1)
    main_frm.columnconfigure(1, weight=1)

    windows["now"] = version_win
    windows["frm"] = main_frm
    version_win.protocol("WM_DELETE_WINDOW", click_close)
    version_win.mainloop()

def saveAndReturnFromVersionWindow():
    version_list = {}
    for index, frame, mcvar, javavar in windows["version_entries"]:
        version_list[index] = [mcvar.get(), javavar.get()]
    saved_content["versions_list"] = version_list
    save_json()
    toDetailWindow()

def select_dir():
    path = selectFiles.openDirdialog(saved_content["dirPath"])
    print(path)
    windows["dirPathVar"].set(path)
    saved_content["dirPath"] = path
    save_json()

def toMainWindow():
    global windows
    saved_content["x"] = windows["now"].winfo_x()
    saved_content["y"] = windows["now"].winfo_y()
    save_json()
    windows["now"].destroy()
    mainWindow()

def versionComboSelect(event):
    saved_content["version_index"] = windows["versionSelector"].current()
    save_json()

def memoryComboSelect(event):
    saved_content["memoryUnit"] = windows["memoryComb"].get()
    save_json()

def memoryChanged(arg1, arg2, arg3):
    saved_content["memory"] = windows["memoryBox"].get()
    save_json()

def toggleButtonSave(var,path):
    saved_content[str(path)] = var.get()
    save_json()

def versionDetectToggle(var):
    saved_content["vCheck"] = var.get()
    if var.get() == "1":
        windows["versionSelector"].state(["disabled"])
        windows["versionSelector_label"].state(["disabled"])
    else:
        windows["versionSelector"].state(["!disabled"])
        windows["versionSelector_label"].state(["!disabled"])
    save_json()

def checkDigit(S):
    if S.isdigit():
        return True
    else:
        return False

def addVersion():
    scroll_frame = windows["version_scroll_frame"]
    key = windows["version_entries"][-1][2].get()
    value = windows["version_entries"][-1][3].get()
    frame = ttk.Frame(scroll_frame)
    index = len(windows["version_entries"])
    mcvar = StringVar(value=str(key))
    mc = ttk.Entry(frame, textvariable=mcvar)
    mc["justify"] = tk.RIGHT
    mc.pack(side=tk.LEFT)
    javavar = StringVar(value=str(value))
    val_cmd = windows["now"].register(checkDigit)
    java = ttk.Entry(frame, textvariable=javavar, validate="key", validatecommand=(val_cmd, '%S'))
    java["justify"] = tk.RIGHT
    java.pack(side=tk.RIGHT)
    windows["version_entries"].append((index, frame, mcvar, javavar))
    frame.pack()

def removeVersion():
    if len(windows["version_entries"]) == 1:
        return
    windows["version_entries"][-1][1].destroy()
    windows["version_entries"].pop()
    if saved_content["version_index"] >= len(windows["version_entries"]):
        saved_content["version_index"] = len(windows["version_entries"]) - 1

def askScan(mode):
    if mode == "full":
        ret = tk.messagebox.askyesno('詳細検出', 'この処理にはかなり時間がかかることがあります\n実行後はウィンドウを閉じずにしばらくお待ちください。\n実行しますか？')
        if ret == True:
            java_task = threading.Thread(target=javaFullScan, args=("fullScan",))
            java_task.start()
    elif mode == "default":
        ret = tk.messagebox.askyesno('自動検出', 'これには少し時間がかかることがあります\n実行しますか？')
        if ret == True:
            java_task = threading.Thread(target=javaFullScan, args=("default",))
            java_task.start()

def javaFullScan(mode):
    windows["autoScan_btn"].state(["disabled"])
    windows["fullScan_btn"].state(["disabled"])
    windows["selfSelect_btn"].state(["disabled"])
    windows["back_btn"].state(["disabled"])
    windows["back_btn_var"].set("検出中...")
    ret = {}
    if mode == "default":
        ret = searchJava.search_path()
    else:
        ret = searchJava.search_path(way=SearchJava.FULL)
    os.chdir(finddata())
    json_open = open("data/java_path.json",'r',encoding="utf-8_sig")
    java_paths = json.load(json_open)
    java_paths = searchJava.compound_javaLists(java_paths,ret)
    json_write = open('data/java_path.json','w',encoding="utf-8_sig")
    json.dump(java_paths, json_write, ensure_ascii=False, indent=4)

    windows["listData"].delete(0, tk.END)
    for i in java_paths:
        windows["listData"].insert(tk.END, f"Java{i}." + java_paths[i]["detail"] + " - " + java_paths[i]["bit"] + "bit", java_paths[i]["path"], "")
    tk.messagebox.showinfo("検出完了", "自動検出が完了しました")

    windows["autoScan_btn"].state(["!disabled"])
    windows["fullScan_btn"].state(["!disabled"])
    windows["selfSelect_btn"].state(["!disabled"])
    windows["back_btn"].state(["!disabled"])
    windows["back_btn_var"].set("戻る")

def select_java():
    out = selectFiles.selectCustomJava(saved_content["dirPath"])
    os.chdir(finddata())
    if out == "error":
        print("errored")
    else:
        json_open = open("data/java_path.json",'r',encoding="utf-8_sig")
        java_paths = json.load(json_open)
        for v in out:
            if v in java_paths:
                java_paths[v] = out[v]
            else:
                java_paths[v] = {}
                java_paths[v] = out[v]
        windows["listData"].delete(0, tk.END)
        for i in java_paths:
            windows["listData"].insert(tk.END, f"Java{i}." + java_paths[i]["detail"] + " - " + java_paths[i]["bit"] + "bit", java_paths[i]["path"], "")
        tk.messagebox.showinfo("処理成功", "反映しました")

def resetAsk():
    ret = tk.messagebox.askyesno('リセット', '初期状態に戻します。\n実行しますか？')
    if ret == True:
            resetData.resetData()
            get_json()
            tk.messagebox.showinfo("処理成功", "リセットしました。")
            toMainWindow()

# def openBrowser(url):
#     webbrowser.open(url)

def click_close():
    global windows
    saved_content["x"] = windows["now"].winfo_x()
    saved_content["y"] = windows["now"].winfo_y()
    save_json()
    windows["now"].destroy()
    sys.exit()