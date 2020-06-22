
import os

import unidecode

from jor_lib.jor_utils import all_civs_plus_none


CITY_XML = "<Replace MapName=\"{}\" X=\"{}\" Y=\"{}\" CityLocaleName=\"{}\" Area=\"{}\" />"
TEXT_XML = "<Replace Tag=\"{}\" Text=\"{}\" Language=\"en_US\" />"
COMMENT_XML = "<!-- {} -->"

TEXT_STRUCTURE = """
<?xml version="1.0" encoding="utf-8"?>
<GameData>
\t<LocalizedText>
\t\t<!-- Localized Text Automatically Produced by Jörmungandr True Location GUI for YnAMP -->
\t\t{}
\t</LocalizedText>
</GameData>
"""

CITY_STRUCTURE = """
<?xml version="1.0" encoding="utf-8"?>
<GameData>
\t<CityMap>
\t\t<!-- City Map Automatically Produced by Jörmungandr True Location GUI for YnAMP -->
\t\t{}
\t</LocalizedText>
</GameData>
"""


def generate_unique_city_code(city_name, city_names_inverse_original, city_names_inverse_to_save):
    clean_name = unidecode.unidecode(city_name).upper().replace(" ", "_")
    code = "LOC_JORMUNGANDR_CITY_NAME_" + clean_name
    # Check our code is not already used
    if (code not in city_names_inverse_original) \
            and (code not in city_names_inverse_to_save):
        return code
    else:
        # Otherwise, we will add a number to differentiate
        i = 1
        while True:
            code_with_number = code + "_" + str(i)
            if (code_with_number not in city_names_inverse_original) \
                    and (code_with_number not in city_names_inverse_to_save):
                return code_with_number
            else:
                code += 1


def save_map(path, map_name, tile_dict, city_names, updates_only=False, separate_civ_files=False):
    # First we need to reverse the city names dictionary, so we look up the code from the name
    # This is the original so we can always refer back to the ones we started with (for if we want to add updates only)
    city_names_inverse_original = {value: key for key, value in city_names.items()}
    # Create a new ones for saving
    city_names_inverse_to_save = {}
    # For each civ we need to produce a map file
    map_raw_xmls = {}
    for civilization in all_civs_plus_none:
        map_raw_xmls[civilization] = []
        # Loop all tiles
        for x, column in tile_dict.items():
            for y, tile in column.items():
                # Check name available
                if civilization in tile.names:
                    # Check if we are doing updates only and if so, if it is an update
                    if (not updates_only) or tile.is_update[civilization]:
                        city_name = tile.names[civilization]
                        city_area = tile.areas[civilization]
                        # Check if we need to add this city name to the dictionary
                        if city_name in city_names_inverse_to_save:
                            # We already have a saved code
                            city_code = city_names_inverse_to_save[city_name]
                        elif city_name in city_names_inverse_original:
                            # We have an original code for this city
                            city_code = city_names_inverse_original[city_name]
                            if not updates_only:
                                # Save if we are doing a full save
                                city_names_inverse_to_save[city_name] = city_code
                        else:
                            # Make a new code
                            city_code = generate_unique_city_code(city_name, city_names_inverse_original,
                                                                  city_names_inverse_to_save)
                            # Add code to the save file
                            city_names_inverse_to_save[city_name] = city_code
                        # Add xml
                        my_xml = CITY_XML.format(map_name, tile.x, tile.y, city_code, city_area)
                        map_raw_xmls[civilization].append(my_xml)
    # Now produce the text file lines
    text_raw_xmls = [TEXT_XML.format(value, key) for key, value in city_names_inverse_to_save.items()]
    # Save the text
    text_output = TEXT_STRUCTURE.format("\n\t\t".join(text_raw_xmls))
    if os.path.exists(path + "_GamePlayText.xml"):
        os.remove(path + "_GamePlayText.xml")
    with open(path + "_GamePlayText.xml", "w", encoding="utf8") as file:
        file.write(text_output)

    # Lastly save the city map (two different ways to do this depending on config)

    def save_city_map_output(file_path, lines):
        city_output = CITY_STRUCTURE.format("\n\t\t".join(lines))
        if os.path.exists(file_path):
            os.remove(file_path)
        with open(file_path, "w", encoding="utf8") as city_file:
            city_file.write(city_output)

    if separate_civ_files:
        for civilization, xmls in map_raw_xmls.items():
            if len(xmls) > 0:
                save_city_map_output(path + "_CityMap_" + civilization + ".xml", xmls)
    else:
        final_map_xmls = []
        for civilization, xmls in map_raw_xmls.items():
            if len(xmls) > 0:
                final_map_xmls.append(COMMENT_XML.format(civilization))
                final_map_xmls += xmls
        save_city_map_output(path + "_CityMap.xml", final_map_xmls)

    # And done
    return True
