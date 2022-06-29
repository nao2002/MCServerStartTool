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
import webbrowser
import resetData

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

    main_win = tk.Tk()

    # メインウィンドウ
    main_win.title("MC_Server_Starter")
    if saved_content["x"] <= -1.0:
        main_win.geometry("520x130")
    else:
        x = saved_content["x"]
        y = saved_content["y"]
        main_win.geometry(f"520x130+{x}+{y}")
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

    #実行ボタン
    app_btn = ttk.Button(main_frm, text="起動", command=start)

    detail_btn = ttk.Button(main_frm, text="詳細設定", command=toDetailWindow)

    # ウィジェットの配置
    folder_label.place(x=5, y=15)
    folder_box.place(x=85, y=15, width=340, height=23)
    folder_btn.place(x=425, y=14, height=25)
    app_btn.place(x=85,y=80, width=100, height=25)
    detail_btn.place(x=315,y=80,width=110,height=25)

    # 配置設定
    main_win.columnconfigure(0, weight=1)
    main_win.rowconfigure(0, weight=1)
    main_frm.columnconfigure(1, weight=1)

    windows["now"] = main_win
    windows["frm"] = main_frm
    main_win.protocol("WM_DELETE_WINDOW", click_close)
    main_win.mainloop()

def start():
    windows["now"].wm_state('iconic')
    errorMessage = startServer.startServer(saved_content=saved_content)
    print(errorMessage)
    if errorMessage != "":
        windows["now"].wm_state('normal')
        if errorMessage != "cancel":
            tk.messagebox.showwarning("エラーが発生しました", errorMessage)

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
    detail_win.geometry(f"420x445+{x}+{y}")
    detail_win.resizable(width=False, height=False)

    # メインフレーム
    main_frm = ttk.Frame(detail_win)
    main_frm.grid(column=0, row=0, sticky=tk.NSEW, padx=5, pady=10)

    #JAVA
    java_label = ttk.Label(main_frm, text="Javaファイルの設定")
    java_btn = ttk.Button(main_frm, text="設定画面を開く", command=toJavaWindow)

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
    main_frm, padding=(10), text='log4j2対策を有効化　*ver1.6以下/ver1.18以上は必要なし',
    variable=log4j2_var, onvalue='1', offvalue='0',
    command=partial(toggleButtonSave, log4j2_var, "log4j2"))

    #バージョン自動検知
    vCheck_var = StringVar(value=str(saved_content["vCheck"]))
    vCheck_toggle = ttk.Checkbutton(
    main_frm, padding=(10), text='バージョンの自動検知　*起動にかかる時間が増えることがあります',
    variable=vCheck_var, onvalue='1', offvalue='0',
    command=partial(toggleButtonSave, vCheck_var, "vCheck"))

    #サーバーエラー確認
    errorCheck_label = ttk.Label(main_frm, text="サーバーのエラーチェックをする")
    errorCheck_btn = ttk.Button(main_frm, text="実行",command=errorCheck)

    #リセット
    reset_label = ttk.Label(main_frm, text="初期状態に戻す")
    reset_btn = ttk.Button(main_frm, text="リセット", command=resetAsk)

    #支援
    support_label = ttk.Label(main_frm, text="開発者を支援する")
    support_btn = ttk.Button(main_frm, text="支援する", command=partial(openBrowser,'https://paypal.me/lyomiproj/'))

    # ウィジェット作成（実行ボタン）
    back_btn = ttk.Button(main_frm, text="戻る", command=toMainWindow)

    # ウィジェットの配置
    #java_label.grid(column=0, row=0, pady=10, columnspan=3, sticky=tk.W)
    #java_btn.grid(column=2, row=0, columnspan=2, sticky=tk.E)
    #directory_label.grid(column=0, row=1, sticky=tk.W, columnspan=1)
    #directory_box.grid(column=1, row=1, sticky=tk.EW, columnspan=3)
    #directory_btn.grid(column=2, row=1, columnspan=1)
    #memory_label.grid(column=0,row=2)
    #memory_box.grid(column=1,row=2, sticky=tk.W)
    #memory_comb.grid(column=2, row=2, sticky=tk.E)
    #gui_toggle.grid(column=0, row=3, pady=10)
    #log4j2_toggle.grid(column=0, row=4)
    #back_btn.grid(column=0, row=5, pady=10)

    java_label.place(x=20, y=7)
    java_btn.place(x=270, y=5, width=100,height=25)
    directory_label.place(x=20, y=58)
    directory_btn.place(x=270,y=55, width=100,height=25)
    directory_box.place(x=25, y=83,width=345)
    memory_label.place(x=20, y=135)
    memory_box.place(x=200, y=135, width=100)
    memory_comb.place(x=300, y=135, width=70)
    gui_toggle.place(x=13, y=170)
    log4j2_toggle.place(x=13, y=205)
    vCheck_toggle.place(x=13,y=240)
    #reset_label.place(x=20, y=285)
    #reset_btn.place(x=270, y=285, width=100, height=25)
    #support_label.place(x=20, y=335)
    #support_btn.place(x=270, y=335, width=100, height=25)
    errorCheck_label.place(x=20, y=285)
    errorCheck_btn.place(x=270, y=285, width=100, height=25)
    reset_label.place(x=20, y=335)
    reset_btn.place(x=270, y=335, width=100, height=25)
    back_btn.place(x=150, y=395, width=100)

    # 配置設定
    detail_win.columnconfigure(0, weight=1)
    detail_win.rowconfigure(0, weight=1)
    main_frm.columnconfigure(1, weight=1)

    windows["now"] = detail_win
    windows["frm"] = main_frm
    detail_win.protocol("WM_DELETE_WINDOW", click_close)
    detail_win.mainloop()

def errorCheck():
    path = selectFiles.openFiledialog(saved_content["dirPath"],saved_content["path"])
    ret = tk.simpledialog.askstring("時間設定", "起動にかける最長時間(秒)を入力してください\nこの秒数を超えるとタイムアウトします")
    if ret == None:
        return
    elif startServer.isint(ret):
        curPath = saved_content["path"]
        saved_content["path"] = path
        save_json()
        windows["now"].wm_state('iconic')
        errorMessage = startServer.startServer(saved_content, int(ret))
        saved_content["path"] = curPath
        save_json()
        windows["now"].wm_state('normal')
        if errorMessage == "":
            errorMessage == "エラーは検出されませんでした"
        tk.messagebox.showinfo("検出結果", errorMessage)
    else:
        tk.messagebox.showwarning("エラーが発生しました", "半角数字のみで指定してください")
        return

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

    autoScan_btn = ttk.Button(main_frm, text="自動検出", command=partial(askScan, "default"))

    fullScan_btn = ttk.Button(main_frm, text="詳細検出", command=partial(askScan, "full"))

    selfSelect_btn = ttk.Button(main_frm, text="手動選択", command=select_java)

    # ウィジェット作成（実行ボタン）
    back_btn = ttk.Button(main_frm, text="戻る", command=toDetailWindow)

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

def memoryComboSelect(event):
    saved_content["memoryUnit"] = windows["memoryComb"].get()
    save_json()

def memoryChanged(arg1, arg2, arg3):
    saved_content["memory"] = windows["memoryBox"].get()
    save_json()

def toggleButtonSave(var,path):
    saved_content[str(path)] = var.get()
    save_json()

def askScan(mode):
    if mode == "full":
        ret = tk.messagebox.askyesno('詳細検出', 'この処理にはかなり時間がかかることがあります\n実行後はウィンドウを閉じずにしばらくお待ちください。\n実行しますか？')
        if ret == True:
            javaFullScan("fullScan")
    elif mode == "default":
        ret = tk.messagebox.askyesno('自動検出', 'これには少し時間がかかることがあります\n実行しますか？')
        if ret == True:
            javaFullScan("default")

def javaFullScan(mode):
    ret = {}
    if mode == "default":
        for d in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if os.path.exists(f'{d}:'):
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

def openBrowser(url):
    webbrowser.open(url)

def click_close():
    global windows
    saved_content["x"] = windows["now"].winfo_x()
    saved_content["y"] = windows["now"].winfo_y()
    save_json()
    windows["now"].destroy()
    sys.exit()