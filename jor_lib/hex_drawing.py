
from shapely.geometry import Polygon, Point
from descartes import PolygonPatch

ZERO_HEX_COORDS = [(+1/2, -(1/3)),
                   (+1/2, +(1/3)),
                   (+0/2, +(2/3)),
                   (-1/2, +(1/3)),
                   (-1/2, -(1/3)),
                   (-0/2, -(2/3))]

COLOUR_LOOKUP = {
    "TERRAIN_OCEAN": "#3252c7",
    16: "#3252c7",
    "TERRAIN_COAST": "#4287f5",
    15: "#4287f5",
    "TERRAIN_PLAINS": "#8f9e3a",
    3: "#8f9e3a",
    "TERRAIN_PLAINS_HILLS": "#7d8a36",
    4: "#7d8a36",
    "TERRAIN_PLAINS_MOUNTAIN": "#272b11",
    5: "#272b11",
    "TERRAIN_DESERT": "#e0d29d",
    6: "#e0d29d",
    "TERRAIN_DESERT_HILLS": "#b3a87f",
    7: "#b3a87f",
    "TERRAIN_DESERT_MOUNTAIN": "#403c2f",
    8: "#403c2f",
    "TERRAIN_TUNDRA": "#bfccb8",
    9: "#bfccb8",
    "TERRAIN_TUNDRA_HILLS": "#a2ad9c",
    10: "#a2ad9c",
    "TERRAIN_TUNDRA_MOUNTAIN": "#3b4039",
    11: "#3b4039",
    "TERRAIN_GRASS": "#3ab52a",
    0: "#3ab52a",
    "TERRAIN_GRASS_HILLS": "#2d8c20",
    1: "#2d8c20",
    "TERRAIN_GRASS_MOUNTAIN": "#0c2609",
    2: "#0c2609",
    "TERRAIN_SNOW": "#ffffff",
    12: "#ffffff",
    "TERRAIN_SNOW_HILLS": "#e3e3e3",
    13: "#e3e3e3",
    "TERRAIN_SNOW_MOUNTAIN": "#575757",
    14: "#575757",
    "natural_wonder": "#fcb603"
}


def get_hex(x, y):
    offset = (y % 2) * 0.5
    my_coords = [(a + x + offset, b + y) for a, b in ZERO_HEX_COORDS]
    poly = Polygon(my_coords)
    return poly


def get_circle_xy(x, y, area=0):
    offset = (y % 2) * 0.5
    centre = Point(x + offset, y)
    return centre.buffer(area+0.45).exterior.xy


def get_edge_xy(x, y, edge):
    offset = (y % 2) * 0.5
    edge = edge.lower()
    if edge == "sw":
        idx_1 = 4
        idx_2 = 5
    elif edge == "se":
        idx_1 = 5
        idx_2 = 0
    else:
        idx_1 = 0
        idx_2 = 1
    return [x + ZERO_HEX_COORDS[idx_1][0] + offset, x + ZERO_HEX_COORDS[idx_2][0] + offset], \
           [y + ZERO_HEX_COORDS[idx_1][1], y + ZERO_HEX_COORDS[idx_2][1]]


def get_colour(value):
    if value[0] in COLOUR_LOOKUP:
        return COLOUR_LOOKUP[value[0]]
    else:
        print("Missing colour for {}".format(value[0]))
        return "grey"


def get_patch(poly, value, natural_wonder=False):
    if natural_wonder:
        my_colour = COLOUR_LOOKUP["natural_wonder"]
    else:
        my_colour = get_colour(value)
    patch = PolygonPatch(poly, color=my_colour, alpha=0.5, linewidth=3)
    # TODO: Rivers
    return patch


if __name__ == "__main__":
    print("Testing hex drawing")
    print(get_hex(0, 0))
