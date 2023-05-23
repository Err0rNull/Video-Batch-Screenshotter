# Video-Batch-Screenshotter
Version: Alpha 01.01.01


Video Batch Screenshotter is a Python-based application that automates the process of extracting screenshots from multiple videos. It is designed with a user-friendly GUI using the Tkinter library, making it easy for users to interact with the program.

Features
Batch Processing: The program allows users to select multiple videos at once, or input YouTube URLs, for screenshot extraction. It also supports .txt and .csv files as input, where each video location or URL is on a new line or in the first column respectively.

Interval Setting: Users can specify the interval between screenshots in seconds.

YouTube Video Support: The program can download YouTube videos and extract screenshots from them.

Output Folder Selection: Users can select the output folder where the screenshots will be saved. There is also an option to save screenshots in a subfolder named after the video.

Progress Display: The program displays the progress of screenshot extraction for each video.

Error Handling: The program provides error messages when it encounters issues during the screenshot extraction process. There is an option to ignore and log these errors for uninterrupted batch processing.

Source Video Deletion: There is an option to delete the source video after it has been processed for screenshots.

Help Tooltip: A tooltip is available to provide users with additional information and help.

Usage
The program is designed to be user-friendly and easy to use. Users can select videos or input YouTube URLs, choose the output folder, set the interval between screenshots, and then click the "Extract Screenshots" button to start the process. The program will then extract screenshots from the selected videos at the specified intervals and save them in the chosen output folder.

Note
This program requires certain Python libraries to function, including Tkinter for the GUI, moviepy for video processing, PIL for image processing, pytube for downloading YouTube videos, and csv for handling .csv files. Please ensure these libraries are installed before running the program.
