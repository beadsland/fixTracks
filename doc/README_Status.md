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


## Prototype
