[Back to Top](../README.md)

# README: Purpose

I currently maintain a 2 terabyte library of podcasts, which I listen to in a
somewhat unconventional manner. I've found that iTunes is increasingly inadequate
as a platform, and so I'm building out a custom media management system.

The issues at hand are fourfold:

## 1. Hardware

For many years piecemeal access to database content was maintained by improvising
a sharding strategy across several portable USB drives attached to a Windows 7
laptop, with frequent time-consuming backups, also to portable USB drives.

Eventually these files were consolidated to a Qnap RAID mirroring between two
hard drives large enough to store the entire collection. This eliminates the
reliance on a manual sharding process, but also eliminates the cost and effort
of backing up portable USB drives.

### Data Storage

Admittedly, this is not a disaster recovery policy, but rather just an attempt
to avoid losing even fractions of a terabyte of data to hard drive failure.

With respect to the custom media management application, the long-term plan is
to integrate peer-to-peer file-sharing features. This will primarily serve to
proactively transfer files to client devices on a just-in-time basis. However,
this also allows for the future possibility of leveraging mesh data storage to
keep redundant copies of historical podcast episodes once those files age out
of their publisher's podcast feeds.

### Operating System

I currently work on an Ubuntu setup, and do not actively maintain a MacOS or
Windows environment. A Windows 7 virtual machine under Qnap Virtualization
Station is the current home of iTunes. The goal is to abandon reliance on Apple's
software in favor of a pure GNU/Linux solution capable of driving Classic iPod,
Android, and pod-kintosh Pi front-ends.

## 2. Performance

The current `iTunes Library.itl` file is just shy of 75 megabytes, which iTunes
somehow expands to over half a gigabyte of active system memory when loaded.
Unfortunately, iTunes seems not to be optimized for managing large data sets,
as every UI operation, including switching views and scrolling through listings,
can take minutes at a time.

> It should be noted that I have held back iTunes to version 11, rather than
> upgrade to the most recent version. My understanding has been that later
> versions of the iTunes database are more stringently locked down so as to
> prevent third-party inspection and modification. As the goal is to extract
> the entirety of the database to another platform, I didn't want to risk
> irrevocable complications that an upgrade might entail.
>
> This does, however, leave open the possibility that performance issues arising
> from abnormally large databases that plague iTunes 11 haven't been rectified
> in later major versions of the same software. Somehow, I doubt this is the
> case, however--if only because abnormally large databases are not the use case
> iTunes would seem to be optimized for.

The goal is to migrate this data set to a CouchDB data environment. CouchDB
implements indices with build-once, read-many-times B-trees. This, coupled with
map-reduce design documents and view parameterization means that UI operations
will need only to query for the records to be displayed--not rebuild the entirety
of a view for every display operation, as iTunes would seem to be doing under
the hood.

Native replication support means that CouchDB also offers the opportunity to
better integrate client devices. Classic iPods could be synced remotely from a
remote laptop from off-site without reliance on the mounting of network shares
over a VPN. Android and Pi devices, meanwhile, could maintain their own replicas
of the database and update playlists (based on activity across devices) in near
real-time. Publishing and sharing of listening histories and prospective
playlists also become a possibility.

## 3. Savvy Playlists

There are a number of methods for constructing playlists that, while trivial to
implement, are simply unavailable in iTunes, even using smart playlists. These
serve admittedly odd use-cases, but as they are my, personal, use-cases, that's
what I'm building for.

Playlist design would offer more complex features for organizing tracks and also
for chaining features together in pipelines. The typical use-case will involve
multiple pipelines consolidated into one or more master listening playlists. The
entire architecture is referred to as _savvy_ playlists.

_See_ [README: Playlists](README_Playlists.md)

## 4. Advanced Features

Imagine:

  * a scrobbleblogging platform that allows for commenting on and discussing
  tracks before and after listening to them;

  * pie charts and other graphs of listening habits by podcast, genre, publisher
  or other folksonomic tag, readily shareable on popular platforms;

  * using the same graphing tools to organize patreon, paypal and other
  contributions to publishers as a function of listening patterns.
