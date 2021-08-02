from pathlib import Path
import json

# Block categories are determined based on the name of the mod the block was defined in
category_names = {
    'Core_ACDeco': 'Decorations',
    'Core_AI': 'AI',
    'Core_APS': 'APS',
    'Core_Air': 'Air',
    'Core_CRAM': 'CRAM',
    'Core_Constructs': 'Subconstructs',
    'Core_ControlSurfaces': 'Air',
    'Core_Decorations': 'Decorations',
    'Core_Depreciated': 'Depricated',
    'Core_Drill': 'Simple Weapons',
    'Core_FuelEngine': 'Fuel Engines',
    'Core_Land': 'Land',
    'Core_Laser': 'Laser',
    'Core_Misc': 'Misc',
    'Core_Missile': 'Missile',
    'Core_NuclearEngine': 'Nuclear Engines',
    'Core_Resource': 'Resource',
    'Core_RingShields': 'Misc',
    'Core_SimpleWeapon': 'Simple Weapons',
    'Core_SteamEngine': 'Steam Engines',
    'Core_Structural': 'Armour',
    'Core_Struts': 'Armour',
    'Core_Surface': 'Water',
    'Core_WarpDrive': 'Warp',
    'Core_Water': 'Water',
    'ExampleMod': 'ExampleMod'
}

class GUID_map:
    '''Handles parsing of game data to generate a dict mapping GUIDs to blocks, and queries for
    information associated with a given block GUID. Mostly a wrapper around the 'gmap' dictionary.'''
    
    item_ext = '.item'
    itemdup_ext = '.itemduplicateandmodify'
    item_dir = 'Items'
    itemdup_dir = 'ItemDup'

    def __init__(self,path=None):
        '''Class initialiser. The path argument must be either None, the path to the game's Mods folder,
        or the path to a pre-generated GUID map saved in json format. If the path is left as None,
        the user must manually set up the gmap member for the class instance at some later time.'''
        self.gmap = {}

        if( path != None ):
            path = Path(path)
            if( path.is_dir() ):
                # if path to mods folder is supplied, load all items from each mod in that folder
                for mod in path.iterdir():
                    # regular items
                    if( (mod/self.item_dir).is_dir() ):
                        for item in (mod/self.item_dir).glob('*'+self.item_ext):
                            self.read(item)
                    else:
                        continue

                    # templated items
                    if( (mod/self.itemdup_dir).is_dir() ):
                        for item in (mod/self.itemdup_dir).glob('*'+self.itemdup_ext):
                            self.read(item)
            elif( path.is_file() ):
                # if path to a pre-generated GUID map is supplied, load it directly instead
                with open(path,'r') as map_file:
                    self.gmap = json.loads(map_file.read())
            else:
                raise ValueError('Invalid path')
            
    # Python specific methods, these just duplicate the corresponding functionality of the core dictionary
    def __contains__(self,guid):
        return guid in self.gmap

    def __getitem__(self,guid):
        if(guid not in self):
            raise ValueError('GUID not found')
        return self.gmap[guid]

    def __setitem__(self,guid,value):
        self.gmap[guid] = value

    def __len__(self):
        return len(self.gmap)

    def __str__(self):
        return str(self.gmap)

    def __iter__(self):
        return iter(self.gmap)

    def __next__(self):
        return next(self.gmap)

    def __reversed__(self):
        return reversed(self.gmap)

    def read_item(self,path):
        '''Specialised method for reading .item files to extend the gmap dict.'''
        with open(path,'r') as sourcefile:
            data = json.loads(sourcefile.read())
        guid = data['ComponentId']['Guid']
        if(guid not in self):
            self[guid] = {
                'name':data['ComponentId']['Name'],
                'cost':data['Cost']['Material'],
                'volume':data['SizeInfo']['ArrayPositionsUsed']*data['SizeInfo']['VolumeFactor'],
                'weight':data['Weight'],
                # 'category':data['InventoryTabOrVariantId']['Reference']['Name']
                'category':category_names.get(path.parts[-3],path.parts[-3])
            }
        
    def read_itemdup(self,path):
        '''Specialised method for reading .itemduplicateandmodify files to extend the gmap dict.'''
        with open(path,'r') as sourcefile:
            data = json.loads(sourcefile.read())
        ref = data['IdToDuplicate']['Reference']
        if(ref['Guid'] not in self):
            raise ValueError('GUID for {} not known, load that first'.format(ref['Name']))

        guid = data['ComponentId']['Guid']
        if(guid not in self):
            # volume calculation
            if(data['change_SizeInfo']):
                vol = data['SizeInfo']['ArrayPositionsUsed']*data['SizeInfo']['VolumeFactor']
            else:
                vol = self[ref['Guid']]['volume']*data['VolumeScaling']
                
            self[guid] = {
                'name':data['ComponentId']['Name'],
                'cost':self[ref['Guid']]['cost']*data['CostWeightHealthScaling']*data['CostScaling'],
                'volume':vol,
                'weight':self[ref['Guid']]['weight']*data['CostWeightHealthScaling']*data['WeightScaling'],
                # 'category':self[ref['Guid']]['category'] #InventoryTabOrVariantId here gives the submenu
                'category':category_names.get(path.parts[-3],path.parts[-3])
            }

    def read(self,path):
        '''Simple convenience function to call the right read function based on the file extension.'''
        if(path.suffix==self.item_ext):
            self.read_item(path)
        elif(path.suffix==self.itemdup_ext):
            self.read_itemdup(path)

    def save(self,path='guid_map.json',indent=2):
        '''Dumps the gmap dict to file in json format for later usage.'''
        with open(path,'w') as map_file:
            map_file.write(json.dumps(self.gmap,indent=indent))

if __name__=="__main__":
    # Path to your FTD installation, may vary per user
    path_prefix = '/mnt/c/Program Files (x86)/Steam/steamapps/common/From The Depths/'

    # Path to the Mods folder from within your FTD folder; this shouldn't need changing
    data_path = 'From_The_Depths_Data/StreamingAssets/Mods/'

    # Construct the GUID map from scratch by passing it the path to your Mods folder
    guid_map = GUID_map(path_prefix+data_path)
    print('Loaded {} items'.format(len(guid_map)))

    # Save the generated GUID map to a json file so that future runs do not need to parse game data again
    guid_map.save(path='guid_map.json')
    
    # To load this, construct a GUID_map by passing it the path to this file instead, eg:
    # guid_map = GUID_map('guid_map.json')


