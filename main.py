
import time

from threading import Thread

from tkinter import *
from tkinter import filedialog

from jor_lib.gui import MainWindow
from jor_lib.input import load_map

# Create loading gui
root = Tk()
root.title("Jörmungandr True Location GUI for YnAMP")
root.minsize(400, 100)
Label(root, text="Loading...").pack()


def launch_func(main):
    # Wait a moment
    time.sleep(1)

    # Get path
    map_path = filedialog.askdirectory() + "/"

    # Read path
    tile_dict, map_name, city_names = load_map(map_path)

    # Launch Main Gui
    root.deiconify()
    MainWindow(root, tile_dict, map_name, city_names)


# Kick off launch function in new thread
Thread(target=lambda: launch_func(root)).start()

# Launch GUI
root.mainloop()
