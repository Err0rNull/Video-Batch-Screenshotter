import os
import googleapiclient.discovery
import googleapiclient.errors
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import csv

def load_config_file():
    with open('config.txt', 'r') as f:
        api_key = f.read().strip()
    api_key_entry.delete(0, END)
    api_key_entry.insert(0, api_key)

def browse_config_file():
    filename = filedialog.askopenfilename()
    with open(filename, 'r') as f:
        api_key = f.read().strip()
    api_key_entry.delete(0, END)
    api_key_entry.insert(0, api_key)

def get_channel_videos(api_key, video_url, max_results):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

    # Extract video ID from URL
    if 'watch?v=' in video_url:
        video_id = video_url.split('watch?v=')[-1]
    elif 'youtu.be/' in video_url:
        video_id = video_url.split('youtu.be/')[-1]
    else:
        raise ValueError("Invalid video URL")

    request = youtube.videos().list(
        part="snippet",
        id=video_id
    )
    response = request.execute()
    if 'items' in response and len(response['items']) > 0:
        channel_id = response['items'][0]['snippet']['channelId']
    else:
        raise ValueError("Video not found")

    video_data = []
    page_token = None
    while len(video_data) < max_results:
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            maxResults=min(max_results - len(video_data), 50),
            order="date",
            pageToken=page_token
        )
        response = request.execute()

        for item in response['items']:
            if item['id']['kind'] == 'youtube#video':
                video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                video_name = item['snippet']['title']
                video_data.append((video_url, video_name))

        if 'nextPageToken' in response:
            page_token = response['nextPageToken']
        else:
            break

    return video_data


def get_playlist_videos(api_key, video_url, max_results):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

    # Extract video ID from URL
    if 'watch?v=' in video_url:
        video_id = video_url.split('watch?v=')[-1]
    elif 'youtu.be/' in video_url:
        video_id = video_url.split('youtu.be/')[-1]
    else:
        raise ValueError("Invalid video URL")

    request = youtube.videos().list(
        part="snippet",
        id=video_id
    )
    response = request.execute()
    if 'items' in response and len(response['items']) > 0:
        playlist_id = response['items'][0]['snippet']['playlistId']
    else:
        raise ValueError("Video not found")

    video_data = []
    page_token = None
    while len(video_data) < max_results:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=min(max_results - len(video_data), 50),
            pageToken=page_token
        )
        response = request.execute()

        for item in response['items']:
            video_url = f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}"
            video_name = item['snippet']['title']
            video_data.append((video_url, video_name))

        if 'nextPageToken' in response:
            page_token = response['nextPageToken']
        else:
            break

    return video_data



def save_to_file(video_data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["URL", "Name"])
        writer.writerows(video_data)


def browse_button():
    filename = filedialog.asksaveasfilename(defaultextension=".csv")
    file_path.set(filename)

def start_extraction():
    api_key = api_key_entry.get()
    video_url = video_url_entry.get()
    filename = file_path.get()
    max_results = int(max_results_entry.get())
    if url_type.get() == "Channel":
        video_urls = get_channel_videos(api_key, video_url, max_results)
    else:  # url_type.get() == "Playlist"
        if 'list=' not in video_url:
            messagebox.showerror("Error", "Invalid playlist URL")
            return
        video_urls = get_playlist_videos(api_key, video_url, max_results)
    save_to_file(video_urls, filename)
    messagebox.showinfo("Success", "Video URLs have been extracted and saved to the file.")

#-----------Tooltip-----------------

class ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tip_window = None
        self.id = None
        self.x = self.y = 0

    def show_tip(self, tip_text):
        "Display text in a tooltip window"
        self.text = tip_text
        if self.tip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 20
        self.tip_window = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = Label(tw, text=self.text, background="#ffffe0", relief=SOLID, borderwidth=1)
        label.pack(ipadx=1)

    def hide_tip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

def create_tooltip(widget, text):
    tool_tip = ToolTip(widget)
    def enter(event):
        tool_tip.show_tip(text)
    def leave(event):
        tool_tip.hide_tip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


#----------------------

root = Tk()
root.title("YouTube Video Extractor")

api_key_entry = Entry(root)
api_key_entry.pack()
Label(root, text="Enter your YouTube API Key").pack()
config_file_button = Button(text="Load API Key from config.txt", command=load_config_file)
config_file_button.pack()

Label(root, text="-----------------------------").pack()

video_url_entry = Entry(root)
video_url_entry.pack()
Label(root, text="Enter the Video URL you want to extract Videos from").pack()

button = Button(root, text="Need Help?")
button.pack()
create_tooltip(button, "The google API is picky, while a Channel ID can be gotten from a single video \n a Playlist cannot, as it would grab the videos from every playlist that video is in. \n \n So, You can use any video URL to get every video from that creators channel, but you have to get the \n specific Playlist URL if you want every video from a playlist.")


url_type = StringVar()
url_type_combobox = ttk.Combobox(root, textvariable=url_type)
url_type_combobox['values'] = ("Channel", "Playlist")
url_type_combobox.current(0)  # set initial selection to "Channel"
url_type_combobox.pack()
Label(root, text="Select whether you want the URLs of Channel Videos or Playlist Videos").pack()

max_results_entry = Entry(root)
max_results_entry.pack()
Label(root, text="Enter the number of videos to extract (between 1 and 400)").pack()

Label(root, text="-----------------------------").pack()

file_path = StringVar()
save_file_button = Button(text="Choose output folder and specify a .csv file name", command=browse_button)
save_file_button.pack()

start_button = Button(text="Start Extraction", command=start_extraction)
start_button.pack()

Label(root, text="Note: This grabs the most recent videos.").pack()

root.mainloop()
