#------------------------------------------------------------------------------------
#  saucefinder.py
# 
#  ChenFengZhang 2020
# 
#
#  Dependencies:
#
#  - BeautifulSoup4
#  - Requests v2.2 or any version probably
#  - Pillow v7.0 or anything really
#  - pywin32 whatever version is on PyPI right now
#
#  created in Python 3.7.4 but there's no reason why it wouldn't work on any version
#  that isn't something ridiculous
#------------------------------------------------------------------------------------

import tkinter as tk
import time
import queue
import webbrowser
from io import BytesIO
from re import compile
from threading import Thread

from PIL import Image, ImageTk
from requests import get
from bs4 import BeautifulSoup
from win32api import EnumDisplayMonitors, GetMonitorInfo



class MainUI(tk.Frame):
    def __init__(self, root, dimensions):
        tk.Frame.__init__(self, root)
        self.root = root
        self.width, self.height, = dimensions
        self.q = queue.Queue()
        self.magic_number = 0
        self.memory = {}
        self.sauce_data = (1, 1, 1, 22, 22, 1, 222, "")
        self.baseUI()
        self.viewmode = 'scaled'


    def baseUI(self):
        self.root.title("Sauce Finder")
        self.img_tmp = ImageTk.PhotoImage(Image.open("template.png"))
        
        # header
        self.header = tk.Label(self.root, width=80, text="Sauce Finder", font=(None, 15))
        
        # 2nd line frame
        self.sub_f = tk.Frame(self.root, bg='red')
        
        # input frame
        self.input_f = tk.Frame(self.sub_f)
        self.prompt = tk.Label(self.input_f, text="Enter Sauce:")
        self.entry = tk.Entry(self.input_f, width=10)
        self.entry.bind("<FocusIn>", lambda event: self.entry.selection_range(0, tk.END))
        self.search = tk.Button(self.input_f, text="GO", command=self.fetchSauce)
        
        # settings
        self.settings_b = tk.Button(self.sub_f, text="settings", command=self.viewSettings)
        
        # sub headers
        self.title_l = tk.Label(self.root, text=" ", font=(None, 14), wraplength=875)
        self.subtitle_l = tk.Label(self.root, text=" ", font=(None, 12), wraplength=875)
        
        # preview frame
        self.preview_f = tk.Frame(self.root)
        self.cover_l = tk.Label(self.preview_f, image=self.img_tmp)
        self.side_f = tk.Frame(self.preview_f)
        self.fields_f = tk.Frame(self.side_f)
        self.options_f = tk.Frame(self.side_f)
        self.view_b = tk.Button(self.options_f, text="View", command=self.viewBook)
        self.link_b = tk.Button(self.options_f, text="Link")
        
        # UI visualization for testing 
        # self.preview_f['bg'] = "red"
        # self.cover_l['bg'] = "blue"
        # self.side_f['bg'] = "green"
        # self.fields_f['bg'] = "yellow"
        self.options_f['bg'] = "white"
        
        self.header.grid(row=0, column=0, padx=(30, 30), pady=(15, 10))
        
        self.sub_f.grid(row=1, column=0, padx=(30, 30), sticky="ew")
        
        self.input_f.grid(row=0, column=0, padx=(300, 300))
        self.prompt.grid(row=0, column=0, padx=(5, 2))
        self.entry.grid(row=0, column=1, padx=(2, 2))
        self.search.grid(row=0, column=2, padx=(2, 5))
        
        self.settings_b.grid(row=0, column=1, sticky="e")
        
        self.title_l.grid(row=2, column=0, padx=(30, 30), pady=(15, 2), sticky=tk.E+tk.W)
        self.subtitle_l.grid(row=3, column=0, padx=(30, 30), pady=(5, 10), sticky=tk.E+tk.W)

        self.preview_f.grid(row=4, padx=(30, 30), pady=(5, 15), sticky=tk.W+tk.E)
        self.cover_l.grid(row=0, column=0, padx=(10, 10), sticky=tk.N+tk.W)        
        self.side_f.grid(row=0, column=1, padx=(0, 10), sticky=tk.N)
        self.fields_f.grid(row=0, sticky=tk.N)
        # self.options_f.grid(row=1, pady=(0, 10))
        self.view_b.grid(row=0, column=0)
        self.link_b.grid(row=0, column=1)


    def renderPreview(self):
        if self.sauce_data:        
            title, subtitle, cover, fields, pages, upload_time, gallery, url = self.sauce_data
            
            # page count and upload date are rendered same as fields in this view
            fields.append(("Pages", [str(pages)]))
            fields.append(("Uploaded", [upload_time]))

            self.title_l['text'] = title
            self.subtitle_l['text'] = subtitle
            
            # I don't know why you have to do this- I just know that if you don't the picture won't appear
            self.cover_l['image'] = cover
            self.cover_l.image = cover
            # oh I know why now, if you don't bind your image to something the garbage collector will delete it once the function returns 
            # and the local variable goes out of scope
            
            # render fields & tags
            for index, (field, tags) in enumerate(fields):
                tk.Label(self.fields_f, text=field, font=(None, 12)).grid(row=index, column=0, sticky=tk.E+tk.N)
                tk.Label(self.fields_f, text=", ".join(tags), font=(None, 12), wraplength=440, justify='left').grid(row=index, column=1, sticky=tk.W+tk.N, padx=(10, 0), pady=(0, 20))
            self.link_b['command'] = lambda: webbrowser.open(url)
            self.options_f.grid(row=1, pady=(0, 10), sticky=tk.W)
            
        else: # make this another function later
            self.title_l['text'] = "File Not Found"
            self.subtitle_l['text'] = "server returned 404"


    def destroyChildren(self, frame):
        for itm in frame.winfo_children():
            itm.destroy()

    # Future loading events go in here
    def loadStart(self, magic_number):
        self.search['state'] = 'disabled'
        self.title_l['text'] = "Loading..."
        self.subtitle_l['text'] = "正在加载。。。"
        self.destroyChildren(self.fields_f)
        self.cover_l['image'] = self.img_tmp
        self.options_f.grid_forget()
        print("data fetch started for {}".format(magic_number))
        self.time_track = time.time()

    # and here
    def loadDone(self):
        end_time = time.time()
        print("response received {}s elapsed".format(end_time-self.time_track))
        self.search['state'] = 'normal'


    def fetchSauce(self):
        # focus an arbitrary label to remove focus from the entry field so the onfocus event to highlight the text can trigger when refocused
        # otherwise the entry will remain focused and the event can't trigger so the user would have to spam backspace or highlight manualy
        self.header.focus() # lol this is really fucking stupid but I can't think of a better way to do this
        
        self.magic_number = self.entry.get()
        
        # for offline testing
        if self.magic_number == "test":
            self.offlineTesting()
            return
        
        if self.magic_number.isdigit():
            self.loadStart(self.magic_number)
            Thread(target=self.getValues, args=(self.q, self.magic_number)).start()
            self.root.after(100, self.awaitSauce)
        else:
            self.title_l['text'] = "invalid number"
            self.subtitle_l['text'] = "无效号码"


    def awaitSauce(self):
        try:
            self.sauce_data = self.q.get(False) # if item is not availible raises queue.Empty error
            self.loadDone()
            self.renderPreview()
            
        except queue.Empty:
            self.root.after(100, self.awaitSauce)


    def getValues(self, q, magic_number):
        # magic_number is already a string by implementation but whatever
        url = "".join(("https://nhentai.net/g/", str(magic_number)))
        
        response = get(url)
        if not response.ok:
            q.put([])
            return

        page = BeautifulSoup(response.text, 'html.parser')
        
        blank_tag = page.new_tag('div')
        blank_tag.string = ""

        # div with all the preview info
        info = page.find('div', id='info')
        
        # get titles - not sure if it's possible for title to also not exist but just to be safe
        title = (info.find('h1') or blank_tag).string.strip()
        subtitle = (info.find('h2') or blank_tag).string.strip()
        
        # get image preview
        cover_container = page.find('div', id='cover')
        img_url = cover_container.find('img')['data-src']
        gallery = int(img_url.split("/")[-2]) # not the be confused with the gallery in the url

        # get image and load
        response = get(img_url)
        load = Image.open(BytesIO(response.content))
        cover = ImageTk.PhotoImage(load)
        
        # get all fields and tags
        visible_fields = info.find_all(lambda x: x.has_attr('class') and 'tag-container' in x['class'] and 'hidden' not in x['class'])
        fields = []
        for field_div in visible_fields:
            field_name, vals = field_div.contents[:2]
            fields.append((field_name.strip().strip(":"), [t.contents[0].strip() for t in vals.contents]))
        
        # get number of pages- this should always exist I hope
        pages = int(info.find('div', text=compile('pages')).string.split()[0])
        
        # get upload time
        upload_time = info.find('time').text

        q.put((title, subtitle, cover, fields, pages, upload_time, gallery, url))


    def viewBook(self):
        Viewer(self.root, self)

    
    def viewSettings(self):
        Settings(self)
    
    
    def offlineTesting(self):
        self.loadStart("test")
        self.sauce_data = ("offline testing", "wow is this legal?", ImageTk.PhotoImage(Image.open("untitled.png").resize((350, 511), Image.ANTIALIAS)), [("Parodies", ("Aokana",)), ("Characters", ("Kurashina Asuka",)), ("Tags", ("lolicon", "flying fish"))], 5, "time", 1, "http://softloli.moe")
        self.loadDone()
        self.renderPreview()
        
        
# all the code from here on down is a complete mess. not that the code above is clean, just after this it gets even worse
class Viewer(tk.Toplevel):
    def __init__(self, root, base):
        tk.Toplevel.__init__(self, base)
        self.root = root
        self.base = base
        self.pages = self.base.sauce_data[4]
        self.gallery = self.base.sauce_data[6]
        self.curr_page = 1
        self.pressed = False
        self.loading = False
        self.q = queue.Queue()
        self.xpad, self.ypad = 20, 20
        
        # this is so fucking jank I should just make them both classes with their own render method 
        self.modes = {'scaled': {'base': self.scaleView, 'render': self.scaleRender}, 'scrolled': {'base': self.scrollView, 'render': self.scrollRender}}
        self.UI()
        self.modes[self.base.viewmode]['base']()
        self.loadPage()
        
    
    def UI(self):
        self.transient(self.base) # popup appears as part of main window(not shown on taskbar)
        self.focus() # give keyboard focus to the toplevel object(for key bindings)
        self.grab_set() # prevent interaction with main window while viewer is open
        
        self.display_f = tk.Frame(self)
        self.display_f.pack(padx=(self.xpad, self.xpad), pady=(self.ypad, self.ypad))
        
        self.bind('<Left>', self.prevPage)
        self.bind('<Right>', self.nextPage)
        
        # system to restrict 1 action per key press- change page functionality is disabled until key is released
        self.bind('<KeyRelease-Left>', self.resetPress)
        self.bind('<KeyRelease-Right>', self.resetPress)


    def scaleView(self):
        win_h = self.base.height - 32 # 26px header + 2 * 3px border
        self.img_h = win_h - 2 * self.ypad
        self.img_w = int(self.img_h * 0.6968)
        win_w = self.img_w + 2 * self.xpad
        
        self.geometry("{}x{}+{}+0".format(self.img_w, win_h, (self.base.width - self.img_w) // 2))
        self.update_idletasks() # required for whatever reason

        self.img_l = tk.Label(self.display_f)
        self.img_l.grid()
        
    
    def scaleRender(self):
        self.img_display = ImageTk.PhotoImage(self.base.memory[self.curr_page].resize((self.img_w, self.img_h), Image.ANTIALIAS))
        self.img_l['image'] = self.img_display
    
    
    def scrollView(self):
        win_h = self.base.height - 32
        self.img_h = win_h - 2 * self.ypad
        
        self.screen = tk.Canvas(self.display_f, width=1080, height=win_h-2*self.ypad)
        self.bar = tk.Scrollbar(self.display_f, orient='vertical', command=self.screen.yview)
        self.screen.configure(yscrollcommand=self.bar.set)
        
        self.screen.grid(row=0, column=0)
        self.bar.grid(row=0, column=1, sticky='ns')
        
        self.bind("<MouseWheel>", self.scroll)


    def scrollRender(self):
        self.img_display = ImageTk.PhotoImage(self.base.memory[self.curr_page])
        self.screen.create_image(0, 0, image=self.img_display, anchor='nw')
        self.screen.configure(scrollregion=self.screen.bbox('all'))
        self.screen.yview_moveto(0)
        

    def scroll(self, event):
        if event.state == 0:
            self.screen.yview_scroll(int(-1 * (event.delta / 120)), 'units')
    
    
    def renderPage(self):
        self.img_l['image'] = self.base.memory[self.curr_page]
        print(self.base.memory[self.curr_page])


    def loadPage(self):
        self.loading = True
        try:
            image = self.base.memory[self.curr_page]
            print("Already loaded")
            self.q.put(0)
        except KeyError:
            
            # offline testing
            if self.base.magic_number == "test":
                self.base.memory[self.curr_page] = Image.open("u" + str(self.curr_page) + ".png")
                print("load testing image")
                self.q.put(0)
            
            else:
                print("image download")
                Thread(target=self.downloadImage, args=(self.gallery, self.curr_page, self.q, self.base.memory)).start()
        self.waitImage()
        

    def waitImage(self):
        try:
            response = self.q.get(False)
            self.modes[self.base.viewmode]['render']()
            self.loading = False
        except queue.Empty:
            self.root.after(100, self.waitImage)

    
    def downloadImage(self, gallery, page, q, mem):
        print("inthread")
        url = "".join(("https://i.nhentai.net/galleries/", str(gallery), "/", str(page), ".jpg"))
        load = Image.open(BytesIO(get(url).content))
        print("got image")
        load = load.resize((516, 740), Image.ANTIALIAS)
        print("resized")
        image = ImageTk.PhotoImage(load)
        mem[page] = image
        q.put(0)
        print("thread done")


    def nextPage(self, event):
        print("next")
        if not self.pressed and not self.loading and self.curr_page < self.pages:
            self.pressed = True
            self.curr_page += 1    
            self.loadPage()


    def prevPage(self, event):
        print("prev")
        if not self.pressed and not self.loading and self.curr_page > 1:
            self.pressed = True
            self.curr_page -= 1
            self.loadPage()


    def resetPress(self, event):
        self.pressed = False
        
    
    # testing alternative ui
    def altUI(self):
        self.canvas = tk.Canvas(self)



class Settings(tk.Toplevel):
    def __init__(self, base):
        tk.Toplevel.__init__(self, base)
        self.base = base
        self.view_options = ""
        self.selection = tk.StringVar()
        self.selection.set(self.base.viewmode)
        self.UI()

        
    def UI(self):
        self.transient(self.base)
        self.grab_set()
        self.focus()
        
        self.l = tk.Label(self, text="viewer mode")
        self.l.grid(row=0, column=0)
        
        tk.Radiobutton(self, text="scaled", variable=self.selection, value="scaled").grid(row=0, column=1)
        tk.Radiobutton(self, text="scrolled", variable=self.selection, value="scrolled").grid(row=0, column=2)
        
        self.ok = tk.Button(self, text="ok", command=self.exit)
        self.cancel = tk.Button(self, text="cancel", command=self.destroy)
        
        self.ok.grid(row=1, column=1, sticky='ew')
        self.cancel.grid(row=1, column=2, sticky='ew')
        
    def exit(self):
        self.base.viewmode = self.selection.get()
        self.destroy()


def main():
    for monitor in EnumDisplayMonitors():
        info = GetMonitorInfo(monitor[0])
        if info['Flags'] == 1:
            break

    root = tk.Tk()
    gui = MainUI(root, info['Work'][2:])
    root.mainloop()


if __name__ == "__main__":
    main()
