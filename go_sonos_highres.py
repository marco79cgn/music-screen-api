import tkinter as tk
import tkinter.font as tkFont
import time
import sys
import sonos_user_data
import sonos_settings
import requests
from io import BytesIO
from PIL import ImageTk, Image
import os
import demaster

###############################################################################
# Parameters and global variables

# set user variables
thumbsize = 600,600   # pixel size of thumbnail if you're displaying detail
screensize = 720,720  # pixel size of HyperPixel 4.0
fullscreen = True
show_details = False   # if set to false then just shows the album art; if set to true then also displays track name + album/artist name
show_artist_and_album = True   #if set to true then shows artist and album at the bottom; if false just shows track name; won't do anything if show_detail is false

# Declare global variables (don't mess with these)
root = None
frame = None
track_name = None
detail_text = None
tk_image = None
font_size = 0
previous_polled_trackname = None
thumbwidth = thumbsize[1]
screenwidth = screensize[1]
sonos_room = None

###############################################################################
# Functions

# Read values from the sensors at regular intervals
def update():

    global root
    global track_name
    global tk_image
    global previous_polled_trackname

    # Get sonos data from API
    current_trackname, current_artist, current_album, current_image, playing_status = sonos_user_data.current(sonos_room)

    # see if something is playing
    if playing_status == "PLAYING":

        # check whether the track has changed - don't bother updating everything if not
        if current_trackname != previous_polled_trackname:

            # update previous trackname so we know what has changed in future
            previous_polled_trackname = current_trackname

            # set the details we need from the API into variables
            track_name.set(current_trackname)
            detail_text.set(current_artist + " • "+ current_album)

            # slim down the trackname
            if sonos_settings.demaster:
                current_trackname = demaster.strip_name (current_trackname)

            # show the image
            image_url = current_image
            image_url_response = requests.get(image_url)
            pil_image = Image.open(BytesIO(image_url_response.content))

            #pil_image = Image.open ('Bleachers.jpg')

            if show_details == True:
                target_image_width = thumbwidth
            else:
                target_image_width = screenwidth

            wpercent = (target_image_width/float(pil_image.size[0]))
            hsize = int((float(pil_image.size[1])*float(wpercent)))
            pil_image = pil_image.resize((target_image_width,hsize), Image.ANTIALIAS)
                        
            tk_image = ImageTk.PhotoImage(pil_image)
            label_albumart.configure (image = tk_image)


    if playing_status != "PLAYING":
        track_name.set("")
        detail_text.set("")
        label_albumart.configure (image = "")
        previous_polled_trackname = ""

    # Schedule the poll() function for another 500 ms from now
    root.after(500, update)

###############################################################################
# Main script

# check if a command line argument has been passed to identify the user, if not ask
if len(sys.argv) == 1:
    # if no room name passed then ask the user to input a room name
    sonos_room = input ("Enter a Sonos room name >>>  ")
else:
    # if command line includes username then set it to that
    sonos_room = str(sys.argv[1])
    print (sonos_room)

# Create the main window
root = tk.Tk()
root.geometry("720x720")
root.title("Music Display")

# Create the main container
frame = tk.Frame(root, bg='black', width=720, height=720)

# Lay out the main container (expand to fit window)
frame.pack(fill=tk.BOTH, expand=1)

# Set variables
track_name = tk.StringVar()
detail_text = tk.StringVar()
if show_artist_and_album:
    track_font = tkFont.Font(family='Helvetica', size=30)
else:
    track_font = tkFont.Font(family='Helvetica', size=40)
image_font = tkFont.Font(size=25)
detail_font = tkFont.Font(family='Helvetica', size=15)

# Create widgets
label_albumart = tk.Label(frame, 
                        image = None,
                        font=image_font, 
                        borderwidth=0,
                        highlightthickness=0, 
                        fg='white',
                        bg='black')  
label_track = tk.Label(frame, 
                        textvariable=track_name, 
                        font=track_font, 
                        fg='white', 
                        bg='black',
                        wraplength=600,
                        justify="center")
label_detail = tk.Label(frame,
                        textvariable=detail_text, 
                        font=detail_font, 
                        fg='white', 
                        bg='black',
                        wraplength=600,
                        justify="center")                      


if show_details == False:
    label_albumart.place (relx=0.5, rely=0.5, anchor=tk.CENTER)

if show_details == True: 
    label_albumart.place(x=360, y=thumbsize[1]/2, anchor=tk.CENTER)
    label_track.place (x=360, y=thumbsize[1]+20, anchor=tk.N)

    label_track.update()
    height_of_track_label = label_track.winfo_reqheight()

    if show_artist_and_album:
        label_detail.place (x=360, y=710, anchor=tk.S)

frame.grid_propagate(False)

# Schedule the poll() function to be called periodically
root.after(20, update)

# Start in fullscreen mode and run
root.attributes('-fullscreen', fullscreen)
root.mainloop()
