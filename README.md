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

Also, need a strategy to avoid name-clashes when returning Playlists as a dict.

_See_ [README: Playlists](doc/README_Playlists.md)

# Project Plan -- Short Term

## iTunes
  1. Rerun scan script to confirm we haven't introduced new backups
  2. Confirm plays post-libgpod actually register in iTunes

## CouchDB
  1. transferLibrary ought to mark tracks no longer in iTunes as deleted
  2. Set up transferLibrary to run periodically (to capture downloads)
  3. Determine elegant solution for storing python-language Views to CouchDB
  4. Replication collision detection and recovery
  5. Confirm updates don't change revision is no actual changes

## Repair
  1. Meta field in Podcast Feed documents for synonymous album tracks
  2. Dupfinder playlist class fronting a CouchDB

## iPod and libgpod
  1. iPod wrapper classes that write auto-import and auto-update CouchDB
  2. Normalize iPod played_date by unwinding roster
  3. Insert non-roster tracks prior to normalization
  4. Normalized iPod skipped_date by unwinding roster
  5. Import iPod tracks to CouchDB

## Savvy Playlists
  1. Umbrella playlist object with history & needle (iterating over views)  
  2. Stagger and Collate as playlist objects
  3. Pruning playlist for removing old tracks from iPod
  4. Process for remote cloning episodes to local and adding to iPod
  5. Implement conversion of non-mp3 files to mp3
  6. Implement conversion of podcast feeds to standard kbps

## Further Repair
  1. Filter orphans by file extension
  2. Mark orphan files

## libgpod Modernization

This prong of development is on hold for the moment.

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
  3. Back up the iPod database before fiddling with it.
  4. Read the iPod database and update the CouchDB database accordingly.
  5. Generate a savvy playlist that implements collation and staggering based
  on unplayed tracks present on the iPod.
  6. Push database with new playlist to iPod.
  7. Begin a track update loop that runs until finished or user interrupts.
  8. Unmount and unbind iPod, so that screen stops flashing "Do Not Disconnect".

The track update loop will perform the following steps:

  1. Generate a savvy playlist based on all tracks in CouchDB.
  2. Clone first file in second playlist absent in first from file server to
  local machine.
  3. Short-circuit to Step 7, if user interrupt received.
  4. Copy same file to iPod.
  5. Regenerate savvy playlist based on iPod contents and push to iPod (as an
  async process)
  6. Repeat from Step 1, unless user interrupt received.
  7. Wait for async process to finish and terminate.

Work began on prototyping in 2018, at which time the plan had been to develop
an Orange Pi Zero-based docking station for a Classic iPod, including an LED
matrix for displaying data transfer status. We may eventually return to this
design. For now, these files are retained under arc/ for reference.

The current prototype successfully transfers a mock playlist to a Classic iPod.
