# Jörmungandr
The mythical Norse serpent Jörmungandr encircled the entire world. Here, I am using the modern day serpent, python to encircle the world of Civilization VI.

Jörmungandr is a map editing tool for the [True Location City Names YnAMP subproject](https://forums.civfanatics.com/threads/ynamp-sub-project-true-location-corresponding-city-names.605960/).

![Jormungandr Example](screenshots/Jormungandr_eg.PNG?raw=true "Jormungandr Example")
![Jormungandr Menu](screenshots/Jormungandr_menu_v1.PNG?raw=true "Jormungandr Menu")

# Instructions
Launch Jörmungandr either by running main.py or downloading a built executable. Where possible, it is recommended to download the source and run directly, this results in a significantly quicker launch time and proves easier to debug.

Currently Jörmungandr immediately prompts the user to select a directory. The following directories are valid:
- A path within the Maps directory of [YnAMP](https://github.com/Gedemon/Civ6-YnAMP/tree/master/Maps) (full folder stucture must exist)
- A mod directory as produced by Zobtzler's Bitmap Converter, [YnABMC](https://github.com/Zobtzler/YnABMC) (Lua & Map folders must exist)
- A single directory containing a YnAMP style LUA file and all required XML files

Once launched, the user can select a civilization, then view and edit their city map. The default selection is "None", i.e. all civilizations.

As of v0.4.0, the user can also select "Apply Rosetta", this will prompt the user to select the Localisation.xml from the [Rosetta](https://forums.civfanatics.com/threads/rosetta-dynamic-city-names.623102/) mod (alternatively, creating a file called Rosetta_Localization.xml will skip this check). Jörmungandr will then use the Rosetta database to create city mappings for the slected civilization for all cities where the generic ("None") mapping can be found in Rosetta. Additionally, the option to supliment Rosetta names with the indigenous names from IndigenousNames.xml can be enabled with the check box, IndigenousNames.xml needs to exist in the same folder as Localisation.xml.

As of v0.5.0, the user can supliment civilization mappings with names from other civilizations. This can be handy for filling in large areas of the map quickly where civilizations have similar cultures / the same language.

Before saving, on the main menu, two options are available:
- Save updates only. This is designed to aid in collaboration, any new cities added in a session are coloured slightly differently, choosing to save only updates will save only these cities. The new files can then be merged or re-used however is required.
- Separate files for each civilization. By default Jörmungandr will aim to minimise the number of files produced by saving all civilizations together, however, these can be separates to better align with current YnAMP practice. Only civilizations with city mappings will have files created.

Jörmungandr does not aim to save completed functioning mods, rather simply CityMap.xml and GamePlayText.xml files, the most time consuming to create. Where possible Jörmungandr will reuse existing GamePlayText mappings and for new cities, will create its own, always preceded by "LOC_JORMUNGANDR_CITY_NAME_" to prevent any conflicts. All produced GamePlayText will be in English (US) only.

# Known Bugs
- Exe build can be slow to load (recommended to run the python direct where possible)
- City names do not initially render when using the magnifying glass zoom function (scroll zoom works fine)

# Planned Features
- Join circles for adjacent tiles with the same city name.
- Improve user interface.
- Better highlight tiles with no name assigned.
- Ability to save from map window (currently the save button only saves an image).
