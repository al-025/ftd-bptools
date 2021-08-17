from blueprint import Blueprint
from pathlib import Path
from os import sys

# Simple example demonstrating how to obtain a per-category summary of the contents of a blueprint.

# Use your method of choice for determining the .blueprint file path to use, eg hardcoded, iterating
# through a directory, or taken from command line arguments as is done here.
if(len(sys.argv)>1):
    path = Path(sys.argv[1])
else:
    path = Path('CL9.blueprint')

# Construct an instance of the Blueprint class by passing in the path to a .blueprint file and
# to a cached GUID map - see guid_map.py for an example of how to create a GUID_map instance directly
# from game data instead.
bp = Blueprint(path=path,gmap='guid_map.json')

# The entire contents of the blueprint can be accessed via the bp member of the Blueprint class
# instance, see blueprint.py for a full listing of the available keys (or print them yourself!).
print(bp.bp['Name'],'\n')

# Call the analyse member function of the Blueprint instance to display the category by category
# composition of the provided blueprint.
categories = bp.analyse(printstyle='table')

# The returned dictionary contains the values used to generate this summary, and can be used to
# create even finer breakdowns (ie within a category).
print('\nAPS breakdown:')
for guid,stats in categories['APS']['breakdown'].items():
    print(bp.gmap[guid]['name'],stats)

