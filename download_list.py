# Assumes you've got file_list.json 

from coloring import *
import json
import requests 
import sys
from pathlib import Path
from onedrive_authorization_utils import load_access_token_from_file

from datetime import datetime
from exif import Image 

from progress.bar import Bar

item_download_errors = []

def load_file_list() -> list:
    with open("file_list.json", "r") as f:
        str = f.read()
        file_items = json.loads(str)
    return file_items

def download_file_by_url(url, local_file_path) -> str:
    # print_baquamarine("Saving to: %s" % local_file_path)
    try: 
        access_token = load_access_token_from_file()
        headers = {"Authorization":"Bearer " + access_token}
        r = requests.get(url, headers=headers, allow_redirects=True)
        if (r.status_code != 200):
            print_red("ERROR COULD NOT GET FILE -- REFRESH YOUR ACCESS TOKEN")
            print(r.status_code)
            exit()
        open(local_file_path, 'wb').write(r.content)
        return local_file_path
    except KeyboardInterrupt as ke:
        print_green("Keyboard pressed. Goodbye")
        return "EXIT"
    except:
        print_red("ERROR IN download_file_by_url %s" % url)
        return None 

def ensure_local_path_exists(local_path):
    Path(local_path).mkdir(parents=True, exist_ok=True)

# from file item, get the local folder path
# can't save it all to one flat directory, 
# or else files with same name in different folders will collide
# also ensures folder path exists  
def get_local_download_folder_by_item(item) -> str:
    master_parent_folder_name = "/drive/root:"
    local_folder_path = item["parentReference"]["path"].replace(master_parent_folder_name, "")
    cwd = Path.cwd()
    return "%s/downloads%s" % (cwd, local_folder_path)

def modify_exif_using_onedrive_item_data(full_filepath, item):
    takenDateTime_ISO_str = item["photo"]["takenDateTime"]
    print_dark_orange("ready to update time")
    print_dark_blue(full_filepath)

    with open(full_filepath, 'rb') as image_file:
        my_image = Image(image_file)
        print_brown(my_image.list_all())
        print_brown(my_image.datetime_original)

    proper_date = datetime.fromisoformat(takenDateTime_ISO_str)
    print_dark_orange("Updating date to %s" % proper_date)

    #Update DateTimeOriginal
    # piexif.remove()

def download_the_list_of_files(access_token:str):
    
    items = load_file_list()
    total = len(items)
    print_orange("There are %s file(s) in file_list.json." % total)
    print_orange("")


    bar = Bar('Processing', max=total)

    index = 0
    for item in items:
        index = index+1 
        print("")
        bar.next()
        download_url = item["@microsoft.graph.downloadUrl"]
        item_type = "unknown"
        if (item.__contains__("photo")):
            item_type = "photo/video"
        elif (item.__contains__("file")):
            item_type = "file"

        if (item_type == "photo/video"):
            try: 
                takenDateTime = item["photo"]["takenDateTime"]
                print_orange("")
                print_orange("[%s of %s] %s: (%s) %s" % (index, total, item["name"], item_type, takenDateTime))

                local_folder_path = get_local_download_folder_by_item(item)
                print_borange("Saving to: %s" % local_folder_path)
                local_file_path = local_folder_path + "/"+item["name"]
                ensure_local_path_exists(local_folder_path)

                file_on_disk = download_file_by_url(download_url, local_file_path)
                if (file_on_disk == "EXIT"):
                    print_green("Exiting.")
                    sys.exit(2) 

                if (file_on_disk is not None):
                    cwd = Path.cwd()
                    json_formatted_str = json.dumps(item, indent=2)
                else:
                    item_download_errors.append(item)
            except SystemExit:
                sys.exit(2)
            except:
                item_download_errors.append(item)

    bar.finish()
    
    total_errors = len(item_download_errors)
    json_error_list = json.dumps(item_download_errors)
    f = open('item_download_errors.json', 'w', encoding="utf8")
    f.write(json_error_list)

    print_red("There were %s total error(s) in download. Often that's due to network errors." % total_errors)
    print_red("Rather than interrupt the loop, I've saved them in 'item_download_errors.json', so you can try manually.")
