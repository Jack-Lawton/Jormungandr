
from tkinter import *
from tkinter import filedialog

from jor_lib.map_window import MapWindow
from jor_lib.jor_utils import all_civs_plus_none
from jor_lib.output import save_map

# GUI stuff


class PopupWindow(object):
    def __init__(self, master, default_name="", default_radius=0, x=None, y=None):
        top = self.top = Toplevel(master)

        label_text = "City Name"
        if (x is not None) and (y is not None):
            label_text += " ({}, {})".format(x, y)

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
        else:
            default_name = ""
            default_radius = 0
        w = PopupWindow(self.master, default_name=default_name, default_radius=default_radius,
                        x=tile.x, y=tile.y)
        self.master.wait_window(w.top)
        if w.value != "":
            is_update = (w.value != default_name) or (w.radius != default_radius)
            tile.add_name(w.value, civilization=self.map.civilization, area=w.radius, is_update=is_update)
        elif default_name != "":
            tile.remove_name(self.map.civilization)

    def save(self):
        self.set_all_states("disabled")
        dest = filedialog.asksaveasfile()
        if not isinstance(dest, str):
            dest = dest.name
        save_map(dest, self.map_name, self.tile_dict, self.city_names,
                 updates_only=self.updates_only_var.get(),
                 separate_civ_files=self.separate_files_var.get())
        # Let the user know we have saved
        w = MessageWindow(self.master, "File Saved!")
        self.master.wait_window(w.top)
        self.set_all_states("normal")
