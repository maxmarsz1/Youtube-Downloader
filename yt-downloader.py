import pytube
import requests
import os
import threading
import time
from tkinter import filedialog, ttk, messagebox, font, Canvas, Entry, Button, Tk, StringVar, Toplevel, HORIZONTAL
from PIL import ImageTk, Image

class Downloader:
    def __init__(self):
        #Path to save bg and thumbnails
        self.data_path = os.path.join(os.getenv("LOCALAPPDATA"), "YouTube Downloader")
        if not os.path.isdir(self.data_path):
            os.mkdir(self.data_path)

        #Current working directory
        self.directory_path = os.getcwd()

        self.thumbnail = None

        #Background img path
        self.bg_path = os.path.join(self.data_path, "bg.jpg")
        
        #Downloading background img
        self.download_thumbnail("http://player69.xyz/img6969/bg.jpg", self.data_path, "bg.jpg")

        #Path to thumbnail
        self.thumbnail_path = os.path.join(self.data_path, "thumb.png")


        ####################################################################################################
        #START OF GUI
        #Initializing main self.window


        self.window = Tk()
        self.window.title("Youtube Downloader")
        self.window.geometry("600x600")
        self.window.configure(bg="#222222")
        self.window.resizable(False, False) 

        #Fonts
        self.titleFont = ("Yu Gothic UI Light", 30)
        self.mainFont = ("Yu Gothic UI Light", 11)
        self.main2Font = ("Yu Gothic UI Light", 13)
        self.downloadFont = ("Yu Gothic UI Light", 16)
        self.authorFont = ("Yu Gothic UI Light", 9)

        #Variables for ComboBoxes        
        self.link_variable = StringVar()
        self.link_variable.set("")
        self.choice_variable = StringVar()
        self.mode_variable = StringVar()

        #Style for ComboBoxes
        self.style = ttk.Style()
        self.style.theme_create('combostyle', parent='alt',
                         settings = {'TCombobox':
                                     {'configure':
                                      {'selectbackground': '#1c1c1c',
                                       'foreground': '#1c1c1c',
                                       'fieldbackground': '#1c1c1c',
                                       'background': '#1c1c1c',
                                       'arrowcolor': '#ffffff'
                                       }}}
                         )
        self.style.theme_use('combostyle') 


        #Creating canvas
        self.canvas = Canvas(self.window, width=600, height=600, bg='yellow')
        self.canvas.pack()

        image = ImageTk.PhotoImage(Image.open(self.bg_path).resize((600,600), Image.ANTIALIAS))
        self.canvas.create_image(0, 0, image=image, anchor='nw')

        self.canvas.create_text(130, 30, text="Youtube", anchor='nw', fill='#ff0000', font=self.titleFont)
        self.canvas.create_text(280, 30, text="Downloader", anchor='nw', fill='#ffffff', font=self.titleFont)
        self.canvas.create_rectangle(127, 83, 485, 85, fill="#ffffff")

        self.canvas.create_text(280, 140, text="LINK:", anchor='nw', fill='#ffffff', font=self.main2Font)

        self.linkEntry = Entry(self.window, width=75, textvariable=self.link_variable, highlightthickness=0, bg="#1c1c1c", fg="#ffffff")
        self.linkEntry.configure(highlightbackground="gray", highlightcolor="gray")
        self.linkEntry.focus_force()
        self.linkEntry.place(x=70, y=170)

        self.browseButton = Button(self.window, width=19, text="SELECT FOLDER...", font = self.mainFont, command=self.browseFiles, bg="#1c1c1c", fg="#ffffff")
        self.browseButton.place(x=218, y=220)

        self.canvas.create_text(95, 280, text="VIDEO/PLAYLIST:", anchor='nw', font=self.mainFont, fill='#ffffff')
        self.canvas.create_text(70, 320, text="DOWNLOAD MODE:", anchor='nw', font=self.mainFont, fill='#ffffff')

       
        self.choiceCombo = ttk.Combobox(self.window, width=18, values=["VIDEO", "PLAYLIST"], state="readonly", foreground="#ffffff", background="#000000", font=self.mainFont, textvariable=self.choice_variable)
        self.choiceCombo.set("VIDEO")
        self.choiceCombo.place(x=218, y=280)

        self.modeCombo = ttk.Combobox(self.window, width=18, values=["AUDIO", "VIDEO"], state="readonly", foreground="#ffffff", font=self.mainFont, textvariable=self.mode_variable)
        self.modeCombo.set("AUDIO")
        self.modeCombo.place(x=218, y=320)
        
        self.button = Button(self.window, text="DOWNLOAD", width=14, height=1 , font = self.downloadFont, command=self.download_thread, bg="#1c1c1c", fg="#ed1212")
        self.button.place(x=218, y=370)

        self.canvas.create_text(240, 450, text="VIDEO DETAILS", anchor='nw', fill="#ffffff", font=self.main2Font)
        self.canvas.create_rectangle(238, 474, 355, 476, fill="#ffffff")

        self.canvas.create_rectangle(149, 489, 295, 572, outline="#ffffff")

        self.textPlaylist = self.canvas.create_text(191, 517, text=None, anchor='nw', fill="#ffffff", font=self.main2Font)
        self.imageThumbnail = self.canvas.create_image(150, 490, anchor='nw', image=self.thumbnail)

        self.title = self.canvas.create_text(310, 490, text="TITLE", anchor='nw', fill='#ffffff', font=self.main2Font)
        self.author = self.canvas.create_text(310, 515, text="AUTHOR", anchor='nw', fill='#ffffff', font=self.authorFont)

        self.canvas.create_rectangle(310, 540, 512, 560, outline="#ffffff")
        #511 max value
        self.progressbar = self.canvas.create_rectangle(311, 541, 311, 559, fill="#AD0000")

        self.progressText = self.canvas.create_text(410, 549, text="0%", fill="#ffffff", font=("Yu Gothic UI Light", 9, "bold"))


        self.canvas.create_text(520, 570, text="BY PIAYER69", anchor='nw', fill="#ffffff", font=self.authorFont)
        
        #END OF GUI
        ######################################################################################################


        self.file_size = 0
        self.progress = 0

        #Tracing link changes
        tracing = threading.Thread(target=self.trace_info)
        tracing.start()

        self.window.mainloop()

    #Tracking variables
    def trace_info(self):
        #Downloading info if link is valid
        self.link_variable.trace("w", self.update_info_thread)
        self.mode_variable.trace("w", self.update_info_thread)
        self.choice_variable.trace("w", self.update_info_thread)
        time.sleep(1)

    #Threading downloading
    def download_thread(self):
        threading.Thread(target=self.download).start()

    #On button click
    def download(self):
        #Getting all variables
        self.button["state"] = "disabled"
        link = self.linkEntry.get()
        choice = self.choiceCombo.get()
        mode = self.modeCombo.get()
        print("Pobieranie")
        print(link, choice, mode)

        #Reseting progress bar
        self.canvas.coords(self.progressbar, 311, 541, 311, 559)
        self.canvas.itemconfigure(self.progressText, text="0%")
        self.progress = 0

        #Checikng if provided link is valid
        try:
            if choice == "VIDEO":
                # self.window.after(0, self.init_progress_window)
                video = pytube.YouTube(link, on_progress_callback=self.progress_update, on_complete_callback=self.progress_complete)
                self.d_video(video, mode)
                messagebox.showinfo("Done", "Downloaded video!")
                
            elif choice == "PLAYLIST":
                video = pytube.Playlist(link)
                self.playlist_length = len(video.video_urls)
                self.downloaded_videos = 0
                self.d_playlist(video, mode)
                messagebox.showinfo("Done", "Downloaded playlist!")
        except:
            messagebox.showinfo("Error", "Invalid link, make sure you selected playlist/video")
        
        self.button["state"] = "normal"

    #Threading update_info()
    def update_info_thread(self, a,b,c):
        y = threading.Thread(target=self.update_info)
        y.start()

    #On linkEntry change trying to download video/playlist info
    def update_info(self):
        link = self.linkEntry.get()
        choice = self.choiceCombo.get()
        print(link, choice)


        try:
            if choice == "VIDEO":
                video = pytube.YouTube(link)
                
                title = self.title_handler(video.title)

                #Updating video info
                self.canvas.itemconfigure(self.title, text=title)
                self.canvas.itemconfigure(self.author, text=video.author)

                #Thumbnail setting
                self.canvas.itemconfigure(self.textPlaylist, text="")
                self.download_thumbnail(video.thumbnail_url, self.data_path, "thumb.png")
                self.thumbnail = ImageTk.PhotoImage(Image.open(self.thumbnail_path).resize((144,81), Image.ANTIALIAS))
                self.canvas.itemconfigure(self.imageThumbnail, image=self.thumbnail)
                    

            elif choice == "PLAYLIST":
                video = pytube.Playlist(link)
                self.playlist_length = len(video.video_urls)

                title = self.title_handler(video.title)

                #Updating playlist info
                self.canvas.itemconfigure(self.title, text=title)
                self.canvas.itemconfigure(self.author, text=f"Videos: {self.playlist_length}")

                self.canvas.itemconfigure(self.imageThumbnail, image="")
                self.canvas.itemconfigure(self.textPlaylist, text="PLAYLIST")
                  
        except pytube.exceptions.RegexMatchError:
            print("Error")
            pass

    #Calling on progress
    def progress_update(self, stream, chunk, bytes_remaining):
        # self.progress_window
        self.progress = (self.file_size - bytes_remaining) / self.file_size * 100
        x1 = 311 + self.progress * 2
        # print(self.progress)
        self.canvas.itemconfigure(self.progressText, text=f"{round(self.progress)}%")
        self.canvas.coords(self.progressbar, 311, 541, x1, 559)

    #Calling when downloaded
    def progress_complete(self, smth, file_path):
        self.canvas.coords(self.progressbar, 311, 541, 511, 559)
        self.canvas.itemconfigure(self.progressText, text="100%")


    def progress_update_playlist(self):
        self.progress = self.downloaded_videos / self.playlist_length * 100
        x1 = 311 + self.progress * 2
        # print(self.progress)
        self.canvas.itemconfigure(self.progressText, text=f"{round(self.progress)}%")
        self.canvas.coords(self.progressbar, 311, 541, x1, 559)

    #File browser
    def browseFiles(self):
        self.directory_path = filedialog.askdirectory(title = "Select a Folder")
        
    #Downloading video
    def d_video(self, video, mode):
        print(f"Video: {video.title}")
        try:
            self.file_size
            if mode == "AUDIO":
                self.file_size = video.streams.filter(only_audio=True).first().filesize
                video.streams.filter(only_audio=True).first().download(output_path=self.directory_path)
                print("Downloaded audio")
            elif mode == "VIDEO":
                self.file_size = video.streams.filter(progressive=True).first().filesize
                video.streams.filter(progressive=True).first().download(output_path=self.directory_path)
                print("Downloaded video")

        except pytube.exceptions.VideoUnavailable:
                print("UNAVAILABLE!!!")

    #Downloading playlist
    def d_playlist(self, playlist, mode):
        print(f"Playlist: {playlist.title}")

        for video in playlist.videos:
            self.d_video(video, mode)
            self.downloaded_videos += 1
            self.progress_update_playlist()
            
    #Thumbnail downloader, %LOCALAPPDATA%/YouTube Downloader
    def download_thumbnail(self, url, path, name):
        thumbnail_link = url
        thumbnail = requests.get(thumbnail_link)
        with open(os.path.join(path, name), "wb") as file:
            file.write(thumbnail.content)

    
    def title_handler(self, title):
        return(f"{title[:20]}...")



if __name__ == "__main__":
    yt = Downloader()