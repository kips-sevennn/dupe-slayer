# dupe-slayer

Find and remove duplicate files in a folder, using MD5 hashing.

## What it does

Point it at a folder. It hashes every file's content, groups files that share a hash (duplicates), and either:
- exports a JSON report of duplicates, or
- deletes duplicates, keeping the oldest copy of each.

## How it works

1. User is prompted for a folder path (console input for now, tkinter UI planned).
2. Program walks the folder, hashes each file's content, chunked (8192 bytes at a time) so large files don't get fully loaded into memory.
3. Files are grouped by hash into `hash_dict`: `{hash: [file1, file2, ...]}`. Files that fail to open (`PermissionError`) are skipped with a message.
4. Program scans `hash_dict`'s groups looking for one with more than one file:
   -If all groups have one file, so no duplicates 
   - First group with 2+ files triggers `deletion_func()`, then stops scanning.
5. Inside `deletion_func()`, user chooses:
   - **N** — export `hash_dict` to a timestamped JSON file in `jsons_folder/` (created if missing).
   - **Y** — for every group with duplicates, sort files by creation time, keep the oldest, delete the rest.
   - Anything else — reprompt (recursive call).
Note: lower case options (n and y) are also supported !

## Output format (JSON)

```json
{
  "<md5_hash>": ["duplicate1.txt", "duplicate2.txt"]
}
```

## Notes / limitations

- Subfolders are currently skipped, I got permission issues while testing; user must select subfolders manually if needed.
- Files without read permission are skipped and reported, not fatal.

## License

MIT — free to use, modify, and distribute, commercial or not. Just keep the copyright notice.
