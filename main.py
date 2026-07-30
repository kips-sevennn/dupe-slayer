import tkinter #UI
import hashlib # For duplicate checks
import os #For file iteration, thanks stackOverflow hehe
from datetime import datetime
import json


#__________Deletion function or method whatever_____________#
def deletion_func(hash_dict):
    deleteDuplicates =  str(input("Delete duplicates? \n[Y]  Yes  [N]  No: ")).upper()
    
    if (deleteDuplicates == "N"): 
            #We make as much json files as executions
            #To do: If the have month old json files we prompt the user to delete all of them
            if not os.path.isdir("jsons_folder"): os.mkdir("jsons_folder")
            json_path = os.path.join("jsons_folder", 'output_'+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+'.json')           
            with open(json_path, 'w') as f:
                json.dump(hash_dict, f, indent=2)
            return
          
    elif (deleteDuplicates == "Y"):
            #Delete duplicates   
            for hash in hash_dict.keys():
                if len(hash_dict[hash]) <= 1: continue
                hash_dict[hash] = sorted(hash_dict[hash], key=lambda f: os.path.getctime(os.path.join(folder, f)))
                for filename in hash_dict[hash][1:]:
                    os.remove(os.path.join(folder, filename))
                    hash_dict[hash].remove(hash_dict[hash][-1])
            return
           
    else: 
            print("Choose either N or Y")
            deletion_func(hash_dict)



#__________Hashing function___________
def hash_function(folderpath):
     
    hash_dict = {}
    perm_denied = []
    for element in os.listdir(folderpath):
        filename = os.fsencode(element)
        file = os.path.join(folderpath, element) 

        file_hash = hashlib.md5()
    
        try:
            with open(file, 'rb') as f:
                for buffer in iter(lambda: f.read(8192), b''): file_hash.update(buffer) 
                hash_dict[str(file_hash.hexdigest())].append(os.fsdecode(filename))
        except PermissionError: 
            print(f"skipping (permission denied): {os.fsdecode(filename)}")      
            perm_denied.append(os.fsdecode(filename)) 
            continue
        except KeyError:
            hash_dict[str(file_hash.hexdigest())]=[os.fsdecode(filename)]  
    return hash_dict, perm_denied



#___________Main program__________________
#Iteration on main folder
folder = str(input("Type folder path: "))
hash_dict,perm_denied = hash_function(folder)
#I gotta reuse it later
def iteration_on_folders(hash_dict):
    isDupe = any(len(files) > 1 for files in hash_dict.values())
    if isDupe:
        deletion_func(hash_dict)
        print("Deletion done")
    else:
        print("No duplicates found!")
        
iteration_on_folders(hash_dict)

#Let's go on subfolders
while(True):
    mustProceed1=""
    if (perm_denied): mustProceed1 = str(input("Explore the subfolders? (won't go to their subfolders) \n[Y]  Yes  [N]  No: ")).upper()

    if (mustProceed1=="N"): break
    elif (mustProceed1=="Y"): 
        for i in range(len(perm_denied)): print(f"{i+1}) {perm_denied[i]}")
        subfolders_indexes = str(input("Choose the subfolders to explore (use commas to separate: 1,2,3,4,5,6)\nInvalid indexes will be ignored: "))
        subfolders_indexes = [int(el) for el in subfolders_indexes.split(',') if el.strip().isnumeric() and int(el) < len(perm_denied)]
        break
    else:
        print("Choose either Y or N")