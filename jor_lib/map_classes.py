from jor_lib import hex_drawing as hd


# Tile class
class Tile:
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value
        self.poly = hd.get_hex(x, y)
        self.references = []
        self.names = {}
        self.areas = {}
        self.is_update = {}
        self.natural_wonder = False

    def plot(self, ax, fontsize=0, civilization="None"):
        # Add hex
        self.references.append(ax.add_patch(hd.get_patch(self.poly, self.value, self.natural_wonder)))

        # Add finer details only at sufficient zoom
        if fontsize > 2:
            # Add rivers
            # For logic reference, see https://github.com/Zobtzler/YnABMC/blob/master/YnABMC/Form1.cs (line 731)
            rivers = self.value[3]
            river_edges = []
            if rivers[0][0] == 1:  # SW river
                river_edges.append("sw")
            if rivers[1][0] == 1:  # E river
                river_edges.append("e")
            if rivers[2][0] == 1:  # SE river
                river_edges.append("se")
            for edge in river_edges:
                rx, ry = hd.get_edge_xy(self.x, self.y, edge)
                self.references += ax.plot(rx, ry, "b-")

            # Add cliffs (same reference as rivers, line 796)
            cliffs = self.value[5]
            cliff_edges = []
            if cliffs[0] == 1:
                cliff_edges.append("sw")
            if cliffs[1] == 1:
                cliff_edges.append("e")
            if cliffs[2] == 1:
                cliff_edges.append("se")
            for edge in cliff_edges:
                rx, ry = hd.get_edge_xy(self.x, self.y, edge)
                self.references += ax.plot(rx, ry, "k-")

        if civilization in self.names:
            if fontsize > 2:
                # We can plot city names
                offset = (self.y % 2) * 0.5
                # Work out how much to show at this level
                if fontsize > 4:
                    text = self.names[civilization]
                    if len(text) > 9:
                        text = text[:8] + ".."
                elif fontsize > 3:
                    text = self.names[civilization][:3] + ".."
                    fontsize += 1
                else:
                    text = "".join([s[0] for s in self.names[civilization].split(" ")])
                    fontsize += 2

                text_ref = ax.text(self.x + offset, self.y, text,
                                   horizontalalignment='center', verticalalignment='center', fontsize=fontsize)
                self.references.append(text_ref)
            if fontsize > 1:
                # We can plot circles
                cx, cy = hd.get_circle_xy(self.x, self.y, self.areas[civilization])
                # Get style
                if not self.is_update[civilization]:
                    style = "m-"
                else:
                    style = "r-"

                circle_ref = ax.plot(cx, cy, style)
                self.references += circle_ref

    def is_mountain(self):
        if isinstance(self.value[0], str):
            return "MOUNTAIN" in self.value[0]
        else:
            return (self.value[0] % 3) == 2

    def is_water(self):
        if isinstance(self.value[0], str):
            return (self.value[0] == "TERRAIN_OCEAN") or (self.value[0] == "TERRAIN_COAST")
        else:
            return (self.value[0] == 16) or (self.value[0] == 15)

    def remove(self):
        for ref in self.references:
            ref.remove()
        self.references = []

    def add_name(self, text, civilization="None", area=0, is_update=False):
        self.names[civilization] = text
        self.areas[civilization] = area
        self.is_update[civilization] = is_update

    def remove_name(self, civilization="None"):
        del self.names[civilization]
        del self.areas[civilization]
        self.is_update[civilization] = True
