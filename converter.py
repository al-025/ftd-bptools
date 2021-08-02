from pathlib import Path
import json
import re

# Dictionary that encodes how to transform the name of a block into 'standard' form for consistency.
# Only used internally.
standard_form = {
    'search': [')(','(',')','left','right','wood','inverted corner','  ','mirrored 4m mirrored'],
    'replace': [' ','','','','mirrored','','inverted triangle corner',' ','mirrored 4m'],
}

# Regex pattern for a depricated method for determining the material and shape of a block from its name
shape_pattern = '\\(|\\)|[0-9]' + '|^R$|(?i)front|back|left|right|up|down' + '|block|square|triangle|wedge|slope|pole|beam' + '|diagonal|offset|corner|cut|inver|mirrored|variant|\Ato|transition'

def standardise_name(name):
    '''Transforms a string containing the name of a structural block into 'standard' form
    for consistency.'''
    name = name.lower()
    for s,r in zip(standard_form['search'],standard_form['replace']):
        name = name.replace(s,r)
    return name.strip()

def get_material_and_shape(name):
    '''Determine the material and shape from the name of an item. Deprecated.'''
    name_words = (standardise_name(name)).split()
    shape_words = []
    material_words = []
    for word in name_words:
        if(re.search(shape_pattern,word)):
            shape_words.append(word.replace('(','').replace(')',''))
        else:
            material_words.append(word.capitalize())
    return ' '.join(material_words), ' '.join(shape_words)

class Converter:
    '''Handles the conversion between material types for a given shape of structural block, using
    a database generated from game files or cached locally.'''
    item_ext = '.item'
    itemdup_ext = '.itemduplicateandmodify'
    item_dir = 'Items'
    itemdup_dir = 'ItemDup'
    
    def __init__(self,path='conversion_map.json'):
        '''Class initialiser. The path argument should be either the path to the Core_Structural mod
        within the game's Mods folder, or the path to a pre-generated conversion map saved in json
        format.'''
        self.by_material = {}
        self.by_shape = {}
        self.guid_to_shape = {}

        if( path != None ):
            path = Path(path)
            if( path.is_dir() ):
                # if given the path to the Core_Structural mod, read all item definitions
                for item in (path/self.item_dir).glob('*'+self.item_ext):
                    if('Wood Block Variant' in str(item) or
                       'ERA' in str(item) or
                       'Window' in str(item) or
                       'Light Block_288e377.item' in str(item)):
                        continue # ignore miscellaneous blocks
                    self.read_item(item)
                for item in (path/self.itemdup_dir).glob('*'+self.itemdup_ext):
                    if('Wood Block Variant' in str(item) or
                       'Glass inverted triangle corner right _5e73653.itemduplicateandmodify' in str(item)):
                        continue # this specific glass shape seems to be duplicated
                    self.read_itemdup(item)

                # Generate a dictionary that maps each block GUID to its shape
                for material in self.by_material:
                    self.guid_to_shape.update({
                        guid: shape
                        for shape,guid in self.by_material[material].items()
                    })
                
            elif( path.is_file() ):
                # if path to a pre-generated conversion map is supplied, load that instead
                with open(path,'r') as conv_file:
                    data = json.loads(conv_file.read())
                self.by_material = data['by_material']
                self.by_shape = data['by_shape']
                self.guid_to_shape = data['guid_to_shape']

    def read_item(self,path):
        '''Specialised method for reading .item files to extend the conversion dictionaries.'''
        with open(path,'r') as itemfile:
            data = json.loads(itemfile.read())

        # Regex substitution to remove 'block' from the name of the block
        material = re.sub('(?i)\sblock','',data['ComponentId']['Name'])
        
        if(material not in self.by_material):
            self.by_material[material] = {}
        self.by_material[material]['block']= data['ComponentId']['Guid']
        
        if('block' not in self.by_shape):
            self.by_shape['block'] = {}
        self.by_shape['block'][material] = data['ComponentId']['Guid']
    
    def read_itemdup(self,path):
        '''Specialised method for reading .itemduplicateandmodify files to extend the
        conversion dictionaries.'''
        with open(path,'r') as itemfile:
            data = json.loads(itemfile.read())

        # Same regex substitution as above to obtain the material name, also obtain the shape
        # by standardising the name of the mesh reference
        material = re.sub('(?i)\sblock','',data['IdToDuplicate']['Reference']['Name'])
        shape = standardise_name(data['MeshReference']['Reference']['Name'])

        # debugging printout
        # print('{}: M={}, S={}'.format(data['ComponentId']['Name'],material,shape))
        
        if(material not in self.by_material):
            self.by_material[material] = {}
        self.by_material[material][shape] = data['ComponentId']['Guid']
        
        if(shape not in self.by_shape):
            self.by_shape[shape] = {}
        self.by_shape[shape][material] = data['ComponentId']['Guid']

    def save(self,path='conversion_map.json',indent=2):
        '''Dumps all generated dictionaries to file in json format for later usage.'''
        with open(path,'w') as map_file:
            map_file.write(json.dumps({
                'by_material': self.by_material,
                'by_shape': self.by_shape,
                'guid_to_shape': self.guid_to_shape
            },indent=indent,sort_keys=True))

    def convert(self,guid,material):
        '''Try to find the block GUID with the same shape as the provided GUID, but in the
        specified material type. If the conversion fails, it will return the same GUID that
        was passed in.'''
        try:
            shape = self.guid_to_shape[guid]
            return self.by_shape[shape][material]
        except KeyError:
            return guid

if __name__=="__main__":
    # Path to your FTD installation, may vary per user
    path_prefix = '/mnt/c/Program Files (x86)/Steam/steamapps/common/From The Depths/'

    # Path to the Core_Structural mod in your FTD folder; this shouldn't need changing
    data_path = 'From_The_Depths_Data/StreamingAssets/Mods/Core_Structural/'

    # Construct the material conversion map from scratch by passing it the path to the
    # Core_Structural mod
    conv = Converter(path_prefix+data_path)

    # Print a list of materials that were found in the game files.
    # For an unmodified game, this should be:
    # ['Glass','Heavy Armour','Lead','Light-weight Alloy','Metal','Rubber','Stone','Wood']
    print([material for material in conv.by_material])

    # Save the generated conversion map to a json file so that future runs do not need
    # to parse game data again
    conv.save(path='conversion_map.json')

    # To load this, pass the path to the saved json file to the initialiser, eg:
    # conv = Converter('conversion_map.json')
