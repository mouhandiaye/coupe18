#!/usr/bin/python
import rospy

class MapElement(object):
    def get(self, requestpath):
        raise NotImplementedError("This is the super class. Needs to be overwritten from the child class.")
    def set(self, requestpath, new_value):
        raise NotImplementedError("This is the super class. Needs to be overwritten from the child class.")


class ListManager(MapElement): # Not used for now
    def __init__(self, classdef, initdict):
        self.Elements = []
        for k in initdict.keys():
            self.Elements.append(classdef(initdict[k]))


class DictManager(MapElement):
    def __init__(self, elemdict):
        self.Dict = elemdict
        for k in self.Dict.keys():
            if isinstance(k, dict):
                raise ValueError("Inner dicts as values NOT allowed. '{}' has a dict inside. Must be initialized beforehand.".format(k))

    def toList(self):
        return self.Dict.values()

    def toDict(self, recursive = False):
        if recursive:
            d = {}
            for item in self.Dict:
                if isinstance(self.Dict[item], DictManager): d[item] = self.Dict[item].toDict(recursive = True)
                else: d[item] = self.Dict[item]
            return d
        else:
            for k in self.Dict.values():
                if isinstance(k, DictManager):
                    rospy.logerr(("    ERROR Trying to transform a DictManager that has other DictManagers inside."
                                " Use '*' at the end to get a recursively-constructed subdict."))
                    return None
            return self.Dict

    def get(self, requestpath):
        if isinstance(requestpath, str):
            requestpath = RequestPath(requestpath)
            if not requestpath.Valid: return None
        keyname = requestpath.getNextKey()
        if requestpath.isLast():
            if "," in keyname:
                keys = keyname.split(",")
                d = {}
                for k in keys:
                    if not isinstance(self.Dict[k], DictManager):
                        d[k] = self.Dict[k]
                    else:
                        rospy.logerr("    GET Request failed : Must include a '*' or '^' dict operator at the end to get a full dict json or object.")
                return d
            elif keyname in self.Dict.keys():
                if not isinstance(self.Dict[keyname], DictManager):
                    return self.Dict[keyname]
                rospy.logerr("    GET Request failed : Must include a '*' or '^' dict operator at the end to get a full dict json or object.")
            elif keyname == '^':
                return self
                # rospy.logerr("    GET Request failed : Asked to get a DictManager object with key operator '^' but '{}' points to a '{}' object.".format(keyname, type(self.Dict[keyname])))
            elif keyname == '*':
                return self.toDict(recursive = True)
            else:
                rospy.logerr("    GET Request failed : Unrecognized last key dict operator '{}'.".format(keyname))
        else:
            if keyname in self.Dict.keys():
                if isinstance(self.Dict[keyname], DictManager):
                    return self.Dict[keyname].get(requestpath)
                else:
                    return self.Dict[keyname]
            elif keyname == "*":
                d = {}
                current_level = requestpath.Counter
                for item in self.Dict:
                    if isinstance(self.Dict[item], DictManager):
                        d[item] = self.Dict[item].get(requestpath)
                        requestpath.Counter = current_level
                    else:
                        d[item] = self.Dict[item]
                return d
            else:
                rospy.logerr("    GET Request failed : Couldn't recognize request path key '{}'.".format(keyname))

    def set(self, requestpath):
        if isinstance(requestpath, str):
            requestpath = RequestPath(requestpath)
            if not requestpath.Valid: return None
        keyname = requestpath.getNextKey()

        if requestpath.isLast():
            assignments = []
            for s in keyname.split(','):
                if s.count("=") != 1:
                    rospy.logerr("    SET Request failed : invalid key part '{}', must have one '=' operator.".format(s))
                    return False
                key, new_value = s.split("=")
                if not key in self.Dict: # Remove this check if need to authorize to create keys
                    rospy.logerr("    SET Request failed : key '{}' does not already exist in dict.".format(key))
                    return False
                if not isinstance(self.Dict[key], DictManager):
                    try:
                        new_value = type(self.Dict[key])(new_value)
                        assignments.append((key, new_value))
                    except (TypeError, ValueError):
                        rospy.logerr("    SET Request failed : new value '{}' not castable to the old value '{}''s type.".format(new_value, self.Dict[keyname]))
                        return False
                    except KeyError:
                        rospy.logerr("    SET Request failed : Couldn't find existing key '{}'.".format(key))
                        return False
                else:
                    raise ValueError("    SET Request failed : Can't SET a whole DictManager to a new value.")

            for assignment in assignments:
                self.Dict[assignment[0]] = assignment[1]
            return True

        else:
            if '=' in keyname:
                rospy.logerr("    SET Request failed : '=' assign operator must only be applied on the last path key.")
                return False
            if keyname in self.Dict:
                return self.Dict[keyname].set(requestpath)



class RequestPath():
    def __init__(self, pathstring):
        self.pathstring = pathstring

        self.Valid = True
        if not len(pathstring):
            rospy.logerr("Invalid path : empty path.")
            self.Valid = False
        if pathstring[-1] == '/':
            rospy.logerr("Invalid path : must not end with '/'.")
            self.Valid = False
        self.Keys = [p for p in pathstring.split('/') if p != '']
        self.Counter = -1

    def getNextKey(self):
        if self.Counter < len(self.Keys) - 1:
            self.Counter += 1
            return self.Keys[self.Counter]
        else:
            raise ValueError("ERROR Not enough levels in path ! Can't reach farther than the last path key.")

    def isLast(self):
        return self.Counter == len(self.Keys) - 1

    def __repr__(self):
        return self.pathstring
