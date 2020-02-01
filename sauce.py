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
        self.sauce_data = ()
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
        self.search = tk.Button(self.input_f, text="GO", command=self.fetchSauce)
        
        # sub headers
        self.title_l = tk.Label(self.root, text=" ", font=(None, 14), wraplength=875)
        self.subtitle_l = tk.Label(self.root, text=" ", font=(None, 12), wraplength=875)
        
        # preview frame
        self.preview_f = tk.Frame(self.root)
        self.cover_l = tk.Label(self.preview_f, image=self.img_tmp)
        self.fields_f = tk.Frame(self.preview_f)
        
        self.header.grid(row=0, column=0, padx=(30, 30), pady=(15, 10))
        
        self.input_f.grid(row=1, column=0)
        self.prompt.grid(row=0, column=0, padx=(5, 2))
        self.entry.grid(row=0, column=1, padx=(2, 2))
        self.search.grid(row=0, column=2, padx=(2, 5))
        
        self.title_l.grid(row=2, column=0, padx=(30, 30), pady=(15, 2), sticky=tk.E+tk.W)
        self.subtitle_l.grid(row=3, column=0, padx=(30, 30), pady=(5, 10), sticky=tk.E+tk.W)

        self.preview_f.grid(row=4, padx=(30, 30), pady=(5, 15), sticky=tk.W+tk.E)
        self.cover_l.grid(row=0, column=0, padx=(10, 10), sticky=tk.N+tk.W)        
        self.fields_f.grid(row=0, column=1, padx=(0, 10), sticky=tk.N)
        
        
    def renderPreview(self):
        if self.sauce_data:        
            title, subtitle, cover, fields, pages, upload_time = self.sauce_data
            
            # page count and upload date are rendered same as fields in this view
            fields.append(("Pages", [str(pages)]))
            fields.append(("Uploaded", [upload_time]))

            self.title_l['text'] = title
            self.subtitle_l['text'] = subtitle
            
            # I don't know why you have to do this- I just know that if you don't the picture won't appear
            self.cover_l['image'] = cover
            self.cover_l.image = cover
            
            # render fields & tags
            for index, (field, tags) in enumerate(fields):
                tk.Label(self.fields_f, text=field, font=(None, 12)).grid(row=index, column=0, sticky=tk.E+tk.N)
                tk.Label(self.fields_f, text=", ".join(tags), font=(None, 12), wraplength=440, justify='left').grid(row=index, column=1, sticky=tk.W+tk.N, padx=(10, 0), pady=(0, 20))       
        else: # make this another function later
            self.title_l['text'] = "File Not Found"
            self.subtitle_l['text'] = "server returned 404"
        
    # Future loading events go in here
    def loadDisplay(self, magic_number):
        self.search['state'] = 'disabled'
        self.title_l['text'] = "Loading..."                
        print("data fetch started for %s" %magic_number)
        self.time_track = time.time()
        
    # and here
    def loadDone(self):
        end_time = time.time()
        print("response received %fs elapsed" %(end_time-self.time_track))
        self.search['state'] = 'normal'
    

    def fetchSauce(self):
        magic_number = self.entry.get()
        self.loadDisplay(magic_number)
        Thread(target=self.getValues, args=(self.q, magic_number)).start()
        self.root.after(100, self.awaitSauce)
    
    
    def awaitSauce(self):
        try:
            self.sauce_data = self.q.get(False) # if item is not availible raises queue.Empty error
            self.loadDone()
            self.renderPreview()
            
        except queue.Empty:
            self.root.after(100, self.awaitSauce)
    
    
    def getValues(self, q, magic_number):
        # generate url. magic_number is already a string by implementation but whatever
        url = "".join(("https://nhentai.net/g/", str(magic_number)))
        
        # get html  
        response = get(url)
        if not response.ok:
            q.put([])
            return
        page = BeautifulSoup(response.text, 'html.parser')
        
        ## temp
        # with open(str(magic_number) + '.html', 'rb') as html:
            # page = BeautifulSoup(html, 'html.parser')
            
        ### simulate sever latency when testing off local file
        # time.sleep(1.5)
        
        # div with all the preview info
        info = page.find('div', id='info')
        
        print(info)
        # get titles
        title = info.find('h1').string.strip()
        subtitle = info.find('h2').string.strip()
        
        # get image preview
        cover_container = page.find('div', id='cover')
        img_url = cover_container.find('img')['data-src']
        
        ### temp
        # img_url = "123202_files/cover.jpg"
        # load = Image.open(img_url)

        # get image and load
        response = get(img_url)
        load = Image.open(BytesIO(response.content))
        cover = ImageTk.PhotoImage(load)
        
        # get all fields and tags
        fields = []
        visible_fields = info.find_all(lambda x: x.has_attr('class') and 'tag-container' in x['class'] and 'hidden' not in x['class'])
        
        for field_div in visible_fields:
            field_name, vals = field_div.contents[:2]
            fields.append((field_name.strip().strip(":"), [t.contents[0].strip() for t in vals.contents]))
        
        # get number of pages
        pages = int(info.find('div', text=compile('pages')).string.split()[0])
        
        print(info.find('time'))
        # get upload time
        upload_time = info.find('time').text

        q.put((title, subtitle, cover, fields, pages, upload_time))


def main():
    root = tk.Tk()
    gui = MainUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
    
