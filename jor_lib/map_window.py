
import time

import matplotlib.pyplot as plt
from matplotlib.backend_bases import NavigationToolbar2, Event

from shapely.geometry import Point


class MapWindow:
    def __init__(self, tile_dict, max_click_length=0.1, civilization=None, select_function=None):
        """
        Initialisation function for the map window object
        :param tile_dict: Tile dictionary to use
        :param max_click_length: Maximum click length for selecting in seconds; anything longer is a drag motion
        :param civilization: Civilization to use for city names
        """
        self.tile_dict = tile_dict
        self.max_click_length = max_click_length
        self.civilization = civilization
        self.select_function = select_function
        self.ax = None  # To be defined later
        self.wait_popup = False
        self.active_tiles = []

    def onclick(self, event):
        self.ax.time_onclick = time.time()

    def onrelease(self, event):
        if self.wait_popup:
            return
        # Only clicks inside this axis are valid.
        if event.inaxes == self.ax:
            if event.button == 1 and ((time.time() - self.ax.time_onclick) < self.max_click_length):
                print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
                      (event.button, event.x, event.y, event.xdata, event.ydata))
                around_x = int(event.xdata)
                around_y = int(event.ydata)
                # Figure out exactly while hex
                matched_hex = self.tile_dict[around_x][around_y]
                for x in range(around_x - 1, around_x + 2):
                    for y in range(around_y - 1, around_y + 2):
                        if (x in self.tile_dict) and (y in self.tile_dict[x]) \
                                and self.tile_dict[x][y].poly.contains(Point(event.xdata, event.ydata)):
                            matched_hex = self.tile_dict[x][y]
                            break
                # call select function
                if self.select_function is not None:
                    self.wait_popup = True
                    self.select_function(matched_hex)
                    self.wait_popup = False
                    self.redraw(None, tile_x=matched_hex.x, tile_y=matched_hex.y)
                    self.ax.figure.canvas.draw()
            else:
                # Zoom or drag, please redraw
                self.redraw(None)
                self.ax.figure.canvas.draw()

    def redraw(self, event, tile_x=None, tile_y=None):
        # Capture axis limits
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        x_start = int(xlim[0])
        x_end = int(xlim[1])
        y_start = int(ylim[0])
        y_end = int(ylim[1])

        # Work out text size
        tile_width = (xlim[1] - xlim[0])
        bbox = self.ax.get_window_extent().transformed(self.ax.figure.dpi_scale_trans.inverted())
        pixel_width = bbox.width * self.ax.figure.dpi
        fontsize = (pixel_width / tile_width) / 8

        if tile_x is not None:
            # If coordinates are provided, replot just this cell
            if (tile_x in self.tile_dict) and (tile_y in self.tile_dict[tile_x]):
                self.tile_dict[tile_x][tile_y].remove()
                self.tile_dict[tile_x][tile_y].plot(self.ax, fontsize=fontsize, civilization=self.civilization)
        else:
            # Otherwise clear all and plot again
            while len(self.active_tiles) > 0:
                self.active_tiles.pop().remove()
            for x in range(x_start+1, x_end+1):
                if x in self.tile_dict:
                    for y in range(y_start+1, y_end+1):
                        if y in self.tile_dict[x]:
                            self.tile_dict[x][y].plot(self.ax, fontsize=fontsize, civilization=self.civilization)
                            self.active_tiles.append(self.tile_dict[x][y])
        # Resize
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)

    def zoom_fun(self, event):
        # https://gist.github.com/tacaswell/3144287
        base_scale = 2
        # get the current x and y limits
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        # set the range
        cur_xrange = (cur_xlim[1] - cur_xlim[0]) * .5
        cur_yrange = (cur_ylim[1] - cur_ylim[0]) * .5
        xdata = event.xdata  # get event x location
        ydata = event.ydata  # get event y location
        if event.button == 'up':
            # deal with zoom in
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            # deal with zoom out
            scale_factor = base_scale
        else:
            # deal with something that should never happen
            scale_factor = 1
            print(event.button)
        # set new limits
        self.ax.set_xlim([xdata - cur_xrange * scale_factor,
                          xdata + cur_xrange * scale_factor])
        self.ax.set_ylim([ydata - cur_yrange * scale_factor,
                          ydata + cur_yrange * scale_factor])
        self.redraw(None)
        self.ax.figure.canvas.draw()

    @staticmethod
    def get_callback_function(toolbar_function, event_name):
        # For setting up button events
        # https://stackoverflow.com/questions/14896580/matplotlib-hooking-in-to-home-back-forward-button-events
        def new_func(self, *args, **kwargs):
            toolbar_function(self, *args, **kwargs)
            event = Event(event_name, self)
            self.canvas.callbacks.process(event_name, event)
        return new_func

    def home(self, event):
        # Set limits to max
        self.ax.set_xlim([-1, len(self.tile_dict) + 1])
        self.ax.set_ylim([-1, len(self.tile_dict[0]) + 1])
        # Then redraw
        self.redraw(None)
        self.ax.figure.canvas.draw()

    def show(self):
        # Set up callback functions for the navigation toolbar
        NavigationToolbar2.home = self.get_callback_function(NavigationToolbar2.home, "home_event")
        NavigationToolbar2.back = self.get_callback_function(NavigationToolbar2.back, "back_event")
        NavigationToolbar2.forward = self.get_callback_function(NavigationToolbar2.forward, "forward_event")

        # Set up figure
        fig = plt.figure()
        self.ax = fig.add_subplot(1, 1, 1)

        # Register events
        fig.canvas.mpl_connect('button_press_event', self.onclick)
        fig.canvas.mpl_connect('button_release_event', self.onrelease)
        fig.canvas.mpl_connect('home_event', self.home)
        fig.canvas.mpl_connect('back_event', self.redraw)
        fig.canvas.mpl_connect('forward_event', self.redraw)
        fig.canvas.mpl_connect('scroll_event', self.zoom_fun)

        # Call home first
        self.home(None)

        # Set equal aspects
        plt.axis('equal')
        # Show
        plt.show()
