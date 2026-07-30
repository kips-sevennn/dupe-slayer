# dupe-slayer (v1.1)

Find and remove duplicate files in a folder, using MD5 hashing.

## What it does

Point it at a folder. It hashes every file's content, groups files that share a hash (duplicates), and either:
- exports a JSON report of duplicates, or
- deletes duplicates, keeping the oldest copy of each.

Also offers to explore folders it couldn't access directly (likely subfolders).

## How it works

1. User is prompted for a folder path (console input for now, tkinter UI planned).
2. `hash_function()` walks the folder, hashes each file's content in binary mode, chunked (8192 bytes at a time) so large files don't get fully loaded into memory.
   - Files are grouped by hash into `hash_dict`: `{hash: [file1, file2, ...]}`.
   - Files that fail to open (`PermissionError`) are skipped, logged, and their names collected in `perm_denied` (assumed to be subfolders).
3. `iteration_on_folders()` checks `hash_dict` with a bool flag: if any group has more than 1 file, duplicates exist and `deletion_func()` runs once. Otherwise prints "No duplicates found!".
4. Inside `deletion_func()`, user chooses:
   - **N** — export `hash_dict` to a timestamped JSON file in `jsons_folder/` (created if missing).
   - **Y** — for every group with duplicates, sort files by creation time, keep the oldest, delete the rest.
   - Anything else — reprompt (recursive call).
5. If `perm_denied` isn't empty, user is asked whether to explore those folders:
   - Each entry is listed with an index.
   - User picks which ones to explore by index (comma-separated).
   - v1.1 only goes one level deep — subfolders of subfolders are not explored.

## Output format (JSON)

```json
{
  "<md5_hash>": ["duplicate1.txt", "duplicate2.txt"]
}
```

## Notes / limitations

- Subfolder exploration is one level deep only (currently doing it); nested subfolders need manual selection (planned for v2).
- Files without read permission are skipped and reported, not fatal.

## License

MIT — free to use, modify, and distribute, commercial or not. Just keep the copyright notice.

