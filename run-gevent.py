import gevent
import os
import taglib
import zmq
import time
import sys
import shutil
import distutils.dir_util
from  multiprocessing import Process
from findtools.find_files import (find_files, Match)

MP3SRCDIR="srcmp3"
MP3DSTDIR="dstmp3"

MP3SRCDIR="/tmp/src"
MP3DSTDIR="/tmp/dst"


def mp3filelist(basedir):
    """ returns a list of .mp3 files containing their full paths """

    mp3_files_pattern = Match(filetype='f', name='*.mp3')

    found_files = find_files(path=basedir, match=mp3_files_pattern)

    l = []
    for f in found_files:
        l.append(f)
    return l


def update_mp3_location(filename, artist, album, title):
    """ renames the mp3 file """
    distutils.dir_util.mkpath(
        "%s/%s/%s/%s" % (
            MP3DSTDIR,
            artist[0].upper(),
            artist, album
        )
    )

    _, extension = os.path.splitext(filename)

    shutil.move(
        filename, "%s/%s/%s/%s/%s%s" % (
            MP3DSTDIR,
            artist[0].upper(),
            artist,
            album,
            title,
            extension
        )
    )

def get_tags(filename):
    mp3file = taglib.File(filename)
    return (
            mp3file.tags['ARTIST'][0],
            mp3file.tags['ALBUM'][0],
            mp3file.tags['TITLE'][0]
    )

def pipeline(filename):
    try:
        artist, album, title = get_tags(filename)
        update_mp3_location(filename, artist, album, title)
        print(
            "moving %s to %s/%s/%s/%s" % (
                filename,
                artist[0].upper(),
                artist,
                album,
                title
            )
        )
    except Exception as e:
        print e


threads = []
for filename in mp3filelist(MP3SRCDIR):
    threads.append(
        gevent.spawn(
            pipeline(filename)
        )
    )

gevent.joinall(threads)

