from pathlib import Path
import json
from guid_map import GUID_map, category_names
from converter import Converter
from numpy import array
from tabulate import tabulate

# Keys in a .blueprint file:
#   FileModelVersion,Name,Version,SavedTotalBlockCount,SavedMaterialCost,ContainedMaterialCost,
#   ItemDictionary,Blueprint
# Keys in the 'Blueprint' dictionary of a .blueprint file:
#   ContainedMaterialCost,CSI,COL,SCs,BLP,BLR,BP1,BP2,BCI,BEI,BlockData,VehicleData,designChanged,
#   blueprintVersion, blueprintName,SerialisedInfo,Name,ItemNumber,LocalPosition,LocalRotation,ForceId,
#   TotalBlockCount,MaxCords,MinCords,BlockIds,BlockState,AliveCount,BlockStringData,BlockStringDataIds,
#   GameVersion,PersistentSubObjectIndex,PersistentBlockIndex,AuthorDetails,BlockCount

def sc_iter(sc):
    '''Generator function to recursively iterate through all subconstructs (depth-first) in the given
    blueprint/subconstruct.'''
    if( len(sc['SCs']) > 0 ):
        for ssc in sc['SCs']:
            for sssc in sc_iter(ssc):
                yield sssc
    yield sc

class Blueprint:
    '''Handles the reading, writing, analysis and editing of blueprint files. Works identically for
    all blueprints regardless of source (ie constructs, subconstructs, and prefabs).'''
    
    def __init__(self,path=None,gmap=None,converter=None):
        '''Class initialiser.
        The path parameter should be the path to a blueprint file, or can be left as None and set
          up later by manually calling read_bp on a blueprint.
        The gmap parameter can be either an existing instance of the GUID_map class, or a valid
          path argument to be passed to the GUID_map initialiser.
        The converter parameter is similar to gmap: either an instance of the Converter class,
          or a valid path argument to pass to its corresponding initialiser.'''
        if( isinstance(gmap,GUID_map) ):
            self.gmap = gmap
        elif( gmap != None ):
            self.gmap = GUID_map(gmap)

        if( isinstance(converter,Converter) ):
            self.conv = converter
        elif( converter != None ):
            self.conv = Converter(converter)

        if( path != None ):
            path = Path(path)
            if( path.is_file() ):
                self.read_bp(path)

    def read_bp(self,path):
        '''Read the contents of a blueprint file into the bp member, and set up the dictionaries for
        converting between integer IDs from the blueprint and block GUIDs.'''
        with open(path,'r') as bpfile:
            self.bp = json.loads(bpfile.read())
        self.to_guid = { int(Id): guid for Id,guid in self.bp['ItemDictionary'].items() }
        self.to_id = { guid: int(Id) for Id,guid in self.bp['ItemDictionary'].items() }

    def save_bp(self,path,indent=None):
        '''Write the contents of the bp member to the specified file.'''
        with open(path,'w') as bpfile:
            bpfile.write( json.dumps(self.bp,indent=indent) )

    def get_conversion_table(self,m_from,m_to):
        '''Generate a dictionary that maps block GUIDs of one material to the corresponding
        shape in another material, but limited to the shapes that were originally present
        in the loaded blueprint.'''
        return {
            guid_from: self.conv.convert(guid_from,m_to)
            for _,guid_from in self.conv.by_material[m_from].items()
            if guid_from in self.to_id
        }

    def convert_all(self,m_from,m_to):
        '''Convert all blocks of one material type in the loaded blueprint to their corresponding
        blocks of the specified material type.'''

        # First, determine what block ID substitutions need to be made.
        # In the case where the resulting block GUID after material conversion does not appear
        # in the original blueprint, just change the blueprint's internal ID to GUID mapping
        # instead.
        ct = {}
        for guid_from,guid_to in self.get_conversion_table(m_from,m_to).items():
            if(guid_to in self.to_id):
                ct[self.to_id[guid_from]] = self.to_id[guid_to]
            else:
                self.bp['ItemDictionary'][str(self.to_id[guid_from])] = guid_to

        # Iterate through all subconstructs in the blueprint
        for sc in sc_iter(self.bp['Blueprint']):
            # Convert the BlockIds list into a numpy array
            block_ids = array(sc['BlockIds'])

            # Apply the required substitutions
            for id_from,id_to in ct.items():
                block_ids[block_ids==id_from] = id_to # numpy's array indexing makes this very clean

            # Write the result back to the blueprint (after converting back to a normal list object)
            sc['BlockIds'] = block_ids.tolist()

    def analyse(self,printstyle='table'):
        '''Generate and return a dictionary containing the distributions of cost, volume, weight
        and block count across the categories defined in guid_map.py and across each block type.
        Optionally also prints the results depending on the value of the printstyle argument.
        Allowed values for printstyle are either 'table' or 'linear'; other values will result
        in nothing being printed.'''
        categories = {
            cname: {
                'breakdown':{},
                'cost':0,
                'volume':0,
                'weight':0,
                'count':0,
                'cost%':0,
                'volume%':0,
                'weight%':0,
                'count%':0
            }
            for _,cname in category_names.items()
        }

        # first get a count of all blocks in the blueprint
        for sc in sc_iter(self.bp['Blueprint']):
            block_ids = array(sc['BlockIds'])
            for bid,guid in self.to_guid.items():
                if( guid not in categories[self.gmap[guid]['category']]['breakdown'] ):
                    categories[self.gmap[guid]['category']]['breakdown'][guid] = {'count':0}
                n = len(block_ids[block_ids==bid])
                categories[self.gmap[guid]['category']]['breakdown'][guid]['count'] += n

        # now fill in the values of interest
        for cat in categories:
            for guid in categories[cat]['breakdown']:
                for qty in ['cost','volume','weight']:
                    total = categories[cat]['breakdown'][guid]['count'] * self.gmap[guid][qty]
                    categories[cat]['breakdown'][guid][qty] = total
                    categories[cat][qty] += total
            categories[cat]['count'] = sum([categories[cat]['breakdown'][guid]['count'] for guid in categories[cat]['breakdown']])

        totals = {
            qty: sum([categories[c][qty] for c in categories])
            for qty in ['cost','volume','weight','count']
        }

        for cat in categories:
            for qty in ['cost','volume','weight','count']:
                if( totals[qty] == 0 ):
                    continue
                categories[cat][qty+'%'] = 100 * categories[cat][qty] / totals[qty]

        # display results
        if(printstyle=='table'):
            res = [
                [cat,
                 '{:,.1f}'.format(categories[cat]['cost']),
                 '({:.1f}%)'.format(categories[cat]['cost%']),
                 '{:,.1f}'.format(categories[cat]['volume']),
                 '({:.1f}%)'.format(categories[cat]['volume%']),
                 '{:,.1f}'.format(categories[cat]['weight']),
                 '({:.1f}%)'.format(categories[cat]['weight%']),
                 '{:,.0f}'.format(categories[cat]['count']),
                 '({:.1f}%)'.format(categories[cat]['count%']),
                ] for cat in categories
                if len(categories[cat]['breakdown'])>0
            ]
            res.append( ['Total',
                         '{:,.1f}'.format(totals['cost']),'',
                         '{:,.1f}'.format(totals['volume']),'',
                         '{:,.1f}'.format(totals['weight']),'',
                         '{:,.0f}'.format(totals['count']),'']
            )
            headers = ['Category','Cost','(%)','Volume','(%)','Weight','(%)','Blocks','(%)']
            print(tabulate(res,headers=headers,tablefmt='presto',numalign='left',stralign='left'))
        elif(printstyle=='linear'):
            print('Totals')
            for qty in ['cost','volume','weight']:
                print('  {}: {:,.1f}'.format(qty.capitalize(),totals[qty]))

            for cat in categories:
                if(len(categories[cat]['breakdown'])>0):
                    print('{} ({} blocks)'.format(
                        cat,
                        sum([
                            categories[cat]['breakdown'][guid]['count']
                            for guid in categories[cat]['breakdown']
                        ])
                    ))
                    for qty in ['cost','volume','weight']:
                        print('  {}: {:,.1f} ({:.1f}%)'.format(
                            qty.capitalize(),
                            categories[cat][qty],
                            categories[cat][qty+'%']))

        return categories

