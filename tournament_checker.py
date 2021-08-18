from guid_map import GUID_map
from blueprint import Blueprint, sc_iter
from numpy import array, in1d, count_nonzero
from pathlib import Path
from os import sys

rotations = {
    'up': [8,9,10,11],
    'down': [4,5,6,7],
    'left': [3,15,21,23],
    'right': [1,13,16,18],
    'forward': [0,12,16,18],
    'back': [2,14,17,19],
}

banned_blocks = {
    'Sky Fortress Turbine': '382a7650-2231-4867-96e4-8d97242a4741',
    'Ram':'c0e407e9-fc15-43fa-9a61-4c79a3acb6a9',
    'Particle Melee Lens': '2099a233-181e-4f50-9a0e-78a547969a8e',
    'Laser Cutter': 'f2f1f8f5-92b5-4047-9ec7-de86d8608583',
    'Steam Shaft Drill Extension 1m': '96c9d85c-425a-4744-8ff3-36a364ceb99d',
    'Steam Shaft Drill Extension 3m': '35cd6905-44d0-4bb3-be0f-20ee2ed670bf',
    'Steam Shaft Drill Extension 5m': 'cbe68b75-1568-494e-8caf-c9e5336faea7',
    'Steam Shaft Drill Head 1m': 'cdc656c1-2266-470b-872c-79faa65dcaae',
    'Steam Shaft Drill Head 3m': '532c3d76-ede3-4fbf-bf87-8e82b3acc73b',
    'Steam Shaft Drill Head 5m': 'c0eecb94-0410-4031-9015-2ec4b8fd4c80',
    'Drill Bit (Large)': 'fc4f02ab-2e74-4deb-8d83-ca3da65c99ff',
    'Drill Bit (Small)': 'edf0442a-4976-43f4-9a9c-66e43f0353ff',
    'Drill Extension horizontal splitter': '1af0aadf-7edc-401a-9750-0074b8b46b6a',
    'Drill Extension vertical splitter': '51cfbd8b-5223-4101-b4f3-f62872a82b58',
    'Drill Extension': '197f8869-1891-4e7d-9465-97b9183aed22',
    'Drill': 'eadfab64-b2a7-4704-8241-37ae3b42f705',
    'Power Input': '83e8cf5c-ad5a-4cfd-a0d0-eb4ca9f48127',
    'Torque Amplifier': 'dfb470c9-e7f2-4530-9b5b-3de8214501da',
    'Subvehicle Spawner': '58e7abb1-de9f-47f9-864b-d5c8218f1769',
    'Vehicle Blueprint Spawner': 'd43b5a55-9e60-48f9-9e77-ac1cfa97dafa',
    'Compact Repair Tentacle': '46fc87ec-0f7f-4c55-a5d3-721365c5f364',
    'Repair Tentacle': '0b59767f-dcf2-43f3-895b-d876afed0063',
    'Light Block': '288e3778-900b-4bfd-a455-e94ed75c6ec2',
    'Laser': '5cf2b4da-c1b8-4005-930b-73cc39ac9d28',
    'Warp Charger (2m)': '24f6df16-98dc-4176-93cf-456a5e4d7ab8',
    'Warp Controller': '0a8d8d02-5d03-4488-8431-e75602fea1e4',
    'Warp Rod (2m)': 'c6497cec-51b5-4d94-940e-107990a25afd',
    'Warp Terminator': 'd6c8b7aa-bdcd-459a-a2ec-fbbba09cffcf',
    'LUA Box': 'd3924bae-be5a-43a0-be19-64fc7c8d6059',
    'LUA Transceiver': 'dc17bd30-20ac-47c3-9c42-af6b3cdebf6e',
}

restricted_blocks = {
    'Firing Pieces': {
        'GUIDs': ['7101e1cb-a501-49bd-8bbe-7a960881e72b', #Simple weapons
                  '0aa0fa2e-1a85-4493-9c4c-0a69c385395d',
                  'aa070f63-c454-4f95-82fd-d946a32a1b66',
                  'c94e1719-bcc7-4c6a-8563-505fad2f9db9',
                  'b92a4ce6-ea93-4c0c-97d7-494ea611caa9',
                  '1217043c-e786-4555-ba24-46cd1f458bf9',
                  'f9f36cb3-cbfd-446a-9313-40f8e31e6e89',
                  '742f063f-d0fe-4f41-8717-a2c75c38d5e0',
                  '58305289-16ea-43cf-9144-2f23b383da81',
                  '3be0cab1-643b-4e3a-9f49-45995e4eb9fb',
                  'd8c5639a-ff5f-448e-a761-c2f69fac661a',
                  '268d79bf-c266-48ed-b01b-76c8d4d31c92',
                  '9b8657b9-c820-43a0-ad19-25ea45a100f1',
                  '2311e4db-a281-448f-ad53-0a6127573a96',
                  'e1d1bcae-f5e4-42bb-9781-6dde51b8e390',
                  '16b67fbc-25d5-4a35-a0df-4941e7abf6ef',
                  'd3e8e14a-58e7-4bdd-b1b3-0f37e4723a73',

                  'dc8f69fe-f97c-404f-996c-1b934afa17b5', #APS and CRAM
                  'a97e03b0-e8da-49e2-9913-ad8c1826d869',

                  '6fc05823-7905-4b5e-bde0-858010860e91', #Missile launchers
                  '9bff4b97-c652-4da7-99df-ab4a1bd5551e',
                  '43d357dd-d896-4f43-a0ff-8c3b091267c4',
                  '9424812a-274e-4223-a3ae-9ee86a7db46b',
                  '6a166a7c-dc50-401c-8498-3a7d6b7f09e7',
                  '77b3c67d-f649-438c-8e24-5779c0f0bdbf',
                  '54a66bcd-dc50-401c-8498-3a7d6b7f09e7',
                  'c743b888-a53c-42b8-b4f0-3afc6d763617',
                  'bfb82ee6-345a-44a4-84e1-d6706cc8b29d',
                  '8ba7a591-3923-4344-9f87-0588c6a1aba0',
                  '26b0f142-9419-41f1-9c13-3a2b62437f60',
                  '1b9aa074-9b04-4b5c-b30e-35bdfa0e0835',
                  'a7aaf947-f16c-489b-a10e-b48d03e0d209',
                  'b8bbf947-f16c-489b-a10e-b48d03e0d209',

                  '7dc67bed-fd0f-4145-9525-5840bbcc4822', #Laser combiners
                  'fd2b6afb-da6f-4a8e-bfc0-e4202b87300d',

                  '3d82f1a3-ad2a-4e81-a4e3-cb88c968f6e9', #PAC lenses
                  '2eea241a-6a32-41c6-a9e4-d082c7e854de',
                  '9896747c-39a5-43bc-8ba9-ccf2f645cca1',
                  'f1746662-adec-4054-98bd-94b553bc6c6d',
                  '1a1c9de5-6db5-4092-97ac-a4883383fadd',
                  '2e429412-2982-4335-bf3c-a6c6609c8cbf',
        ],
        'max': 50,
        'message': None
    },
    'LAMS Nodes': {
        'GUIDs': ['9385face-922e-4158-9632-7ab9fcb00166'],
        'max': 4,
        'message': 'LAMS nodes present, check number of connected laser systems'
    },
    'Offensive Lasers': {
        'GUIDs': ['7dc67bed-fd0f-4145-9525-5840bbcc4822',
                  'fd2b6afb-da6f-4a8e-bfc0-e4202b87300d',],
        'max': -1,
        'message': 'Offensive lasers present, check DPS/AP of connected systems'
    },
    'PACs': {
        'GUIDs': ['3d82f1a3-ad2a-4e81-a4e3-cb88c968f6e9',
                  '2eea241a-6a32-41c6-a9e4-d082c7e854de',
                  '9896747c-39a5-43bc-8ba9-ccf2f645cca1',
                  'f1746662-adec-4054-98bd-94b553bc6c6d',
                  '1a1c9de5-6db5-4092-97ac-a4883383fadd',
                  '2e429412-2982-4335-bf3c-a6c6609c8cbf',],
        'max': -1,
        'message': 'PACs present, check max charge'
    },
    'Shield Projectors': {
        'GUIDs': ['f7042d78-d7ae-4a0b-b273-197813c61648'],
        'max': -1,
        'message': 'Shield projectors present'
    },
    'Ring Shields': {
        'GUIDs': ['61228ef0-e45f-4074-bd16-9dc47b19be5b'],
        'max': -1,
        'message': 'Ring shields present, check orientations'
    },
    'Missiles': {
        'GUIDs': ['6fc05823-7905-4b5e-bde0-858010860e91',
                  '9bff4b97-c652-4da7-99df-ab4a1bd5551e',
                  '43d357dd-d896-4f43-a0ff-8c3b091267c4',
                  '9424812a-274e-4223-a3ae-9ee86a7db46b',
                  '6a166a7c-dc50-401c-8498-3a7d6b7f09e7',
                  '77b3c67d-f649-438c-8e24-5779c0f0bdbf',
                  '54a66bcd-dc50-401c-8498-3a7d6b7f09e7',
                  'c743b888-a53c-42b8-b4f0-3afc6d763617',
                  'bfb82ee6-345a-44a4-84e1-d6706cc8b29d',
                  '8ba7a591-3923-4344-9f87-0588c6a1aba0',
                  '26b0f142-9419-41f1-9c13-3a2b62437f60',
                  '1b9aa074-9b04-4b5c-b30e-35bdfa0e0835',
                  'a7aaf947-f16c-489b-a10e-b48d03e0d209',
                  'b8bbf947-f16c-489b-a10e-b48d03e0d209',],
        'max': 20,
        'message': None
    },
    'Huge Missile Launchers': {
        'GUIDs': ['6fc05823-7905-4b5e-bde0-858010860e91',
                  '9bff4b97-c652-4da7-99df-ab4a1bd5551e',],
        'max': 2,
        'message': 'Huge missiles present, check module counts'
    },
    'Simple Weapons': {
        'GUIDs': ['7101e1cb-a501-49bd-8bbe-7a960881e72b',
                  '0aa0fa2e-1a85-4493-9c4c-0a69c385395d',
                  'aa070f63-c454-4f95-82fd-d946a32a1b66',
                  'c94e1719-bcc7-4c6a-8563-505fad2f9db9',
                  'b92a4ce6-ea93-4c0c-97d7-494ea611caa9',
                  '1217043c-e786-4555-ba24-46cd1f458bf9',
                  'f9f36cb3-cbfd-446a-9313-40f8e31e6e89',
                  '742f063f-d0fe-4f41-8717-a2c75c38d5e0',
                  '58305289-16ea-43cf-9144-2f23b383da81',
                  '3be0cab1-643b-4e3a-9f49-45995e4eb9fb',
                  'd8c5639a-ff5f-448e-a761-c2f69fac661a',
                  '268d79bf-c266-48ed-b01b-76c8d4d31c92',
                  '9b8657b9-c820-43a0-ad19-25ea45a100f1',
                  '2311e4db-a281-448f-ad53-0a6127573a96',
                  'e1d1bcae-f5e4-42bb-9781-6dde51b8e390',
                  '16b67fbc-25d5-4a35-a0df-4941e7abf6ef',
                  'd3e8e14a-58e7-4bdd-b1b3-0f37e4723a73',],
        'max': 20,
        'message': None
    },
    'Helium Pumps': {
        'GUIDs': ['0d466e68-7a97-4e27-a73c-6bda4010f7e7'],
        'max': 2,
        'message': None
    },
    'Lighting': {
        'GUIDs': ['c0afc8a9-5c49-4f15-8834-6e39ff144da3',
                  '87bd3e7e-16f0-4f0c-99b9-34ddfa032a87',
                  'f71f9cfc-a107-4404-bb2c-7dc30e10e8da',],
        'max': 10,
        'message': None
    },
    'Repair Bots': {
        'GUIDs': ['bf0db0d2-8582-41d2-bcfe-5299bec3d06b'],
        'max': 10,
        'message': None
    },
}

rotation_restrictions = {
    'Mortars': {
        'GUIDs': ['a97e03b0-e8da-49e2-9913-ad8c1826d869'],
        'max': 6,
        'banned_rotations': ['up'],
    },
    'Vertical Propulsion': {
        # props, steam props, steam jets, jet engines, cje controller/exhausts, ion thrusters
        'GUIDs': ['ceae02f9-2a21-40a0-b0d5-fdb0e4975826',
                  '3d03785a-21b9-42c7-8acb-17cf43de9d58',
                  'd43a0af4-69e3-4f28-a0fc-9d36b21273e2',
                  '6542630e-e790-4c24-9888-c949b4723ee4',
                  'bf008077-997c-4371-a116-57de7d351fe7',
                  '0c5a2ff0-a0bf-490d-8cd7-219d71a1b629',
                  '5373c818-c0e4-4cad-afc5-bed89f5236b4',
                  'a8dcd83f-ec5f-40fc-901e-0bf45a8e551b',
                  '3a59c6f8-59dc-4a12-8fd3-c509a9d84906',
                  '576e79a6-07e1-4485-903d-e5929d512c08',
                  '9710b923-9e8c-4762-aa74-bffefb263a7e',
                  '50626002-c1bc-41a3-ade6-ee83ba4c548a',
                  'b74c27c0-081a-45b7-8e81-cdd84ff33490',
                  'a70f015e-a9fe-45f1-958c-fc501ec7e2ea',
                  'b50989c9-03d4-4201-a8d4-459dcea86b05',
                  '3af2aa7c-86c8-47f5-896d-26d9622cdea8',
                  'b9fabb99-ff73-4018-8521-08441d2f18cf',
                  '35d7b71f-0247-4e73-8307-5199180d1cbb',
                  '89c3beb4-0fa3-4c3f-a065-7e53497cbe64',
                  'd62b91f6-8356-4fbc-8415-6405e04cba92',
                  'c7d3ffb8-3ceb-40ae-a2b0-69c1f4d59462',
                  '97ab0a32-c1c7-4663-a497-574fb15d9318',
                  '2b2d4fdc-8ffa-4399-985a-f9f5ec1263d0',
                  '1fb31e58-d0bf-4234-8e92-ae6e46869e55',
                  '0083a83e-a716-4c67-aa49-d14fbcd00248',
                  '02ea8321-aaff-4d03-8c50-20c241a82632',
                  '1d206e3b-4641-4002-9d3d-940036154408',
                  '2718d6ad-07a2-4d98-bd7e-9cdb2b3f70db',],
        'max': 0,
        'banned_rotations': ['up','down']
    },
    'Vertical Dediblades': {
        'GUIDs': ['564a75cd-8d7c-469b-a4b3-053d772b7d9d'],
        'max': 0,
        'banned_rotations': ['forward','back','left','right']
    },
}

subobject_limit = 20
max_cost = 1e6
max_volume = 2e5
max_length = 350
max_width = 250
max_height = 100

def check_bp(path):
    bp = Blueprint(path=path,gmap='guid_map.json')
    print('Analysing {}'.format(bp.bp['Name']))

    print('\nChecking build constraints...')
    errors = 0
    categories = bp.analyse(printstyle=None)
    if(categories['Totals']['cost']>max_cost):
        print('! Material budget exceeded: {:,.0f}/{:,.0f}'.format(categories['Totals']['cost'],max_cost))
        errors += 1
    else:
        print('  Material cost: {:,.0f}/{:,.0f}'.format(categories['Totals']['cost'],max_cost))
    if(categories['Totals']['volume']>max_volume):
        print('! Volume limit exceeded: {:,.0f}/{:,.0f}'.format(categories['Totals']['volume'],max_volume))
        errors += 1
    else:
        print('  Volume: {:,.0f}/{:,.0f}'.format(categories['Totals']['volume'],max_volume))
    min_coords = [int(c) for c in bp.bp['Blueprint']['MinCords'].split(',')]
    max_coords = [int(c) for c in bp.bp['Blueprint']['MaxCords'].split(',')]
    width = max_coords[0] - min_coords[0] + 1
    height = max_coords[1] - min_coords[1] + 2
    length = max_coords[2] - min_coords[2] + 1
    
    print('  Width: {}, Height: {}, Length: {}'.format(width, height, length))
    if(errors>0):
        print('Errors in section: {}'.format(errors))
    else:
        print('Section OK')

    print('\nChecking subobjects...')
    errors = 0
    sc_count = 0
    for sc in sc_iter(bp.bp['Blueprint']):
        sc_count += 1
    sc_count -= 1
    if( sc_count > len(bp.bp['Blueprint']['SCs']) ):
        print('! Subobject stacking detected!')
        errors += 1
    else:
        print('  No stacking detected')
    if( sc_count > subobject_limit ):
        print('! Subobject limit exceeded! {}/{}'.format(sc_count,subobject_limit))
        errors += 1
    else:
        print('  {}/{} subobjects used'.format(sc_count,subobject_limit))
    if(errors>0):
        print('Errors in section: {}'.format(errors))
    else:
        print('Section OK')

    print('\nChecking for banned blocks...')
    errors = 0
    for name, guid in banned_blocks.items():
        count = bp.get_block_count(guid)
        if(count>0):
            print('! Found {} {}!'.format(count,name))
            errors += 1
    if(errors>0):
        print('Found {} types of banned blocks!'.format(errors))
    else:
        print('Section OK')

    print('\nChecking for restricted blocks...')
    errors = 0
    for block_type in restricted_blocks:
        count = 0
        for guid in restricted_blocks[block_type]['GUIDs']:
            count += bp.get_block_count(guid)
        if(restricted_blocks[block_type]['message']!=None and count>0):
            print('- '+restricted_blocks[block_type]['message'])
        if(restricted_blocks[block_type]['max']>=0 and count>restricted_blocks[block_type]['max']):
                print('! Limit for {} exceeded! {}/{}'.format(block_type, count, restricted_blocks[block_type]['max']))
                errors += 1
    if(errors>0):
        print('Errors in section: {}'.format(errors))
    else:
        print('Section OK')

    print('\nChecking block rotations...')
    errors = 0
    for block_type in rotation_restrictions:
        count = 0
        for guid in rotation_restrictions[block_type]['GUIDs']:
            type_count = bp.get_block_count(guid)
            if(type_count>0):
                for sc in sc_iter(bp.bp['Blueprint']):
                    check_id = bp.to_id[guid]
                    sel = array(sc['BlockIds'])==check_id
                    rots = array(sc['BLR'])[sel]
                    for b_rots in rotation_restrictions[block_type]['banned_rotations']:
                        num = count_nonzero(in1d(rots, rotations[b_rots]))
                        count += num
                        if(num>0):
                            print('- {} bad rotations for {}'.format(count_nonzero(in1d(rots, rotations[b_rots])),bp.gmap[guid]['name']))
        if(rotation_restrictions[block_type]['max']>=0):
            if(count>rotation_restrictions[block_type]['max']):
                print('! Limit for {} exceeded! {}/{}'.format(block_type, count, rotation_restrictions[block_type]['max']))
                errors += 1
        else:
            if(count>0):
                print('- '+rotation_restrictions[block_type]['message'])
    if(errors>0):
        print('Errors in section: {}'.format(errors))
    else:
        print('Section OK')

# Execution begins
if(len(sys.argv)>1):
    path = Path(sys.argv[1])
else:
    path = Path('.')

if( path.is_file() ):
    check_bp(path)
elif( path.is_dir() ):
    for bp_file in path.glob('*.blueprint'):
        print('---\n')
        check_bp(bp_file)
else:
    print('Invalid path')
