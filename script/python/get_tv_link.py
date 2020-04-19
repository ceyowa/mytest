#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2020-03-29 16:59:05
import queue
import threading
import time
from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

import requests
# 引入Beautiful Soup包
# from bs4 import BeautifulSoup
from pyquery import PyQuery

from Tkinker.progressbar import GressBar

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}


# 支持从www.meijubie.com获取下载链接
class BaseWebSiteProcesser:
    def __init__(self, website):
        self.webSite = website

    def getDownloadLink(self, targetUrl):
        return []


class Meijubie(BaseWebSiteProcesser):
    def __init__(self):
        super().__init__("www.meijubie.com")

    def getDownloadLink(self, requestUrl):
        r = requests.get(requestUrl, headers=headers)
        # print(r.text)
        # soup = BeautifulSoup(r.text, 'lxml')
        # links = soup.findAll("#downlist1 .ldgcopy")
        doc = PyQuery(r.text)
        # print(doc)
        links = doc('#downlist1 script').text().split(';')[0].split('=')[1].strip().replace('"', '').split('###')
        results = []
        for item in links:
            results.append(item.split('$')[1])
        # print(results)
        return results


PROCESS_FUN_LIST = [Meijubie()]
PROCESS_FUN_DICT = {}
for f in PROCESS_FUN_LIST:
    PROCESS_FUN_DICT.setdefault(f.webSite, f)
PROCESS_FUN_NAME_LIST = list(map(lambda x: x.webSite, PROCESS_FUN_LIST))


class MY_GUI():
    def __init__(self, tk_win):

        self.tk_win = tk_win

        self.input_url = StringVar()
        self.input_url.set('https://www.meijubie.com/movie/index44655.html')

        self.processing = False

        self.selectProcess = StringVar()

        self.init_window()

        self.notify_queue = queue.Queue()
        self.process_msg()

    def process_msg(self):
        # self.tk_win.after(500, self.process_msg)
        # while not self.notify_queue.empty():
        #     try:
        #         msg = self.notify_queue.get()
        #         if msg[0] == 'gress_bar_quit':
        #             self.gress_bar.quit()
        #
        #     except queue.Empty:
        pass

    def set_init_window(self):

        self.tk_win.grid_rowconfigure(1, weight=1)
        self.tk_win.grid_columnconfigure(0, weight=1)

        labelframe = LabelFrame(text="输入")
        labelframe.grid_columnconfigure(1, weight=1)
        labelframe.grid(column=0, row=0, padx=10, pady=10, sticky=EW)

        Label(labelframe, text="目标网址", justify=LEFT, width=10).grid(row=0, column=0)
        entry = Entry(labelframe, textvariable=self.input_url)
        entry.grid(row=0, column=1, sticky=EW, padx=5)
        entry.bind('<Key-Return>', self.getResourceLink)

        self.button = Button(labelframe, text="获取", command=self.getResourceLink, width=10)
        self.button.grid(row=0, column=2, sticky=E, padx=5)

        Label(labelframe, text="处理器", justify=LEFT, width=10).grid(row=1, column=0)
        select_process = ttk.Combobox(labelframe, textvariable=self.selectProcess,
                                      state="readonly",
                                      values=PROCESS_FUN_NAME_LIST,
                                      width=90)
        select_process.set("请选择网址处理器")
        select_process.grid(row=1, column=1, sticky=EW, columnspan=2, padx=5, pady=5)
        if len(PROCESS_FUN_NAME_LIST) > 0:
            select_process.set(PROCESS_FUN_NAME_LIST[0])

        output_frame = LabelFrame(text="链接结果")
        output_frame.grid(column=0, row=1, sticky=NSEW, padx=10)

        self.copy_btn = Button(output_frame, text="复制到剪贴板", command=lambda: self.copy(self.output_txt))
        self.copy_btn.config(state=DISABLED)
        self.copy_btn.pack()

        self.output_txt = ScrolledText(output_frame)
        self.output_txt.pack(side=TOP, expand=TRUE, fill=BOTH, padx=10, pady=10)
        self.output_txt.bind("<Button-3>", lambda x: self.rightKey(x, self.output_txt))  # 绑定右键鼠标事件
        self.output_txt.bind("<<Selection>>", self.on_text_selection)  # 绑定选择事件

        # self.output_txt.grid(column=0, columnspan=4)
        # self.vbar = ttk.Scrollbar(output_frame, orient=VERTICAL, command=self.output_txt.yview)
        # self.output_txt.configure(yscrollcommand=self.vbar.set)

    def on_text_selection(self, event=NONE):
        try:
            selection = self.output_txt.get(SEL_FIRST, SEL_LAST)
        except Exception:
            selection = NONE
        if selection is not NONE and len(selection) > 0:
            self.copy_btn.config(state=NORMAL)
        else:
            self.copy_btn.config(state=DISABLED)

    def init_window(self):
        self.tk_win.title("网页链接获取")
        # 窗口宽高为100
        ww = 800
        wh = 600
        self.tk_win.minsize(int(ww / 2), int(wh / 2))
        # 得到屏幕宽度
        sw = self.tk_win.winfo_screenwidth()
        # 得到屏幕高度
        sh = self.tk_win.winfo_screenheight()
        # 窗口位置
        x = (sw - ww) / 2
        y = (sh - wh) / 2
        self.tk_win.geometry("%dx%d+%d+%d" % (ww, wh, x, y))

    def getResourceLink(self, event=NONE):
        if self.processing:
            return
        self.processing = True
        # 禁用按钮
        self.button.state = DISABLED
        th = threading.Thread(target=self.doGetResourceLink)
        th.setDaemon(True)
        th.start()
        # 启动进度条
        self.gress_bar = GressBar()
        self.gress_bar.start()
        pass

    def doGetResourceLink(self):
        self.output_txt.insert(END, '##########################Begin#########################\n')
        requestUrl = self.input_url.get()
        self.output_txt.insert(END, requestUrl + '\n')
        self.output_txt.insert(END, '\n')

        processer = PROCESS_FUN_DICT[self.selectProcess.get()]
        if processer is NONE:
            self.output_txt.insert(END, '未找到对应的网站处理器\n')
        else:
            last_time = time.time_ns()
            results = processer.getDownloadLink(requestUrl)
            index_start = self.output_txt.index("end-1c linestart")
            for item in results:
                self.output_txt.insert(END, item + '\n')
            index_end = self.output_txt.index("end-1c linestart")
            self.output_txt.insert(END, '\n耗时=%d毫秒\n' % ((time.time_ns() - last_time) / 1E6))

        self.output_txt.insert(END, '###########################End##########################\n')

        self.gress_bar.quit()
        self.button.state = NORMAL
        self.processing = False

        # 移除之前的选择
        self.output_txt.tag_remove(SEL, '1.0', END)
        # 设置选中状态
        print("\nstart=%s,end=%s\n" % (index_start, index_end))
        self.output_txt.tag_add(SEL, index_start, index_end)
        self.output_txt.focus_set()
        # self.output_txt.selection_range(index_start, index_end)

    def cut(self, editor, event=None):
        editor.event_generate("<<Cut>>")

    def copy(self, editor, event=None):
        editor.event_generate("<<Copy>>")

    def paste(self, editor, event=None):
        editor.event_generate('<<Paste>>')

    def rightKey(self, event, editor):
        menubar = Menu(self.tk_win, tearoff=False)  # 创建一个菜单
        menubar.delete(0, END)
        # menubar.add_command(label='剪切', command=lambda: self.cut(editor))
        menubar.add_command(label='复制', command=lambda: self.copy(editor))
        # menubar.add_command(label='粘贴', command=lambda: self.paste(editor))
        menubar.post(event.x_root, event.y_root)


def main():
    tk_win = Tk()
    ui = MY_GUI(tk_win)

    ui.set_init_window()
    tk_win.mainloop()
    pass


if __name__ == "__main__":
    main()
