
import os

import jor_lib.rosetta as rosetta

from tkinter import *
from tkinter import filedialog

from jor_lib.map_window import MapWindow
from jor_lib.jor_utils import all_civs_plus_none, all_civs
from jor_lib.output import save_map

# GUI stuff


class PopupWindow(object):
    def __init__(self, master, default_name="", default_radius=0, x=None, y=None, tile_name=None):
        top = self.top = Toplevel(master)

        label_text = "City Name"
        if (x is not None) and (y is not None):
            label_text += " ({}, {})".format(x, y)
        if tile_name is not None:
            label_text += " ({})".format(tile_name)

        self.l = Label(top, text=label_text)
        self.l.pack()
        self.e = Entry(top)
        self.e.insert(0, default_name)
        self.e.pack()
        self.radius_var = IntVar()
        self.r1 = Radiobutton(top, text="One Tile", variable=self.radius_var, value=0)
        self.r2 = Radiobutton(top, text="Seven Tiles", variable=self.radius_var, value=1)
        # self.r3 = Radiobutton(top, text="Nineteen Tiles", variable=self.radius_var, value=2)
        self.r1.pack()
        self.r2.pack()
        # self.r3.pack()
        if default_radius == 1:
            self.r2.select()
        # elif default_radius > 1:
            # self.r3.select()
        self.b = Button(top, text='Ok', command=self.cleanup)
        self.b.pack()
        self.value = default_name
        self.radius = default_radius

        self.top.bind("<Return>", self.cleanup)

        master.focus_force()
        self.e.focus()

    def cleanup(self, *args):
        self.top.unbind("<Return>")
        self.value = self.e.get()
        self.radius = self.radius_var.get()
        self.top.destroy()


class WarningWindow(object):
    def __init__(self, master, text="Warning!"):
        top = self.top = Toplevel(master)
        self.l = Label(top, text=text)
        self.l.pack()
        self.b1 = Button(top, text='Ok', command=self.ok)
        self.b1.pack()
        self.b2 = Button(top, text='Cancel', command=self.cleanup)
        self.b2.pack()
        self.accepted = False

        self.top.bind("<Return>", self.ok)

        self.b1.focus()
        master.focus_force()

    def ok(self, *args):
        self.top.unbind("<Return>")
        self.accepted = True
        self.cleanup()

    def cleanup(self):
        self.top.destroy()


class MessageWindow(object):
    def __init__(self, master, text="Hello World!"):
        top = self.top = Toplevel(master)
        self.l = Label(top, text=text)
        self.l.pack()
        self.b1 = Button(top, text='Ok', command=self.cleanup)
        self.b1.pack()

        self.top.bind("<Return>", self.cleanup)

        self.b1.focus()
        master.focus_force()

    def cleanup(self, *args):
        self.top.destroy()


class MainWindow(object):
    def set_all_states(self, state):
        self.c_ind["state"] = state
        self.rb["state"] = state
        self.sb["state"] = state
        self.b["state"] = state
        self.options["state"] = state
        self.check_1["state"] = state
        self.check_2["state"] = state
        self.b2["state"] = state

    def show_map(self):
        self.set_all_states("disabled")
        self.map = MapWindow(self.tile_dict, civilization=self.variable.get(), select_function=self.popup)
        self.map.show()
        self.set_all_states("normal")

    def __init__(self, master, tile_dict, map_name, city_names):
        self.master = master
        self.map = None
        self.tile_dict = tile_dict
        self.map_name = map_name
        self.city_names = city_names

        self.l = Label(master, text=self.map_name + "\n\nChoose Civ:")
        self.l.pack()

        self.variable = StringVar(master)
        self.variable.set("None")
        self.options = OptionMenu(master, self.variable, *all_civs_plus_none)
        self.options.pack()

        self.indigenous_var = BooleanVar()
        self.c_ind = Checkbutton(master, text="Supplement Rosetta with Indigenous Names", variable=self.indigenous_var)
        self.c_ind.pack()

        self.rb = Button(master, text="Apply Rosetta", command=lambda: self.apply_rosetta(self.indigenous_var.get()))
        self.rb.pack()

        self.sb = Button(master, text="Suppliment From Another Civ", command=self.supplement)
        self.sb.pack()

        self.b = Button(master, text="Open Map", command=self.show_map)
        self.b.pack()

        self.updates_only_var = BooleanVar()
        self.check_1 = Checkbutton(master, text="Save Updates Only", variable=self.updates_only_var)
        self.check_1.pack()
        self.separate_files_var = BooleanVar()
        self.check_2 = Checkbutton(master, text="Separate Files For Each Civ", variable=self.separate_files_var)
        self.check_2.pack()

        self.b2 = Button(master, text="Save Map", command=self.save)
        self.b2.pack()

    def popup(self, tile):
        # First do a warning check
        warning_text = None
        if tile.natural_wonder:
            warning_text = "Warning, this tile has a natural wonder on it, names may be ineffective."
        elif tile.is_mountain():
            warning_text = "Warning, this tile has a mountain on it, names may be ineffective."
        elif tile.is_water():
            warning_text = "Warning, this tile has water on it, names may be ineffective."
        if warning_text is not None:
            w = WarningWindow(self.master, warning_text)
            self.master.wait_window(w.top)
            if not w.accepted:
                # We have canceled out of the operation
                return None
        # Carry on as normal
        if self.map.civilization in tile.names:
            default_name = tile.names[self.map.civilization]
            default_radius = tile.areas[self.map.civilization]
        elif "None" in tile.names:
            default_name = tile.names["None"]
            default_radius = tile.areas["None"]
        else:
            default_name = ""
            default_radius = 0
        # Work out tile name (if applicable)
        if (self.map.civilization != "None") and ("None" in tile.names) and (tile.names["None"] != default_name):
            tile_name = tile.names["None"]
        else:
            tile_name = None
        w = PopupWindow(self.master, default_name=default_name, default_radius=default_radius,
                        x=tile.x, y=tile.y, tile_name=tile_name)
        self.master.wait_window(w.top)
        is_update = (w.value != default_name) or (w.radius != default_radius)
        if w.value == "":
            tile.remove_name(self.map.civilization)
        elif is_update:
            tile.add_name(w.value, civilization=self.map.civilization, area=w.radius, is_update=is_update)

    def save(self):
        self.set_all_states("disabled")
        dest = filedialog.asksaveasfile()
        if (dest is None) or (dest == ""):
            # Null, response, re-enable window
            self.set_all_states("normal")
            return None
        if not isinstance(dest, str):
            dest = dest.name
        save_map(dest, self.map_name, self.tile_dict, self.city_names,
                 updates_only=self.updates_only_var.get(),
                 separate_civ_files=self.separate_files_var.get())
        # Let the user know we have saved
        w = MessageWindow(self.master, "File Saved!")
        self.master.wait_window(w.top)
        self.set_all_states("normal")

    def apply_rosetta(self, indigenous=False):
        self.set_all_states("disabled")
        civilization = self.variable.get()
        if civilization == "None":
            # Check the user is ok with not specifying a civ
            w = WarningWindow(self.master, "You are about to apply Rosetta for ALL civilizations. Are you sure?")
            self.master.wait_window(w.top)
            if not w.accepted:
                # We have canceled out of the operation
                self.set_all_states("normal")
                return None
        # Find the path to rosetta
        if os.path.exists("Rosetta_Localization.xml"):
            rosetta_path = "Rosetta_Localization.xml"
            rosetta_dir = os.getcwd()
        else:
            rosetta_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
            if rosetta_path == "":
                # Empty path, treat as cancellation
                self.set_all_states("normal")
                return None
            # Otherwise, set directory
            rosetta_dir = "/".join(rosetta_path.split("/")[:-1])
        # Find the indigenous file (if required)
        if (not indigenous) or (civilization == "None"):
            bl = None
            tl = None
        else:
            possible_files = os.listdir(rosetta_dir)
            indigenous_path = None
            for file in possible_files:
                if ("Indigenous" in file) and (file.lower()[-4:] == ".xml"):
                    indigenous_path = rosetta_dir + "/" + file
                    break
            if indigenous_path is None:
                # We have failed, quit
                w = MessageWindow(self.master, "Failed to find valid indigenous file!")
                self.master.wait_window(w.top)
                self.set_all_states("normal")
                return None
            # Otherwise, load the indigenous file
            bl, tl = rosetta.load_rosetta(indigenous_path, force_civ=civilization)
        # Next load proper rosetta
        bl, tl = rosetta.load_rosetta(rosetta_path, bl, tl)
        # Now apply
        n_changes = 0
        if civilization == "None":
            # Apply rosetta to all
            for loop_civ in all_civs_plus_none:
                if loop_civ != "None":
                    n_changes += rosetta.add_to_tile_dict(self.tile_dict, loop_civ, bl, tl)
        else:
            # Just one civ
            n_changes += rosetta.add_to_tile_dict(self.tile_dict, civilization, bl, tl)
        # Let the user know we have completed
        w = MessageWindow(self.master, "Added {} New City Mappings!".format(n_changes))
        self.master.wait_window(w.top)
        self.set_all_states("normal")

    def supplement(self):
        self.set_all_states("disabled")
        # First check we can
        civilization = self.variable.get()
        if civilization == "None":
            # Tell the user to select a civ first
            w = MessageWindow(self.master, "Please select a civilization to map to first.")
        else:
            # Launch supplement window
            w = SupplementWindow(self.master, civilization, self.tile_dict)
        # Wait on window then reset states
        self.master.wait_window(w.top)
        self.set_all_states("normal")
        return None


class SupplementWindow(object):
    def __init__(self, master, civilization, tile_dict):
        self.civilization = civilization
        self.tile_dict = tile_dict

        top = self.top = Toplevel(master)
        self.l = Label(top, text="Select a civilization to supplement {} with names from:".format(civilization))
        self.l.pack()
        self.variable = StringVar(top)
        self.variable.set(all_civs[0])
        self.options = OptionMenu(top, self.variable, *all_civs)
        self.options.pack()

        self.b1 = Button(top, text='Ok', command=self.ok)
        self.b1.pack()
        self.b2 = Button(top, text='Cancel', command=self.cleanup)
        self.b2.pack()

    def ok(self):
        # Get new civ
        source_civ = self.variable.get()
        # Loop tile dict and apply
        count = 0
        for x, column in self.tile_dict.items():
            for y, tile in column.items():
                count += tile.copy_mapping(source_civ, self.civilization)
        # Done
        self.cleanup(count)

    def cleanup(self, count=None):
        master = self.top.master
        self.top.destroy()
        if count is not None:
            # Show user count
            w = MessageWindow(master, "Successfully mapped {} names!".format(count))
            master.wait_window(w.top)
