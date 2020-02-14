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

# 177978 for testing - this one hentai literaly has every possible jank that breaks my code


class MainUI(tk.Frame):
    """
    defines the main window
    """
    def __init__(self, root, dimensions):
        tk.Frame.__init__(self, root)
        self.root = root
        self.width, self.height, = dimensions
        self.q = queue.Queue()
        self.magic_number = 0
        self.loading = False
        self.memory = {}
        self.sauce_data = ()
        self.baseUI()
        f = open("config.txt", "r")
        self.viewmode = f.read()
        f.close()
        self.entry.focus()


    def baseUI(self):
        self.root.title("Sauce Finder")
        self.img_tmp = ImageTk.PhotoImage(Image.open("tmep.png"))
        
        self.head_f = tk.Frame(self, borderwidth=3, relief='ridge')
        
        # header
        self.header = tk.Label(self.head_f, width=80, text="Sauce Finder", font=(None, 15))
        
        # 2nd line frame
        self.sub_f = tk.Frame(self.head_f)
        
        # input frame
        self.input_f = tk.Frame(self.sub_f)
        self.prompt = tk.Label(self.input_f, text="Enter Sauce")
        self.entry = tk.Entry(self.input_f, width=8)
        self.entry.bind("<FocusIn>", lambda event: self.entry.selection_range(0, tk.END))
        self.entry.bind("<Return>", lambda event: self.fetchSauce())
        self.search = tk.Button(self.input_f, width=4, text="GO", command=self.fetchSauce)
        
        # settings
        self.settings_b = tk.Button(self.sub_f, width=10, text="settings", command=self.viewSettings)
        
        #
        self.line = tk.Frame(self, height=2, bg='black')
        
        # sub headers
        self.title_l = tk.Label(self, text=" ", font=(None, 14), wraplength=875)
        self.subtitle_l = tk.Label(self, text=" ", font=(None, 12), wraplength=875)
        
        # preview frame
        self.preview_f = tk.Frame(self)
        self.cover_l = tk.Label(self.preview_f, image=self.img_tmp)
        self.side_f = tk.Frame(self.preview_f)
        self.fields_f = tk.Frame(self.side_f)
        self.options_f = tk.Frame(self.side_f)
        self.view_b = tk.Button(self.options_f, width=10, text="View", command=self.viewBook)
        self.link_b = tk.Button(self.options_f, width=10, text="Link")
        
        # UI visualization for testing 
        # self.preview_f['bg'] = "red"
        # self.cover_l['bg'] = "blue"
        # self.side_f['bg'] = "green"
        # self.fields_f['bg'] = "yellow"
        # self.options_f['bg'] = "white"
        
        self.pack(padx=(30, 30))

        self.head_f.grid(row=0, pady=(15, 0))
        self.header.grid(row=0, column=0, pady=(5, 5))
        
        self.sub_f.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        self.sub_f.grid_columnconfigure(0, weight=1)
        self.sub_f.grid_columnconfigure(2, weight=1)

        self.input_f.grid(row=0, column=1, padx=(20 + 10 * 8, 0))
        self.prompt.grid(row=0, column=0, padx=(5, 5))
        self.entry.grid(row=0, column=1, padx=(5, 5))
        self.search.grid(row=0, column=2, padx=(5, 5))
        self.settings_b.grid(row=0, column=2, sticky="e", padx=(0, 20))

        # self.line.grid(row=0, column=0, pady=(5, 5), sticky='ew')
        
        self.title_l.grid(row=1, column=0, pady=(15, 2), sticky='ew')
        self.subtitle_l.grid(row=2, column=0, pady=(5, 10), sticky='ew')

        self.preview_f.grid(row=3, pady=(5, 15), sticky='ew')
        self.cover_l.grid(row=0, column=0, padx=(10, 10), sticky='nw')        
        self.side_f.grid(row=0, column=1, padx=(0, 10), sticky='n')
        self.fields_f.grid(row=0, sticky='n')
        # self.options_f.grid(row=1, pady=(0, 10))
        self.view_b.grid(row=0, column=0, padx=(20, 20))
        self.link_b.grid(row=0, column=1, padx=(20, 0))


    def renderPreview(self):
        if self.sauce_data:        
            title, subtitle, cover, fields, pages, upload_time, gallery, url, self.file_ending = self.sauce_data
            
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
                tk.Label(self.fields_f, text=field + ":", font=(None, 12)).grid(row=index, column=0, sticky='ne')
                tk.Label(self.fields_f, text=", ".join(tags), font=(None, 12), wraplength=420, justify='left').grid(row=index, column=1, sticky='nw', padx=(10, 0), pady=(0, 20))
            self.link_b['command'] = lambda: webbrowser.open(url)
            self.options_f.grid(row=1, pady=(20, 10), sticky=tk.W)
            
        else: # make this another function later
            self.title_l['text'] = "File Not Found"
            self.subtitle_l['text'] = "server returned 404"


    def destroyChildren(self, frame):
        """
        permanently delete all the items spawned inside a widget
        """
        for itm in frame.winfo_children():
            itm.destroy()

    # Future loading events go in here
    def loadStart(self):
        """
        procedures to be run when preview loading begins
        """
        self.loading = True
        self.search['state'] = 'disabled'
        self.title_l['text'] = "Loading..."
        self.subtitle_l['text'] = "正在加载。。。"
        self.destroyChildren(self.fields_f) # destroy any tags rendered from previous previews
        self.cover_l['image'] = self.img_tmp
        self.options_f.grid_forget()
        print("data fetch started for {}".format(self.magic_number))
        self.time_track = time.time()

    # and here
    def loadDone(self):
        """
        procedures to be run when preview loading ends
        """
        end_time = time.time()
        print("response received {}s elapsed".format(end_time-self.time_track))
        self.search['state'] = 'normal'
        self.loading = False


    def fetchSauce(self):
        """
        run when user clicks go/enter key, starts the thread with fetch process and starts waiting for response
        """
        if not self.loading:
            # focus an arbitrary label to remove focus from the entry field so the onfocus event to highlight the text can trigger when refocused
            # else the entry will remain focused and the event can't trigger so the user would have to spam backspace or highlight the previous input manually
            self.header.focus() # lol this is really fucking stupid but I can't think of a better way to do this
            
            self.magic_number = self.entry.get()
            
            # for offline testing
            if self.magic_number == "test":
                self.offlineTesting()
                return
            
            # some validation- won't catch invalid numbers
            if self.magic_number.isdigit():
                self.loadStart()
                Thread(target=self.getValues, args=(self.q, self.magic_number)).start()
                self.root.after(100, self.awaitSauce)
            else:
                self.title_l['text'] = "invalid number"
                self.subtitle_l['text'] = "无效号码"
                self.destroyChildren(self.fields_f)
                self.cover_l['image'] = self.img_tmp
                self.options_f.grid_forget()


    def awaitSauce(self):
        """
        wait for fetch thread to finish and push results in the queue before render
        """
        try:
            self.sauce_data = self.q.get(False) # if item is not availible raises queue.Empty error
            self.loadDone()
            self.renderPreview()

        except queue.Empty:
            self.root.after(100, self.awaitSauce)


    def getValues(self, q, magic_number):
        """
        get the html response and process out the required information- also predownload some images
        
        to be run with Thread due to internet latency
        """
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
        split = img_url.split("/")
        gallery = split[-2] # not the be confused with the gallery in the url
        file_ending = split[-1].split(".")[-1] # for whatever reason the file types are not consistent
        print(file_ending)
        
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
        
        # get first image of book
        self.memory[1] = Image.open(BytesIO(get("".join(("https://i.nhentai.net/galleries/", str(gallery), "/1.", file_ending))).content))

        q.put((title, subtitle, cover, fields, pages, upload_time, gallery, url, file_ending))


    def viewBook(self):
        """
        run the viewer
        """
        Viewer(self) # why is this even a function

    
    def viewSettings(self):
        Settings(self)
    
    # testing stuff ignore
    def offlineTesting(self):
        self.loadStart()
        self.sauce_data = ("offline testing", "wow is this legal?", ImageTk.PhotoImage(Image.open("untitled.png").resize((350, 511), Image.ANTIALIAS)), [("Parodies", ("Aokana",)), ("Characters", ("Kurashina Asuka",)), ("Tags", ("lolicon", "flying fish"))], 5, "time", 1, "http://softloli.moe", "png")
        self.memory[1] = Image.open("u1.png")
        self.loadDone()
        self.renderPreview()


    def destroy(self): # write settings to file upon exit
        """
        override destroy method to save settings to file when gui is exited
        """
        x = open("config.txt", "w")
        x.write(self.viewmode)
        x.close()
        
        tk.Frame.destroy(self)

        
# all the code from here on down is a complete mess. not that the code above is clean, just after this it gets even worse
class Viewer(tk.Toplevel):
    """
    for the viewer- the window that pops up when you click view and shows you the images
    
    'page' and 'image' both mean the same thing- every page is a jpg image
    
    basically how this mess works is that the viewer subclasses a popup and based on the settings
    will create and display a frame object from either Scale or Scroll
    
    both the classes have a render method that gets called to display the next image when button is pressed
    
    the first image is already downloaded with the preview data and subsequent images are downloaded when the one previous is displayed
    eg. viewing page 1 will trigger the download for page 2, and viewing 2 will download 3
    
    only 1 image can be downloaded at a time and calls to display next image will be ignored if the image is still downloading
    eg. if image 2 is displayed and 3 is still downloading, image 3 can not be displayed until it is downloaded as spawning multiple threads
    at once will make the program hang forever
    
    """
    def __init__(self, base):
        tk.Toplevel.__init__(self, base)
        self.root = base.root
        self.base = base
        
        self.pages = self.base.sauce_data[4]
        self.gallery = self.base.sauce_data[6]
        
        self.img_w, self.img_h = self.base.memory[1].size
        self.win_h = self.base.height - 32
        self.xpad = (20, 20)
        self.ypad = (10, 30)
        
        self.curr_page = 1

        self.views = {'scaled': Scale, 'scrolled': Scroll}        
        
        self.pressed = False
        self.loading = False
        
        self.q = queue.Queue()
        
        self.UI()
        self.loadPage()


    def UI(self):
    
        # decided to make the viewer non-transient so it appears as a seperate window and can be viewed without the main window open
        # this should make it easier to interact with it through alt-tab and such should you need to hide from people watching your screen 
        # self.transient(self.base)
        self.focus() # give keyboard focus to the toplevel object(for key bindings)
        self.grab_set() # prevent interaction with main window while viewer is open
        
        self.viewframe = self.views[self.base.viewmode](self) # this seems pretty jank
        self.viewframe.pack(padx=self.xpad, pady=self.ypad)
        
        self.bind('<Left>', lambda event: self.prevPage())
        self.bind('<Right>', lambda event: self.nextPage())
        
        # restrict 1 action per key press- change page functionality is disabled until key is released
        self.bind('<KeyRelease-Left>', self.resetPress)
        self.bind('<KeyRelease-Right>', self.resetPress)
        
        self.bind("<Button-1>", self.clickHandle)


    def loadPage(self):
        """
        called to load a new image
        """
        print("call to load page {}".format(self.curr_page))
        try:
            self.renderPage() # image is already in the memory and can instantly load 

        except KeyError: # background loading has not caught up
            # self.loading = True
            print("load not finished retry in 100ms")
            self.root.after(100, self.loadPage)


    def renderPage(self):
        """
        display the image to the screen and starts the background loading of the next image
        """
        print("rendering page {}".format(self.curr_page))
        self.viewframe.render(self.base.memory[self.curr_page])
        self.title("".join((self.base.magic_number, "- page ", str(self.curr_page))))

        print("buffering page {}".format(self.curr_page + 1))
        self.bufferNext()


    def bufferNext(self):
        """
        load the next image
        """
        if self.curr_page < self.pages:
            try: # image is already in memory nothing to do
                self.base.memory[self.curr_page + 1]
                print("page already loaded OK")

            except KeyError: # start thread to get the next image
                print("page not loaded downloading")
                if self.base.magic_number == "test": # testing ignore
                    self.base.memory[self.curr_page + 1] = Image.open("u" + str(self.curr_page + 1) + ".png")
                else:
                    self.loading = True
                    Thread(target=self.downloadImage, args=(self.gallery, self.curr_page + 1, self.q, self.base.memory)).start()  
                    self.root.after(100, self.waitImage)


    def waitImage(self):
        """
        wait for thread to finish and catch reponse in the queue
        """
        try:
            response = self.q.get(False)
            self.loading = False
        except queue.Empty:
            self.root.after(100, self.waitImage)


    def downloadImage(self, gallery, page, q, mem):
        """
        download an image and save it
        
        to be run with Thread
        """
        print("thread started- fetching image")
        url = "".join(("https://i.nhentai.net/galleries/", str(gallery), "/", str(page), ".", self.base.file_ending))
        load = Image.open(BytesIO(get(url).content))
        print("got image")
        mem[page] = load
        q.put(0)
        print("thread done")


    def nextPage(self):
        """
        call to next page, begin loading if conditions allow
        """
        print("next")
        if not self.pressed and not self.loading and self.curr_page < self.pages:
            self.pressed = True
            self.curr_page += 1    
            self.loadPage()


    def prevPage(self):
        """
        same as next but for prev
        """
        print("prev")
        if not self.pressed and self.curr_page > 1: # previous pages will always be loaded so no need restrict when loading
            self.pressed = True
            self.curr_page -= 1
            self.loadPage()

    
    def clickHandle(self, event):
        """
        called from click binding and determines next or prev based on mouse position
        """
        self.resetPress()
        self.nextPage() if event.x > self.viewframe.display_width / 2 else self.prevPage()


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
        
        base.geometry("{}x{}+{}+0".format(win_w, base.win_h, (base.base.width - win_w) // 2)) # base.base- thats not confusing at all
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
        
        base.geometry("{}x{}+{}+0".format(win_w, base.win_h, (base.base.width - win_w) // 2))
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
        self.UI()


    def UI(self):
        self.transient(self.base) # usual stuff
        self.grab_set()
        self.focus()
        
        self.f1 = tk.Frame(self)
        self.f1.grid(row=0, padx=(10, 10), pady=(10, 10))
        self.l = tk.Label(self.f1, text="viewer mode")
        self.l.grid(row=0, column=0)
        
        tk.Radiobutton(self.f1, text="scaled", variable=self.selection, value="scaled").grid(row=0, column=1)
        tk.Radiobutton(self.f1, text="scrolled", variable=self.selection, value="scrolled").grid(row=0, column=2)
        
        self.exit_f = tk.Frame(self)
        self.ok = tk.Button(self.exit_f, width=7, text="ok", command=self.exit)
        self.cancel = tk.Button(self.exit_f, width=7, text="cancel", command=self.destroy)
        
        self.exit_f.grid(row=1, pady=(0, 10), sticky='ew')
        self.exit_f.grid_columnconfigure(0, weight=1)
        self.ok.grid(row=0, column=1, padx=(0, 10), sticky='e')
        self.cancel.grid(row=0, column=2, padx=(0, 10), sticky='e')


    def exit(self):
        self.base.viewmode = self.selection.get()
        self.destroy()


def main():
    # get screen size info 
    for monitor in EnumDisplayMonitors():
        info = GetMonitorInfo(monitor[0])
        if info['Flags'] == 1:
            break

    root = tk.Tk()
    gui = MainUI(root, info['Work'][2:])
    root.mainloop()


if __name__ == "__main__":
    main()
