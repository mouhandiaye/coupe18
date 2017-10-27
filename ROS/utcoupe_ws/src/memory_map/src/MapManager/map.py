#!/usr/bin/python
import rospy
from loader import MapLoader, LoadingHelpers
from map_bases import MapElement, ListManager
import map_classes


class Map(MapElement):
    def __init__(self, filename):
        super(Map, self).__init__("map")
        initdict = MapLoader.loadFile(filename)

        # Loading objects from the YML dict
        LoadingHelpers.checkKeysExist(initdict, "terrain", "entities", "objects")
        self.Terrain    = map_classes.Terrain("terrain", initdict["terrain"])
        self.Entities   = ListManager("entities", map_classes.Entity, initdict["entities"])
        self.Objects    = map_classes.ObjectContainer("objects", initdict) # Small hack to properly initialize ObjectContainer
        rospy.loginfo("[memory/map] Loaded map successfully.")

    def get(self, path):
        pass

    def set(self, path, new_value):
        pass
