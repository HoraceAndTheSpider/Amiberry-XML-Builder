import sys
import lhafile
import os
from pathlib import Path
import math

import hashlib
import tempfile
from whdload import whdload_slave
from slave_lha.parse_lha.read_lha import LhaSlaveArchive

from utils import text_utils

def sha1(fname):
    hash_sha1 = hashlib.sha1()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha1.update(chunk)
    return hash_sha1.hexdigest()


def value_list(in_file, game_name):
    file_name = "settings/" + in_file

    if os.path.isfile(file_name) is False:
        return 0

    with open(file_name) as f:
        content = f.readlines()
        content = [x.strip() for x in content]
    f.close()

    answer = 0

    for this_line in content:
        if not this_line == "":
            this_word = this_line.split()
            if this_word[0] == game_name:
                answer = this_word[1]
                break

    return answer

def check_list(in_file, game_name):

    temp_game = game_name

    if text_utils.right(temp_game.lower(),4) == ".iso" or text_utils.right(temp_game.lower(),4) == ".cue":
        temp_game = text_utils.left(temp_game,len(temp_game)-4)
        
    if text_utils.right(temp_game.lower(),4) == ".adf" or text_utils.right(temp_game.lower(),4) == ".hdf":
        temp_game = text_utils.left(temp_game,len(temp_game)-4)
    
    file_name = "settings/" + in_file

    if os.path.isfile(file_name) is False:
        return False

    with open(file_name) as f:
        content = f.readlines()
        content = [x.strip() for x in content]
    f.close()

    answer = False

    for this_line in content:
        if this_line == temp_game:
            answer = True
            break

    return answer


# =======================================

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


    # Defaults
    HW_CHIPSET = "ECS"
    HW_PROCESSOR = "68020"
    HW_SPEED = "7"
    HW_CHIP = .5
    HW_FAST = 0
    HW_Z3 = 0
    
    hardware = ""
    
    # From here, we need to process WHDLoad header information out of the slave files!
    for slave in slave_archive.slaves:
        slave.get_hash()
        print(text_utils.FontColours.BOLD + 'Slave Name: ', end='')
        print(slave.name)
        print( "{} Hash: ".format(slave.hasher.name.upper()), end='')
        print(slave.hash_digest + text_utils.FontColours.ENDC)

    # extract the slave as a temp file
        fp = tempfile.NamedTemporaryFile()
        fp.write(slave.data)
        fp.seek(0)
        this_slave = whdload_slave.whdload_factory(fp.name)
        fp.close()

        
  #     we could work something out here later... but maybe it doesnt even matter here
  #     we can use the 'sub path' of slave.name to get the old UAE Config Maker folder name
        slave_path = os.path.dirname(slave.name)
        sub_path = text_utils.left(slave.name,len(slave_path) - len(slave.name))        
        full_game_name = text_utils.make_full_name(sub_path)
        print("Game name: "+ full_game_name)


    # Extract H/W settings from the slaves
        for slave_flag in this_slave.flags:
            #print(slave_flag)
            if slave_flag == "Req68020":
                HW_PROCESSOR = "68020"
                
            if slave_flag == "ReqAGA":
                HW_CHIPSET = "AGA"
                HW_SPEED = "14"

  # where we have multiple slaves, we will set the requirements as the highest ones found
  # e.g. the one needing most memory etc

        # round up any wierd chipram values       
        temp_chip_ram = this_slave.base_mem_size/1048576
        for i in range(0, 2):
            low_ram = int(math.pow(2, i-1))
            high_ram = int(math.pow(2, i ))           
            if temp_chip_ram > low_ram and temp_chip_ram < high_ram:
                temp_chip_ram = high_ram

        # update the value if the highest slave requirement
        if temp_chip_ram > HW_CHIP:
                HW_CHIP = temp_chip_ram
                
        # round up any wierd fastram values       
        temp_fast_ram = this_slave.exp_mem/1048576
        for i in range(0, 5):
            low_ram = int(math.pow(2, i-1))
            high_ram = int(math.pow(2, i )) 
            if temp_fast_ram > low_ram and temp_fast_ram < high_ram:
                temp_fast_ram = high_ram

        # update the value if the highest slave requirement
        if temp_fast_ram > HW_FAST:
                HW_FAST = temp_fast_ram

        # we use the name of the 'last' slave, if there is only one
        last_slave = slave.name.replace(slave_path +"/","")
        print()



    
    # get what settings we can, based on the name lookup in old Config Maker Files


    # ' ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #


    # '======== DISPLAY SETTINGS =======
    # ' ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ' screen Y/X Offsets

    screen_offset_y = value_list("Screen_OffsetY.txt", this_file)
    screen_offset_x = value_list("Screen_OffsetX.txt", this_file)

    # ' screen heights
    screen_height = 240
    if check_list("Screen_Height_270.txt", sub_path) is True:
                    screen_height = 270
    if check_list("Screen_Height_262.txt", sub_path) is True:
                    screen_height = 262
    if check_list("Screen_Height_256.txt", sub_path) is True:
                    screen_height = 256
    if check_list("Screen_Height_240.txt", sub_path) is True:
                    screen_height = 240
    if check_list("Screen_Height_224.txt", sub_path) is True:
                    screen_height = 224
    if check_list("Screen_Height_216.txt", sub_path) is True:
                    screen_height = 216
    if check_list("Screen_Height_200.txt", sub_path) is True:
                    screen_height = 200

    # ' extras
    use_ntsc = check_list("Screen_ForceNTSC.txt", sub_path)
                
    # '======== CONTROL SETTINGS =======
    # ' ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ' mouse / mouse 2 / CD32

    use_mouse1 = check_list("Control_Port0_Mouse.txt", sub_path)
    use_mouse2 = check_list("Control_Port1_Mouse.txt", sub_path)
    use_cd32_pad = check_list("Control_CD32.txt", sub_path)


    print (use_mouse1)
    
    # quick clean-up on memory requirements
    HW_Z3 = 0        
    if HW_FAST>8:
        HW_Z3 = HW_FAST
        HW_FAST = 0



##;FAST_COPPER=TRUE
##;CPU=68000/68010/68020/68040
##;BLITTER=IMMEDIATE/WAIT/NORMAL
##;CLOCK=7/14/28/FASTEST/TURBO
##;CHIPSET=OCS/ECS/AGA
##;JIT=TRUE
##;CPU_COMPATIBLE=TRUE
##;SPRITES=NONE/PLAYFIELDS/SPRITES/FULL
##;SCREEN_HEIGHT=200
##;SCREEN_Y_OFFSET=0
##;NTSC=TRUE
##;CHIP_RAM=0.5/1/2
##;FAST_RAM=1/2/4/8/16/32
##;Z3_RAM=16/32/64/128


    # ================================
    # building the hardware section
    if use_mouse1 == True:
        hardware += ("PRIMARY_CONTROL=MOUSE") + chr(10)
    else:
        hardware += ("PRIMARY_CONTROL=JOYSTICK")  + chr(10)       

    # building the hardware section
    if use_mouse1 == True:
        hardware += ("PORT0=MOUSE") + chr(10)
    elif use_cd32_pad == True:
        hardware += ("PORT0=CD32") + chr(10)
    else:
        hardware += ("PORT0=JOY")  + chr(10)       

    if use_mouse2 == True:
        hardware += ("PORT1=MOUSE") + chr(10)
    elif use_cd32_pad == True:
        hardware += ("PORT1=CD32")  + chr(10)       
    else:
        hardware += ("PORT1=JOY")  + chr(10)      



 #   hardware += ("FAST_RAM="+str())
 #   hardware += ("Z3_RAM="+)
    
    # custom controls
    custom_file = "customcontrols/" + full_game_name + ".controls"
    custom_text = ""
                    
    if os.path.isfile(custom_file) == True:

    # remove any items which are not amiberry custom settings
        with open(custom_file) as f:
            content = f.readlines()
        f.close()
                        
        for this_line in content:
            if this_line.find("amiberry_custom") > -1:
                custom_text += this_line


    ##generate XML
    
    XML = XML + chr(9)+ '<game filename="' + text_utils.left(this_file,len(this_file) - 4) + '"  sha1="' + ArchiveSHA + '">' + chr(10)
    XML = XML + chr(9)+ chr(9) + '<name>' + full_game_name + '</name>' + chr(10)
    XML = XML + chr(9)+ chr(9) + '<slave_count>' + full_game_name + '</slave_count>' + chr(10)
    if len(slave_archive.slaves) == 1:
            XML = XML + chr(9)+ chr(9) + '<slave_default>' + last_slave + '</slave_default>' + chr(10)
    else:
            XML = XML + chr(9)+ chr(9) + '<slave_default>' + '</slave_default>' + chr(10)
    
    XML = XML + chr(9)+ chr(9) + '<name>' + full_game_name + '</name>' + chr(10)           
    XML = XML + chr(9)+ chr(9) + '<hardware>' + chr(10) + hardware  + chr(10) + chr(9) + chr(9) + '</hardware>' + chr(10)
    XML = XML + chr(9)+ chr(9) + '<custom_controls>' + chr(10) + custom_text  + chr(10) + chr(9) + chr(9) + '</custom_controls>' + chr(10)
    
    XML = XML + chr(9)+ '</game>' + chr(10)
   
    # limit  it to a certian number of archives (for testing)
    if count == 999999:
        break
    count = count + 1


XML = XML + "</whdbooter>" + chr(10)


#print(XML)
text_file = open("whdload_db.xml", "w+")
text_file.write(XML)
text_file.close()
