import requests 
import json
from coloring import *
from tabulate import tabulate 
from onedrive_authorization_utils import procure_new_tokens_from_user, load_access_token_from_file, save_access_token, BASE_URL

# You'll want to change this to the folder YOU want to start with.
# In my OneDrive, I've created top-level folders for A, B, C... Z
# In the "P" folder, I have what I really wanted to download: Pictures

root_folder = "/me/drive/root:/P"


# 1) Get Access Token
# 2) When Access Token expires, get a new one. 
# 3) We want to first build a list of all the names and files to fetch. 
#    Don't download anything at first, just traverse the folders and build up a task list. 

#    Build a list of folders to traverse, by: 
#    folders = [] 

#    def process_folder_url(url:str):
#          get pageful of items in folder
#                if the item in list is a folder, append it to work queue
#          if there's a next_link, process_folder_url(next_link) 
#                else return
#          for each folder in the list of items:
#                process_folder 
# 


# Go to Portal / App Registrations to create one.




def get_next_link_from_response_dictionary(dict) -> str:
    if (dict.__contains__("@odata.nextLink")):
        return dict["@odata.nextLink"]
    return None 


########### Access token ############
# access_token = load_access_token_from_file()

# if (access_token is None):
#     access_token = procure_new_tokens_from_user()
#     save_access_token(access_token)
#####################################################
# print_green("token: %s" % access_token)




current_folder = root_folder 

def get_current_endpoint() -> str:
    return BASE_URL + current_folder + ":/children"

# Given an item dictionary of a folder object, construct its ms opengraph "children" inspector endpoint
def get_folder_endpoint_by_folder_item(item) -> str:
    return BASE_URL + "/me" + item["parentReference"]["path"] + "/" + item["name"] + ":/children"

# examples: 
# endpoint = base_url + "/me/drive/special/photos/children"
#endpoint = base_url + "/me/drive/special/cameraroll/children"
#endpoint = base_url + "/me/drive/root/P/Pictures/Camera Roll/children"

folder_list = []
file_list = []

# To list what's in a folder, append :/children to the folder name 
def process_folder_pagefull(endpoint:str, access_token:str):
    headers = {"Authorization":"Bearer "+access_token}
    print_blue("getting "+endpoint)
    try: 
        response = requests.get(endpoint, headers = headers)
        
    except:
        print_red(response.json()["error"]["code"])
        error_code = response.json()["error"]["code"]
        if (error_code=="InvalidAuthenticationToken"):
            access_token = procure_new_tokens_from_user()
            save_access_token(access_token)
            print_green("New access token saved, which is good for 1 hour. Please re-run program.")
            exit()

    # print_alice_blue(json.dumps(response.json(), indent=2))
    content = response.json()
    item_count = len(content["value"])
    print_azure("There are %s item(s) in this folder." % item_count)

    # Items are going to either be folders or files. 
    for item in content["value"]:
        is_folder = item.__contains__("folder") 
        msg = "%s %s" % (item["name"] , ("[FOLDER]" if is_folder else "[FILE]"))
        print_blue_violet(msg)
        if not is_folder:
            # print("DOWNLOAD %s" % item["@microsoft.graph.downloadUrl"])
            file_list.append(item)
        else:
            folder_list.append(item)
            # process the folder 
            endpoint = get_folder_endpoint_by_folder_item(item)
            process_folder_pagefull(endpoint, access_token=access_token)

    next_link = get_next_link_from_response_dictionary(content)
    print_purple("Next link:")
    print_purple(next_link)
    if (next_link is not None):
        return process_folder_pagefull(next_link, access_token=access_token)

    return len(folder_list)


# START

def generate_list_of_all_files_and_folders(access_token:str):
    
    endpoint = get_current_endpoint()

    result_count = process_folder_pagefull(endpoint, access_token=access_token)
    print_green("%s folder item(s) found" % result_count)

    print_bbisque(file_list[1])
    print_orange(folder_list[0])

    print_orange("Writing list of files and folders to process:")
    # save file_list to file
    json_file_list = json.dumps(file_list)
    f = open('file_list.json', 'w', encoding="utf8")
    f.write(json_file_list)

    # save folder_list to file 
    json_folder_list = json.dumps(folder_list)
    f = open('folder_list.json', 'w', encoding="utf8")
    f.write(json_folder_list)
    print_orange("")
    print_orange("file_list.json and folder_list.json have been saved to the current folder.")
    print_orange("")
    table = [["","Count"],["Files",len(file_list)],["Folders",len(folder_list)]]
    print_bisque("OneDrive Folder: %s " % root_folder.replace("/me/drive/root:",""))
    print_bisque(tabulate(table, tablefmt="fancy_grid"))
    print_orange("")
    print_orange("Done.")

