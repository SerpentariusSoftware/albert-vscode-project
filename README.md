# Albert launcher plugin for Visual Studio Code
This is a plugin for the [albert launcher](https://albertlauncher.github.io/) which lists and lets you start projects of VS Code IDE

Supports listing of recently opened paths and integrates with [Project Manager extension](https://marketplace.visualstudio.com/items?itemName=alefragnani.project-manager)

Sorting is based on
1) If query matches on either path or name of a Project Manager entry, it will be sorted first and then alphabetically by name
2) If query matches on the tag of Project Manager entry, it will be sorted second and then alphabetically by name
3) Last come recently opened paths in VS Code sorted in the same way as they are shown in VS Code File -> Open Recent

## How to install
Copy contents of this directory to $HOME/.local/share/albert/python/plugins/albert-vscode-project

## How to use
Start by typing `vc `. If you have any recently opened paths you should immediately see the latest ones at the top.
Or type in `vc r` for recent opened folders.

## Project Manager
If you have PM extension installed the search is performed against the rootPath of the project, its name and its tags.

## Disclaimer

Not a python guy, this plugin was scripted together with my buddy ol' pal uncle Google. Like... Entirely.

I am in no way affiliated with VS Code or Microsoft.

VS Code logo used based on the [brand guidelines](https://code.visualstudio.com/brand).

# Based on (updated)
Based on https://github.com/Sharsie/albertlauncher-vscode-projects

Based on https://github.com/mqus/jetbrains-albert-plugin