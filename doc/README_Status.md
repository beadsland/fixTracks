[Back to Top](../README.md)

# README: Status

The fixTracks project involves three different development prongs: fleshing
out installation of the libgpod shared libraries and bindings, cleaning up the
existing iTunes database, and prototyping scripts to manage the savvy playlists
and database on a Classic iPod.

## libgpod

Developed as part of the gtkpod project, [libgpod](http://www.gtkpod.org/libgpod/)
is a project that provides shared libraries and bindings for reading and writing
data to Apple iPod devices.

The official release of this project is a SourceForge project from 2011, while
the development branch was last touched in 2013 (with documentation edits in
2014). Several clones of the project appear on github, the most up-to-date of
which appears to be this:

  https://github.com/jburton/libgpod.git

_NOTE: This prong is on holding final database transfer and a working_ savvy
_playlist prototype for the Classic iPod._

### Build Process

The current version relies on libraries and toolchain that is largely deprecated,
when not outright abandoned in modern distributions. One configuration step
seeks a version of a build tool above a certain version, and then hard-codes
checks for that version and the next N versions only. The current version of
said tool is several version past that check. Meanwhile, the most recent versions
of some build tools introduce changes that break the build process.

Including ferreting out where missing libraries and dependencies might be hiding,
the build process for libgpod can take hours. Even then, one has to pay careful
attention to the messages coming from the configuration scripts, as it is
entirely possible to successfully build and install libgpod without any bindings
being built or installed.

Also, the libgpod bindings for python are only for python 2 and are exposed via
`import gpod`. Unfortunately, there's another package available for pip
install from PyPI, a "general purpose object detector", which is also identified
as gpod. Needless to say, this can make for some confusion.

### Streamlining

Streamlining libgpod builds will proceed in several steps:

 1. Document the steps required to get up and running on a fresh install of
 Ubuntu Bionic.

 2. Create and distribute a docker container preconfigured with a fully built
 and installed version.

 3. Build a cmake project to generate builds for legacy libraries and toolchain
 dependencies.

 4. Consolidate merges from other github forks.

 5. Merge in latest development branch from SourceForge.

 6. Progressively upgrade build toolchain, to bring build environment current.

 7. Rename python bindings and provide bindings for python3.

 8. Write NIFs for using libgpod from Elixir and other BEAM languages.

## Database

Cleaning up and migrating the iTunes database involves four steps: fixing legacy
file paths, transferring the library to CouchDB, repairing duplicated tracks and
case-sensitive file paths, archiving orphaned audio files, implementing downloads
from podcast feeds.

### Legacy Paths

Over the years, the iTunes database has been moved from one portable hard drive
to another, and eventually to network shares from various file servers. Meanwhile,
space constraints on available hard drives and servers has required a manual
process of sharding files to alternate storage. Both processes have introduced
corruption in path names as stored in iTunes.

Before iTunes 11, it was possible upon moving a database to another location,
to update the database to re-point all tracks to the new path. For whatever
reason, this feature was not present in iTunes 11. It was reintroduced in
iTunes 12 and thereafter, but as we froze iTunes at 11 to avoid Apple's efforts
to lock down the iTunes database in later versions, that feature has remained
unavailable.

#### Sharding and Naming

Manual sharding was accomplished by inspecting the folders of those podcasts
consuming the largest share of hard drive space, selecting a release year midway
between 2005 and the current year, and moving those files with that release date
en-masse to another hard drive or server. (Windows 7 conveniently provides for
viewing ID3 properties in the file Explorer.)

This introduces issues when moving files back. Even without duplication, some
podcasts issue episodes with strikingly similar titles over the years. When
iTunes saves an mp3 file, it transliterates non-alphanumeric characters and
truncates the string to allow for Windows file name restrictions. If another
file is already present in the given folder with the same name, it chops off a
few more characters and appends a number. This works fine if the like-named file
is there to collide with. Not so much if the file has been moved to another
device to recover disk space.

As a result, when files were consolidated on the RAID, there were filename
collisions. When those happen, the duplicates were stored to parallel folder
systems for later linkage back to the appropriate tracks.

#### Repair Process

Tools exist to repair iTunes database path names, including commercial software
products and freeware Visual Basic Scripts designed to address typical use cases.
These proved inadequate. A custom VBscript was able to address these issues, but
not directly.

Not all properties of tracks in the iTunes database are exposed to VBscript
bindings, but those properties are exposed in the `iTunes Library.xml` backup file.
Notably, for our purposes, the Location field of tracks are only provided to
VBscript if valid. This is why existing VBscript solutions in the wild are unable
to fix tracks where paths have merely moved: the VBscript can't determine where
the track path used to be in order to change it to where it is supposed to be.

Thus for our solution, a python script reads the XML backup file, extracts
necessary fields, together with fields that are exposed to VBscript, and saves
the result to a tab-delimited text file. The VBscript then reads this text file,
builds several nested dict structures from it as lookup tables, and then proceeds
to make a variety of repairs to the database using this information.

This process is now finished, and the scripts involved in the process,
`getModDates.py` and `localhostFix.vbs` are retained in the util/ directory of
this project for archival purposes.

### Data Transfer

This has been a relatively simple process of parsing the backup XML file from
iTunes and pushing the same data to a fresh CouchDB database. Well, not entirely
simple, as the `iTunes Library.xml` file breaks from the XML standard and
incorrectly specifies its encoding, but these problems were solved when building
lookup tables for properties unexposed to VBscript, above.

Thankfully, this process is simple enough that it can be done repeatedly while
resolving duplicates and case-sensitivity issues, below.

### Dups and Case-Sensitivity

In addition to duplicates being introduced by redownloads of feeds by iTunes,
and filename collisions, it is also surprisingly easy to slip at the keyboard
while working with tracks in iTunes and inadvertently create duplicates of
selected tracks.

The ongoing process for fixing this is as follows:

  1. Export current iTunes Library to XML.
  2. Delete the current copy of the CouchDB database.
  3. Transfer the XML database to a new CouchDB database.
  4. Cache an iterator snapshot of the file system via a python script.
  5. Scan the CouchDB database, removing each file name seen from the cache.
  6. Stop on encountering a CouchDB record that can't be found in the cache.

At each stop, we investigate to determine if the issue is a duplicate track, a
missing file (rare), a case sensitivity failure in the filename, or a case
insensitivity failure in the podcast folder.

iTunes running on Windows 7 is stymied by case insensitivity under Windows. Or
rather, non-Windows systems are stymied by such case insensitivity when trying
to match filenames created in Windows to those stored in the iTunes database.

If it's just a filename case mismatch, and this isn't the result of duplication
of case-differing tracks, we rename the file in place. If the podcast folder has
a filename case mismatch, we duplicate the folder and its contents, and then
name the alternate folder with alternative case. (Copied files that don't match
up by podcast folder case will be marked as orphaned, per below.)

If all that is required is renaming a file or copying a folder, we return to
Step 3, above.

Otherwise, we make necessary changes in iTunes. If a track is
duplicated in iTunes, we delete the duplicate. If it is a filename duplication
resulting from manual sharding (and not already fixed by the VBscript, above),
we relink the track to the appropriate file in its parallel folder. If the
underlying file is simply missing, we delete the track that references it.

We then return to Step 1 above and repeat.

### Orphan Files

Any files that cannot be tied back to a track in the database at the end of this
process will be added to the CouchDB database as an orphaned track record.
Orphaned tracks will be prioritized, by age, for subsequent archival and weeding
by the new media management system, ahead of all tracks on the tail of the
master playlist.

### Feed Downloads

The last step in transferring the iTunes database to CouchDB will involve
replacing the feature of downloading new episodes of podcast feeds. Initially,
this will be provided as a processing step of the Classic iPod management
prototype. Eventually, however, it will be a discrete system service, and then
Elixir app, that will run on the RAID.

Once the prototype version of podcast feed downloads is implemented, full
retirement of the iTunes system will be achieved.

## Prototype
