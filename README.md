Last year I got tired of forgetting which academic talks I had attended and what all my colleagues and research senpais are up to, so I started taking brief notes for every talk. Initially I just had a single file with researchers listed in alphabetical order, but this quickly got unwieldy (dozens of pages to scroll through). This is a simple command-line tool which maintains notes for each talk in a separate .txt file and keeps track of metadata like when and where each talk was given. 

### Example usage:
Add a new researcher: `python talk_notes.py <metadata_file_path> <database_path> -n "firstname lastname"`, which will return the id of the new researcher.

Add a new talk: `python talk_notes.py <metadata_file_path> <database_path> -a <researcher_id>`, which will open a text file where you can take notes and edit metadata.

### Miscellaneous
Written and tested* in Python 3.9.4 on Windows 10.
The only non-standard package required is click (https://pypi.org/project/click/).

*Tested very lightly, use at your own risk!
