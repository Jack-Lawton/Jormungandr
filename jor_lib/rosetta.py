
import operator

import xmltodict

from collections import defaultdict

ROSETTA_BUFFER = "_XSCX_"


def load_rosetta(path, base_lookup=None, text_lookup=None, force_civ=None):
    with open(path, "r", encoding="utf8") as file:
        rosetta_raw = xmltodict.parse(file.read())

    if base_lookup is None:
        base_lookup = defaultdict(lambda: list())
    if text_lookup is None:
        text_lookup = defaultdict(lambda: dict())

    for row in rosetta_raw["GameData"]["LocalizedText"]["Replace"]:
        base_name, civilization = row["@Tag"].split(ROSETTA_BUFFER)
        text = row["@Text"]

        if force_civ is not None:
            civilization = force_civ

        base_lookup[text].append(base_name)
        text_lookup[base_name][civilization] = text

    return base_lookup, text_lookup


def apply_rosetta(name, civilization, base_lookup, text_lookup):
    if name not in base_lookup:
        # No match
        return None
    else:
        bases = base_lookup[name]
        # For each base, see if it is applicable to our civ
        applicable_bases = []
        for base in bases:
            if civilization in text_lookup[base]:
                applicable_bases.append(base)
        # Consider only these
        if len(applicable_bases) == 0:
            # No matches
            return None
        elif len(applicable_bases) == 1:
            selected_base = applicable_bases[0]
        else:
            # There is a potential conflict
            # If any of the names match what it already is, keep it
            for base in applicable_bases:
                if text_lookup[base][civilization] == name:
                    return name
            # Unclear which to choose.
            # For now, just pick the shortest base name as that is likely be to be most definitive
            base_length_pairs = [(base, len(base)) for base in applicable_bases]
            selected_base = min(base_length_pairs, key=operator.itemgetter(1))[0]
        # If we get here, return the name from selected base base
        return text_lookup[selected_base][civilization]


def add_to_tile_dict(tile_dict, civilization, base_lookup, text_lookup):
    n_changes = 0
    for x, column in tile_dict.items():
        for y, tile in column.items():
            # First check if this civ needs a new name for the tile and there is a generic one to use for rosetta
            if (civilization not in tile.names) and ("None" in tile.names):
                # If so, use rosetta to get a name
                rosetta_name = apply_rosetta(tile.names["None"], civilization, base_lookup, text_lookup)
                # If rosetta found a new name...
                if rosetta_name is not None:
                    # Add name
                    tile.add_name(rosetta_name, civilization=civilization, area=tile.areas["None"], is_update=True)
                    n_changes += 1
    # Done
    return n_changes


if __name__ == "__main__":
    # Test
    bl, tl = load_rosetta("..\Rosetta_Localization.xml")
    print(apply_rosetta("London", "CIVILIZATION_ROME", bl, tl))
