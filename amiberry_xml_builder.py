import sys
import lhafile
import os
from pathlib import Path
import math
import argparse
import hashlib
import openretroid
import datetime
import platform

import tempfile
from whdload import whdload_slave
from slave_lha.parse_lha.read_lha import LhaSlaveArchive

from utils import text_utils


def sha1(fname):
    hash_sha1 = hashlib.sha1()
    with open(str(fname), "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha1.update(chunk)
    return hash_sha1.hexdigest()


def value_list(in_file, game_name):
    file_name = "settings/" + in_file

    if os.path.isfile(file_name) is False:
        return ""

    with open(file_name) as f:
        content = f.readlines()
        content = [x.strip() for x in content]
    f.close()

    answer = ""

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
# main section starting here...

print()
print(
    text_utils.FontColours.BOLD + text_utils.FontColours.OKBLUE + "HoraceAndTheSpider and osvaldolove" + text_utils.FontColours.ENDC + "'s " + text_utils.FontColours.BOLD +
    "Amiberry XML Builder" + text_utils.FontColours.ENDC + text_utils.FontColours.OKGREEN + " (0.6)" + text_utils.FontColours.ENDC + " | " + "" +
    text_utils.FontColours.FAIL + "www.ultimateamiga.co.uk" + text_utils.FontColours.ENDC)
print()


parser = argparse.ArgumentParser(description='Create Amiberry XML for WHDLoad Packs.')

parser.add_argument('--scandir', '-s',                         # command line argument
                    help='Directories to Scan',
                    default='/home/pi/RetroPie/roms/amiga/'    # Default directory if none supplied
#                    default = "/media/MARVIN/Geek/WHDLoad/"
                    )

parser.add_argument('--refresh', '-n',                      # command line argument
                    action="store_true",                    # if argument present, store value as True otherwise False
                    help="Full XML refresh"
                    )

parser.add_argument('--forceinput', '-f',                  # command line argument
                    action="store_true",                    # if argument present, store value as True otherwise False
                    help="Force -S to be used on OSX, and ignore timecheck"
                    )

# Parse all command line arguments
args = parser.parse_args()

# Get the directories to scan (or default)
# yeah, i shouldnt do this, but i'm lazy, so i will.
if platform.system() == "Darwin" and args.forceinput != True:
        input_directory = "/Volumes/Macintosh HD/Users/horaceandthespider/Google Drive/Geek/Shared Pi Games/amiga/_Standard/"
else:
        input_directory = args.scandir

#input_directory = args.scandir

# Timecheck the original XML

#text_file = open("whdload_db.xml", "r")
#XML_OLD = text_file.read()
#text_file.close()

# set the name of the db file
whdbfile = 'whdload_db.xml'
      
# >> Setup Bool Constant for xml refresh
FULL_REFRESH  = args.refresh

hash_algorithm = 'SHA1'
count = 1

XML_HEADER= '<?xml version="1.0" encoding="UTF-8"?>' + chr(10)
XML_HEADER = XML_HEADER + '<whdbooter timestamp="' + datetime.datetime.now().strftime("%Y-%m-%d at %H:%M:%S") + '">' + chr(10)
XML_OLD = ""

if FULL_REFRESH == False:    
    text_file = open(whdbfile, "r")
    XML_OLD = text_file.read()
    text_file.close()

    a = XML_OLD.find("<whdbooter")
    for b in range(a , a+100):
        if XML_OLD[b]==">":
            break

    c = XML_OLD.find("</whdbooter")            

    XML_OLD = XML_OLD[b+2:c]
    # print(XML_OLD)
    
XML = ""
XML_FOOTER = "</whdbooter>" + chr(10)

ERROR_MSG    = 'Problem file log: ' + datetime.datetime.now().strftime("%Y-%m-%d at %H:%M:%S") + '' + chr(10)
COMPLETE_MSG = 'Scanned file log: ' + datetime.datetime.now().strftime("%Y-%m-%d at %H:%M:%S") + '' + chr(10)


for file2 in Path(input_directory + "/").glob('**/*.lha'):
    archive_path = str(file2)
    this_file = os.path.basename(archive_path)

    # check for a skip, and that its value for skipping
    if (FULL_REFRESH==False and XML_OLD.find('<game filename="' + this_file[0:len(this_file)-4].replace("&", "&amp;") + '"')>-1):        
        print("Skipping: " + text_utils.FontColours.OKBLUE + text_utils.FontColours.BOLD  + this_file + text_utils.FontColours.ENDC)
        COMPLETE_MSG = COMPLETE_MSG + "Skipped: " + this_file + chr(10)
    elif text_utils.left(this_file,2)=="._":
        ...
        count = count - 1
    else:
        print()
        print("Processing: " + text_utils.FontColours.FAIL + text_utils.FontColours.BOLD  + this_file + text_utils.FontColours.ENDC)
        
        try:
                slave_archive = LhaSlaveArchive(archive_path, hash_algorithm)
                file_details = openretroid.parse_file(archive_path)
                
                #print(text_utils.FontColours.OKGREEN + slave_archive.absolute_path + text_utils.FontColours.ENDC)

                
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
                SLAVE_XML=""
                first_slave=""
                UUID = ""
                n=1
                default_slave = ""
                default_slave_found = False
                
                UUID = file_details['uuid']                    
                print("Openretro URL: " + text_utils.FontColours.UNDERLINE + text_utils.FontColours.OKBLUE +  "http://www.openretro.org/game/{}".format(UUID) + text_utils.FontColours.ENDC)
                #print("Variant UUID: {}".format(file_details['uuid']))
                print()
                # we should get the default slave here, so that we only select it if it

                def_msg = ""
                
                # default slave
                default_slave = value_list("WHD_DefaultSlave.txt", text_utils.left(this_file,len(this_file) - 4))
                if default_slave != "":
                     def_msg = " (Lookup from list using File Name)"                               

                # From here, we need to process WHDLoad header information out of the slave files!
                for slave in slave_archive.slaves:
                    slave.get_hash()
                    print(text_utils.FontColours.BOLD + '  Slave Found: ', end='')
                    print(text_utils.FontColours.OKBLUE + slave.name + text_utils.FontColours.ENDC)
                    #print( "{} Hash: ".format(slave.hasher.name.upper()), end='')
                    #print(slave.hash_digest + text_utils.FontColours.ENDC)

                    if default_slave != "":
                        if  slave.name.find(default_slave) >0:
                            default_slave_found = True
                        
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

                    #print("check settings: "+sub_path)
                    if first_slave == "":
                        first_slave = slave.name.replace(slave_path +"/","")
                        
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
                            whd_chip_ram = temp_chip_ram
                            
                    # round up any wierd fastram values       
                    temp_fast_ram = this_slave.exp_mem/1048576
                    for i in range(0, 5):
                        low_ram = int(math.pow(2, i-1))
                        high_ram = int(math.pow(2, i )) 
                        if temp_fast_ram > low_ram and temp_fast_ram < high_ram:
                            temp_fast_ram = high_ram

                    # update the value if the highest slave requirement
                    whd_fast_ram = 0
                    if temp_fast_ram > HW_FAST:
                            whd_fast_ram = temp_fast_ram

                    # we use the name of the 'last' slave, if there is only one
                    last_slave = slave.name.replace(slave_path +"/","")

                    SLAVE_XML = SLAVE_XML + chr(9)+ chr(9)+ '<slave number="' + str(n) + '">' + chr(10)
                    SLAVE_XML = SLAVE_XML + chr(9)+ chr(9)+ chr(9) + '<filename>' + (slave.name.replace(slave_path +"/","")).replace("&", "&amp;") + '</filename>' + chr(10)
                    SLAVE_XML = SLAVE_XML + chr(9)+ chr(9)+ chr(9) + '<datapath>' + (this_slave.current_dir).replace("&", "&amp;") + '</datapath>' + chr(10)
                    if (this_slave.config) is not None:
                        SLAVE_XML = SLAVE_XML + chr(9)+ chr(9)+ chr(9) + '<custom>'  + chr(10)

                        for configs in this_slave.config:
                            if configs is not None:
                                SLAVE_XML = SLAVE_XML + chr(9)+ chr(9)+ chr(9) + ((configs.replace("<","")).replace(">","")).replace("&", "&amp;") + chr(10)


                        SLAVE_XML = SLAVE_XML + chr(9)+ chr(9)+ chr(9) + '</custom>'  + chr(10)
                        
                    SLAVE_XML = SLAVE_XML + chr(9)+ chr(9)+ '</slave>'  + chr(10)

                    n=n+1
                    
                    
                # end of slave checking

                print()
                print("Game name: " + text_utils.FontColours.HEADER + full_game_name + text_utils.FontColours.ENDC)
                print("Lookup Name: " + text_utils.FontColours.HEADER + sub_path + text_utils.FontColours.ENDC)
                
                # resurn of the default slave!
                if default_slave_found == False:
                        default_slave = ""
                        
                if len(slave_archive.slaves) == 1 and default_slave=="":
                        default_slave = last_slave
                        def_msg = " (Only slave in archive search)"

                elif default_slave=="":
                        default_slave = first_slave
                        def_msg = " (First slave in archive search)"
                        
                print("Default Slave: " + text_utils.FontColours.HEADER + default_slave + text_utils.FontColours.WARNING + def_msg + text_utils.FontColours.ENDC)

                # get what settings we can, based on the name lookup in old Config Maker Files

                # ======== DISPLAY SETTINGS =======

                # prior to Amiberry 3.2 possible heights { 200, 216, 224, 240, 256, 262, 270 };
                # since 3.2 => heights { 400, 432, 448, 480, 512, 524, 540 };
                listheights = ['400', '432', '448', '480', '512', '524', '540']
                HW_HEIGHT = ''

                for possibleheight in listheights:
                    if check_list('Screen_Height_'+possibleheight+'.txt', sub_path) is True:
                        HW_HEIGHT = possibleheight
                        break

                # screen widths  { 320, 352, 384, 640, 704, 720, 768 };
                listwidths = ['320', '352', '384', '640', '704', '720', '768']
                HW_WIDTH = ''

                for possiblewidth in listwidths:
                    if check_list('Screen_Width_'+possiblewidth+'.txt', sub_path) is True:
                        HW_WIDTH = possiblewidth
                        break

                # screen centering
                HW_H_CENTER = 'SMART'
                if check_list('Screen_NoCenter_H.txt', sub_path) is True:
                  HW_H_CENTER = 'NONE'

                HW_V_CENTER = 'SMART'
                if check_list('Screen_NoCenter_V.txt', sub_path) is True:
                  HW_V_CENTER = 'NONE'
                                
                # auto centering
                HW_AUTO_HEIGHT = 'FALSE'
                if check_list('Screen_AutoHeight.txt', sub_path) is True or HW_HEIGHT == "":
                    HW_AUTO_HEIGHT = 'TRUE'

                # extras
                HW_NTSC = ""
                if check_list("Screen_ForceNTSC.txt", sub_path) is True:
                     HW_NTSC = "TRUE"       
                elif this_file.find("NTSC") > -1:
                     HW_NTSC = "TRUE" 
                            

                # ======== CONTROL SETTINGS =======
                #  mouse / mouse 2 / CD32

                use_mouse1 = check_list("Control_Port0_Mouse.txt", sub_path)
                use_mouse2 = check_list("Control_Port1_Mouse.txt", sub_path)
                use_cd32_pad = check_list("Control_CD32.txt", sub_path)

                # quick clean-up on WHDLoad memory requirements
                whd_z3_ram = 0

                if whd_fast_ram>8:
                    whd_z3_ram = whd_fast_ram
                    whd_fast_ram = 0

                chip_ram = 2
                fast_ram = 8
               
                
                old_chip_ram = chip_ram
                for i in range(0, 4):
                    chip_ram = int(math.pow(2, i)) / 2
                    if chip_ram >= 1:
                                    chip_ram = int(chip_ram)

                    if check_list("Memory_ChipRam_" + str(chip_ram) + ".txt", sub_path) is True:
                                    chip_ram = int(chip_ram * 2)
                                    break
                    chip_ram = old_chip_ram
                    # whd chip-memory overwrite
                if whd_chip_ram >= chip_ram: chip_ram = whd_chip_ram


                # ' ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                # ' when we want different fast ram!!
                # No longer required as of Amiberry 5.0 | Default is 8Mb of fast RAM.

                old_fast_ram = fast_ram
                for i in range(0, 4):
                    fast_ram = int(math.pow(2, i))
                    if check_list("Memory_FastRam_" + str(fast_ram) + ".txt", sub_path) is True:
                        break
                    fast_ram = old_fast_ram

                # whd fast-memory overwrite
                if whd_fast_ram >= fast_ram and whd_fast_ram <= 8 : fast_ram = whd_fast_ram

                # ' ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                # ' when we want different Z3 ram!!

                for i in range(0, 8):
                    z3_ram = int(math.pow(2, i))
                    if check_list("Memory_Z3Ram_" + str(z3_ram) + ".txt", sub_path) is True:
                        break
                    z3_ram = 0

                    # whd z3-memory overwrite
                if whd_fast_ram >= z3_ram and whd_fast_ram > 8 : z3_ram = whd_chip_ram


                # '======== CHIPSET SETTINGS =======
                # ' ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                # ' sprite collisions

                HW_SPRITES = ""
                if check_list("Chipset_CollisionLevel_full.txt", sub_path) is True:
                                HW_SPRITES = "FULL"
                if check_list("Chipset_CollisionLevel_none.txt", sub_path) is True:
                                HW_SPRITES = "NONE"
                if check_list("Chipset_CollisionLevel_playfields.txt", sub_path) is True:
                                HW_SPRITES = "PLAYFIELDS"
                if check_list("Chipset_CollisionLevel_sprites.txt", sub_path) is True:
                                HW_SPRITES = "SPRITES"

                # ' blitter    
                HW_BLITS = ""        
                if check_list("Chipset_ImmediateBlitter.txt", sub_path) is True:
                    HW_BLITS = "IMMEDIATE"
                if  check_list("Chipset_NormalBlitter.txt", sub_path) is True:
                    HW_BLITS = "NORMAL"
                if  check_list("Chipset_WaitBlitter.txt", sub_path) is True:
                    HW_BLITS = "WAIT"

                # copper
                HW_FASTCOPPER = "FALSE"
                if check_list("Chipset_FastCopper.txt", sub_path) is True:
                    HW_FASTCOPPER = "TRUE"


                # '======== CPU SETTINGS =======
                # ' ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

                # ' max emu speed
                HW_SPEED = ""
                if check_list("CPU_MaxSpeed.txt", sub_path) is True:
                                HW_SPEED = "MAX"
                if check_list("CPU_RealSpeed.txt", sub_path) is True:
                                HW_SPEED = "REAL"
                # ' clock speed
                if check_list("CPU_ClockSpeed_7.txt", sub_path) is True:
                                HW_SPEED = "7"
                if check_list("CPU_ClockSpeed_14.txt", sub_path) is True:
                                HW_SPEED = "14"
                if check_list("CPU_ClockSpeed_25.txt", sub_path) is True:
                                HW_SPEED = "25"


                HW_CPU = ""
                # ' cpu model 68000
                if check_list("CPU_68000.txt", sub_path) is True:
                                HW_CPU = "68000"
                                
                # ' cpu model 68010
                if check_list("CPU_68010.txt", sub_path) is True:
                                HW_CPU = "68010"
                                HW_24BIT = "FALSE"
                                
                # ' cpu model 68040
                if check_list("CPU_68040.txt", sub_path) is True:
                                HW_CPU = "68040"
                                HW_24BIT = "FALSE"

                # ' 24 bit addressing 
                HW_24BIT = ""
                if not check_list("CPU_No24BitAddress.txt", sub_path) is False:
                    HW_24BIT = "FALSE"
             
                # compatible CPU 
                HW_CPUCOMP = ""
                if check_list("CPU_Compatible.txt", sub_path) is True:
                    HW_CPUCOMP = "TRUE"
                    
                # cycle_exact = check_list("CPU_CycleExact.txt", sub_path)

                # JIT Cache
                # when JIT is True to prevent a bug Z2 must be set to 0
                # hence we need to set some Z3 (if not already set).
                HW_JIT = "FALSE"
                if check_list("CPU_ForceJIT.txt",sub_path) == True:
                    #HW_SPEED = 'MAX'
                    HW_JIT = 'TRUE'
                    fast_ram = 0
                    if z3_ram == 0 or z3_ram == '':
                        z3_ram = 16

                # CHIPSET
                HW_CHIPSET = ""
                if check_list("CPU_ForceAGA.txt",sub_path) == True:
                        HW_CHIPSET = "AGA"
                elif check_list("CPU_ForceECS.txt", sub_path) == True:
                        HW_CHIPSET = "ECS"  
                elif check_list("CPU_ForceOCS.txt", sub_path) == True:
                        HW_CHIPSET = "OCS"  

                if this_file.find("_AGA") > -1:
                        HW_CHIPSET = "AGA"                                       
                if this_file.find("_CD32") > -1:
                        HW_CHIPSET = "AGA"
                        use_cd32_pad = True



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

             #   hardware += ("PRIMARY_CONTROL=MOUSE") + chr(10)

                if HW_FASTCOPPER != "":
                    hardware += ("FAST_COPPER=") + HW_FASTCOPPER + chr(10)

                if HW_BLITS != "":
                    hardware += ("BLITTER=") + HW_BLITS + chr(10)

                if HW_SPRITES != "":
                    hardware += ("SPRITES=") + HW_CPU + chr(10)
                    
                if HW_24BIT != "":
                    hardware += ("CPU_24BITADDRESSING=") + HW_24BIT + chr(10)

                if HW_CPUCOMP != "":
                    hardware += ("CPU_COMPATIBLE=") + HW_CPUCOMP + chr(10)

                if HW_CPU != "":
                    hardware += ("CPU=") + HW_CPU + chr(10)
                
                if HW_JIT != "":
                    hardware += ("JIT=") + HW_JIT + chr(10)

                if HW_SPEED != "":
                    hardware += ("CLOCK=") + HW_SPEED + chr(10)

                if HW_CHIPSET != "":
                    hardware += ("CHIPSET=") + HW_CHIPSET + chr(10)
                    
                if HW_NTSC != "":
                    hardware += ("NTSC=") + HW_NTSC + chr(10)

                # SCREEN OPTIONS
                if HW_AUTO_HEIGHT == 'FALSE':
                    hardware += ('SCREEN_AUTOHEIGHT=') + HW_AUTO_HEIGHT + chr(10)
                    hardware += ('SCREEN_HEIGHT=') + HW_HEIGHT + chr(10)
                else:
                    hardware += ('SCREEN_AUTOHEIGHT=') + HW_AUTO_HEIGHT + chr(10)

                if HW_WIDTH != "":
                    hardware += ("SCREEN_WIDTH=") + HW_WIDTH + chr(10)

                if HW_H_CENTER != '':
                    hardware += ('SCREEN_CENTERH=') + HW_H_CENTER + chr(10)

                if HW_V_CENTER != '':
                    hardware += ('SCREEN_CENTERV=') + HW_V_CENTER + chr(10)


                # MEMORY OPTIONS

                if chip_ram != 2:
                    hardware += ("CHIP_RAM=") + str(chip_ram) + chr(10)

                if fast_ram != 8:
                    hardware += ("FAST_RAM=") + str(fast_ram) + chr(10)

                if z3_ram != 0:
                    hardware += ("Z3_RAM=") + str(z3_ram) + chr(10)

                    
                # custom controls
                custom_file = "customcontrols/" + full_game_name + ".controls"
                custom_text = ""
                                
                # remove any items which are not amiberry custom settings
                if os.path.isfile(custom_file) == True:
                    with open(custom_file) as f:
                        content = f.readlines()
                    f.close()
                                    
                    for this_line in content:
                      if this_line.find('amiberry_custom') > -1 and '\n' in this_line:
                        custom_text += chr(9) + chr(9) + this_line
                      elif this_line.find('amiberry_custom') > -1 and not '\n' in this_line:
                        custom_text += chr(9) + chr(9) + this_line + chr(10)

                # 
                extra_libs = "False"
                if check_list("WHD_Libraries.txt", sub_path) is True:
                    extra_libs = "True"

                COMPLETE_MSG = COMPLETE_MSG + "Scanned: " + full_game_name + chr(10)
                ##generate XML
                
                
                XML = XML + chr(9)+ '<game filename="' + text_utils.left(this_file,len(this_file) - 4).replace("&", "&amp;") + '"  sha1="' + ArchiveSHA + '">' + chr(10)
                XML = XML + chr(9)+ chr(9) + '<name>' + full_game_name.replace("&", "&amp;") + '</name>' + chr(10)
                XML = XML + chr(9)+ chr(9) + '<subpath>' + sub_path.replace("&", "&amp;") + '</subpath>' + chr(10)
                XML = XML + chr(9)+ chr(9) + '<variant_uuid>' + UUID + '</variant_uuid>' + chr(10)
                XML = XML + chr(9)+ chr(9) + '<slave_count>' + str(len(slave_archive.slaves)) + '</slave_count>' + chr(10)
                XML = XML + chr(9)+ chr(9) + '<slave_default>' + default_slave.replace("&", "&amp;")  + '</slave_default>' + chr(10)
                XML = XML + chr(9)+ chr(9) + '<slave_libraries>' + extra_libs  + '</slave_libraries>' + chr(10)
                XML = XML + SLAVE_XML
                XML = XML + chr(9)  + chr(9) + '<hardware>'
                XML = XML + chr(10) + chr(9) + chr(9) + hardware.replace(chr(10), chr(10) + chr(9) + chr(9) )
                XML = XML + chr(10) + chr(9) + chr(9) + '</hardware>' + chr(10)


                if len(custom_text)>0:
                    XML = XML + chr(9)+ chr(9) + '<custom_controls>' + chr(10) + custom_text  + chr(9) + chr(9) + '</custom_controls>' + chr(10)
                
                XML = XML + chr(9)+ '</game>' + chr(10)

        except FileNotFoundError:
                print("Could not find LHA archive: {}".format(archive_path))
                ERROR_MSG = ERROR_MSG + "Could not find LHA archive: {}".format(this_file)  + chr(10)
                #sys.exit(1)
                
        except lhafile.BadLhafile:
                print("Could not read LHA archive: {}".format(archive_path))
                ERROR_MSG = ERROR_MSG + "Could not read LHA archive: {}".format(this_file)  + chr(10) 
                #sys.exit(1)
        except KeyboardInterrupt:
                print()
                print("User Abort")
                break
        except:
                print("Something went wrong with LHA archive: {}".format(archive_path))
                ERROR_MSG = ERROR_MSG + "Could not read LHA archive: {}".format(this_file)  + chr(10) 
       
    # limit  it to a certian number of archives (for testing)
    if count >= 99999:
        break
    count = count + 1

XML = XML_HEADER + XML_OLD + XML + XML_FOOTER

#print(XML)
print("Generating XML File")
text_file = open(whdbfile, "w+")
text_file.write(XML)
text_file.close()

######
# no more offsetX/Y related lines and remove anythig else specified like blank lines
offtext = ['FAST_RAM=8', 'SCREEN_X_OFFSET=', 'SCREEN_Y_OFFSET=', '\t\t\n']

with open(whdbfile, 'r') as nomoreoffset:
    olines = nomoreoffset.readlines()

with open(whdbfile, 'w') as nomoreoffset:
    for line in olines:
        if not any(offset in line for offset in offtext) and all(ord(ch) < 128 for ch in line): #also ensure only ASCII character
            nomoreoffset.write(line)
#
######

text_file = open("files_scanned.txt", "w+")
text_file.write(COMPLETE_MSG)
text_file.close()

##if ERROR_MSG != "":
text_file = open("files_failed.txt", "w+")
text_file.write(ERROR_MSG)
text_file.close()
