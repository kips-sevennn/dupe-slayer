import hashlib # For duplicate checks
import os #For file iteration, thanks stackOverflow hehe
from datetime import datetime
from send2trash import send2trash
import re
import fnmatch
import json

def allDirectoriesOf(root_folder: str, filter: dict) -> dict:
    excluded_paths = filter.get('excluded_paths', [])
    excluded = set(os.path.normpath(p) for p in excluded_paths)
    dirs_dict = {}
    i = 0
    for root, dirs, files in os.walk(root_folder):
        root_norm = os.path.normpath(root)
        if root_norm in excluded:
            dirs[:] = []
            continue
        dirs_dict[i] = root
        i += 1
    return dirs_dict

def filter_function() -> dict:
    """
    Asks the user to choose the filters it wants, filter based on size, file format, date range, path exclusion, name pattern (regex support)
    Output example: {'size_range': [100, 5000], 'formats': ['.txt', '.jpg'], 'date_range': [datetime.datetime(2006, 12, 12, 0, 0), datetime.datetime(2006, 9, 30, 0, 0)], 'excluded_paths': ['C:/Windows'], 'name': ['re:*.jpg']}
    """
    settings = {}
    print("Want filters?\n1) Size\n2) File Format\n3) Date range(creation date)\n4) Path exclusion\n5) Name (wildcard and regex supported)\nUse commas to separate (blank for none)\n")
    raw = [x.strip() for x in input().split(",") if x.strip().isnumeric()]
    choices = [int(x) for x in raw if 1 <= int(x) <= 5]

    size = 1 in choices
    file_form = 2 in choices
    date = 3 in choices
    path_exclusion = 4 in choices
    name = 5 in choices

    if not choices:
        return settings

    if size:
        while True:
            parts = input("Enter size range in KB (e.g. 10-500): ").strip()
            if not parts: break
            parts=parts.split("-")
            if len(parts) == 2 and all(p.strip().isnumeric() for p in parts):
                settings["size_range"] = [int(parts[0]), int(parts[1])]
                break
            print("Invalid range, try again (format: min-max, numbers only).")

    if file_form:
        formats = input("Enter file formats (comma separated, e.g. .txt,.jpg): ").strip().split(",")
        settings["formats"] = [f.strip() for f in formats if f.strip()]

    if date:
        while True:
            raw_dates = input("Enter date range, blank if none (DD-MM-YYYY,DD-MM-YYYY): ").strip()
            if not raw_dates: break
            raw_dates = raw_dates.split(",")
            try:
                start = datetime.strptime(raw_dates[0].strip(), "%d-%m-%Y")
                end = datetime.strptime(raw_dates[1].strip(), "%d-%m-%Y")
            except (ValueError, IndexError):
                print("Invalid date format, try again (DD-MM-YYYY,DD-MM-YYYY).")
                continue
            if end < start:
                print("Invalid interval, try again (DD-MM-YYYY,DD-MM-YYYY)")
                continue

            settings["date_range"] = [start, end]
            break

    if path_exclusion:
        excluded = input("Enter folders to exclude (comma separated): ").strip().split(",")
        settings["excluded_paths"] = [p.strip().strip('"\'') for p in excluded if p.strip()]

    if name:
        names = input("For regex, prefix with 're:' e.g. re:^IMG_\\d+\\.jpg\nType name and/or pattern, comma separated: ").strip().split(",")
        settings["name"] = [n.strip() for n in names if n.strip()]

    settings={key:value for key,value in settings.items() if value}
    return settings

def get_hash(path: str, cache: dict) -> str:
    stat = os.stat(path)
    cached = cache.get(path)
    if cached and cached["mtime"] == stat.st_mtime and cached["size"] == stat.st_size:
        return cached["hash"]

    h = hashlib.md5()
    with open(path, 'rb') as f:
        for buffer in iter(lambda: f.read(8192), b''):
            h.update(buffer)
    digest = h.hexdigest()
    cache[path] = {"mtime": stat.st_mtime, "size": stat.st_size, "hash": digest}
    return digest


def files_hash(folderpath: str, filter: dict = None, cache: dict = None) -> dict:
    filter = filter or {}
    cache = cache if cache is not None else {}
    hash_dict = {}

    for element in os.listdir(folderpath):
        file_path = os.path.join(folderpath, element)
        file_path = os.path.normpath(file_path)

        if not os.path.isfile(file_path):
            continue

        if "formats" in filter:
            if not any(element.lower().endswith(ext.lower()) for ext in filter["formats"]):
                continue

        if "size_range" in filter:
            size_kb = os.path.getsize(file_path) / 1024
            min_kb, max_kb = filter["size_range"]
            if not (min_kb <= size_kb <= max_kb):
                continue

        if "date_range" in filter:
            file_date = datetime.fromtimestamp(os.path.getctime(file_path))
            start, end = filter["date_range"]
            if not (start <= file_date <= end):
                continue

        if "name" in filter:
            match = False
            for pattern in filter["name"]:
                if pattern.startswith("re:"):
                    if re.search(pattern[3:], element):
                        match = True
                        break
                elif fnmatch.fnmatch(element, pattern):
                    match = True
                    break
            if not match:
                continue

        try:
            digest = get_hash(file_path, cache)
        except PermissionError:
            print(f"skipping (permission issues): {element}")
            continue

        hash_dict.setdefault(digest, []).append(file_path)

    return hash_dict

def process_duplicate(hash_dict: dict, user_choices: list, jsons_folder: str) -> None:
    perma = 5 in user_choices
    select_mode = 3 in user_choices
    list_only = 2 in user_choices



    if list_only:
        #Make json file
        if not os.path.isdir("JSONS_FOLDER"): os.mkdir("JSONS_FOLDER")
        json_path = os.path.join("JSONS_FOLDER", 'output_'+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+'.json')  
        duplicates = {h:paths for h,paths in hash_dict.items() if len(paths) > 1 }
        with open(json_path, 'w') as f: json.dump(duplicates, f, indent=2)

   
    for hash_val, paths in hash_dict.items():
        if len(paths) <= 1:
            continue

        paths_sorted = sorted(paths, key=os.path.getctime)
        keep = paths_sorted[0]
        candidates = paths_sorted[1:]


        
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

#__________Main program__________

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSONS_FOLDER = os.path.join(SCRIPT_DIR, "jsons_folder")
CACHE_PATH = os.path.join(SCRIPT_DIR, "cache.json")

# load, before the main loop
if os.path.exists(CACHE_PATH):
    with open(CACHE_PATH) as f:
        cache = json.load(f)
else:
    cache = {}

user_choices=[]
while not user_choices:
    print(
        "\nChoose options (separate with commas)\n" 
        "1) Delete all detected duplicates\n" 
        "2) Get the list of duplicates\n"
        "3) Select duplicates to delete\n"   
        "Note: Option 1 will be ignored if selected with opt 3\n"
        "Tip: If first time on directory, use 2 and 3 to avoid deleting important files"
    )

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

#Handle user settings here
filter_settings = filter_function()
folder=str(input("Enter folder path: "))
dirs_dict=allDirectoriesOf(folder, filter_settings)


global_hash_dict={}
for index in dirs_dict.keys():
    current_directory = dirs_dict[index]
    print(f"\nCurrently working on: {current_directory}")
    local_hashes =  files_hash(current_directory, filter_settings, cache)
    for h, paths in local_hashes.items():
        global_hash_dict.setdefault(h, []).extend(paths)

process_duplicate(global_hash_dict, user_choices, JSONS_FOLDER)

with open(CACHE_PATH, "w") as f:
    json.dump(cache, f, indent=2)

