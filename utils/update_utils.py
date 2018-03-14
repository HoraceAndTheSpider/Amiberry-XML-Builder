import ssl
import urllib
import urllib.request
from .text_utils import FontColours

try:
    ssl._create_default_https_context = ssl._create_unverified_context
except:
    pass


def download_update(in_file,put_file):
    # get_file = "http://www.djcresswell.com/RetroPie/ConfigMaker/" +infile
    get_file = "https://raw.githubusercontent.com/HoraceAndTheSpider/UAEConfigMaker/develop/" + in_file
    get_file = urllib.parse.quote(get_file)
    get_file = str.replace(get_file,"https%3A","https:")

    
    if put_file == "":
        put_file = "" + in_file

    try:
        urllib.request.urlretrieve(get_file, put_file)
        print("Update downloaded for " + FontColours.OKBLUE + in_file + FontColours.ENDC + ".")
    except:
        print("No update downloaded for " + FontColours.FAIL + in_file + FontColours.ENDC + ". (Web Page not found)")
    return


def run_updater():
    # initialisations

    print()
    print(
        FontColours.BOLD + FontColours.OKBLUE + "HoraceAndTheSpider" + FontColours.ENDC + "'s " + FontColours.BOLD +
        "UAE Configuration Maker" + FontColours.ENDC + FontColours.OKGREEN + " (Auto-Update)" + FontColours.ENDC + " | " + "" +
        FontColours.FAIL + "www.ultimateamiga.co.uk" + FontColours.ENDC)
    print()

    # and these are the files to update
    download_update("uae_config_maker.py","")
    download_update("UAE%20Config%20Maker.sh","/home/pi/RetroPie/retropiemenu/")
    download_update("README.md","")
    download_update("TODO.md","")
    download_update("whdload/whdload_slave.py","")
    download_update("utils/general_utils.py","")
    download_update("utils/text_utils.py","")
    download_update("utils/update_utils.py","")    
    return
