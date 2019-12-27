#!/usr/bin/env python3

# https://medium.com/@leojosefm/python-analyzing-itunes-library-97bec60e13cb

import pandas as pd
import xml.etree.ElementTree as ET ## XML parsing
import urllib.parse
import struct
import binascii
import dateutil.parser
import datetime
import os

lib=os.path.expanduser("~/Qnap/Data/iTunes/iTunes Library.xml")

print("Parsing file...")

parser = ET.XMLParser(encoding="ISO 8859-1")
tree = ET.parse(lib, parser=parser)
root = tree.getroot()
main_dict=root.findall('dict')
for item in main_dict[0].getchildren():
    if item.tag=="dict":
        tracks_dict=item
        break
tracklist=list(tracks_dict.findall('dict'))

print("Extracting podcasts...")

podcast=[] #All podcast elements
itunesu=[]
#purchased=[] # All purchased music
#apple_music=[] # Music added to lirary through subscription
genre={}
for item in tracklist:
    x=item.getchildren()
    trigger = False
    for i in range(len(x)):

        if x[i].text=="Genre":
            genre[x[i+1].text]=genre.get(x[i+1].text,0)+1
        if x[i].text=="Kind":
            genre[x[i+1].text]=genre.get(x[i+1].text,0)+1

        if x[i].text=="Genre" and x[i+1].text=="Podcast":
            if not trigger: podcast.append(x)
            trigger = True
        if x[i].text=="Genre" and x[i+1].text.startswith("iTunes"):
            if not trigger: podcast.append(x)
            trigger = True

        if x[i].text=="Kind" and x[i+1].text.find("audio file") != -1:
            if not trigger: podcast.append(x)
            trigger = True
        if x[i].text=="Kind" and x[i+1].text.find("video file") != -1:
            if not trigger: podcast.append(x)
            trigger = True

#        if x[i].text=="Kind" and x[i+1].text=="Purchased AAC audio file":
#            purchased.append(item.getchildren())
#        if x[i].text=="Kind" and x[i+1].text=="Apple Music AAC audio file":
#            apple_music.append(item.getchildren())

genre = [(k, genre[k]) for k in sorted(genre, key=genre.get, reverse=False)]
for k, v in genre:
  print(v, k)

print("Number of tracks under Podcast: ",str(len(podcast)))
#print("Number of tracks Purchased: ",str(len(purchased)))
#print("Number of Music added thought Apple Music subscription: ",str(len(apple_music)))

def cols(kind):
    cols=[]
    for i in range(len(kind)):
        for j in range(len(kind[i])):
            if kind[i][j].tag=="key":
                cols.append(kind[i][j].text)
    return set(cols)

podcast_cols=cols(podcast)
#purchased_cols=cols(purchased)
#apple_music_cols=cols(apple_music)

print(podcast_cols)

print("Generating Lookup Table...")

#podcast = itunesu + podcast


def map_dates(kind):
#    df=pd.DataFrame(columns=cols)
#    dict1={}
  THRESH = dateutil.parser.parse("2020-01-01 00:00:00Z")
  with open('addtomod.txt', 'w') as f:
    for i in range(len(kind)):
        dict1 = {}
        print("%d of %d" % (i, len(kind)), end='\r')

        for j in range(len(kind[i])):
            if kind[i][j].tag=="key":
              if kind[i][j].text in ["Date Modified", "Date Added", "Location", "Persistent ID", "Play Count"]:
                dict1[kind[i][j].text]=kind[i][j+1].text

        added = dict1["Date Added"]
        modif = dict1.get("Date Modified", "1999-09-09 00:00:00")
        locat = dict1["Location"].replace("file://localhost/", "")
        locat = urllib.parse.unquote(locat)
        # https://stackoverflow.com/questions/6727041/itunes-persistent-id-music-library-xml-version-and-itunes-hex-version
        (highID, lowID) = struct.unpack('!ii', binascii.a2b_hex(dict1["Persistent ID"]))
        playc = int(dict1["Play Count"]) if "Play Count" in dict1 else 0
        if not locat.startswith("http://"):
          if dateutil.parser.parse(added) < THRESH:
            f.write("%s\t%s\t%s\t%d\t%d\t%d\n" % (added, locat, modif, highID, lowID, playc))


map_dates(podcast)



#        list_values=[i for i in dict1.values()]
#        list_keys=[j for j in dict1.keys()]
#        df_temp=pd.DataFrame([list_values],columns=list_keys)
#        df = pd.concat([df,df_temp],axis=0,ignore_index=True,sort=True)
#    return df
#df_apple_music = df_creation(apple_music,apple_music_cols)


#df_podcast = df_creation(podcast,podcast_cols)
#df_purchased = df_creation(purchased,purchased_cols)

#df_podcast[['track_id','play_count','skip_count','year_of_release']] = df_podcast[['track_id',\
#        'play_count','skip_count','year_of_release']].apply(pd.to_numeric)
#df_podcast[['play_date','skip_date','release_date','date_modified']] = df_podcast[['play_date',\
#        'skip_date','release_date','date_modified']].apply(pd.to_datetime)


#df = df_podcast[['Date Modified', 'Location', 'Date Added']]
