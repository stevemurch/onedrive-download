from simple_term_menu import TerminalMenu
from onedrive_authorization_utils import save_refresh_token, load_access_token_from_file, procure_new_tokens_from_user, get_new_access_token_using_refresh_token, save_access_token, load_refresh_token_from_file
from generate_list import generate_list_of_all_files_and_folders
from coloring import *
from download_list import download_the_list_of_files
from tabulate import tabulate 

def do_get_refresh_and_access_tokens():
    print_orange("To generate a new access_token, see the web browser I've launched.")
    print_orange("Click 'Continue' to grant permission. After you've given it permissions,")
    print_orange("it will try to reload a webpage at 'localhost:8080'. That page won't work, BUT that's OK.")
    print_orange("That's because what we really want here is the value of the 'code' parameter.")
    print_orange("Typically that code parameter looks like M.R3......xyz.")
    access_token, refresh_token, name = procure_new_tokens_from_user()
    save_refresh_token(refresh_token)
    print_yellow("Hello %s! Success." % name)
    print_yellow("I've saved two files, access_token.txt and refresh_token.txt.")
    print_yellow("Please keep these secure, and delete them when you're done.")
    print_yellow("With these tokens, hackers could modify or delete your OneDrive files.")
    
def do_use_refresh_token_to_get_new_access_token():
    refresh_token = load_refresh_token_from_file()
    if (refresh_token is None):
        print_red("Error, there's nothing in refresh_token.txt")
        print_red("Solution: re-run the program, to generate the tokens.")
        return 
    new_access_token = get_new_access_token_using_refresh_token(refresh_token)
    print_orange("Got a new access token from your refresh token. Saving it to the file: access_token.txt.")
    save_access_token(new_access_token)

def main():
    main_welcome = ["ONEDRIVE DOWNLOADER"]
    print(tabulate(main_welcome, tablefmt="fancy_grid"))

    options = ["1. Get refresh and access tokens (access_tokens last 1 hour)", 
    "2. Get new access_token based on previously saved refresh_token (saves you entering the 'code' if you've done step 1)",
    "3. Generate list of all files and folders",
    "4. Download the files enumerated by step 3"]
    terminal_menu = TerminalMenu(options)
    menu_entry_index = terminal_menu.show()
    print(f"You have selected {menu_entry_index+1}")
    match menu_entry_index:
        case 0:
            do_get_refresh_and_access_tokens()
            main()
        case 1:
            do_use_refresh_token_to_get_new_access_token()
            main()
        case 2:
            access_token = load_access_token_from_file()
            generate_list_of_all_files_and_folders(access_token=access_token)
        case 3:
            access_token = load_access_token_from_file()
            download_the_list_of_files(access_token)

if __name__ == "__main__":
    print("\033c") # clear screen
    main()