from __future__ import unicode_literals
from tkinter import *
import tkinter.ttk as ttk
import youtube_dl
from PIL.ImageTk import PhotoImage
from PIL import Image, ImageTk
import threading
from tkinter import filedialog
import queue

import urllib
import io

#For this code to work correcting requires the user to have ffmpeg installed and added to path on their machine

#class and function to pass to options to control output
class MyLogger(object):
    def debug(self, msg):
        # print(msg)
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    """Fucntion with is passed to the downloader, it outputs the download percentage and updates the progress bar"""
    if d['status'] != "finished":
        percentDone, junk = d['_percent_str'].split('%')
        percentDone = float(percentDone.strip())
        bar(float(percentDone))
       
def bar(percentDone): 
    #Updates the progress bar based on the percentage completed
    progress['value'] = percentDone



def changePath():
    """Opens a dialog box and asks the user to select a folder, then converts the output to the correct format and updates the options"""
    global Path
    Path = filedialog.askdirectory(initialdir = 'C:\\Users\\callu_000\\Downloads')#opens file explorer
    Path = Path.replace("/", "\\\\")
    
 

def download():
    """Once called this function will continuously execute in a secondary thread, it will not wait until there is an item
    placed in the queue then proceed. Firstly it determines the download location which may or may not have been changed. 
    Then sets the default values. If the mp3 box was checked a few more options are added and the format is updated.
    Finally the given url is downloaded with the specified options"""

    global audioBol, Path
    
    while True:
        q.get()
        Location = '%s \%(title)s.%(ext)s'.replace("%s ", Path)
        ydl_opts = {
            'outtmpl': Location,
            'logger': MyLogger(),
            'progress_hooks': [my_hook],
            'format': 'bestvideo+bestaudio/best'        
                }
        if audioBol.get() == 1:
            ydl_opts["format"] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192',}]
            ydl_opts['keepvideo'] = False
        URL=url.get()#gets url from entry
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([URL])    

def startDownload():
    """Retreives the URL, checks if it is a playlist. If not then the title and thumbnail are fetched and displayed, if it is
    then the user is given the error. After the title and thumbnail are displayed a value is placed inot the queue which triggers
    the download thread"""
    URL=url.get()
    if not '&list' in URL:
        with youtube_dl.YoutubeDL({'logger': MyLogger()}) as ydl:
            #all the meta data about the video
            info_dict = ydl.extract_info(URL, download=False)
            video_title = info_dict.get('title', None)
            thumbnail = info_dict.get('thumbnail', None)
        #puts the video title on the gui
        videoTitle.config(text=video_title[:55])

        #converts a url to the thumbnail to a format that can be displayed in tkinter
        raw_data = urllib.request.urlopen(thumbnail).read()
        im = Image.open(io.BytesIO(raw_data))
        img = im.resize((200, 120), Image.ANTIALIAS)
        image = ImageTk.PhotoImage(img)
        thumbnailIM.config(image=image)
        thumbnailIM.image = image
        q.put(300)
        bar(0)
    else:
        videoTitle.config(text="Playlists are not currently supported")


def _from_rgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    return "#%02x%02x%02x" % rgb   


def CreateLabel(row, col, h, w, rowspan, columnspan, bg, fg, **kwargs):
    """Fucntion to simplify and standardise creating labels for my grid system"""
    if "sticky" in kwargs:
        sk = kwargs["sticky"]
        label = Label(root, height = h, width=w, font = ('caviar dreams', 15), bg=bg, fg=fg)
        label.grid(sticky = sk, row=row, column= col, rowspan = rowspan, columnspan = columnspan)
    else:
        label = Label(root, height = h, width=w, bg = bg)
        label.grid(row=row, column= col, rowspan = rowspan, columnspan = columnspan)
    return label


#Default download path
Path = 'C:\\Users\\callum\\Downloads'
#Creating and starting the necessary thread and queue
q = queue.Queue()
t =  threading.Thread(target = download, name = "thread", daemon = True)
t.start()


#Tkinter Window
root = Tk()
root.title('Youtube Downloader')
root.geometry("600x200")



#Creating the grid sutem for widget placement
Left = CreateLabel(0, 0, 20, 43, 2, 1, _from_rgb((51, 51, 51)), "black")

RightUpper = CreateLabel(0, 1, 10, 43, 1, 1, _from_rgb((51, 51, 51)), "black")
RightLower = CreateLabel(1, 1, 10, 43, 1, 1, _from_rgb((51, 51, 51)), "black")

Bottom = CreateLabel(2, 0, 3, 90, 1, 2, _from_rgb((51, 51, 51)), "black", sticky = "s")

#===============================================================>

label = Label(root, font = ('caviar dreams', 12, 'bold'), bg=_from_rgb((51, 51, 51)), fg='white')
label.config(text="Enter the YouTube URL")
label.grid(in_ = RightUpper, row=0)

InputStrings = StringVar()
url = Entry(root, textvariable=InputStrings, width = 50, )
url.grid(in_ = RightUpper, row=1, ipadx=20, pady = 5, ipady = 5)

#==========================Left====================================>

#Puts the YouTube Logo into the left hand side and resizes
path= 'imgs/YoutubeLogo.png'
img = Image.open(path)
img = img.resize((180, 120), Image.ANTIALIAS)
image = PhotoImage(img)#converts image to tkinter friendly format
thumbnailIM = Label(root, image=image, borderwidth = 0)
thumbnailIM.image = image
thumbnailIM.grid(in_=Left, row =0, column = 0, pady = 10)

#=========================Right====================================>
#Creating all the buttons
icon = Image.open('imgs/folder.png')
icon = icon.resize((20, 20), Image.ANTIALIAS)
Icon = PhotoImage(icon)

folderBut = Button(root, image = Icon, text='Change Download Folder', font=("Ariel", 9, "bold"),  command=changePath)
folderBut.grid(in_ = RightLower, row=2, column = 0, padx = 10)

downloadBut = Button(root, text='Download', font=("Ariel", 9, "bold"), command=startDownload)
downloadBut.grid(in_ = RightLower, row=2, column = 1, padx = 10)


audioBol = IntVar()
audio = Checkbutton(root, text="mp3", variable=audioBol)
audio.grid(in_= RightLower, row=2, column = 4, padx = 10)

#=========================Bottom=================================>

progress = ttk.Progressbar(root, orient = HORIZONTAL, length = 600, mode = 'determinate') 
progress.grid(in_=Bottom, row=1)


videoTitle = Label(root, font = ('caviar dreams', 12), bg=_from_rgb((51, 51, 51)), fg='white')
videoTitle.grid(in_ = Bottom, row=0)



root.configure(bg=_from_rgb((51, 51, 51))) 

root.mainloop()




