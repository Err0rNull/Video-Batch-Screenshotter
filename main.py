

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import PhotoImage
from moviepy.editor import VideoFileClip
from PIL import Image, ImageTk
import os
import os.path
from pytube import YouTube
import csv

root = tk.Tk()  # Define root globally
screenshot_label = tk.Label(root) # Define globally
screenshot_label.pack() # Define globally

# Create a list to store the images
images = []

# Create a label for the spinner and pack it (but don't display it yet)
spinner_label = tk.Label(root, text="Screenshotting in Progress")
spinner_label.pack_forget()

def select_videos():
    video_paths = filedialog.askopenfilenames(filetypes=[("Video files", "*.mp4;*.avi;*.mkv"), ("Text files", "*.txt"), ("CSV files", "*.csv")])
    video_paths_list = []
    for path in video_paths:
        if path.endswith('.txt'):
            with open(path, 'r') as f:
                video_paths_list.extend(f.read().splitlines())
        elif path.endswith('.csv'):
            with open(path, 'r', encoding='utf-8') as f:  # Open with UTF-8 encoding
                reader = csv.reader(f)
                next(reader, None)  # skip the headers
                video_paths_list.extend(row[0] for row in reader)
        else:
            video_paths_list.append(path)
    video_path_entry.delete(0, tk.END)
    video_path_entry.insert(0, ', '.join(video_paths_list))


def select_output_folder():
    output_folder = filedialog.askdirectory()
    output_folder_entry.delete(0, tk.END)
    output_folder_entry.insert(0, output_folder)

def extract_screenshots_from_video(video_path, output_folder, interval):
    # Check if the video path is a YouTube URL
    if "youtube.com" in video_path or "youtu.be" in video_path:
        try:
            yt = YouTube(video_path)
            video = yt.streams.get_highest_resolution()
            video_path = video.download(output_folder)
        except Exception as e:
            if ignore_errors_var.get() == 0:  # If the "Ignore errors" checkbox is not checked
                messagebox.showerror("Error", "Failed to download YouTube video: " + str(e))
            else:
                with open('error_log.txt', 'a') as f:  # Open the error log file in append mode
                    f.write(
                        f"Failed to download YouTube video {video_path}: {str(e)}\n")  # Write the error message to the file
            return

        if not os.path.isfile(video_path):
            messagebox.showerror("Error", "Invalid video path: " + video_path)
            return

        # Get the video name
        video_name = os.path.splitext(os.path.basename(video_path))[0]

        # Update the window title with the video name
        root.title(f"Video Batch Screenshotter | {video_name} | Screenshotting in Progress...")

        # Update the spinner label with the video name
        spinner_label.config(text=f"{video_name} | Screenshotting in Progress...")

        # Check if the "Save in subfolder" option is checked
        if save_in_subfolder_var.get():
            output_folder = os.path.join(output_folder, video_name)

            # Create the subfolder if it doesn't exist
            os.makedirs(output_folder, exist_ok=True)

        try:
            clip = VideoFileClip(video_path)
            duration = clip.duration

            progress_bar['maximum'] = duration

            for i in range(0, int(duration), interval):
                frame = clip.get_frame(i)
                frame_image = Image.fromarray(frame)

                # Check if a file with the same name already exists
                base_filename = f"screenshot_{i}"
                extension = ".png"
                counter = 1
                while os.path.isfile(os.path.join(output_folder, base_filename + extension)):
                    base_filename = f"screenshot_{i}_{counter}"
                    counter += 1

                frame_image.save(os.path.join(output_folder, base_filename + extension))

                # Update progress bar
                progress_bar['value'] = i
                root.update()

                # Update screenshot label
                screenshot = ImageTk.PhotoImage(frame_image)
                screenshot_label.config(image=screenshot)

                # Add the image to the list to prevent it from being garbage collected
                images.append(screenshot)

                root.update()

            # Update progress bar
            progress_bar['value'] = duration

            # Close the VideoFileClip object
            clip.close()

            # After extracting screenshots, check if the "Delete source video" option is checked
            if delete_source_video_var.get():
                try:
                    os.remove(video_path)
                    spinner_label.config(
                        text=f"Screenshots extracted successfully and source video {video_name} deleted!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete source video {video_path}: {str(e)}")
            else:
                spinner_label.config(text=f"Screenshots extracted successfully from {video_name}!")

        except Exception as e:
            messagebox.showerror("Error", str(e))


def extract_screenshots():
    video_paths = video_path_entry.get().split(', ')
    output_folder = output_folder_entry.get()
    interval = interval_entry.get()

    # Convert interval to an integer
    try:
        interval = int(interval)
    except ValueError:
        if ignore_errors_var.get() == 0:  # If the "Ignore errors" checkbox is not checked
            messagebox.showerror("Error", "Interval must be an integer")
        return

    # Show the spinner while the processing is happening
    spinner_label.pack()

    for video_path in video_paths:
        try:
            extract_screenshots_from_video(video_path, output_folder, interval)
        except Exception as e:
            # If there's an error with one of the videos, show an error message and continue with the next video
            if ignore_errors_var.get() == 0:  # If the "Ignore errors" checkbox is not checked
                messagebox.showerror("Error", f"Failed to extract screenshots from {video_path}: {str(e)}")
            else:
                with open('error_log.txt', 'a') as f:  # Open the error log file in append mode
                    f.write(
                        f"Failed to extract screenshots from {video_path}: {str(e)}\n")  # Write the error message to the file
            continue

    # Hide the spinner after the processing is done
    spinner_label.pack_forget()

    # Reset the window title
    root.title("Video Batch Screenshotter")

    # Show the success message after all videos have been processed
    spinner_label.config(text="Screenshots extracted successfully from all videos!")


def open_YTChannelVideoList(): # Open Youtube Channel Video URL Extractor
    os.system('python YTChannelVideoList.py')

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
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, background="#ffffe0", relief=tk.SOLID, borderwidth=1)
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

def main():
    global video_path_entry, output_folder_entry, interval_entry, progress_bar, screenshot_label, save_in_subfolder_var, delete_source_video_var, ignore_errors_var

    root.title("Video Batch Screenshotter")

    video_path_label = tk.Label(root, text="Select Video(s) or input YouTube URL(s) Separate multiple URLs \nwith a comma, Or use a .txt or .csv with each video location on a new line.")
    video_path_label.pack()
    video_path_entry = tk.Entry(root, width=50)
    video_path_entry.pack()
    video_path_button = tk.Button(root, text="Select Videos", command=select_videos)
    video_path_button.pack()

    open_program_label = tk.Label(root, text="OR \n Click to create a list of videos from a youtube channel and save into a .CSV file that can be loaded into the video input. \n Warning: YouTube Videos are downloaded before being screenshot, so make sure you have enough drive space.")
    open_program_label.pack()
    open_program_button = tk.Button(root, text="YouTube Channel Videos to .CSV File", command=open_YTChannelVideoList)
    open_program_button.pack()

    # Add a checkbox for the "Delete source video" option
    delete_source_video_var = tk.IntVar()
    delete_source_video_checkbutton = tk.Checkbutton(root,
                                                     text="Check box to delete source video after processing \n WARNING: Only click this if you want to delete the videos after ripping screenshots!",
                                                     variable=delete_source_video_var)
    delete_source_video_checkbutton.pack()


    tk.Label(root, text="-----------------------------").pack()

    output_folder_label = tk.Label(root, text="Output Folder")
    output_folder_label.pack()
    output_folder_entry = tk.Entry(root)
    output_folder_entry.pack()
    output_folder_button = tk.Button(root, text="Select Folder", command=select_output_folder)
    output_folder_button.pack()

    # Add a checkbox for the "Save in subfolder" option
    save_in_subfolder_var = tk.IntVar()
    save_in_subfolder_checkbutton = tk.Checkbutton(root, text="Check box to Save screenshots in video-named subfolder", variable=save_in_subfolder_var)
    save_in_subfolder_checkbutton.pack()

    tk.Label(root, text="-----------------------------").pack()

    interval_label = tk.Label(root, text="Interval between screenshots (in seconds)")
    interval_label.pack()
    interval_entry = tk.Entry(root)
    interval_entry.pack()

    tk.Label(root, text="-----------------------------").pack()

    # Add a checkbox for the "Ignore errors" option
    ignore_errors_var = tk.IntVar()
    ignore_errors_checkbutton = tk.Checkbutton(root, text="Ignore errors? - Will suppresses all error messages and log them instead.", variable=ignore_errors_var)
    ignore_errors_checkbutton.pack()

    need_help_button = tk.Button(root, text="Need Help?")
    need_help_button.pack()
    create_tooltip(need_help_button,
                   "FAQ\n------------ \n\n What video formats are supported?\nThe program supports .mp4, .avi, and .mkv video formats for local files. It also supports YouTube URLs. \n\nStruggling to add a .txt or .csv list for import? \nIn the bottom right hand change the file type to the file type of your list, and make sure you are in the right folder. \n\n What does the \"Interval between screenshots\" option do?\nThis option allows you to set the time interval between each screenshot in seconds.\nFor example, if you set it to 10, the program will take a screenshot every 10 seconds of the video. \n\nWhat does the \"Save in subfolder\" option do?\nIf this option is checked, the screenshots for each video will be saved in a separate subfolder named after the video.\nIf it\'s not checked, all screenshots will be saved in the main output folder. \n\nWhat does the \"Delete source video\" option do?\nIf this option is checked, the program will delete the source video file after extracting screenshots from it. \nBe careful with this option, as it will permanently delete the video file from your disk. \n\n Will the program delete the only copy I have of my favorite irreplacable family video?\nFirst, why the hell don\'t you have other backups of it? Second, if you have the \"Delete source video\" checkbox checked, then YES, yes it will. But seriously, back up your important vids before doing things with them. \n\n Why would I want error messages? \nJust in case your video wont process for some reason, it\'s nice to know the reason! But for batch processing, \nI highly reccomend checking to disable error messages, it will create an error_log file instead so you'll know what failed and why, \nbut won\'t require you sit there and click error messages to keep things running. \n\nWhat happens if the program is interrupted during the screenshot extraction process? \nIf the program is interrupted during the screenshot extraction process, it may not complete the extraction for the current video. \nYou will need to run the program again to extract screenshots from the interrupted video. \n\nWhat happens if I don\'t have enough disk space for the screenshots? \nIf you run out of disk space during the screenshot extraction process, the program may fail and you may not get all the screenshots. \nMake sure you have enough disk space before you start the process. \n\nHow can I improve the speed of screenshot extraction? \nThe speed of screenshot extraction depends on the processing power of your computer and the size of the video. \nIf you want to speed up the process, you can try closing other programs to free up system resources. \n\nWhy are my screenshots not in the order I expected? \nThe screenshots are named based on the timestamp in the video they were extracted from. \nIf you\'re seeing them in an unexpected order, it may be because your file explorer is sorting them differently. \nTry sorting by file name in your file explorer. \n\nRemember, it\'s always a good idea to back up your videos and other important files \nbefore running any kind of processing or modification program.")

    tk.Label(root, text="-----------------------------").pack()

    extract_button = tk.Button(root, text="Click to Extract Screenshots!", command=extract_screenshots)
    extract_button.pack()

    progress_bar_label = tk.Label(root, text="Progress")
    progress_bar_label.pack()
    progress_bar = ttk.Progressbar(root)
    progress_bar.pack()

    root.mainloop()

if __name__ == "__main__":
    main()
