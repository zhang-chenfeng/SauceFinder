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
#
#  created in Python 3.7.4 but there's no reason why it wouldn't work on any version
#  that isn't something ridiculous
#------------------------------------------------------------------------------------

import tkinter as tk
import time
import queue
from io import BytesIO
from re import compile
from threading import Thread

from PIL import Image, ImageTk
from requests import get
from bs4 import BeautifulSoup


class MainUI(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root
        self.q = queue.Queue()
        self.magic_number = 0
        self.memory = {}
        self.sauce_data = (1, 1, 1, 22, 22, 1, 222)
        self.baseUI()


    def baseUI(self):
        self.root.title("Sauce Finder")
        self.img_tmp = ImageTk.PhotoImage(Image.open("template.png"))
        
        # header
        self.header = tk.Label(self.root, width=80, text="Sauce Finder", font=(None, 15))
        
        # input frame
        self.input_f = tk.Frame(self.root)
        self.prompt = tk.Label(self.input_f, text="Enter Sauce:")
        self.entry = tk.Entry(self.input_f, width=10)
        self.entry.bind("<FocusIn>", lambda event: self.entry.selection_range(0, tk.END))
        self.search = tk.Button(self.input_f, text="GO", command=self.fetchSauce)
        
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
        
        # UI visualization for testing 
        self.preview_f['bg'] = "red"
        self.cover_l['bg'] = "blue"
        self.side_f['bg'] = "green"
        self.fields_f['bg'] = "yellow"
        self.options_f['bg'] = "white"
        
        self.header.grid(row=0, column=0, padx=(30, 30), pady=(15, 10))
        
        self.input_f.grid(row=1, column=0)
        self.prompt.grid(row=0, column=0, padx=(5, 2))
        self.entry.grid(row=0, column=1, padx=(2, 2))
        self.search.grid(row=0, column=2, padx=(2, 5))
        
        self.title_l.grid(row=2, column=0, padx=(30, 30), pady=(15, 2), sticky=tk.E+tk.W)
        self.subtitle_l.grid(row=3, column=0, padx=(30, 30), pady=(5, 10), sticky=tk.E+tk.W)

        self.preview_f.grid(row=4, padx=(30, 30), pady=(5, 15), sticky=tk.W+tk.E)
        self.cover_l.grid(row=0, column=0, padx=(10, 10), sticky=tk.N+tk.W)        
        self.side_f.grid(row=0, column=1, padx=(0, 10), sticky=tk.N)
        self.fields_f.grid(row=0, sticky=tk.N)
        self.options_f.grid(row=1, pady=(0, 10))
        self.view_b.grid(column=0)


    def renderPreview(self):
        if self.sauce_data:        
            title, subtitle, cover, fields, pages, upload_time, gallery = self.sauce_data
            
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
        print("data fetch started for %s" %magic_number)
        self.time_track = time.time()

    # and here
    def loadDone(self):
        end_time = time.time()
        print("response received %fs elapsed" %(end_time-self.time_track))
        self.search['state'] = 'normal'


    def fetchSauce(self):
        # focus an arbitrary label to remove focus from the entry field so the onfocus event to highlight the text can trigger when refocused
        # otherwise the entry will remain focused and the event can't trigger so the user would have to spam backspace or highlight manualy
        self.header.focus() # lol this is really fucking stupid but I can't think of a better way to do this
        
        self.magic_number = self.entry.get()
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
        print(img_url)
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

        q.put((title, subtitle, cover, fields, pages, upload_time, gallery))


    def viewBook(self):
        Viewer(self.root, (self.magic_number, self.sauce_data[4], self.sauce_data[6]), self.memory)


class Viewer(tk.Toplevel):
    def __init__(self, base, book_data, memory):
        tk.Toplevel.__init__(self, base)
        self.sauce, self.pages, self.gallery = book_data # self.sauce is currently useless
        self.base = base
        self.memory = memory
        self.curr_page = 1
        self.pressed = False
        self.loading = False
        self.q = queue.Queue()
        self.UI()
        self.loadPage()
        
    
    def UI(self):
        self.img_l = tk.Label(self)
        
        self.desc_f = tk.Frame(self)
        self.index = tk.Label(self.desc_f)
        self.img_desc = tk.Label(self.desc_f, text=" ".join(("of", str(self.pages))))
        
        self.desc_f['bg'] = 'red'
        self.index['bg'] = 'white'
        self.img_desc['bg'] = 'beige'
        
        
        self.img_l.grid(row=0, padx=(10, 10), pady=(10, 10))
        self.desc_f.grid(row=1)
        self.index.grid(row=0, column=0, sticky=tk.E)
        self.img_desc.grid(row=0, column=1, sticky=tk.W)
                
        self.transient(self.base) # popup appears as part of main window(not shown on taskbar)
        self.focus() # give keyboard focus to the toplevel object(for key bindings)
        self.grab_set() # prevent interaction with main window while viewer is open
        
        self.bind('<Left>', self.prevPage)
        self.bind('<Right>', self.nextPage)
        
        # system to restrict 1 action per key press- change page functionality is disabled until key is released
        self.bind('<KeyRelease-Left>', self.resetPress)
        self.bind('<KeyRelease-Right>', self.resetPress)


    def renderPage(self):
        self.index['text'] = str(self.curr_page)
        # self.img_l['text'] = self.memory[self.curr_page] # temppp
        self.img_l['image'] = self.memory[self.curr_page]


    def loadPage(self):
        self.loading = True
        try:
            image = self.memory[self.curr_page]
            print("Already loaded")
            self.q.put(0)
        except KeyError:
            print("image download")
            Thread(target=self.downloadImage, args=(self.gallery, self.curr_page, self.q, self.memory)).start()
        self.waitImage()
        

    def waitImage(self):
        try:
            response = self.q.get(False)
            self.renderPage()
            self.loading = False
        except queue.Empty:
            self.base.after(100, self.waitImage)

    
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
        if not self.pressed and not self.loading and self.curr_page < self.pages:
            self.curr_page += 1    
            self.loadPage()
            self.pressed = True


    def prevPage(self, event):
        if not self.pressed and not self.loading and self.curr_page > 1:
            self.curr_page -= 1
            self.loadPage()
            self.pressed = True


    def resetPress(self, event):
        self.pressed = False


def main():
    root = tk.Tk()
    gui = MainUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
