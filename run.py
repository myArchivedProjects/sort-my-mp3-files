import os
import taglib
import zmq
import time
import sys
import shutil
import distutils.dir_util
from  multiprocessing import Process
from findtools.find_files import (find_files, Match)

"""
    sorts out my mp3 collection, moving my files around so that they are
    store in the right place

"""

MP3DIR="/home/azul/git-annex/Music/"


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
    distutils.dir_util.mkpath("%s/%s" % (artist, album))

    _, extension = os.path.splitext(filename)

    print "moving %s to %s/%s/%s" % (
        filename,
        artist,
        album,
        title
    )

    shutil.move(filename, "%s/%s/%s%s" % ( artist, album, title, extension))


def client(ports=["5556"]):
    """ publishes a list of mp3 files to the service """

    context = zmq.Context()

    print "Connecting to server with ports %s" % ports

    socket = context.socket(zmq.REQ)
    for port in ports:
        socket.connect ("tcp://localhost:%s" % port)

    for f in mp3filelist(MP3DIR):
        print "Sending request ", f,"..."
        socket.send(f)

        # do we care about a response ?
        message = socket.recv()
        print "Received reply ", f, "[", message, "]"


def server(port="5556"):
    """ our worker node """
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:%s" % port)
    print "Running server on port: ", port

    for reqnum in range(99999):
        # Wait for next request from client
        msg = socket.recv()

        filename = msg

        mp3file = taglib.File(filename)
        artist = mp3file.tags['ARTIST'][0]
        album = mp3file.tags['ALBUM'][0]
        title = mp3file.tags['TITLE'][0]

        update_mp3_location(
            filename,
            artist,
            album,
            title
        )

        socket.send_json("OK")


if __name__ == "__main__":
    # Now we can run a few servers
    server_ports = range(5550,5558,2)
    for server_port in server_ports:
        Process(target=server, args=(server_port,)).start()

    # Now we can connect a client to all these servers
    Process(target=client, args=(server_ports,)).start()