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
#  just install from requirements.txt
#
#
#  this is of course a joke but I'm sure there's some use to it
#
#------------------------------------------------------------------------------------

import tkinter as tk
from tkinter.filedialog import askdirectory
import time
import os
import queue
from io import BytesIO
from re import compile
from threading import Thread
from webbrowser import open as browser

from PIL import Image, ImageTk
from requests import get, exceptions
from bs4 import BeautifulSoup
from win32api import EnumDisplayMonitors, GetMonitorInfo



class SauceFinder(tk.Frame):
    """
    defines the main window
    """
    def __init__(self, root, dimensions):
        tk.Frame.__init__(self, root)
        self.root = root
        self.width, self.height, = dimensions
        self.q = queue.Queue()
        self.loading = False
        self.memory = {}
        self.cancel = False
        self.v = None
        self.sauce_data = {'title': '', 'subtitle': '', 'cover': None, 'fields': '', 'pages': 0, 'upload': '', 'gallery': '', 'number': '', 'ending': ''}
        self.baseUI()
        with open("config.txt", "r") as f:
            try:
                self.viewmode, self.folder = f.read().split("\n")
            except ValueError: # bad save file
                self.viewmode = "scaled"
                self.folder = f"{os.getcwd()}/saves"
        self.entry.focus()


    def baseUI(self):
        self.root.title("Sauce Finder")
        self.img_tmp = ImageTk.PhotoImage(Image.open("tmep.png"))

        head_f = tk.Frame(self, borderwidth=3, relief='ridge')
        
        # header
        header = tk.Label(head_f, width=80, text="Sauce Finder", font=(None, 15))
        
        # 2nd line frame
        sub_f = tk.Frame(head_f)

        # input frame
        input_f = tk.Frame(sub_f)
        prompt = tk.Label(input_f, text="Enter Number")
        self.entry = tk.Entry(input_f, width=8)
        self.entry.bind("<FocusIn>", lambda event: self.entry.selection_range(0, tk.END))
        self.entry.bind("<Return>", lambda event: self.fetchSauce())
        self.search = tk.Button(input_f, width=6, text="search", command=self.fetchSauce)
        
        # settings
        settings_b = tk.Button(sub_f, width=10, text="settings", command=lambda: Settings(self))
        
        # sub headers
        self.title_l = tk.Label(self, text=" ", font=(None, 14), wraplength=875)
        self.subtitle_l = tk.Label(self, text=" ", font=(None, 13), wraplength=875)

        # preview frame
        preview_f = tk.Frame(self)
        self.cover_l = tk.Label(preview_f, image=self.img_tmp)
        side_f = tk.Frame(preview_f)
        self.fields_f = tk.Frame(side_f)

        # bottom part under tags
        self.footer = tk.Frame(side_f)
        options_f = tk.Frame(self.footer)
        view_b = tk.Button(options_f, width=10, text="View", command=self.viewBook)
        link_b = tk.Button(options_f, width=10, text="Link", command=lambda: browser(f"https://nhentai.net/g/{self.sauce_data['number']}/"))
        self.down_b = tk.Button(options_f, width=10, text="Save", command=self.save)
        
        # download status frame
        self.status_f = tk.Frame(self.footer)
        self.s_l = tk.Label(self.status_f, width=11)
        self.down_l = tk.Label(self.status_f, width=7)
        bar_container = tk.Frame(self.status_f, height=20, width=150, bg='red')
        self.bar = tk.Frame(bar_container, height=20, width=0, bg='green')
        
        # yikes
        self.pack(padx=(30, 30))

        head_f.grid(row=0, pady=(15, 0))
        header.grid(row=0, column=0, pady=(5, 5))
        
        sub_f.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        sub_f.grid_columnconfigure(0, weight=1)
        sub_f.grid_columnconfigure(2, weight=1)
        input_f.grid(row=0, column=1, padx=(20 + 10 * 8, 0))
        prompt.grid(row=0, column=0, padx=(5, 5))
        self.entry.grid(row=0, column=1, padx=(5, 5))
        self.search.grid(row=0, column=2, padx=(5, 5))
        
        settings_b.grid(row=0, column=2, sticky="e", padx=(0, 20))
        
        self.title_l.grid(row=1, column=0, pady=(15, 2), sticky='ew')
        self.subtitle_l.grid(row=2, column=0, pady=(5, 10), sticky='ew')

        preview_f.grid(row=3, pady=(5, 15), sticky='ew')
        self.cover_l.grid(row=0, column=0, padx=(10, 10), sticky='nw')        
        side_f.grid(row=0, column=1, padx=(0, 10), sticky='n')
        self.fields_f.grid(row=0, sticky='nw')
        options_f.grid(row=0, pady=(0, 10))
        view_b.grid(row=0, column=0, padx=(20, 20))
        link_b.grid(row=0, column=1, padx=(20, 20))
        self.down_b.grid(row=0, column=2, padx=(20, 20))

        self.s_l.grid(row=0, column=0, padx=(20, 0), sticky='w')
        self.down_l.grid(row=0, column=1, padx=(0, 5), sticky='e')
        bar_container.grid(row=0, column=2, padx=(0, 15), sticky='w')
        bar_container.grid_propagate(0)
        self.bar.grid(sticky='w')
        tk.Button(self.status_f, text="cancel", command=self.stop).grid(row=0, column=3)


    def renderPreview(self):
        data = self.sauce_data

        self.title_l['text'] = data['title']
        self.subtitle_l['text'] = data['subtitle']
        self.cover_l['image'] = data['cover']

        # render fields & tags
        fields = data['fields']
        
        for index, (field, tags) in enumerate(fields):
            tk.Label(self.fields_f, text=field, font=(None, 12, 'bold')).grid(row=index, column=0, sticky='ne')
            tk.Label(self.fields_f, text=",  ".join(tags), font=(None, 12), wraplength=420, justify='left').grid(row=index, column=1, sticky='nw', padx=(10, 0), pady=(0, 15))
        self.footer.grid(row=1, pady=(20, 10), sticky=tk.W)


    def errPage(self, data):
        self.title_l['text'] = data[0]
        self.subtitle_l['text']  = data[1]
        

    def destroyChildren(self, frame):
        """
        permanently delete all the items spawned inside a widget
        """
        for itm in frame.winfo_children():
            itm.destroy()


    def loadStart(self):
        """
        procedures to be run when preview loading begins
        """
        self.search['state'] = 'disabled'
        self.title_l['text'] = "Loading..."
        self.subtitle_l['text'] = "正在加载。。。"
        self.destroyChildren(self.fields_f) # destroy any tags rendered from previous previews
        self.cover_l['image'] = self.img_tmp
        self.footer.grid_forget()
        self.status_f.grid_forget()
        self.down_l['text'] = ''
        print(f"data fetch started for {self.sauce_data['number']}")
        self.time_track = time.time()


    def loadDone(self):
        """
        procedures to be run when preview loading ends
        """
        end_time = time.time()
        print(f"response received {end_time - self.time_track:.3f}s elapsed")
        self.search['state'] = 'normal'


    def fetchSauce(self):
        """
        run when user clicks go/enter key, starts the thread with fetch process and starts waiting for response
        """
        if not (self.loading or self.v):
            # remove focus form entry so onfocus event can trigger again
            self.cover_l.focus()
            
            self.sauce_data['number'] = self.entry.get()
            # some validation- won't catch invalid numbers
            if self.sauce_data['number'].isdigit():
                self.loadStart()
                Thread(target=self.getFixed).start()
                self.root.after(100, self.awaitSauce)
            else:   
                self.errPage(("invalid number", "无效号码"))
                self.destroyChildren(self.fields_f)
                self.cover_l['image'] = self.img_tmp
                self.footer.grid_forget()    


    def awaitSauce(self):
        """
        wait for fetch thread to finish and push results in the queue before render
        """
        try:
            response = self.q.get(False) # if item is not availible raises queue.Empty error
            self.loadDone()
            self.errPage(response) if response else self.renderPreview()
                
        except queue.Empty:
            self.root.after(100, self.awaitSauce)
    
    
    def getFixed(self):
        data = self.sauce_data
        url = f"https://nhentai.net/g/{data['number']}"

        try:
            response = get(url, timeout=5)
        except exceptions.ConnectTimeout: # timeout - either server down or connection is bad
            self.q.put(("connection timeout", "check your connection"))
            return
        except: # probably the result of no internet
            self.q.put(("Fatal Error", "(is your internet working?)"))
            return

        if not response.ok: # probably error 404
            self.q.put(("File Not Found", "server returned 404"))
            return
        
        page = BeautifulSoup(response.text, 'html.parser')

        blank_tag = page.new_tag('div')
        blank_tag.string = ""

        info = page.find('div', id='info')
        
        data['title'] = "".join((info.find('h1', class_='title') or blank_tag).strings)
        data['subtitle'] = "".join((info.find('h2', class_='title') or blank_tag).strings)

        fields = []
        for tag in info.find('section', id='tags'):
            if 'hidden' not in tag['class']:
                ls = tag.stripped_strings
                cat = next(ls)
                tags = list(ls)[::2]
                fields.append((cat, tags))
                if cat == "Pages:":
                    data['pages'] = int(tags[0])
        data['fields'] = fields
        
        # cover
        cover_container = page.find('div', id='cover')
        img_url = cover_container.find('img', class_='lazyload')['data-src']
        split = img_url.split("/")
        data['gallery'] = split[-2]
        
        # for whatever reason the file types are not always consistent
        # assume ending of first image is primary ending
        data['ending'] = split[-1].split(".")[-1]
        data['other'] = ('jpg', 'png')[~('jpg', 'png').index(data['ending'])]
        
        # get cover image and load
        response = get(img_url)
        load = Image.open(BytesIO(response.content))
        w, h = load.size
        if w > 350: # scale the cover if too big
            load = load.resize((350, 350 * h // w), Image.ANTIALIAS)
        data['cover'] = ImageTk.PhotoImage(load)

        self.memory.clear()
        
        loc = f"{self.folder}/{data['number']}"
        if os.path.exists(loc):
            for file in os.scandir(loc):
                try:
                    self.memory[int(os.path.splitext(file.name)[0])] = Image.open(file.path)
                except: # for whatever reason the image can not be processed
                    pass
        try:
            self.memory[1]  
        except KeyError:
            # get first image of book
            self.memory[1] = Image.open(BytesIO(get(f"https://i.nhentai.net/galleries/{data['gallery']}/1.{data['ending']}").content))

        self.q.put(0)


    def getValues_LEGACY(self):
        """
        No longer functional


        This worked on the old version of the site up that was updated around 06/2020
        
        rip why no api
        """
        data = self.sauce_data
        url = f"https://nhentai.net/g/{data['number']}"

        try:
            response = get(url, timeout=5)
        except exceptions.ConnectTimeout: # timeout - either server down or connection is bad
            self.q.put(("connection timeout", "check your connection"))
            return
        except: # probably the result of no internet
            self.q.put(("Fatal Error", "(is your internet working?)"))
            return

        if not response.ok: # probably error 404
            self.q.put(("File Not Found", "server returned 404"))
            return

        page = BeautifulSoup(response.text, 'html.parser')
        
        blank_tag = page.new_tag('div')
        blank_tag.string = ""

        # div with all the preview info
        info = page.find('div', id='info')
        
        # get titles - not sure if it's possible for title to also not exist but just to be safe
        data['title'] = (info.find('h1') or blank_tag).string.strip()
        data['subtitle'] = (info.find('h2') or blank_tag).string.strip()
        
        # get image preview
        cover_container = page.find('div', id='cover')
        img_url = cover_container.find('img')['data-src']
        split = img_url.split("/")
        
        data['gallery'] = split[-2]
        
        # for whatever reason the file types are not always consistent
        # assume ending of first image is primary ending
        data['ending'] = split[-1].split(".")[-1]
        data['other'] = ('jpg', 'png')[~('jpg', 'png').index(data['ending'])]

        # get cover image and load
        response = get(img_url)
        load = Image.open(BytesIO(response.content))
        w, h = load.size
        if w > 350: # scale the cover if too big
            load = load.resize((350, 350 * h // w), Image.ANTIALIAS)
        data['cover'] = ImageTk.PhotoImage(load)
        
        # get all fields and tags
        visible_fields = info.find_all(lambda x: x.has_attr('class') and 'tag-container' in x['class'] and 'hidden' not in x['class'])
        fields = []
        for field_div in visible_fields:
            field_name, vals = field_div.contents[:2]
            fields.append((field_name.strip().strip(":"), [t.contents[0].strip() for t in vals.contents]))
        data['fields'] = fields
        
        # get number of pages- this should always exist I hope
        data['pages'] = int(info.find('div', text=compile('pages')).string.split()[0])
        
        # get upload time
        data['upload'] = info.find('time').text
        
        self.memory.clear()
        
        loc = f"{self.folder}/{data['number']}"
        if os.path.exists(loc):
            for file in os.scandir(loc):
                try:
                    self.memory[int(os.path.splitext(file.name)[0])] = Image.open(file.path)
                except: # for whatever reason the image can not be processed
                    pass
        try:
            self.memory[1]  
        except KeyError:
            # get first image of book
            self.memory[1] = Image.open(BytesIO(get(f"https://i.nhentai.net/galleries/{data['gallery']}/1.{data['ending']}").content))

        self.q.put(0)

    
    def save(self):
        """
        saves the images so you can fap later or something

        will download anything that is not in memory
        """
        print("start saveall")
        self.loading = True
        self.cancel = False
        self.down_b['state'] = 'disabled'
        self.d_page = 1
        self.s_l['text'] = "downloading"
        self.down_l['text'] = f"0/{self.sauce_data['pages']}"
        self.status_f.grid(row=1, sticky='w')
        self.loc = f"{self.folder}/{self.sauce_data['number']}"
        if not os.path.exists(self.loc):
            os.mkdir(self.loc)
        self.root.after(10, self.downprocess)


    def downprocess(self):
        # calls store which then calls this in a loop until all images are gone through
        if self.cancel:
            self.s_l['text'] = "cancelled"
            self.down_b['state'] = 'normal'
            self.loading = False
        elif self.d_page > self.sauce_data['pages']:
            print("download complete")
            self.s_l['text'] = "finished"
            self.down_b['state'] = 'normal'
            self.loading = False
        else:
            try:
                self.store()
            except KeyError:
                Thread(target=self.imgDownload, args=(self.d_page, self.q)).start()
                self.root.after(100, self.waitImg)


    def store(self):
        """
        will not overwrite anything already existing
        """
        page, total = self.d_page, self.sauce_data['pages']
        image = self.memory[page]

        img_path = "{}/{}.{}".format(self.loc, self.d_page, {"JPEG": "jpg", "PNG": "png"}[image.format])
        if not os.path.exists(img_path): # won't overwrite
            image.save(img_path)
            print(f"{page} saved")
        self.down_l['text'] = f"{page}/{total}"
        self.bar['width'] = 150 * page // total
        self.d_page += 1
        self.root.after(10, self.downprocess)


    def stop(self):
        self.cancel = True


    def waitImg(self):
        try:
            response = self.q.get(False)
            self.store()
        except queue.Empty:
            self.root.after(100, self.waitImg)


    def imgDownload(self, num, q): # the download now runs from here so that a save option is available
        """
        for downloading images- the viewer also uses this
        """
        url = f"https://i.nhentai.net/galleries/{self.sauce_data['gallery']}/{num}"
        print(f"{url}.{self.sauce_data['ending']}")
        try:
            response = get(f"{url}.{self.sauce_data['ending']}", timeout=5)
        except: # loading missing image if download fail
            self.memory[num] = Image.open("img.png")
        else:
            if not response.ok: # file encoding is jank
                # need to repeat this again is there a better way to do this
                try:
                    response = get(f"{url}.{self.sauce_data['other']}", timeout=5) ## YIKES
                except:
                    self.memory[num] = Image.open("img.png")
            load = Image.open(BytesIO(response.content))
            self.memory[num] = load
        q.put(0)


    def viewBook(self):
        """
        run the viewer
        """
        if not self.v:
            print("viewer up")
            self.v = Viewer(self)
            self.v.protocol("WM_DELETE_WINDOW", self.viewer_die)


    def viewer_die(self):
        self.v.destroy()
        self.v = None
        print("viewer destroy")


    def destroy(self): # write settings to file upon exit
        """
        override destroy method to save settings to file when gui is exited
        """
        with open("config.txt", "w") as f:
            f.write("\n".join((self.viewmode, self.folder)))
        tk.Frame.destroy(self)




class Viewer(tk.Toplevel):
    """
    for the viewer- the window that pops up when you click view and shows you the images
    
    1st image is already downloaded- will download image when viewing previous one- unless download is already happening from outside
    """
    def __init__(self, base):
        tk.Toplevel.__init__(self, base)
        self.root = base.root
        self.base = base

        self.pages = base.sauce_data['pages']
        self.gallery = base.sauce_data['gallery']
        self.curr_page = 1
        # scaling stuff
        self.img_w, self.img_h = self.base.memory[1].size
        self.win_h = self.base.height - 32
        self.xpad = (20, 20)
        self.ypad = (10, 30)

        self.pressed = False
        self.loading = 0
        self.q = queue.Queue()

        self.main_ending = self.base.sauce_data['ending'] # assume the first image uses the main encoding
        self.other_ending = self.base.sauce_data['ending'] # lol nice jank

        self.UI()
        self.loadPage()


    def UI(self):
        # viewer is non-transient so it appears as a seperate window and can be viewed without the main window open
        # makes it easier to interact with it through alt-tab and such should you need to hide from people watching your screen 

        self.focus() # give keyboard focus to the toplevel object(for key bindings)
        # create selected view mode
        self.viewframe = {'scaled': Scale, 'scrolled': Scroll}[self.base.viewmode](self) # this seems pretty jank
        self.viewframe.pack(padx=self.xpad, pady=self.ypad)
        
        self.bind('<Left>', lambda event: self.left())
        self.bind('<Right>', lambda event: self.right())
        # restrict 1 action per key press- change page functionality is disabled until key is released
        self.bind('<KeyRelease-Left>', self.resetPress) # it just feels more right this way
        self.bind('<KeyRelease-Right>', self.resetPress)
        self.bind("<Button-1>", self.click)


    def loadPage(self):
        # redraw the screen- at least try to
        try:
            self.renderPage()
        except KeyError: # loading has not caught up
            self.curr_page -= 1
            self.title(f"{self.base.sauce_data['number']}- page {self.curr_page} of {self.base.sauce_data['pages']} ... loading ...")
            if not self.base.loading:
                self.loading = self.curr_page


    def renderPage(self):
        # display the image to the screen and starts the background loading of the next image- if needed
        self.viewframe.render(self.base.memory[self.curr_page])
        self.title(f"{self.base.sauce_data['number']}- page {self.curr_page} of {self.base.sauce_data['pages']}")
        
        if self.base.loading:
            print("saving...")
        else:
            self.bufferNext()


    def bufferNext(self):
        # preload the next image
        if self.curr_page < self.pages:
            try: # image is already in memory nothing to do
                self.base.memory[self.curr_page + 1]

            except KeyError: # start thread to get the next image- uses the image downloader in the main class
                Thread(target=self.base.imgDownload, args=(self.curr_page + 1, self.q)).start()  
                self.root.after(100, self.waitImage)


    def waitImage(self):
        try:
            response = self.q.get(False)
            self.loading = 0
            self.title(f"{self.base.sauce_data['number']}- page {self.curr_page} of {self.base.sauce_data['pages']}")
        except queue.Empty:
            self.root.after(100, self.waitImage)

    # load prev and next pages
    def prevPage(self):
        if self.curr_page > 1: # previous pages will always be loaded so no need restrict when loading
            self.curr_page -= 1
            self.loadPage()

    def nextPage(self):
        if self.loading != self.curr_page and self.curr_page < self.pages:
            self.curr_page += 1    
            self.loadPage()

    # for mouse clicks
    def click(self, event):
        """
        called from click binding and determines next or prev based on mouse position
        """
        self.nextPage() if event.x > self.viewframe.display_width / 2 else self.prevPage()

    # for left and right arrow
    def left(self, event=None):
        if not self.pressed:
            self.pressed = True
            self.prevPage()
    
    def right(self, event=None):
        if not self.pressed:
            self.pressed = True
            self.nextPage() 
    

    def resetPress(self, event=None):
        """
        prevent rapid calling by holding down left/right key
        """
        self.pressed = False



class Scale(tk.Frame):
    """
    to render images in scaled form
    """
    def __init__(self, base):
        tk.Frame.__init__(self, base)
        self.base = base
        # calculate image size
        self.scaled_height = base.win_h - sum(base.ypad)
        self.display_width = int(self.scaled_height * base.img_w / base.img_h)
        win_w = self.display_width + sum(base.xpad)
        
        base.geometry(f"{win_w}x{base.win_h}+{(base.base.width - win_w) // 2}+0") # base.base- thats not confusing at all
        base.update_idletasks() # required for whatever reason

        self.img_l = tk.Label(self)
        self.img_l.grid()
    
    
    def render(self, image):
        """
        called to change the displayed image
        """
        img_w, img_h = image.size
        max_h = self.scaled_height
        display_width = int(max_h * img_w / img_h)
        if display_width > self.display_width:
            display_width = self.display_width
            max_h = int(display_width * img_h / img_w)
            
        self.img_display = ImageTk.PhotoImage(image.resize((display_width, max_h), Image.ANTIALIAS))
        self.img_l['image'] = self.img_display



class Scroll(tk.Frame):
    """
    to render images in fullsize form
    """
    def __init__(self, base):
        tk.Frame.__init__(self, base)
        
        self.display_width = base.img_w
        win_w = self.display_width + sum(base.xpad)
        screen_height = base.win_h - sum(base.ypad)
        
        base.geometry(f"{win_w}x{base.win_h}+{(base.base.width - win_w) // 2}+0")
        base.update_idletasks()
        
        self.screen = tk.Canvas(self, width=self.display_width, height=screen_height)
        self.bar = tk.Scrollbar(self, orient='vertical', command=self.screen.yview)
        self.screen.configure(yscrollcommand=self.bar.set)
        
        self.screen.grid(row=0, column=0)
        self.bar.grid(row=0, column=1, sticky='ns')
        
        base.bind("<MouseWheel>", self.scroll)
        base.bind("<Up>", lambda event: self.screen.yview_scroll(-1, "units"))
        base.bind("<Down>", lambda event: self.screen.yview_scroll( 1, "units"))


    def render(self, image):
        img_w, img_h = image.size
        if img_w > self.display_width:
            image = image.resize((self.display_width, int(self.display_width * img_h / img_w)), Image.ANTIALIAS)
        
        self.img_display = ImageTk.PhotoImage(image)
        self.screen.delete('all')
        self.screen.create_image(0, 0, image=self.img_display, anchor='nw')
        self.screen.configure(scrollregion=self.screen.bbox('all'))
        self.screen.yview_moveto(0)
        
        
    def scroll(self, event):
        """
        handle mouse scrolling
        """
        if event.state == 0:
            self.screen.yview_scroll(int(-1 * (event.delta / 120)), 'units')


# class for the settings tab. Im thinking to just integrate this into the base UI(no popup)
class Settings(tk.Toplevel):
    """
    settings popup
    """
    def __init__(self, base):
        tk.Toplevel.__init__(self, base)
        self.title("settings")
        self.base = base
        self.selection = tk.StringVar()
        self.selection.set(self.base.viewmode)
        self.folder = tk.StringVar()
        self.folder.set(self.base.folder)
        self.UI()


    def UI(self):
        self.transient(self.base) # opens with base window
        self.grab_set() # prevent interation with base window
        self.focus()
        
        tk.Label(self, text="image view mode", font=(None, 9, 'bold')).grid(row=0, column=0, pady=(10, 0))

        f1 = tk.Frame(self)
        f1.grid(row=1, padx=(10, 10), pady=(0, 10))
        
        tk.Radiobutton(f1, text="scaled", variable=self.selection, value="scaled").grid(row=0, column=1, padx=10)
        tk.Radiobutton(f1, text="fullsize", variable=self.selection, value="scrolled").grid(row=0, column=2, padx=10)
        
        # f1_5 = tk.Frame(self)
        tk.Label(self, text="save folder", font=(None, 9, 'bold')).grid(row=2)
        
        f2 = tk.Frame(self)
        f2.grid(row=3, padx=(10, 10), pady=(0, 10))
        
        tk.Label(f2, textvariable=self.folder).grid(row=0, column=0)
        tk.Button(f2, text="browse", command=lambda: self.folder.set(askdirectory() or self.folder.get())).grid(row=0, column=1)

        exit_f = tk.Frame(self)
        tk.Button(exit_f, width=7, text="ok", command=self.exit).grid(row=0, column=1, padx=(0, 10), sticky='e') # okay
        tk.Button(exit_f, width=7, text="cancel", command=self.destroy).grid(row=0, column=2, padx=(0, 10), sticky='e') # cancel
        
        exit_f.grid(row=4, pady=(0, 10), sticky='ew')
        exit_f.grid_columnconfigure(0, weight=1)


    def exit(self):
        self.base.viewmode, self.base.folder = self.selection.get(), self.folder.get()
        self.destroy()


def main():
    # get screen size info 
    for monitor in EnumDisplayMonitors():
        info = GetMonitorInfo(monitor[0])
        if info['Flags'] == 1:
            break

    root = tk.Tk()
    gui = SauceFinder(root, info['Work'][2:])
    root.mainloop()


if __name__ == "__main__":
    main()
