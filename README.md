Migrating my 2 terabyte iTunes database to a custom CouchDB-backed media
management system that provides for _savvy_, rather than merely smart, playlists
and improved performance in managing large, even distributed, podcast libraries.

Presently, the `parseIpod.py` script is set up to create a collation of two
staggered playlists, one historical the other contemporary, drawing entirely
from the tracks in place on the iPod. Staggers account for recent plays.

History playlist captures played tracks (and addresses issues where the iPod
clock hasn't been set, such as after a battery change), but doesn't yet account
for skipped (_i.e._, incomplete) plays. Similarly, the needle (or first) track
of the main playlist doesn't yet know what skipped track was last played, so
selects the first track with a bookmark.

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

## Data Import

### Scanning Files
  1. Trigger StopIteration in `scanUntrackedFiles.py`

### iTunes to CouchDB
  1. Refactor couch.database from `transferLibrary.py`
  2. Use bulk uploads rather than individual saves
  3. Determine elegant solution for storing python-language Views to CouchDB
  4. Use batch iteration backed by bulk downloads
  5. Common lazydict to cull down to deleted tracks

### Commandline UX
  1. View of undeleted tracks for progress of `transferLibrary.py`
  2. Refactor data import to use `pv` for progress bar
  3. Module loading scheme using `pv` (???)
  4. Simplify itunes.database exception generation to use default language

### Data Reprentation
  1. Datetime/String subclass to allow json.dump of datetime objects
  2. JsonData class for parsing data fields in `iTunes Library.xml`

## Data Maintenance

### iPod
  1. Refactor `transferLibrary.py` for common use in iPod sync
  2. Copy artwork data from iPod
  3. Process to recover iPod from CouchDB after iTunes sync
  4. Import from good backup to pick up old tracks
  5. Replication collision detection and recovery

### Repair
  1. Dupfinder playlist class fronting a CouchDB
  2. Meta field in Podcast Feed documents for synonymous album tracks
  3. Dup removal from iTunes database

### Maintenance
  1. Confirm updates don't change revision if no actual changes
  2. Set up transferLibrary to run periodically (to capture downloads)

## iPod Sync

### iPod and libgpod
  1. Unique ID for identifying an iPod
  2. Normalize iPod played_date by unwinding roster
  3. Insert non-roster tracks prior to normalization
  4. Normalized iPod skipped_date by unwinding roster

### Savvy Playlists
  1. Umbrella playlist object with history & needle (iterating over views)  
  2. Stagger and Collate as playlist objects
  3. Implement support for inclusion of music tracks

### Incremental Updates
  1. Pruning playlist for removing old tracks from iPod
  2. Process for remote cloning episodes to local and adding to iPod
  3. Implement conversion of non-mp3 files to mp3
  4. Implement conversion of podcast feeds to standard kbps

## Et cetera

### Further Repair
  1. Filter orphans by file extension
  2. Mark orphan files

### libgpod Modernization

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
