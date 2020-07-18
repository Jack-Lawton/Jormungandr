
import os
import re
import traceback

import xmltodict

from collections import defaultdict
from jor_lib.map_classes import Tile


def read_map_lua(path):
    # read map lines
    with open(path, "r") as f:
        lua_content = f.read()

    lua_map_commands = re.findall(r"MapToConvert\[\d+\]\[\d+\][^\n]*\n", lua_content)

    python_map_commands = [s.replace("{", "[")
                               .replace("}", "]")
                               .replace("MapToConvert", "map_dict")
                               .split("--")[0]
                           for s in lua_map_commands]

    # Define our map
    map_dict = defaultdict(lambda: dict())

    # Execute python map commands
    for c in python_map_commands:
        exec(c)

    # Create tile dictionary
    tile_dict = {}
    for x, col in map_dict.items():
        tile_dict[x] = {}
        for y, value in col.items():
            this_tile = Tile(x, y, value)
            tile_dict[x][y] = this_tile
    # And done
    return tile_dict


def read_city_names(game_play_text, city_names=None):
    if city_names is None:
        city_names = {}
    if isinstance(game_play_text["GameData"]["LocalizedText"], list):
        parts = game_play_text["GameData"]["LocalizedText"]
    else:
        parts = [game_play_text["GameData"]["LocalizedText"]]
    for part in parts:
        for name_details in part["Replace"]:
            # For now, we only support en_US, localisation for other languages would have to be done manually
            if name_details["@Language"] == "en_US":
                if "@Text" in name_details:
                    city_names[name_details["@Tag"]] = name_details["@Text"]
                elif "Text" in name_details:
                    city_names[name_details["@Tag"]] = name_details["Text"]
    return city_names


def add_city_details(city_details, city_names, tile_dict):
    if "@Civilization" in city_details:
        civilization = city_details["@Civilization"]
    else:
        civilization = "None"
    x = int(city_details["@X"])
    y = int(city_details["@Y"])
    if (x in tile_dict) and (y in tile_dict[x]):
        if city_details["@CityLocaleName"] not in city_names:
            print("Warning, could not find {}".format(city_details["@CityLocaleName"]))
            return False
        text = city_names[city_details["@CityLocaleName"]]
        if "@Area" in city_details:
            area = int(city_details["@Area"])
        else:
            # One is the default area where none is provided
            area = 1
        tile_dict[x][y].add_name(text, civilization, area)
        return True
    return False


def read_city_details(city_map, city_names, tile_dict):
    if isinstance(city_map["GameData"]["CityMap"], list):
        parts = city_map["GameData"]["CityMap"]
    else:
        parts = [city_map["GameData"]["CityMap"]]
    for part in parts:
        if "Replace" in part:
            if isinstance(part["Replace"], list):
                # Add each city in the file
                for city_details in part["Replace"]:
                    add_city_details(city_details, city_names, tile_dict)
            else:
                # If part["Replace"] is not a list, there is only a single city to add
                add_city_details(part["Replace"], city_names, tile_dict)
    # Done
    return tile_dict


def read_natural_wonders(wonders, tile_dict):
    if isinstance(wonders["GameData"]["NaturalWonderPosition"], list):
        parts = wonders["GameData"]["NaturalWonderPosition"]
    else:
        parts = [wonders["GameData"]["NaturalWonderPosition"]]
    for part in parts:
        if "Replace" in part:
            for wonder_details in part["Replace"]:
                tile_dict[int(wonder_details["@X"])][int(wonder_details["@Y"])].natural_wonder = True
    return tile_dict


def loop_map_directory(dir_, tile_dict):
    files = os.listdir(dir_)
    city_maps_xml = []
    city_names_xml = []
    wonders_xml = []
    for name in files:
        if name.split(".")[-1].lower() != "xml":
            continue
        with open(dir_ + name, "r", encoding="utf8") as f:
            try:
                my_xml = xmltodict.parse(f.read())
            except:
                print("Warning, {} malformed.".format(name))
                traceback.print_exc()
                # Ignore malformed xml (for now)
                continue
            if ("GameData" in my_xml) and (my_xml["GameData"] is not None):
                if ("CityMap" in my_xml["GameData"]) and \
                        (my_xml["GameData"]["CityMap"] is not None):
                    city_maps_xml.append(my_xml)
                if ("LocalizedText" in my_xml["GameData"]) and \
                        (my_xml["GameData"]["LocalizedText"] is not None):
                    city_names_xml.append(my_xml)
                if ("NaturalWonderPosition" in my_xml["GameData"]) and \
                        (my_xml["GameData"]["NaturalWonderPosition"] is not None):
                    wonders_xml.append(my_xml)
    # Load in all names first
    # First check we have all the city names
    if (len(city_names_xml) == 0) and (dir_[-9:] != "Gameplay/"):
        # Assume this is the YnAMP folder structure - i.e. go up two directory levels then to "Gameplay"
        new_dir = "/".join(dir_.split("/")[:-3]) + "/Gameplay/"
        if os.path.exists(new_dir):
            # Provided the directory exists, use it
            map_name, city_names = loop_map_directory(new_dir, tile_dict)
        else:
            # Otherwise, we will just have to live without city names
            city_names = {}
    else:
        # We have files, read in as normal
        city_names = {}
        for xml in city_names_xml:
            city_names = read_city_names(xml, city_names)
    # Then add to tile dict
    for xml in city_maps_xml:
        read_city_details(xml, city_names, tile_dict)
    # Then add wonders
    for xml in wonders_xml:
        read_natural_wonders(xml, tile_dict)
    # If we can, work out the map name
    if (len(city_maps_xml) > 0) and not isinstance(city_maps_xml[0]["GameData"]["CityMap"], list) \
            and (len(city_maps_xml[0]["GameData"]["CityMap"]["Replace"]) > 0):
        map_name = city_maps_xml[0]["GameData"]["CityMap"]["Replace"][0]["@MapName"]
    elif (len(city_maps_xml) > 0) and (len(city_maps_xml[0]["GameData"]["CityMap"][0]["Replace"]) > 0):
        map_name = city_maps_xml[0]["GameData"]["CityMap"][0]["Replace"][0]["@MapName"]
    elif (len(wonders_xml) > 0) and not isinstance(wonders_xml[0]["GameData"]["NaturalWonderPosition"], list) \
            and (len(wonders_xml[0]["GameData"]["NaturalWonderPosition"]["Replace"]) > 0):
        map_name = wonders_xml[0]["GameData"]["NaturalWonderPosition"]["Replace"][0]["@MapName"]
    elif (len(wonders_xml) > 0) and (len(wonders_xml[0]["GameData"]["NaturalWonderPosition"][0]["Replace"]) > 0):
        map_name = wonders_xml[0]["GameData"]["NaturalWonderPosition"][0]["Replace"][0]["@MapName"]
    else:
        map_name = "UNKNOWN_JORMUNGANDR_MAP"
    # Done
    return map_name, city_names


def find_file_with_extension(dir_, extension):
    files = os.listdir(dir_)
    extension = extension.lower()
    for file in files:
        if file.split(".")[-1].lower() == extension:
            return file
    return None


def load_map(dir_):
    # First the LUA
    if os.path.exists(dir_ + "Lua"):
        lua_file = "Lua/" + find_file_with_extension(dir_ + "Lua/", "lua")
    else:
        lua_file = find_file_with_extension(dir_, "lua")
    tile_dict = read_map_lua(dir_ + lua_file)
    # Then the XML
    if os.path.exists(dir_ + "Map"):
        map_name, city_names = loop_map_directory(dir_ + "Map/", tile_dict)
    else:
        map_name, city_names = loop_map_directory(dir_, tile_dict)
    # Done
    return tile_dict, map_name, city_names
