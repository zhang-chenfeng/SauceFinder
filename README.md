# SauceFinder
*This started as a joke but somehow actually turned into something legit*

This program will accept your 6 digit number(s) and generate a preview corresponding to the respective gallery number of a certain website that begins with the letter 'n'


### TODO
- [x] Image preview
- [x] Display tags correctly
- [x] Balance GUI (partially done, more improvements in future)
- [x] data fetch on a seperate thread so the gui doesn't freeze if your internet sucks
- [x] general code improvements
- [x] full image previews maybe
- [x] downloading & saving?
- [x] probably some sort of input validation but anything wrong should just return 404
- [x] some sort of catch for connection timeout so it doesn't hang forever
- [x] add clicking support of the viewer
- [x] image downloading in backgrounds

### Installation
In case you are braindead:
1. `git clone https://github.com/zhang-chenfeng/SauceFinder.git saucefinder`
2. `cd saucefinder (activate your venv)`
3. `python -m pip install -r requirements.txt`
4. `python sauce.py`

### Usage

#### UI
![UI](https://cdn.discordapp.com/attachments/496020212764901387/709459413919989760/unknown.png)\
UI Elements
#### Viewer
![view](https://cdn.discordapp.com/attachments/496020212764901387/709833761130414171/viewer_2.png)\
view your stuffs. Supports navigation with mouse and/or arrow keys

#### Settings
![setting](https://cdn.discordapp.com/attachments/496020212764901387/709528532195213442/setting.png)\
choose between a scaled and fullsize view

#### Download 
![down](https://cdn.discordapp.com/attachments/496020212764901387/709544131076161546/down_2.png)\
save images to local
