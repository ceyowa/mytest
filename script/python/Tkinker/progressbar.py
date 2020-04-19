from tkinter import *
from tkinter import ttk


class GressBar():
    def __init__(self, top=NONE):
        if top is NONE:
            top = Toplevel()
        self.master = top
        self._destroyed = False

        top.overrideredirect(True)
        top.title("进度条")
        Label(top, text="任务正在运行中,请稍等……", fg="green").pack(pady=2)
        prog = ttk.Progressbar(top, mode='indeterminate', length=200)
        prog.pack(pady=10, padx=35)
        prog.start()

        top.resizable(False, False)
        top.grab_set()
        top.update()
        curWidth = top.winfo_width()
        curHeight = top.winfo_height()
        scnWidth, scnHeight = top.maxsize()
        tmpcnf = '+%d+%d' % ((scnWidth - curWidth) / 2, (scnHeight - curHeight) / 2)
        top.geometry(tmpcnf)

    def start(self):
        if self._destroyed:
            return
        top = self.master
        top.mainloop()

    def quit(self):
        if self.master:
            self.master.destroy()
        self.master = None
        self._destroyed = True
