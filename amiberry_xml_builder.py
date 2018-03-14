import sys
import lhafile
import os
from pathlib import Path

import hashlib
from whdload import whdload_slave
from slave_lha.parse_lha.read_lha import LhaSlaveArchive

from utils import text_utils

def sha1(fname):
    hash_sha1 = hashlib.sha1()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha1.update(chunk)
    return hash_sha1.hexdigest()


print()
print(
    text_utils.FontColours.BOLD + text_utils.FontColours.OKBLUE + "HoraceAndTheSpider and osvaldolove" + text_utils.FontColours.ENDC + "'s " + text_utils.FontColours.BOLD +
    "Amiberry XML Builder" + text_utils.FontColours.ENDC + text_utils.FontColours.OKGREEN + " (0.1)" + text_utils.FontColours.ENDC + " | " + "" +
    text_utils.FontColours.FAIL + "www.ultimateamiga.co.uk" + text_utils.FontColours.ENDC)
print()

hash_algorithm = 'SHA1'
input_directory = ("/Users/horaceandthespider/Documents/Geek/AmigaWHD_LHA/")
count = 1

XML= ""
XML = XML + "<whdbooter>" + chr(10)

for file2 in Path(input_directory + "/").glob('**/*.lha'):
    archive_path = str(file2)
    
    this_file = os.path.basename(archive_path)

    try:
            slave_archive = LhaSlaveArchive(archive_path, hash_algorithm)
    except FileNotFoundError:
            print_("" +
                   "Could not find LHA archive: {}".format(archive_path))
            sys.exit(1)
    except lhafile.BadLhafile:
            print_("" +
                   "Could not read LHA archive: {}".format(archive_path))
            sys.exit(1)

    print("Processing: " + text_utils.FontColours.OKBLUE + text_utils.FontColours.BOLD  + this_file + text_utils.FontColours.ENDC)
    print(text_utils.FontColours.OKGREEN + slave_archive.absolute_path + text_utils.FontColours.ENDC)
    print()
    
    slave_archive.read_lha()
    ArchiveSHA = sha1(file2)
    
    # From here, we need to process WHDLoad header information out of the slave files!
    for slave in slave_archive.slaves:
        slave.get_hash()
        print(text_utils.FontColours.BOLD + 'Slave Name: ', end='')
        print(slave.name)
        print( "{} Hash: ".format(slave.hasher.name.upper()), end='')
        print(slave.hash_digest + text_utils.FontColours.ENDC)


  #     we could work something out here later... but maybe it doesnt even matter here
  #     we can use the 'sub path' of slave.name to get the old UAE Config Maker folder name
        slave_path = os.path.dirname(slave.name)
        full_game_name = text_utils.make_full_name(slave_path)
        print(full_game_name)

        
  # where we have multiple slaves, we will set the requirements as the highest ones found
  # e.g. the one needing most memory etc

#	<hardware>
#PRIMARY_CONTROL=JOYSTICK
#PORT0=JOY
#PORT1=JOY
#SCREEN_HEIGHT=200
#SCREEN_Y_OFFSET=8
#FAST_RAM=1
#	</hardware>
#	<custom_controls>   check for a game name.controls  file
#	</custom_controls>
#</game>   

        last_slave = slave.name.replace(slave_path +"/","")
        print()
        # i assume we need to use slave.data here
#        this_slave = whdload_slave.WHDLoadSlaveFile(slave.data)
#       this_slave = whdload_slave.WHDLoadSlaveBase(slave.data)       
#       print (this_slave.name)

##generate XML
    print ("what did your last slave die of: " + last_slave)
    
    XML = XML + chr(9)+ '<game filename="' + this_file + '"  sha1="' + ArchiveSHA + ">" + chr(10)
    XML = XML + chr(9)+ chr(9) + '<name>' + full_game_name + '</name>' + chr(10)
    XML = XML + chr(9)+ chr(9) + '<slave_count>' + full_game_name + '</slave_count>' + chr(10)
    if len(slave_archive.slaves) == 1:
            XML = XML + chr(9)+ chr(9) + '<slave_default>' + last_slave + '</slave_default>' + chr(10)
    else:
            XML = XML + chr(9)+ chr(9) + '<slave_default>' + '</slave_default>' + chr(10)
    
    XML = XML + chr(9)+ chr(9) + '<name>' + full_game_name + '</name>' + chr(10)           
    XML = XML + chr(9)+ chr(9) + '<hardware>' + '</hardware>' + chr(10)
    XML = XML + chr(9)+ chr(9) + '<custom_controls>' + '</custom_controls>' + chr(10)
    
    XML = XML + chr(9)+ '</game>' + chr(10)
   
    # limit  it to a certian number of archives (for testing)
    if count == 5:
        break
    count = count + 1


XML = XML + "</whdbooter>" + chr(10)


print(XML)
