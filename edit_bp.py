from blueprint import Blueprint, sc_iter
from numpy import array

# material_categories = ['Glass','Heavy Armour','Lead','Light-weight Alloy','Metal','Rubber','Stone','Wood']

# Simple example demonstrating two common use cases:
#  -convert all structural blocks of one material into the corresponding block of a different material
#  -swap one paint for another for all blocks on the blueprint

# First construct an instance of the Blueprint class. In order to make use of the material conversion
# functionality, you must pass in a valid instance or path for a Converter, in addition to the
# blueprint file and a GUID map. See converter.py and guid_map.py for more details.
bp = Blueprint(path='CL9.blueprint',gmap='guid_map.json', converter='conversion_map.json')

# To convert all structural blocks of one material to another, simply invoke the member function
# convert_all:
bp.convert_all(m_from='Wood',m_to='Light-weight Alloy')

# The key-value format of the arguments is optional, but can make it clearer which way the conversion
# will proceed.
bp.convert_all('Stone','Metal')

# Values in the blueprint can be manipulated directly, in this case to change all blocks painted one
# colour to be painted a different colour instead.

# The cmap dictionary lists all the paint substitutions we wish to make
cmap = {28:17,29:18,30:19,31:20}

# Iterate through all subconstructs in the blueprint
for sc in sc_iter(bp.bp['Blueprint']):
    # Convert the 'block colour index' list to a numpy array
    bci = array(sc['BCI'])

    # Make our desired substitutions
    for c_from,c_to in cmap.items():
        bci[bci==c_from] = c_to # numpy's array indexing makes this very clean and easy

    # Write the result back to the blueprint (after converting back to a normal Python list object)
    sc['BCI'] = bci.tolist()

# Changes made so far are only to the Python object stored in memory - make sure to save the result
# to a (probably different) file.
bp.save_bp('out.blueprint')

