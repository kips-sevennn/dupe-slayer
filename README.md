# dupe-slayer

Find and remove duplicate files across a folder and all its subfolders, using MD5 hashing — with filters and a hash cache for fast repeat scans.

## What you'll need
- Python 3.8 (or later)
- send2trash module (pip install send2trash)
- pyinstaller, if you want to make an executable from it - (pip install pyinstaller)

Other modules are installed with python by default :)

### Tip
If you need to make an executable out of it, open a terminal on the folder and execute
```shell
pyinstaller --onefile main.py
```

## What it does

Point it at a folder. It walks the full folder tree, hashes every file's content (respecting any filters you set), groups files that share a hash across ALL subfolders, and lets you:
- export a JSON report of duplicates,
- delete all duplicates automatically (keeping the oldest copy of each), or
- review each duplicate group and manually pick which copies to delete.

Deletion can go to the OS trash bin (recoverable) or be permanent. Filters let you narrow the scan by size, extension, date, name pattern, or excluded folders. A hash cache skips rehashing unchanged files on repeat runs.

## How it works

1. User is asked what they want to do, upfront, before anything runs:
   - **1** — delete all detected duplicates
   - **2** — get the list of duplicates (JSON export)
   - **3** — select which duplicates to delete, per group
   - Options can be combined (e.g. "2,3"). If **1** and **3** are both picked, **1** is ignored (manual selection wins).
   - Input is validated and reprompted until at least one valid option is given.
2. If deletion (**1** or **3**) is selected, a second prompt asks:
   - **5** — permanent delete (`os.remove`)
   - **6** — send to trash bin (`send2trash`, recoverable)
   - If both picked, **5** is ignored (trash wins, safer default).
3. `filter_function()` optionally asks for filters:
   - **Size** — KB range.
   - **File format** — list of extensions.
   - **Date range** — creation date, DD-MM-YYYY to DD-MM-YYYY.
   - **Path exclusion** — folders to skip entirely (and everything nested under them).
   - **Name** — wildcard (`*.jpg`) by default, or regex if prefixed with `re:`.
   - Any filter can be left blank to skip it.
4. `allDirectoriesOf()` walks the full folder tree (`os.walk`), pruning excluded folders at walk time so their subtrees are never even visited.
5. For each directory, `files_hash()` filters files per the active settings, then hashes what's left via `get_hash()`:
   - Checks a persistent cache (`cache.json`, keyed by file path, storing mtime/size/hash).
   - If a file's mtime and size match the cache, the stored hash is reused — no rehashing.
   - Otherwise the file is rehashed (chunked binary reads, 8192 bytes at a time) and the cache entry updated.
6. Each directory's hashes are merged into one `global_hash_dict` spanning the whole tree — duplicates are caught even across different subfolders.
7. `process_duplicate()` runs once on the merged dict:
   - Groups with only 1 file are skipped (no duplicate).
   - Groups with 2+ files are sorted by creation time; the oldest is kept.
   - **List mode** exports all duplicate groups to a timestamped JSON file in `jsons_folder/`.
   - **Select mode** prints each candidate for deletion with an index, user picks which to remove.
   - **Delete-all mode** removes every duplicate except the oldest, no per-file prompt.
   - Every deletion is printed (path + method: perma or trash).
8. The hash cache is saved back to `cache.json` at the end of the run, next to the script.

## Output format (JSON)

```json
{
  "<md5_hash>": ["duplicate1.txt", "duplicate2.txt"]
}
```

## Notes / limitations

- Duplicates are detected tree-wide, across all subfolders under the root you provide.
- Cache is keyed by full path + mtime + size — a file edited without changing mtime (rare, but possible) could return a stale hash.
- No confirmation prompt before deletion beyond choosing trash vs. permanent — trash bin is the recoverable option if unsure.
- Hashing is currently single-threaded/single-core; large scans on many files will be CPU-bound.

## License

MIT — free to use, modify, and distribute, commercial or not. Just keep the copyright notice.

