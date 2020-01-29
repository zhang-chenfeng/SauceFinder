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
from io import BytesIO

from PIL import Image, ImageTk
from requests import get
from bs4 import BeautifulSoup

class Main(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root
        root.title("Sauce Finder")
        
        self.header = tk.Label(root, text="Sauce Finder", font=(None, 12))
        
        self.input_f = tk.Frame(root)
        
        self.prompt = tk.Label(self.input_f, text="Enter Sauce:")
        self.entry = tk.Entry(self.input_f, width=10)
        self.search = tk.Button(self.input_f, text="GO", command=self.renderPreview)

        
        self.header.grid(row=0, column=0, columnspan=5, padx=(30, 30), pady=(15, 10))
        
        self.input_f.grid(row=1)
        self.prompt.grid(row=0, column=0, padx=(5, 2))
        self.entry.grid(row=0, column=1, padx=(2, 2))
        self.search.grid(row=0, column=2, padx=(2, 5))


    def renderPreview(self):
        title, subtitle, img_url, fields = getHTML(self.entry.get())
        length = len(fields)
        # print(title, length)
        
        title_l = tk.Label(self.root, text=title, font=(None, 14))
        subtitle_l = tk.Label(self.root, text=subtitle, font=(None, 12))
        
        title_l.grid(row=2, column=0, columnspan=5, padx=(30, 30), pady=(15, 5))
        subtitle_l.grid(row=3, column=0, columnspan=5, padx=(0, 0), pady=(5, 10))
        
        ### temp
        img_url = "123202_files/cover.jpg"
        load = Image.open(img_url)
        
        # get image and load
        # response = get(img_url)
        # load = Image.open(BytesIO(response.content))
        cover = ImageTk.PhotoImage(load)
        
        # preview frame
        preview_f = tk.Frame(self.root)
        preview_f.grid(row=4)
        
        cover_l = tk.Label(preview_f, image=cover)
        cover_l.img = cover
        cover_l.grid(row=0, column=0, rowspan = length, padx=(30, 30))
        
        # render fields & tags
        for n in range(length):
            field, tags = fields[n]
            
            tk.Label(preview_f, text=field, font=(None, 11)).grid(row=n, column=1, sticky=tk.E, padx=(0, 10))
            tk.Label(preview_f, text=", ".join(tags), font=(None, 10)).grid(row=n, column=2, sticky=tk.W)
        
        
    
def main():
    root = tk.Tk()
    gui = Main(root)
    root.mainloop()


def getHTML(magic_number):
    # generate url
    url = "".join(("https://nhentai.net/g/", str(magic_number)))
    
    # get html
    # response = get(url)
    
    # create beautifulsoup object
    # page = BeautifulSoup(response.text, 'html.parser')
    
    ## temp
    with open(str(magic_number) + '.html', 'rb') as html:
        page = BeautifulSoup(html, 'html.parser')
    
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
        field_name = field_name.strip().strip(":")

        fields.append((field_name, [t.contents[0].strip() for t in vals.contents]))
    
    return title, subtitle, img_url, fields

    
    
if __name__ == "__main__":
    main()
    
