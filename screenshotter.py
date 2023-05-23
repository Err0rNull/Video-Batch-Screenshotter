import tkinter as tk
from tkinter import filedialog, messagebox
from moviepy.editor import VideoFileClip
from PIL import Image
import os

def select_video():
    video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.mkv")])
    video_path_entry.delete(0, tk.END)
    video_path_entry.insert(0, video_path)

def select_output_folder():
    output_folder = filedialog.askdirectory()
    output_folder_entry.delete(0, tk.END)
    output_folder_entry.insert(0, output_folder)

def extract_screenshots():
    video_path = video_path_entry.get()
    output_folder = output_folder_entry.get()
    interval = interval_entry.get()

    if not os.path.isfile(video_path):
        messagebox.showerror("Error", "Invalid video path")
        return

    if not os.path.isdir(output_folder):
        messagebox.showerror("Error", "Invalid output folder")
        return

    try:
        interval = int(interval)
    except ValueError:
        messagebox.showerror("Error", "Interval must be an integer")
        return

    try:
        clip = VideoFileClip(video_path)
        duration = clip.duration

        for i in range(0, int(duration), interval):
            frame = clip.get_frame(i)
            frame_image = Image.fromarray(frame)
            frame_image.save(f"{output_folder}/screenshot_{i}.png")

        messagebox.showinfo("Success", "Screenshots extracted successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()

video_path_label = tk.Label(root, text="Video Path")
video_path_label.pack()
video_path_entry = tk.Entry(root)
video_path_entry.pack()
video_path_button = tk.Button(root, text="Select Video", command=select_video)
video_path_button.pack()

output_folder_label = tk.Label(root, text="Output Folder")
output_folder_label.pack()
output_folder_entry = tk.Entry(root)
output_folder_entry.pack()
output_folder_button = tk.Button(root, text="Select Folder", command=select_output_folder)
output_folder_button.pack()

interval_label = tk.Label(root, text="Interval (in seconds)")
interval_label.pack()
interval_entry = tk.Entry(root)
interval_entry.pack()

extract_button = tk.Button(root, text="Extract Screenshots", command=extract_screenshots)
extract_button.pack()

root.mainloop()
