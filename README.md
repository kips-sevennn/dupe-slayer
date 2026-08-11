# dupe-slayer (v2.0)

Find and remove duplicate files across a folder and all its subfolders, using MD5 hashing.

## What it does

Point it at a folder. It walks the full folder tree, hashes every file's content, groups files that share a hash across ALL subfolders (not just per-folder), and lets you:
- export a JSON report of duplicates,
- delete all duplicates automatically (keeping the oldest copy of each), or
- review each duplicate group and manually pick which copies to delete.

Deletion can go to the OS trash bin (recoverable) or be permanent.

## How it works

1. User is asked what they want to do, upfront, before anything runs:
   - **1** — delete all detected duplicates
   - **2** — get the list of duplicates (JSON export)
   - **3** — select which duplicates to delete, per group
   - Options can be combined (e.g. "2,3"). If **1** and **3** are both picked, **1** is ignored (manual selection wins).
   - Input is validated and reprompted until at least one valid option is given.
2. If deletion (**1** or **3**) is selected, a second prompt asks:
   - **5** — permanent delete 
   - **6** — send to trash bin 
   - If both picked, **5** is ignored (trash wins, safer default).
3. `allDirectoriesOf()` walks the full folder tree (`os.walk`) and returns every directory found in a dictionnary.
4. For each directory, `files_hash()` hashes every file inside it (w/o filling the ram). Files that can't be opened (`PermissionError`) are skipped.
> Note: On my tests I managed to have workarounds for the subfolders with permission issues 
5. Each directory's hashes are merged into one `global_hash_dict` spanning the whole tree — so duplicates are caught even if they live in different subfolders.
6. `deletion_func()` runs once on the merged dict:
   - Groups with only 1 file are skipped (no duplicate).
   - Groups with 2+ files are sorted by creation time; the oldest is kept.
   - **List mode** exports all duplicate groups to a timestamped JSON file in `jsons_folder/` (created if missing).
   - **Select mode** prints each candidate for deletion with an index, user picks which to remove (comma-separated, blank = none).
   - **Delete-all mode** removes every duplicate except the oldest, no per-file prompt.
   - Every deletion is printed on the console(path + method: perma or trash).

## Output format (JSON)

```json
{
  "<md5_hash>": ["duplicate1.txt", "duplicate2.txt"]
}
```

## Notes / limitations

- Duplicates are detected tree-wide, across all subfolders under the root you provide.
- No hash caching yet — every run rehashes every file from scratch.
- No confirmation prompt before deletion beyond choosing trash vs. permanent — trash bin is the recoverable option if unsure.

## License

MIT — free to use, modify, and distribute, commercial or not. Just keep the copyright notice.