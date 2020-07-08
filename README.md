# SauceFinder

This program will accept your 6 digit number(s) and generate a preview corresponding to the respective gallery number of a certain website that begins with the letter 'n'


*still not sure whether or not there is an api. apparently there is an undocumented one?*

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
Something along these lines:
1. `git clone https://github.com/zhang-chenfeng/SauceFinder.git saucefinder`
2. `cd saucefinder (activate your venv)`
3. `python -m pip install -r requirements.txt`
4. `python sauce.py`

### Usage

#### UI
UI Elements\
<img src="https://cdn.discordapp.com/attachments/496020212764901387/709842419306463242/main.png" width="600">

#### Viewer
Viewer supports navigation with mouse and/or arrow keys\
<img src="https://cdn.discordapp.com/attachments/496020212764901387/709833761130414171/viewer_2.png" width="400">

#### Settings
Choose between a scaled and fullsize view\
<img src="https://cdn.discordapp.com/attachments/496020212764901387/709528532195213442/setting.png" width="300">

#### Download
Save images to local\
<img src="https://cdn.discordapp.com/attachments/496020212764901387/709843641597821088/down.png" width="600">
