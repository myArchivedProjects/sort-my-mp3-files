Some python code to re-organize my mp3 collection.

It grabs a directory with a large number of unsorted files, 
checks their ID tags and re-arranges them based on /LETTER/artist/album/title


edit MP3DIR with the path for your mp3 files


on nixos:

```
    nix-shell
    python run.py
```

on other beasts:

```
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
python run.py
```
