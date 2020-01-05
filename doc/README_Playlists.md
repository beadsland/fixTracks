[Back to Top](../README.md)

# README: Playlists

There are a number of methods for constructing playlists that, while trivial to
implement, are simply unavailable in iTunes, even using smart playlists. These
serve admittedly odd use-cases, but as they are my, personal, use-cases, that's
what I'm building for.

Playlist design would offer more complex features for organizing tracks and also
for chaining features together in pipelines. The typical use-case will involve
multiple pipelines consolidated into one or more master listening playlists. The
entire architecture is referred to as _savvy_ playlists.

## 1. Collation and Date Sorting

My preference is to alternate between listening to historical podcasts (dating
back to ca. 2005) in chronological order, and listening to contemporary podcasts
in reverse chronological order. Currently, this involves manually switching back
and forth between different playlists.

### Chronological Sorting

Unfortunately, these playlists, even in-and-of-themselves, don't accurately
reflect the state of the underlying database. To get a chronologically-ordered
list of all podcasts released in a given year, one must create a playlist large
enough (in gigabytes) to encompass every track released that year. If the
playlist is smaller than this, included tracks can either be randomly selected
or selected based on how recently they were downloaded (not how recently they
were released). This means tracks that ought to be included in, even lead, a
playlist may be omitted simply because of when they were downloaded relative to
others.

Of course, this could be solved by merely maintaining a large enough gigabyte
cap on said playlist to accomodate all tracks in a given year. Which is fine in
iTunes, not so useful when syncing all the tracks of such a playlist to a
portable or mobile device with limited storage capacity.

Essentially, the problem is that while iTunes provides for sorting tracks in a
playlist by release date, it does not provide for including tracks--prior to
sorting them--in the same playlist by release date. A CouchDB view ordered by
release date would address both simultaneously.

### Collation of Playlists

Take two playlists, and specify a ratio of how many minutes of one to serve in
relation to the other. When compiled, the collated playlist would seek to
maintain a balance of tracks according to said ratio. In a one-to-one ratio
configuration, after an hour long track from one playlist, play tracks from the
other until at least an hour of tracks have been added, then add another track
from the first, and so on.

This feature would also recognize if a track from one source playlist is present
in or has already been supplied by the other, and count the track against the
playing time contributed by both playlists. This contribution might optionally
be weighted.

One use case for this weighted contribution feature: I want to shuffle in music
tracks in ratio to my podcast minutes. A few of my podcasts are music news
programs, which I would weight at a fraction of a music-only track. The resulting
collated playlist would thus balance random music tracks against in-feed music
news tracks.

## 2. Staggering

Some podcast feeds will drop multiple tracks on or around the same release
datetime. This can sometimes result in many hours of content from a single feed
being clustered together to the exclusion of other feeds. This is also an issue
for historical playlists with tracks that predate most of the rest of the
library or were published without a release date.

A staggered playlist would track how many minutes have been allotted to each
feed, and--as per collation--defer serving tracks from feeds that are already
over-represented, until such time as other feeds have filled in the playlist.

The staggering (and also the aforementioned collation) feature would take into
account play history, such that playlists that, for instance, only include
unplayed tracks will nonetheless base deferment of content based on overall
listening history, rather than just the current content of source playlists.

## 3. De-duplication

Here there are two issues: one concerning content, the other retrieval.

In the content condition, there are times when tracks may appear multiple times
in the same feed or across related feeds. A de-duplication playlist will allow
for various heuristics for identifying duplicates, and withhold duplicated tracks.
A provision may also be provided for marking such tracks as duplicate and thus
candidates for weeding (see below).

In the retrieval condition, when set to download all unlistened content, iTunes
will sometimes hiccup and redownload the entirety of a podcast feed. It is
assumed that feed publishers are making changes to their feed that lead iTunes
to recognize it as all new content. In one case, a daily feed of regional
political commentary was redowloading hundreds of tracks to iTunes every day for
weeks before I realized it was happening and unsubscribed.

The new system will track the release date of the last track successfully
downloaded for each feed, and only affirmatively add to the download queue those
tracks from after that release date. A secondary process will track changes in
podcast feeds in order to identify unique tracks that may have been retroactively
added by publishers, by matching those feeds against prior downloads.

## 4. Pruning and Updating

While of no relevance for use on Classic iPods, which receive their playlists
and tracks by sync over a proprietary USB cable, and are otherwise offline, in
the case of Android and Pi devices with wifi (and even mobile) connectivity,
live updating of playlists will be profoundly useful.

Unlike traditional playlists, as represented by iTunes and iPod playlists, which
are static (even if dynamically generated) lists of tracks, savvy playlists will
be represented a bounded play history, a now-playing index, or _needle_, and a
future play roster. The UI will typically display the needle track followed by
the play roster, but the play history will be readily available for view.

Tracks in the play history will be candidates for removal from local storage by
time-since-played, to make room for staging tracks from the play roster. That
said, a track may appear in both the roster and the history, in the case where
it has been previously played or skipped and yet has been requeued by the play
roster.

### The Needle

Once the needle track is played or skipped, it is moved to the play history. By
default, the next track moves from the play roster to the needle. Alternatively,
a user may browse the roster or history and select that track to be played,
resumed or replayed in the needle, removing said track from its position in the
roster or history.

A mechanism to "rewind" playback a specified number of minutes--in the event of
a client being inadvertently left in unattended play mode, for instance--
effectively unwinding play history for one or more tracks, will also be provided.

As selecting tracks out of playlist order may have consequence for weighted
ordering (collation and staggering), play history and the current needle can
then be referenced to rebuild the play roster on-the-fly. This will also occur
in the event that new podcast downloads are picked up by reverse chronological
playlists. These tracks will be added to the play roster irrespective of their
release time with respect to the current needle track.

## 5. Preferential Sorting

There are times when a track comes up in a playlist that one just does want to
listen to, but doesn't want to listen to in the moment. A preferential playlist
can re-add such a track to the play roster, but defer it by a configured number
of hours, so that it will hopefully return to the needle at a more optimal time
for listening. A multiplier can also be applied so that, if a track is repeatedly
skipped over many days, it eventually will be deferred into the oblivion. (See
weeding, below.)

Moreover, there are times when a podcast seems compelling at the time downloaded,
but proves to be less interesting than anticipated. Here, the history of all
skips within the podcast (or a time-bound segment thereof) can be taken into
account, and applied as a deferral factor to all tracks in that podcast. With
the result that especially frequently skipped podcasts being deferred into
oblivion.

## 6. Archival and Weeding

My podcast archive is presently well over 2 terabytes of mp3 and other files,
representing over three-and-a-half years of continuous listening. New content
is added from podcast feeds daily, and I often add entirely new feeds to the
database. Obviously, even listening at both ends of the chronological candle,
it is unlikely that I'm going to ever listen to everything in the database.

A reverse listing of the master playlist will be used to identify those tracks
that, baring significant changes to playlist pipelines, are least likely to
ever be listened to. These tracks will first be compressed to save disk space,
and then beyond a set storage threshold, marked deleted in the CouchDB database
and purged from the hard drive.

A bias will be included to preserve older tracks no longer or likely soon to be
removed from publisher podcast feeds longer than newer tracks that are more
likely to still be available from a publisher's server if wanted. When peer-by-
peer file sharing functionality has been incorporated, peers may also negotiate
archival storage between themselves, such that tracks may be retrieved for
research or reference long after their publishers drop them or even go offline.

## 7. Contextual and Comingling

Do you listen to your playlist on speakers at the office, but some feeds are
NSFW? Do you listen when you're trying to fall asleep and prefer to omit anxiety-
inducing news podcasts at night? Contextual playlists will filter the master
playlist based on tagged criteria, effectively deferring unwanted tracks until
such time as context has changed.

Similarly, in the ideal world where more folk than me are using this playlist
management system, imagine subscribing to a friend's playlist, and having that
playlist collated into your own as if it were a discrete podcast of its own.

Alternatively, lets say two users of this system were listening to podcasts on
speakers from the same device. A comingled playlist could offer up the subset
of unlistened podcasts that are on both user's master playlists, deferring tracks
not mutually listed until each is listening again on their own.

Similar use cases could be imagined for music listening, where dozens of
attendees at a party or even on a virtual channel could register their preferred
music playlists to a comingled playlist device that queues up tracks based on
consensus preference for those tracks.
