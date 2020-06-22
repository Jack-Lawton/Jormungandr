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

Before saving, on the main menu, two options are available:
- Save updates only. This is designed to aid in collaboration, any new cities added in a session are coloured slightly differently, choosing to save only updates will save only these cities. The new files can then be merged or re-used however is required.
- Separate files for each civilization. By default Jörmungandr will aim to minimise the number of files produced by saving all civilizations together, however, these can be separates to better align with current YnAMP practice. Only civilizations with city mappings will have files created.

Jörmungandr does not aim to save completed functioning mods, rather simply CityMap.xml and GamePlayText.xml files, the most time consuming to create. Where possible Jörmungandr will reuse existing GamePlayText mappings and for new cities, will create its own, always preceded by "LOC_JORMUNGANDR_CITY_NAME_" to prevent any conflicts. All produced GamePlayText will be in English (US) only.

# Known Bugs
- Maps can be slow to render when changing zoom (particularly when far out)
- City names do not initially render when using the magnifying glass zoom function (scroll zoom works fine)

(In short, matplotlib was definitely not designed for the kind of dynamic graphical heavy lifting I am using it for)

# Planned Features
- Suggest civilization specific city names using names from the general (None) mapping.
- Option to enable automatic generation of civilization specific city names using [Rosetta](https://forums.civfanatics.com/threads/rosetta-dynamic-city-names.623102/) (where available).
