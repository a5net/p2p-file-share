

# CS333 Computer Networks - Homework 3

## Libraries

Python version: 3.6.9
Libraries: Tkinter with ttk extension (for GUI)

## How to use?

 1. Launch server.py and write the port number on which server should
    operate.
 2. Launch client.py and connect to File Tracker Server using 
    information from step 1. Also, choose available port number for 
    client.
 3. Once connected your files in "/files" will be available to other
    peers.
 4. Try to search for a file, note that name of the file has to be an
    exact much. For example if you want to download "dog_in_park" file,
    then type "dog_in_park", "dog_in_" will return an empty result
 5. Press "Download" button, file will be saved in "/downloads" which
    has be located in the same directory as "client.py"

## Screenshots

![Client GUI (Tkinter)](https://github.com/ayanginet/p2p-File-Share/tree/master/screenshots/gui.png)