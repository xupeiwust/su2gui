
# ##################################### JSON ##############################
from uicard import ui_card, ui_subcard, server

import json,jsonschema
from jsonschema import validate, ValidationError, SchemaError

state, ctrl = server.state, server.controller

# ##################################### JSON ##############################

#class jsonManager:
#    def __init__(self, state, name):
#        """ initialize the pipeline """
#        self._state = state
#        self._name = name
#        self._next_id = 1
#        self._nodes = {}
#        self._children_map = defaultdict(set)

# ##################################### JSON ##############################
# Opening JSON file, which is a python dictionary
def read_json_data(filenam):
  with open(filenam,"r") as jsonFile:
    state.jsonData = json.load(jsonFile)
  return state.jsonData
# ##################################### JSON ##############################

# Read the default values for the SU2 configuration.
state.jsonData = read_json_data('config.json')


# get the json name from the dictionary
def GetJsonName(value,List):
  entry = [item for item in List if item["value"] == value]
  return(entry[0]["json"])

def GetBCName(value,List):
  entry = [item for item in List if item["bcName"] == value]
  return(entry[0])