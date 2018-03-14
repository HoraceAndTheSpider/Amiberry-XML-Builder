import sys
import lhafile
import os
#import colorama
from slave_lha.parse_lha.read_lha import LhaSlaveArchive
from pathlib import Path

from utils import text_utils


print()
print(
    text_utils.FontColours.BOLD + text_utils.FontColours.OKBLUE + "HoraceAndTheSpider and osvaldolove" + text_utils.FontColours.ENDC + "'s " + text_utils.FontColours.BOLD +
    "Amiberry XML Builder" + text_utils.FontColours.ENDC + text_utils.FontColours.OKGREEN + " (0.1)" + text_utils.FontColours.ENDC + " | " + "" +
    text_utils.FontColours.FAIL + "www.ultimateamiga.co.uk" + text_utils.FontColours.ENDC)
print()

hash_algorithm = 'SHA1'
input_directory = ("/Users/horaceandthespider/Documents/Geek/AmigaWHD_LHA/")

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

    print(text_utils.FontColours.OKGREEN + slave_archive.absolute_path)
    slave_archive.read_lha()

    print (slave_archive.slaves.count)
    
    for slave in slave_archive.slaves:
        slave.get_hash()
        print(text_utils.FontColours.BOLD + 'Slave Name: ', end='')
        print(slave.name)
        print( "{} Hash: ".format(slave.hasher.name.upper()),
            end='')
        print(slave.hash_digest + text_utils.FontColours.ENDC)
