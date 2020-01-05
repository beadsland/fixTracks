Migrating my 2 terabyte iTunes database to a custom CouchDB-backed media
management system that provides for _savvy_, rather than merely smart, playlists
and improved performance in managing large, even distributed, podcast libraries.

# Purpose

I currently maintain a 2 terabyte library of podcasts, which I listen to in a
somewhat unconventional manner. I've found that iTunes is increasingly inadequate
as a platform, and so I'm building out a custom media management system.

_See_ [README: Purpose](doc/README_Purpose.md)

In particular, there are a number of methods for constructing playlists that,
while trivial to implement, are simply unavailable in iTunes, even using smart
playlists. These serve admittedly odd use-cases, but as they are my, personal,
use-cases, that's what I'm building for.

Playlist design would offer more complex features for organizing tracks and also
for chaining features together in pipelines. The typical use-case will involve
multiple pipelines consolidated into one or more master listening playlists. The
entire architecture is referred to as _savvy_ playlists.

_See_ [README: Playlists](doc/README_Playlists.md)

# Status

The fixTracks project involves three different development prongs: fleshing
out installation of the libgpod shared libraries and bindings, cleaning up the
existing iTunes database, and prototyping scripts to manage the savvy playlists
and database on a Classic iPod.

## libgpod

Developed as part of the gtkpod project, [libgpod](http://www.gtkpod.org/libgpod/)
is a project that provides shared libraries and bindings for reading and writing
data to Apple iPod devices.

_See_ [README: libgpod](doc/README_libgpod.md)

## Database

Cleaning up and migrating the iTunes database involves five steps: fixing legacy
file paths, transferring the library to CouchDB, repairing duplicated tracks and
case-sensitive file paths, archiving orphaned audio files, implementing downloads
from podcast feeds.

_See_ [README: Database](doc/README_Database.md)

## Prototype

Ultimately, the plan is for a full-fledged media management server and peer-to-
peer file server, written in Elixir, coupled with an iPod synchronization client,
probably written in Rust, an podkintosh Pi implementation, and eventually an
Android client.

Initially, I just want to get something up and running, and so I'm building out
a working prototype script in Python2. The prototype, when finished, will perform
the following steps when run:

  1. Resolve any replication conflicts in the CouchDB database.
  2. Download new episodes of podcasts.
  3. Read the iPod database and update the CouchDB database accordingly.
  4. Generate a savvy playlist that implements collation and staggering based
  on unplayed tracks present on the iPod.
  5. Push database with new playlist to iPod.
  5. Begin a track update loop that runs until finished or user interrupts.
  6. Unmount and unbind iPod, so that screen stops flashing "Do Not Disconnect".

The track update loop will perform the following steps:

  1. Generate a savvy playlist based on all tracks in CouchDB.
  2. Clone first file in second playlist absent in first from file server to
  local machine.
  3. Copy same file to iPod.
  4. Regenerate savvy playlist based on iPod contents and push to iPod (as an
  async process)
  5. Repeat until user interrupt received.

Work began on prototyping in 2018, at which time the plan had been to develop
an Orange Pi Zero-based docking station for a Classic iPod, including an LED
matrix for displaying data transfer status. We may eventually return to this
design. For now, these files are retained under arc/ for reference.

The current prototype successfully transfers a mock playlist to a Classic iPod.

Currently efforts are focused on unbinding the Classic iPod as a USB device.
Unfortunately, detaching alone, while making the iPod inaccessible to the OS,
does not signal to the iPod that it is safe to disconnect, so the message
"**Do Not Disconnect**" continues to flash on the device screen. That said,
ubinding requires sudoer's rights, so we'll need a system service to do the heavy
lifting.
