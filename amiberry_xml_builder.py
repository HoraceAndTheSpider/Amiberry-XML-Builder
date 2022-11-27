import argparse
import datetime
import hashlib
import lhafile
import math
import openretroid
import os
from pathlib import Path
import platform
from slave_lha.parse_lha.read_lha import LhaSlaveArchive
import sys
import tempfile
from utils import text_utils
from whdload import whdload_slave
import xml.etree.ElementTree as etree

# =======================================
# Functions
# =======================================
def sha1(fname):
    hash_sha1 = hashlib.sha1()
    with open(str(fname), "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha1.update(chunk)
    return hash_sha1.hexdigest()

# Get a value from a file
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

# Ensure a game package is set within a file
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
# Variables definition
# =======================================
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

# set the name of the db file
whdbfile = 'whdload_db.xml'

# Setup Bool Constant for xml refresh
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

XML = ""
XML_FOOTER = "</whdbooter>" + chr(10)

# Reports
ERROR_MSG    = 'Problem file log: ' + datetime.datetime.now().strftime("%Y-%m-%d at %H:%M:%S") + '' + chr(10)
COMPLETE_MSG = 'Scanned file log: ' + datetime.datetime.now().strftime("%Y-%m-%d at %H:%M:%S") + '' + chr(10)

# =======================================
# main section starts here...
# =======================================
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
                print()

                # default slave
                def_msg = ""
                default_slave = value_list("WHD_DefaultSlave.txt", text_utils.left(this_file,len(this_file) - 4))
                if default_slave != "":
                     def_msg = " (Lookup from list using File Name)"

                # From here, we need to process WHDLoad header information out of the slave files!
                for slave in slave_archive.slaves:
                    slave.get_hash()
                    print(text_utils.FontColours.BOLD + '  Slave Found: ', end='')
                    print(text_utils.FontColours.OKBLUE + slave.name + text_utils.FontColours.ENDC)

                    if default_slave != "":
                        if  slave.name.find(default_slave) >0:
                            default_slave_found = True

                    # extract the slave as a temp file
                    fp = tempfile.NamedTemporaryFile()
                    fp.write(slave.data)
                    fp.seek(0)
                    this_slave = whdload_slave.whdload_factory(fp.name)
                    fp.close()

                    # we could work something out here later... but maybe it doesnt even matter here
                    # we can use the 'sub path' of slave.name to get the old UAE Config Maker folder name
                    slave_path = os.path.dirname(slave.name)
                    sub_path = text_utils.left(slave.name,len(slave_path) - len(slave.name))
                    full_game_name = text_utils.make_full_name(sub_path)

                    if first_slave == "":
                        first_slave = slave.name.replace(slave_path +"/","")

                    # Extract H/W settings from the slaves
                    for slave_flag in this_slave.flags:
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

                    SLAVE_XML += chr(9)+ chr(9)+ '<slave number="' + str(n) + '">' + chr(10)
                    SLAVE_XML += chr(9)+ chr(9)+ chr(9) + '<filename>' + (slave.name.replace(slave_path +"/","")).replace("&", "&amp;") + '</filename>' + chr(10)
                    SLAVE_XML += chr(9)+ chr(9)+ chr(9) + '<datapath>' + (this_slave.current_dir).replace("&", "&amp;") + '</datapath>' + chr(10)
                    if (this_slave.config) is not None:
                        SLAVE_XML += chr(9)+ chr(9)+ chr(9) + '<custom>'  + chr(10)

                        for configs in this_slave.config:
                            if configs is not None:
                                SLAVE_XML += chr(9)+ chr(9)+ chr(9) + ((configs.replace("<","")).replace(">","")).replace("&", "&amp;") + chr(10)

                        SLAVE_XML += chr(9)+ chr(9)+ chr(9) + '</custom>'  + chr(10)

                    SLAVE_XML += chr(9)+ chr(9)+ '</slave>'  + chr(10)

                    n=n+1
                # end of slave checking

                print()
                print("Game name: " + text_utils.FontColours.HEADER + full_game_name + text_utils.FontColours.ENDC)
                print("Lookup Name: " + text_utils.FontColours.HEADER + sub_path + text_utils.FontColours.ENDC)

                # return of the default slave!
                if default_slave_found == False:
                        default_slave = ""

                if len(slave_archive.slaves) == 1 and default_slave=="":
                        default_slave = last_slave
                        def_msg = " (Only slave in archive search)"

                elif default_slave=="":
                        default_slave = first_slave
                        def_msg = " (First slave in archive search)"

                print("Default Slave: " + text_utils.FontColours.HEADER + default_slave + text_utils.FontColours.WARNING + def_msg + text_utils.FontColours.ENDC)

                # =======================================
                # DISPLAY SETTINGS

                # Amiberry 3.2+: HEIGHT can be any value yet let's stick to the following
                # values to keep things tidy and easy to maintain.
                # Possible values: 400, 432, 480, 512, 524, 540, 568
                # default: AUTOHEIGHT
                listheights = ['400', '432', '480', '512', '524', '540', '568']
                HW_HEIGHT = ''

                for possibleheight in listheights:
                    if check_list('Screen_Height_'+possibleheight+'.txt', sub_path) is True:
                        HW_HEIGHT = possibleheight
                        break

                # Amiberry 3.2+: WIDTH can be any value yet let's stick to the following
                # values to keep things tidy and easy to maintain.
                # Possible values: 640, 704, 720
                # default: 720
                listwidths = ['640', '704']
                HW_WIDTH = '720'

                for possiblewidth in listwidths:
                    if check_list('Screen_Width_'+possiblewidth+'.txt', sub_path) is True:
                        HW_WIDTH = possiblewidth
                        break

                # centering
                # default: enabled
                HW_H_CENTER = 'SMART'
                if check_list('Screen_NoCenter_H.txt', sub_path) is True:
                  HW_H_CENTER = 'NONE'

                HW_V_CENTER = 'SMART'
                if check_list('Screen_NoCenter_V.txt', sub_path) is True:
                  HW_V_CENTER = 'NONE'
                                
                # offset
                # default: 0 (for both horizontal and vertical)
                offset_h = value_list("Screen_Offset_H.txt", sub_path)
                offset_v = value_list("Screen_Offset_V.txt", sub_path)

                min_offset_h = -60
                max_offset_h = 60

                if offset_h.lstrip('-').isnumeric():
                    HW_H_OFFSET = int(offset_h)
                    if min_offset_h <= HW_H_OFFSET <= max_offset_h:
                        pass
                    elif HW_H_OFFSET < min_offset_h:
                        HW_H_OFFSET = min_offset_h
                    elif HW_H_OFFSET > max_offset_h:
                        HW_H_OFFSET = max_offset_h
                else:
                    HW_H_OFFSET = ''

                min_offset_v = -20
                max_offset_v = 20

                if offset_v.lstrip('-').isnumeric():
                    HW_V_OFFSET = int(offset_v)
                    if min_offset_v <= HW_V_OFFSET <= max_offset_v:
                        pass
                    elif HW_V_OFFSET < min_offset_v:
                        HW_V_OFFSET = min_offset_v
                    elif HW_V_OFFSET > max_offset_v:
                        HW_V_OFFSET = max_offset_v
                else:
                    HW_V_OFFSET = ''

                # NTSC
                HW_NTSC = ""
                if check_list("Screen_ForceNTSC.txt", sub_path) is True:
                     HW_NTSC = "TRUE"       
                elif this_file.find("NTSC") > -1:
                     HW_NTSC = "TRUE" 
                            
                # =======================================
                # CONTROL SETTINGS
                #  mouse / mouse 2 / CD32

                use_mouse1 = check_list("Control_Port0_Mouse.txt", sub_path)
                use_mouse2 = check_list("Control_Port1_Mouse.txt", sub_path)
                use_cd32_pad = check_list("Control_CD32.txt", sub_path)

                # =======================================
                # MEMORY SETTINGS
                # Let's limit possible Z3 values to 128Mb.
                # Amiberry 5+: 8Mb of fast RAM/Z2 set as default
                # Default: 2Mb Chip / 8Mb Z2 / 0Mb Z3

                for i in range(0, 8):
                    z3_ram = int(math.pow(2, i))
                    if check_list("Memory_Z3Ram_" + str(z3_ram) + ".txt", sub_path) is True:
                        HW_24BIT = "FALSE"
                        break
                    else:
                        z3_ram = 0
                        HW_24BIT = ""

                # =======================================
                # CHIPSET SETTINGS

                # sprite collisions
                # Default: Playfield
                # can't find a single case requiring value different than default.

                # blitter
                # Default: Wait for Blitter
                HW_BLITS = ""
                if check_list("Chipset_ImmediateBlitter.txt", sub_path) is True:
                    HW_BLITS = "IMMEDIATE"
                if  check_list("Chipset_NormalBlitter.txt", sub_path) is True:
                    HW_BLITS = "NORMAL"

                # fast copper
                # Default: False
                HW_FASTCOPPER = ""
                if check_list("Chipset_FastCopper.txt", sub_path) is True:
                    HW_FASTCOPPER = "TRUE"

                # =======================================
                # CPU SETTINGS

                # clock speed
                # Default: 14
                HW_SPEED = ""
                if check_list("CPU_ClockSpeed_7.txt", sub_path) is True:
                    HW_SPEED = "7"
                if check_list("CPU_ClockSpeed_25.txt", sub_path) is True:
                    HW_SPEED = "25"
                if check_list("CPU_ClockSpeed_Max.txt", sub_path) is True:
                    HW_SPEED = "MAX"

                # cpu model
                # Default: 68020
                HW_CPU = ""
                if check_list("CPU_68000.txt", sub_path) is True:
                    HW_CPU = "68000"
                if check_list("CPU_68010.txt", sub_path) is True:
                    HW_CPU = "68010"
                    HW_24BIT = "FALSE"
                if check_list("CPU_68040.txt", sub_path) is True:
                    HW_CPU = "68040"
                    HW_24BIT = "FALSE"

                # 24 bit addressing
                # Default: True / you can set Z3 separately

                # compatible CPU
                # Defalult: True

                # CPU cycle exact
                # available only for 68000 CPU
                # Default: False
                HW_CPUEXACT = ""
                if check_list("CPU_CycleExact.txt", sub_path) is True and HW_CPU == "68000":
                    HW_CPUEXACT = "TRUE"

                # JIT Cache
                # Default: False
                HW_JIT = ""
                if check_list("CPU_ForceJIT.txt",sub_path) == True:
                    HW_JIT = "TRUE"

                # CHIPSET
                HW_CHIPSET = ""
                if this_file.find("_AGA") > -1:
                    HW_CHIPSET = "AGA"
                if this_file.find("_CD32") > -1:
                    HW_CHIPSET = "AGA"
                    use_cd32_pad = True

                # ================================
                # building hardware section

                if HW_BLITS != '':
                    hardware += chr(10) + ('BLITTER=') + HW_BLITS

                if HW_CHIPSET != '':
                    hardware += chr(10) + ('CHIPSET=') + HW_CHIPSET

                if HW_SPEED != '':
                    hardware += chr(10) + ('CLOCK=') + HW_SPEED

                if HW_CPU != '':
                    hardware += chr(10) + ('CPU=') + HW_CPU

                if HW_24BIT != '':
                    hardware += chr(10) + ('CPU_24BITADDRESSING=') + HW_24BIT

                if HW_FASTCOPPER != '':
                    hardware += chr(10) + ('FAST_COPPER=') + HW_FASTCOPPER

                if HW_CPUEXACT != '':
                    hardware += chr(10) + ('CPU_EXACT=') + HW_CPUEXACT

                if HW_JIT != '':
                    hardware += chr(10) + ('JIT=') + HW_JIT

                if HW_NTSC != '':
                    hardware += chr(10) + ('NTSC=') + HW_NTSC

                if use_mouse1 == True:
                    hardware += chr(10) + ('PRIMARY_CONTROL=MOUSE')
                else:
                    hardware += chr(10) + ('PRIMARY_CONTROL=JOYSTICK')

                if use_mouse1 == True:
                    hardware += chr(10) + ('PORT0=MOUSE')
                elif use_cd32_pad == True:
                    hardware += chr(10) + ('PORT0=CD32')
                else:
                    hardware += chr(10) + ('PORT0=JOY')

                if use_mouse2 == True:
                    hardware += chr(10) + ('PORT1=MOUSE')
                elif use_cd32_pad == True:
                    hardware += chr(10) + ('PORT1=CD32')
                else:
                    hardware += chr(10) + ('PORT1=JOY')

                # SCREEN OPTIONS
                # Screen: size, auto-height/crop
                # Disable AUTOHEIGHT and set HEIGHT only when there's HEIGHT
                if HW_HEIGHT != '':
                    HW_AUTO_HEIGHT = 'FALSE'
                    hardware += chr(10) + ('SCREEN_AUTOHEIGHT=') + HW_AUTO_HEIGHT
                    hardware += chr(10) + ('SCREEN_HEIGHT=') + HW_HEIGHT
                else:
                    HW_AUTO_HEIGHT = 'TRUE'
                    hardware += chr(10) + ('SCREEN_AUTOHEIGHT=') + HW_AUTO_HEIGHT

                if HW_WIDTH != '720' or HW_AUTO_HEIGHT == 'FALSE':
                    hardware += chr(10) + ('SCREEN_WIDTH=') + HW_WIDTH

                # H_CENTER only if there's no H_OFFSET
                if HW_H_CENTER == 'SMART' and HW_H_OFFSET != '':
                    HW_H_CENTER = 'NONE'

                hardware += chr(10) + ('SCREEN_CENTERH=') + HW_H_CENTER

                # V_CENTER only if there's no V_OFFSET
                if HW_V_CENTER == 'SMART' and HW_V_OFFSET != '':
                    HW_V_CENTER = 'NONE'

                hardware += chr(10) + ('SCREEN_CENTERV=') + HW_V_CENTER

                if HW_H_OFFSET != '':
                    hardware += chr(10) + ('SCREEN_OFFSETH=') + str(HW_H_OFFSET)

                if HW_V_OFFSET != '':
                    hardware += chr(10) + ('SCREEN_OFFSETV=') + str(HW_V_OFFSET)

                if z3_ram != 0:
                    hardware += chr(10) + ('Z3_RAM=') + str(z3_ram)

                # custom controls
                custom_file = 'customcontrols/' + sub_path
                custom_text = ''

                # remove any items which are not amiberry custom settings
                if os.path.isfile(custom_file) == True:
                    with open(custom_file) as f:
                        customsettings_content = f.readlines()
                    f.close()

                    for this_line in customsettings_content:
                      if this_line.find('amiberry_custom') > -1 and '\n' in this_line:
                        custom_text += chr(9) + chr(9) + chr(9) + this_line
                      elif this_line.find('amiberry_custom') > -1 and not '\n' in this_line:
                        custom_text += chr(9) + chr(9) + chr(9) + this_line + chr(10)

                # external libraries (eg. xpk, required for Dungeon Master)
                extra_libs = 'False'
                if check_list('WHD_Libraries.txt', sub_path) is True:
                    extra_libs = 'True'

                # generate XML
                XML += chr(10) + chr(9)+ '<game filename="' + text_utils.left(this_file,len(this_file) - 4).replace("&", "&amp;") + '" sha1="' + ArchiveSHA + '">' + chr(10)
                XML += chr(9) + chr(9) + '<name>' + full_game_name.replace("&", "&amp;") + '</name>' + chr(10)
                XML += chr(9) + chr(9) + '<subpath>' + sub_path.replace("&", "&amp;") + '</subpath>' + chr(10)
                XML += chr(9) + chr(9) + '<variant_uuid>' + UUID + '</variant_uuid>' + chr(10)
                XML += chr(9) + chr(9) + '<slave_count>' + str(len(slave_archive.slaves)) + '</slave_count>' + chr(10)
                XML += chr(9) + chr(9) + '<slave_default>' + default_slave.replace("&", "&amp;")  + '</slave_default>' + chr(10)
                XML += chr(9) + chr(9) + '<slave_libraries>' + extra_libs  + '</slave_libraries>' + chr(10)
                XML += SLAVE_XML
                XML += chr(9) + chr(9) + '<hardware>'
                XML += hardware.replace(chr(10), chr(10) + chr(9) + chr(9) + chr(9))
                XML += chr(10) + chr(9) + chr(9) + '</hardware>' + chr(10)

                if len(custom_text) > 0:
                    XML += chr(9) + chr(9) + '<custom_controls>' + chr(10) + custom_text + chr(9) + chr(9) + '</custom_controls>' + chr(10)

                XML += chr(9)+ '</game>'

                COMPLETE_MSG += "Scanned: " + full_game_name + chr(10)

        except FileNotFoundError:
                print("Could not find LHA archive: {}".format(archive_path))
                ERROR_MSG += "Could not find LHA archive: {}".format(this_file)  + chr(10)

        except lhafile.BadLhafile:
                print("Could not read LHA archive: {}".format(archive_path))
                ERROR_MSG += "Could not read LHA archive: {}".format(this_file)  + chr(10)

        except KeyboardInterrupt:
                print()
                print("User Abort")
                break
        except:
                print("Something went wrong with LHA archive: {}".format(archive_path))
                ERROR_MSG += "Could not read LHA archive: {}".format(this_file)  + chr(10)

    # limit to a certian number of archives (for testing)
    if count >= 99999:
        break
    count = count + 1

# =======================================
# XML snippets
# for recent games
# =======================================
print()
print('Adding external XML snippets')

snippet_dir = 'snippets/'
snippet_text =  ''

# add fake root to 'old' XML to get valid xml
xml_old_snippet = '<root>' + XML_OLD + '</root>'
snipoldroot = etree.fromstring(xml_old_snippet)

for snippet_file in os.listdir(snippet_dir):
    xmlsnip = os.path.join(snippet_dir,snippet_file)
    with open(xmlsnip, 'r') as snippets_content:

        # add fake root to 'snippets' to get valid xml
        xml_snippet = '<root>' + snippets_content.read() + '</root>'
        sniproot = etree.fromstring(xml_snippet)

        # check if snippet's element has no duplicate then update it
        for snipgame in sniproot.findall('game'):
            snippet_filename = snipgame.get('filename')
            snippet_sha1 = snipgame.get('sha1')

            # check for sha1 in new packages or snippets
            if snippet_sha1 in XML or snippet_sha1 in snippet_text:
               COMPLETE_MSG += 'Snippet skipped: ' + snippet_filename + chr(10)
               continue

            # check for sha1 in 'old' XML
            # if found delete it - it will be re-added below
            # this way we would always get the latest version
            if snippet_sha1 in XML_OLD:
               for old_elem in snipoldroot.findall('.//game[@sha1="{value}"]'.format(value=snippet_sha1)):
                   snipoldroot.remove(old_elem)

            # add element from snippet
            snipstr = etree.tostring(snipgame).decode().strip()
            if snipstr.startswith('\t'):
               snippet_text += snipstr + chr(10)
            else:
               snippet_text += chr(9) + snipstr + chr(10)
            # add to report
            COMPLETE_MSG += 'Snippet added: ' + snippet_filename + chr(10)

# return a string and delete the fake root
XML_OLD = etree.tostring(snipoldroot).decode()
XML_OLD = XML_OLD.replace('<root>', '').replace('</root>', '').replace('<root />', '')

if len(snippet_text) > 0:
   XML += chr(10) + snippet_text + chr(9)

# =======================================
# XML is complete, let's put it all together
# =======================================
XML = XML_HEADER + XML_OLD + XML + XML_FOOTER

# =======================================
# write down XML file
# =======================================
print("Generating XML File")
text_file = open(whdbfile, "w+")
text_file.write(XML)
text_file.close()

# =======================================
# Line Squasher
# * line(s) matching specified characters will be deleted
# * ensure only ASCII characters are written
#
# eg.:
# offtext = ['FAST_RAM=8', '\t\t\n']
# =======================================
offtext = []

with open(whdbfile, 'r') as deloffset:
    olines = deloffset.readlines()

with open(whdbfile, 'w') as nomoreoffset:
    for line in olines:
        # remove blank lines
        if line.rstrip():
        # ensure only ASCII characters
            if not any(offset in line for offset in offtext) and all(ord(ch) < 128 for ch in line):
               nomoreoffset.write(line)

# =======================================
# Reports
# =======================================
text_file = open("files_scanned.txt", "w+")
text_file.write(COMPLETE_MSG)
text_file.close()

##if ERROR_MSG != "":
text_file = open("files_failed.txt", "w+")
text_file.write(ERROR_MSG)
text_file.close()
