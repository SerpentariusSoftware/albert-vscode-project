# -*- coding: utf-8 -*-
# Copyright (c) 2024 Szilard Herczeg

"""This plugin allows you to quickly list and open VSCode projects based on recently opened paths."""

import os
import unicodedata
import json
#from json import load, loads, dumps
from pathlib import Path
from shutil import which
from typing import List, Optional

from albert import *

# Original author = "Sharsie"
md_iid = "3.0"
md_version = "1.2"
md_name = "VS Code Projects"
md_description = "Open & search Visual Studio Code Project files."
md_license = "MIT"
md_url = "https://github.com/SerpentariusSoftware/albert-vscode-project"
md_authors = ["@silureth"]
md_bin_dependencies = "code"
md_trigger = "vc "


class Plugin(PluginInstance, TriggerQueryHandler):

    #ICON = [f"file:{Path(__file__).parent}/vscode.svg"]
    EXECUTABLE = which("code")
    HOME_DIR = os.environ["HOME"]

    # User/sync/globalState/lastSyncglobalState.json
    # Path to the vscode storage json file where recent paths can be queried
    STORAGE_DIR_XDG_CONFIG_DIRS = [
        os.path.join(HOME_DIR, ".config/Code/storage.json"),
        os.path.join(HOME_DIR, ".config/Code/User/globalStorage/storage.json"),
    ]

    # Path to the Project Manager plugin configuration
    PROJECT_MANAGER_XDG_CONFIG_DIR = os.path.join(
        HOME_DIR,
        ".config/Code/User/globalStorage/alefragnani.project-manager/projects.json"
    )

    # If Project Manager is installed, you can disable recent projects by switching
    # the following variable to True
    INCLUDE_RECENT = True

    # Sort order of the Project Manager entries (match by Name)
    ORDER_PM_NAME = 0
    # Sort order of the Project Manager entries (match by Path)
    ORDER_PM_PATH = 0
    # Sort order of the Project Manager entries (match by Tags)
    ORDER_PM_TAG = 100
    # Sort order of the recently opened paths in VSCode
    ORDER_RECENT = 200

    def __init__(self):
        TriggerQueryHandler.__init__(self)#, id=md_id, name=md_name, description=md_description, defaultTrigger=md_trigger,synopsis='<vc | name>')
        PluginInstance.__init__(self) #, extensions=[self])
            
        self.iconUrls = [
            f"file:{Path(__file__).parent}/vscode.svg"
            # "xdg:preferences-system-search",
            # "xdg:system-search",
            # "xdg:search",
            # "xdg:text-x-generic",
        ]

    # Normalizes search string (accents and whatnot)

    def synopsis(self, query):
        return "<project name>"

    def defaultTrigger(self):
        return "vc "

    def normalizeString(self,input):
        return ''.join(c for c in unicodedata.normalize('NFD', input)
                    if unicodedata.category(c) != 'Mn').lower()

    # Helper method to create project entry from various sources

    def createProjectEntry(self,name, path, index, secondary_index):
        return {
            'name': name,
            'path': path,
            # Zeropad for easy sorting
            'index': '{0:04d}'.format(index),
            # Secondary index is used for sorting based on recently opened path order
            'index_secondary': '{0:04d}'.format(secondary_index),
        }
    # Return a item.
    def make_item(self,id: str, text: str, subtext: str = "", actions: List[Action] = []) -> Item:        
        return StandardItem(id=id, iconUrls=self.iconUrls, text=text, subtext=subtext, actions=actions)#id='vc'

    def make_found_items(self, el) -> Item:
        project = el[1]
        name = project['name']
        path = project['path']
        item_id= "%s_%s" % (path, name)

        return self.make_item(
            item_id,
            name, 
            path,
            #[Action(path, "Open in Visual Studio Code",lambda p=path: openUrl("file://%s" % p))] #works
            [
                Action("open", f"Open {path} in Visual Studio Code", lambda p=path: openUrl("file://%s" % p))
             ]#lambda: runDetachedProcess([self.EXECUTABLE, path]))]
        )

    # The entry point for the plugin, will be called by albert.   
    def handleTriggerQuery(self, query):# -> Optional[List[Item]]:
        if not self.EXECUTABLE:
            return query.add(self.make_item("Visual Studio Code not installed"))
                    # Array of Items we will return to albert launcher
        items = []
        projects = {}
        if len(query.string) > 1:
            #query_text = 
            
            #debug("query: '{}'".format(query_text))
            #if query.isTriggered:
                # Create projects dictionary to store projects by paths
        

            # Normalize user query
            normalizedQueryString = self.normalizeString(query.string)


            # Check whether the Project Manager config file exists
            if os.path.exists(self.PROJECT_MANAGER_XDG_CONFIG_DIR):
                with open(self.PROJECT_MANAGER_XDG_CONFIG_DIR) as configFile:
                    configuredProjects = json.loads(configFile.read())

                    for project in configuredProjects:
                        # Make sure we have necessarry keys
                        if (
                            not "rootPath" in project
                            or not "name" in project
                            or not "enabled" in project
                            or project['enabled'] != True
                        ):
                            continue

                        # Grab the path to the project
                        rootPath = project['rootPath']
                        if not os.path.exists(rootPath):
                            continue

                        # Normalize name and dir of the project
                        normalizedName = self.normalizeString(project['name'])
                        normalizedDir = self.normalizeString(
                            rootPath.split("/")[-1])

                        found = False
                        orderIndex = 0

                        # Search against the query string
                        if normalizedName.find(normalizedQueryString) != -1:
                            orderIndex = self.ORDER_PM_NAME
                            found = True
                        elif normalizedDir.find(normalizedQueryString) != -1:
                            orderIndex = self.ORDER_PM_PATH
                            found = True
                        elif "tags" in project:
                            for tag in project['tags']:
                                if self.normalizeString(tag).find(normalizedQueryString) != -1:
                                    orderIndex = self.ORDER_PM_TAG
                                    found = True
                                    break

                        if found:
                            projects[rootPath] = self.createProjectEntry(
                                project['name'],
                                rootPath,
                                orderIndex,
                                # Secondary index is zero, because we will sort the rest by project name
                                0
                            )

            # disable automatic sorting
            #query.disableSort()

            # Sort projects by indexes
            sorted_project_items = sorted(projects.items(), key=lambda item: "%s_%s_%s" % (
                item[1]['index'], item[1]['index_secondary'], item[1]['name']), reverse=False)

            for element in sorted_project_items:
                output_entry = self.make_found_items(element)
                item = query.add(output_entry)
                #items.append(item)
            #return items
        elif len(query.string) >= 1 and query.string == 'r': 
            for storageFile in self.STORAGE_DIR_XDG_CONFIG_DIRS:
                # No vscode storage file
                if os.path.exists(storageFile):
                    with open(storageFile) as configFile:
                        # Load the storage json
                        storageConfig = json.loads(configFile.read())

                        if (
                            self.INCLUDE_RECENT == True
                            and "lastKnownMenubarData" in storageConfig
                            and "menus" in storageConfig['lastKnownMenubarData']
                            and "File" in storageConfig['lastKnownMenubarData']['menus']
                            and "items" in storageConfig['lastKnownMenubarData']['menus']['File']
                        ):
                            # Use incremental index for sorting which will keep the projects
                            # sorted from least recent to oldest one
                            sortIndex = self.ORDER_RECENT + 1

                            # These are all the menu items in File dropdown
                            for menuItem in storageConfig['lastKnownMenubarData']['menus']['File']['items']:
                                # Cannot safely detect proper menu item, as menu item IDs change over time
                                # Instead we will search all submenus and check for IDs inside the submenu items
                                if (
                                    not "id" in menuItem
                                    or not "submenu" in menuItem
                                    or not "items" in menuItem['submenu']
                                ):
                                    continue

                                for submenuItem in menuItem['submenu']['items']:
                                    # Check of submenu item with id "openRecentFolder" and make sure it contains necessarry keys
                                    if (
                                        not "id" in submenuItem
                                        or submenuItem['id'] != "openRecentFolder"
                                        or not "enabled" in submenuItem
                                        or submenuItem['enabled'] != True
                                        or not "label" in submenuItem
                                        or not "uri" in submenuItem
                                        or not "path" in submenuItem['uri']
                                    ):
                                        continue

                                    # Get the full path to the project
                                    recentPath = submenuItem['uri']['path']
                                    if not os.path.exists(recentPath):
                                        continue

                                    # Normalize the directory in which the project resides
                                    normalizedDir = self.normalizeString(recentPath.split("/")[-1])
                                    normalizedLabel = self.normalizeString(submenuItem['label'])

                                    # Compare the normalized dir with user query
                                    # if (
                                    #     normalizedDir.find(normalizedQueryString) != -1
                                    #     or normalizedLabel.find(normalizedQueryString) != -1
                                    # ):
                                    # Inject the project
                                    projects[recentPath] = self.createProjectEntry(
                                        normalizedDir, recentPath, self.ORDER_RECENT, sortIndex)
                                    # Increment the sort index
                                    sortIndex += 1
            sorted_project_items = sorted(projects.items(), key=lambda item: "%s_%s_%s" % (
            item[1]['index'], item[1]['index_secondary'], item[1]['name']), reverse=False)
            print(sorted_project_items)
            for element in sorted_project_items:
                output_entry = self.make_found_items(element)
                item = query.add(output_entry)
            
