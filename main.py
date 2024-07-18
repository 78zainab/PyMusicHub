import pygame
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import random
from mutagen.mp3 import MP3
from tkinter import font

# Initialize Pygame mixer
pygame.mixer.init()

# Function to load songs from the music_library directory
def load_songs():
    song_directory = os.path.join(os.getcwd(), 'music_library')
    if os.path.exists(song_directory):
        os.chdir(song_directory)
        songs = [f for f in os.listdir(song_directory) if f.endswith('.mp3')]
        listbox.delete(*listbox.get_children())  # Clear existing listbox items
        for song in songs:
            audio = MP3(song)
            title = audio.get('TIT2', os.path.splitext(song)[0])
            artist = audio.get('TPE1', 'Unknown Artist')
            duration = int(audio.info.length)
            mins, secs = divmod(duration, 60)
            duration_str = f"{mins:02d}:{secs:02d}"
            listbox.insert("", "end", values=(title, artist, duration_str))
    else:
        messagebox.showerror("Error", "Music library directory not found!")

# Function to play the selected song
def play_song():
    try:
        selected_item = listbox.selection()[0]
        selected_song = listbox.item(selected_item, 'values')[0]
        pygame.mixer.music.load(selected_song + '.mp3')
        pygame.mixer.music.play()
        update_progress_bar()
        update_beat_bar()
    except IndexError:
        messagebox.showerror("Error", "No song selected!")

# Function to pause the song
def pause_song():
    pygame.mixer.music.pause()

# Function to resume the song
def resume_song():
    pygame.mixer.music.unpause()
    update_progress_bar()
    update_beat_bar()

# Function to play the next song
def next_song():
    try:
        next_song_index = (listbox.index(listbox.selection()[0]) + 1) % len(listbox.get_children())
        listbox.selection_clear()
        listbox.selection_set(listbox.get_children()[next_song_index])
        play_song()
    except IndexError:
        messagebox.showerror("Error", "No song selected!")

# Function to play the previous song
def previous_song():
    try:
        prev_song_index = (listbox.index(listbox.selection()[0]) - 1) % len(listbox.get_children())
        listbox.selection_clear()
        listbox.selection_set(listbox.get_children()[prev_song_index])
        play_song()
    except IndexError:
        messagebox.showerror("Error", "No song selected!")

# Function to update the progress bar
def update_progress_bar():
    if pygame.mixer.music.get_busy():
        current_pos = pygame.mixer.music.get_pos() / 1000  # Current position in seconds
        selected_item = listbox.selection()[0]
        selected_song = listbox.item(selected_item, 'values')[0]
        song_length = MP3(selected_song + '.mp3').info.length  # Song length in seconds
        progress['value'] = (current_pos / song_length) * 100

        mins, secs = divmod(int(current_pos), 60)
        elapsed_time_label.config(text=f"{mins:02d}:{secs:02d}")
        
        root.after(1000, update_progress_bar)  # Update every second

# Function to update the beat bar
def update_beat_bar():
    if pygame.mixer.music.get_busy():
        canvas.delete("all")
        for i in range(10):
            x0 = i * 30
            x1 = x0 + 20
            y1 = random.randint(10, 100)
            canvas.create_rectangle(x0, 100, x1, 100 - y1, fill="green")
        root.after(100, update_beat_bar)  # Update every 100 ms

# Function to set volume
def set_volume(val):
    volume = float(val) / 100
    pygame.mixer.music.set_volume(volume)

# Function to toggle mute
def toggle_mute():
    global muted
    global current_volume  # Declare current_volume as global before using it
    if muted:
        pygame.mixer.music.set_volume(current_volume)
        mute_button.config(text="🔊")  # Speaker on
    else:
        current_volume = pygame.mixer.music.get_volume()
        pygame.mixer.music.set_volume(0)
        mute_button.config(text="🔇")  # Speaker off
    muted = not muted

# Initialize the main window
root = tk.Tk()
root.title("PyMusicHub")
root.geometry("700x600")

# Set custom font and color for the title
title_font = font.Font(family='Helvetica', size=18, weight='bold')
title_label = tk.Label(root, text="PyMusicHub", font=title_font, fg='black')
title_label.grid(row=0, column=0, columnspan=4, pady=10)

# Create buttons
# Create buttons with colors
play_button = tk.Button(root, text="Play", command=play_song, bg="lightgrey", fg="black")
pause_button = tk.Button(root, text="Pause", command=pause_song, bg="skyblue", fg="black")
resume_button = tk.Button(root, text="Resume", command=resume_song, bg="lightgrey", fg="black")
next_button = tk.Button(root, text="Next", command=next_song, bg="skyblue", fg="black")
previous_button = tk.Button(root, text="Previous", command=previous_song, bg="lightgrey", fg="black")
list_button = tk.Button(root, text="List", command=load_songs, bg="skyblue", fg="black")

# Arrange buttons in grid
play_button.grid(row=1, column=0, padx=20, pady=5)
pause_button.grid(row=1, column=1, padx=20, pady=5)
resume_button.grid(row=1, column=2, padx=20, pady=5)
next_button.grid(row=2, column=0, padx=20, pady=5)
previous_button.grid(row=2, column=1, padx=20, pady=5)
list_button.grid(row=2, column=2, padx=20, pady=5)

# Create a treeview with columns for the song list
columns = ("Title", "Artist", "Duration")
listbox = ttk.Treeview(root, columns=columns, show="headings")
listbox.heading("Title", text="Title")
listbox.heading("Artist", text="Artist")
listbox.heading("Duration", text="Duration")
listbox.grid(row=3, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")

# Create a progress bar
progress = ttk.Progressbar(root, orient="horizontal", mode="determinate")
progress.grid(row=4, column=0, columnspan=4, padx=5, pady=5, sticky="we")

# Create a beat bar (canvas)
canvas = tk.Canvas(root, width=300, height=100, bg="black")
canvas.grid(row=5, column=0, columnspan=4, padx=5, pady=5)

# Create a label to display elapsed time
elapsed_time_label = tk.Label(root, text="00:00")
elapsed_time_label.grid(row=6, column=0, padx=5, pady=5)

# Create a volume slider
volume_slider = ttk.Scale(root, from_=0, to=100, orient="horizontal", command=set_volume)
volume_slider.set(50)  # Set initial volume to 50%
volume_slider.grid(row=6, column=1, columnspan=2, padx=5, pady=5, sticky="we")

# Create a mute button with Unicode characters
mute_button = tk.Button(root, text="🔊", command=toggle_mute)
mute_button.grid(row=6, column=3, padx=5, pady=5)

# Initialize volume and mute state
current_volume = 0.5
muted = False

# Configure grid weights
root.grid_rowconfigure(3, weight=1)
root.grid_columnconfigure(3, weight=1)

# Run the main event loop
root.mainloop()
