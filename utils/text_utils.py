##  TEXT UTILS
##   V1.0    (can we put this in a constant here??)
##
##    now with numbering so that file can be shared between programs.
##     please increment the number for each function added, 
##       and increment the sub-number for each revision of existing function 


import os

class FontColours:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

def left(s, amount):
    return s[:amount]


def right(s, amount):
    return s[-amount:]


def mid(s, point, amount):
    return s[point:point+amount]


def mid_amos(s, point, amount):
    if point == 0:
        point = 1
    return s[point-1:point-1+amount]


def add_space(in_bit, pos):
    in_bit = left(in_bit, pos - 1) + " " + right(in_bit, len(in_bit) - pos + 1)
    return in_bit

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")


def make_full_cd32_name(in_name):
    # check the txt file
    file_name = "settings/UAEConfigMaker_CD32ISO_Longname_Fixes.txt"
    content = ""

    if os.path.isfile(file_name):
        with open(file_name) as f:
            content = f.readlines()
            content = [x.strip() for x in content]
        f.close()

    for this_line in content:
        if this_line.find("|") > -1:
            find_part = left(this_line, this_line.find("|"))
            replace_part = right(this_line, len(this_line) - this_line.find("|") - 1)

            if in_name == find_part:
                in_name = replace_part

    return in_name


def make_full_name(in_name):
    # special "clean up" rules
    in_name = in_name.replace("'n'", " 'n'")
    in_name = in_name.replace("+", " +")
    in_name = in_name.replace("&", " &")

    old_name = in_name
    in_name += "___"

    first_length = len(in_name)

    # special loop
    #    for A in range(2, first_length - 3):
    A = 1
    B = len(old_name)

    while A < len(in_name) and A < B:
        A += 1

        prev_char_2 = ord(mid_amos(in_name, A - 2, 1))
        prev_char = ord(mid_amos(in_name, A - 1, 1))
        this_char = ord(mid_amos(in_name, A, 1))
        next_char = ord(mid_amos(in_name, A + 1, 1))
        # never used?
        # next_char_2 = ord(text_utils.mid_amos(in_name, A + 2, 1))

        #  ===== add spaces

        if 65 <= this_char <= 90:
            # we are a capital letter

            # special MB rule
            if chr(this_char) == "M" and chr(next_char) == "B" and (48 <= this_char <= 57):
                pass
            # two underscores ... ignore
            elif prev_char == 95 and prev_char_2 == 95:
                pass
            elif prev_char == 92 and prev_char_2 == 92:
                pass
            # previous is a capital A, but not part of AGA
            elif prev_char == 65 and this_char != 71 and next_char != 65:
                in_name = add_space(in_name, A)
                A += 1
                B += 1
            # and the previous letter is not a space , and not also capital, or dash
            elif prev_char != 32 and prev_char != 45 and not (65 <= prev_char <= 90):
                in_name = add_space(in_name, A)
                A += 1
                B += 1

        # we are a number
        elif 48 <= this_char <= 57:
            # and previous number was not a number and not a space
            if not (48 <= prev_char <= 57) and prev_char != 32:
                in_name = add_space(in_name, A)
                A += 1
                B += 1

        if A > first_length:
            break

    # dirty manual fixes
    in_name = in_name.replace("  ", " ")
    in_name = in_name.replace("___", "")
    in_name = in_name.replace("CD 32", "CD32")
    in_name = in_name.replace(" CD32", " [CD32]")
    in_name = in_name.replace(" CDTV", " [CDTV]")
    in_name = in_name.replace(" AGA", " [AGA]")
    in_name = in_name.replace(" 512 Kb", " (512Kb)")
    in_name = in_name.replace(" 1 MB", " (1MB)")
    in_name = in_name.replace(" 2 MB", " (2MB)")
    in_name = in_name.replace(" 4 MB", " (4MB)")
    in_name = in_name.replace(" 8 MB", " (8MB)")
    in_name = in_name.replace(" 1 Disk", " (1 Disk)")
    in_name = in_name.replace(" 2 Disk", " (2 Disk)")
    in_name = in_name.replace(" 3 Disk", " (3 Disk)")
    in_name = in_name.replace(" 4 Disk", " (4 Disk)")
    in_name = in_name.replace(" Files", " (Files)")
    in_name = in_name.replace(" Image", " (Image)")
    in_name = in_name.replace(" Chip", " (Chip)")
    in_name = in_name.replace(" Fast", " (Fast)")
    in_name = in_name.replace("(Fast) Break", "Fast Break")
    in_name = in_name.replace("R³sselsheim", "Russelsheim")

    # check the txt file
    file_name = "settings/UAEConfigMaker_WHD_Longname_Fixes.txt"
    content = ""

    if os.path.isfile(file_name) is True:
        with open(file_name) as f:
            content = f.readlines()
            content = [x.strip() for x in content]
        f.close()

    for this_line in content:
        if this_line.find("|") > -1:
            find_part = left(this_line, this_line.find("|"))
            replace_part = right(this_line, len(this_line) - this_line.find("|") - 1)

            if in_name == find_part:
                in_name = replace_part

    # language rules
    language = right(in_name, 3)

    if language == " De":
        in_name = left(in_name, len(in_name) - 3) + " (Deutsch)"
    elif language == " Pl":
        in_name = left(in_name, len(in_name) - 3) + " (Polski)"
    elif language == " It":
        in_name = left(in_name, len(in_name) - 3) + " (Italiano)"
    elif language == " Dk":
        in_name = left(in_name, len(in_name) - 3) + " (Dansk)"
    elif language == " Es":
        in_name = left(in_name, len(in_name) - 3) + " (Espanol)"
    elif language == " Fr":
        in_name = left(in_name, len(in_name) - 3) + " (Francais)"
    elif language == " Cz":
        in_name = left(in_name, len(in_name) - 3) + " (Czech)"
    elif language == " Se":
        in_name = left(in_name, len(in_name) - 3) + " (Svenska)"
    elif language == " Fi":
        in_name = left(in_name, len(in_name) - 3) + " (Finnish)"

    return in_name


def get_whdload_page(in_name):
    # check the txt file
    file_name = "settings/UAEConfigMaker_WHD_PageList.txt"
    content = ""
    out_page = ""


    if os.path.isfile(file_name):
        with open(file_name) as f:
            content = f.readlines()
            content = [x.strip() for x in content]
        f.close()

    for this_line in content:
        if this_line.find("|") > -1:
            find_part = left(this_line, this_line.find("|"))
            replace_part = right(this_line, len(this_line) - this_line.find("|") - 1)

            if in_name.lower() == find_part.lower():
                out_page = replace_part

    return out_page


