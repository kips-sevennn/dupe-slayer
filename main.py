import hashlib # For duplicate checks
import os #For file iteration, thanks stackOverflow hehe
from datetime import datetime
from send2trash import send2trash
import json

def allDirectoriesOf(root_folder: str) -> dict:
    dirs_dict = {}
    for i, (root, dirs, files) in enumerate(os.walk(root_folder)):
        dirs_dict[i] = root
    return dirs_dict

def files_hash(folderpath: str) -> dict:
    #Note: I deleted filename = os.fsencode(element) and replaced os.fsdecode(filename) by element (in case i get type errors)
    hash_dict = {}
    for element in os.listdir(folderpath):
        file_path = os.path.join(folderpath, element) 
        file_path = os.path.normpath(file_path)
        file_hash = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                for buffer in iter(lambda: f.read(8192), b''): file_hash.update(buffer) 
                hash_dict[str(file_hash.hexdigest())].append(file_path)
        except PermissionError: 
            print(f"skipping (permission issues): {element}")    
            continue
        except KeyError:
            hash_dict[str(file_hash.hexdigest())]=[file_path]  
    return hash_dict

def deletion_func(hash_dict: dict, user_choices: list) -> None:
    perma = 5 in user_choices
    select_mode = 3 in user_choices
    list_only = 2 in user_choices

   
    for hash_val, paths in hash_dict.items():
        if len(paths) <= 1:
            continue

        paths_sorted = sorted(paths, key=os.path.getctime)
        keep = paths_sorted[0]
        candidates = paths_sorted[1:]


        if list_only:
            #Make json file
            if not os.path.isdir("jsons_folder"): os.mkdir("jsons_folder")

            json_path = os.path.join("jsons_folder", 'output_'+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+'.json')  
            duplicates = {h:paths for h,paths in hash_dict.items() if len(paths) > 1 }
            with open(json_path, 'w') as f: json.dump(duplicates, f, indent=2)

        if select_mode:
            print(f"Group (keep {keep}):")
            for i, p in enumerate(candidates):
                print(f"{i+1}) {p}")
            picks = input("Select which to delete (comma-separated, blank=none): ")
            indexes = [int(x.strip())-1 for x in picks.split(",") if x.strip().isnumeric()]
            to_delete = [candidates[i] for i in indexes if 0 <= i < len(candidates)]
        elif 1 in user_choices: to_delete = candidates
        else:
            to_delete = []

        for path in to_delete:
            if perma:
                os.remove(path)
                print(f"Deleted (perma): {path}")
            else:
                send2trash(path)
                print(f"Sent to trash: {path}")

user_choices=[]
while not user_choices:
    print(
        "What options do you want? (separate with commas)\n" 
        "1) Delete all detected duplicates\n" 
        "2) Get the list of duplicates\n"
        "3) Select duplicates to delete\n"   
        "Note: Option 1 will be ignored if selected with opt 3\n"
        "Tip: If first time on directory, use 2 and 3 to avoid deleting important files"
    )
    
    #Handling user input
    raw = input().split(",")
    user_choices = [int(el.strip()) for el in raw if el.strip().isnumeric() and 1 <= int(el.strip()) <= 3]

if 3 in user_choices and 1 in user_choices:
    user_choices.remove(1)

if 1 in user_choices or 3 in user_choices:
    print("5) Perma delete\n6) Trash bin\nIf both selected, opt 5 will be ignored\nTip: Choose trash bin if you don't know the concerned files")
    raw2 = input().split(",")
    delete_choice = [int(el.strip()) for el in raw2 if el.strip().isnumeric() and 1 <= int(el.strip()) <= 6]
    if 5 in delete_choice and 6 in delete_choice:
        delete_choice.remove(5)
    user_choices += delete_choice

folder=str(input("Enter folder path: "))
dirs_dict=allDirectoriesOf(folder)


global_hash_dict={}
for index in dirs_dict.keys():
    current_directory = dirs_dict[index]
    print(f"\nCurrently working on: {current_directory}")
    local_hashes =  files_hash(current_directory)
    for h, paths in local_hashes.items():
        global_hash_dict.setdefault(h, []).extend(paths)
deletion_func(global_hash_dict, user_choices)

