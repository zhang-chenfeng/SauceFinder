#----------------------------------------------------------------------------------
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
#----------------------------------------------------------------------------------

import tkinter as tk
import time
import threading
import queue
from io import BytesIO
from re import compile

from PIL import Image, ImageTk
from requests import get
from bs4 import BeautifulSoup

class MainUI(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root
        root.title("Sauce Finder")
        self.img_tmp = ImageTk.PhotoImage(Image.open("template.png"))
        self.q = queue.Queue()
        self.sauce_data = ()
        
        # header
        self.header = tk.Label(root, text="Sauce Finder", font=(None, 15))
        
        # input frame
        self.input_f = tk.Frame(root)
        self.prompt = tk.Label(self.input_f, text="Enter Sauce:")
        self.entry = tk.Entry(self.input_f, width=10)
        self.search = tk.Button(self.input_f, text="GO", command=self.fetchSauce)
        
        # sub headers
        self.title_l = tk.Label(self.root, text="", font=(None, 14))
        self.subtitle_l = tk.Label(self.root, text="", font=(None, 12))
        
        # preview frame
        self.preview_f = tk.Frame(self.root)
        self.cover_l = tk.Label(self.preview_f, image=self.img_tmp)
        self.fields_f = tk.Frame(self.preview_f)
        
        self.header.grid(row=0, column=0, columnspan=5, padx=(30, 30), pady=(15, 10))
        
        self.input_f.grid()
        self.prompt.grid(row=0, column=0, padx=(5, 2))
        self.entry.grid(row=0, column=1, padx=(2, 2))
        self.search.grid(row=0, column=2, padx=(2, 5))
        
        self.title_l.grid(row=2, column=0, columnspan=5, padx=(30, 30), pady=(15, 2))
        self.subtitle_l.grid(row=3, column=0, columnspan=5, padx=(0, 0), pady=(5, 10))

        self.preview_f.grid(row=4, pady=(5, 10))
        self.cover_l.grid(row=0, column=0, padx=(30, 30), sticky=tk.N)        
        self.fields_f.grid(row=0, column=1, sticky=tk.N)
        
        
    def renderPreview(self):
        self.title_l["text"] = "Loading..."
        # title, subtitle, img_url, fields, pages, upload_time = getHTML(self.entry.get())
        title, subtitle, img_url, fields, pages, upload_time = self.sauce_data
        
        # page count and upload date are rendered same as fields in this view
        fields.append(("Pages", [str(pages)]))
        fields.append(("Uploaded", [upload_time]))
        
        length = len(fields)
        
        self.title_l['text'] = title
        self.subtitle_l['text'] = subtitle
        
        ### temp
        img_url = "123202_files/cover.jpg"
        load = Image.open(img_url)
        
        # get image and load
        # response = get(img_url)
        # load = Image.open(BytesIO(response.content))
        cover = ImageTk.PhotoImage(load)
        
        # I don't know why you have to do this- I just know that if you don't the picture won't appear
        self.cover_l['image'] = cover
        self.cover_l.image = cover
        
        # render fields & tags
        for n in range(length):
            field, tags = fields[n]
            tk.Label(self.fields_f, text=field, font=(None, 12)).grid(row=n, column=0, sticky=tk.E+tk.N)
            tk.Label(self.fields_f, text=", ".join(tags), font=(None, 11), wraplength=450, justify='left').grid(row=n, column=1, sticky=tk.W+tk.N, padx=(10, 10), pady=(0, 20))       

    
    # Future loading events go in here
    def loadDisplay(self):
        self.search['state'] = 'disabled'
        self.title_l['text'] = "Loading..."
        
    def loadDone(self):
        self.search['state'] = 'normal'
    

    def fetchSauce(self):
        self.loadDisplay()
        magic_number = self.entry.get()
        
        print("data fetch started for %s" %magic_number)
        
        NetworkRequest(self.q, magic_number).start()
        self.root.after(100, self.awaitSauce)
    
    def awaitSauce(self):
        try:
            self.sauce_data = self.q.get(False) # if item is not availible raises queue.Empty error
            print("sauce get")
            self.loadDone()
            self.renderPreview()
        except queue.Empty:
            print("waiting")
            self.root.after(100, self.awaitSauce)


class NetworkRequest(threading.Thread):
    def __init__(self, q, magic_number):
        threading.Thread.__init__(self)
        self.q = q
        self.number = magic_number
        
    # same thing as getHTML()
    def run(self):
        # generate url. magic_number is already a string by implementation but whatever
        url = "".join(("https://nhentai.net/g/", str(self.number)))
        
        # get html  
        # response = get(url)
        # page = BeautifulSoup(response.text, 'html.parser')
        
        ## temp
        with open(str(self.number) + '.html', 'rb') as html:
            page = BeautifulSoup(html, 'html.parser')
            
        ### simulate sever latency when testing off local file
        time.sleep(1.5)
        
        # div with all the preview info
        info = page.find('div', id='info')
        
        # get titles
        title = info.find('h1').string.strip()
        subtitle = info.find('h2').string.strip()
        
        # get image preview
        cover_container = page.find('div', id='cover')
        img_url = cover_container.find('img')['data-src']
        
        # get all fields and tags
        fields = []
        visible_fields = info.find_all(lambda x: x.has_attr('class') and 'tag-container' in x['class'] and 'hidden' not in x['class'])
        
        for field_div in visible_fields:
            field_name, vals = field_div.contents[:2]
            fields.append((field_name.strip().strip(":"), [t.contents[0].strip() for t in vals.contents]))
        
        # get number of pages
        pages = int(info.find('div', text=compile('pages')).string.split()[0])

        # get upload time
        upload_time = info.find('time')['title']
        
        self.q.put((title, subtitle, img_url, fields, pages, upload_time))


def main():
    root = tk.Tk()
    gui = MainUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
    
