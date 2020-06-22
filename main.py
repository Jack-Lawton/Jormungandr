
from tkinter import *
from tkinter import filedialog

from jor_lib.gui import MainWindow
from jor_lib.input import load_map

# Get path
root = Tk()
root.title("Jörmungandr True Location GUI for YnAMP")
root.minsize(400, 100)
root.withdraw()
map_path = filedialog.askdirectory() + "/"

# Read path
tile_dict, map_name, city_names = load_map(map_path)

# Launch Gui
root.deiconify()
m = MainWindow(root, tile_dict, map_name, city_names)
root.mainloop()


