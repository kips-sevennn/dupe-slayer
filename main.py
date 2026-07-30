import tkinter #UI
import hashlib # For duplicate checks
import os #For file iteration, thanks stackOverflow hehe
from datetime import datetime
import json

#__________Deletion function or method whatever_____________#
def deletion_func():
    deleteDuplicates =  str(input("Delete duplicates? \n[Y]  Yes  [N]  No: ")).upper()
    
    if (deleteDuplicates == "N"): 
            #We make as much json files as executions
            #To do: If the have month old json files we prompt the user to delete all of them
            if not os.path.isdir("jsons_folder"): os.mkdir("jsons_folder")
            json_path = os.path.join("jsons_folder", 'output_'+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+'.json')           
            with open(json_path, 'w') as f:
                json.dump(hash_dict, f, indent=2)
            print("JSON file created")
            return
          
    elif (deleteDuplicates == "Y"):
            #Delete duplicates
    
            for hash in hash_dict.keys():
                if len(hash_dict[hash]) <= 1: continue
                hash_dict[hash] = sorted(hash_dict[hash], key=lambda f: os.path.getctime(os.path.join(folder, f)))
                for filename in hash_dict[hash][1:]:
                    os.remove(os.path.join(folder, filename))
                    hash_dict[hash].remove(hash_dict[hash][-1])
            print(hash_dict)
            print("Deletion done! Have a good day <3")
            return
           
    else: 
            print("Choose either N or Y")
            deletion_func()

#First things first let's do everything on the console
folder = str(input("Type folder path: "))
hash_dict = {}

for element in os.listdir(folder):
    filename = os.fsencode(element)
    file = os.path.join(folder, element) #gives me smth like C:Folder/file1 (i dunno if the user is gotta add the / at the end of their filepath), i could also return it as bytes, sure thing the types should match
    file_hash = hashlib.md5()
    #Opening file and reading the bytes (use 'rb' for that)
    try:
        with open(file, 'rb') as f:
           for buffer in iter(lambda: f.read(8192), b''): file_hash.update(buffer) #8192 is arbitrary gotta see if better value later
           hash_dict[str(file_hash.hexdigest())].append(os.fsdecode(filename))
    except PermissionError: #I think i'll harvest these names and try to acess them if they're folders (gotta just edit the folder variable with os.file.join)
        print(f"skipping (permission denied): {os.fsdecode(filename)}")      
        continue
    except KeyError: #useful only when adding the key for the first time
        hash_dict[str(file_hash.hexdigest())]=[os.fsdecode(filename)]   

for files in hash_dict.values():
    if len(files) == 1: 
        print("Nothing to do, see ya!")
    else: 
        deletion_func()
        break
    
           


   

