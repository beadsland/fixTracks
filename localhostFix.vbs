Option Explicit

Wscript.Echo "Setting up objects..."
Dim iTunes, Tracks
Set iTunes=CreateObject("iTunes.Application")
Set Tracks=iTunes.LibraryPlaylist.Tracks

Dim objStream, ModLookup, TZOffset
Set objStream = CreateObject("ADODB.Stream")
Set ModLookup = CreateObject("Scripting.Dictionary")
TZOffset = GetTimeZoneOffset / 24

Dim objFSO
Set objFSO = CreateObject("Scripting.FileSystemObject")

Dim totalFound, totalSeen

'''
' Main program
'''
'FixArchives 1000, 21000
'FixDriveLetter
'FindArchives

'''
' Consolidate all files onto same drive
'''
Sub FixDriveLetter()
  Wscript.Echo "Fixing drive letter..."

  Dim Letters
  Letters = Array("C", "E", "G")

  Dim I, Location, T, count, letter, newstr
  count = Tracks.Count
  For I = 1 to count
    Wscript.Stdout.Write chr(13) & "# " & I & " of " & count & " > "
    Set T = PersistentObject(Tracks(I))
    If T.Kind=1 Then
      For Each letter in Letters
        If InStr(T.Location, letter & ":\") Then
          If InStr(T.Location, "Archived Podcasts") = 0 Then
            Wscript.Echo T.Location
            newstr = Replace(T.Location, letter & ":\", "N:\")
            T.Location = newstr
          End If
        End If
      Next
    End If
  Next
  Wscript.Echo ""
  Wscript.Echo "Found " & totalFound & " of " & totalSeen
End Sub

'''
' Relink Archived Podcasts to iTunes Media paths of media files
'''
Sub FixArchives(first, last)
  LoadModLookup

  Wscript.Echo "Fixing archives..."

  totalFound = 0
  totalSeen = 0

  Dim start, count
  start = IIF(first, first, 1)
  count = IIF(last, last, Tracks.Count)

  Dim I, Location, T
  For I = start to count
    Wscript.Stdout.Write chr(13) & "# " & I & " of " & count & " > "
    Set T = PersistentObject(Tracks(I))
    If T.Kind=1 Then
      If InStr(T.Location, "Archived Podcasts") Then
        FixArchiveTrack Tracks(I), "G:\Archived Podcasts"
      End If
    End If
  Next
  Wscript.Echo ""
  Wscript.Echo "Found " & totalFound & " of " & totalSeen
End Sub

Sub FindArchives(first, last)
  LoadModLookup

  Wscript.Echo "Finding archives..."

  totalFound = 0
  totalSeen = 0

  Dim start, count
  start = IIF(first, first, 1)
  count = IIF(last, last, Tracks.Count)

  Dim I, Location, T
  For I = start to count
    Wscript.Stdout.Write chr(13) & "# " & I & " of " & count & " > "
    Set T = PersistentObject(Tracks(I))
    If T.Kind=1 Then
      If Not objFSO.FileExists(path) Then
        Wscript.Echo path
        Wscript.Quit
        ''FixArchiveTrack Tracks(I), "N:\iTunes\iTunes Media\Podcasts"
      End If
    End If
  Next
  Wscript.Echo ""
  Wscript.Echo "Found " & totalFound & " of " & totalSeen
End Sub

Sub FixArchiveTrack(T, prefix)
  Dim AddDate, ModDate, Dest
  AddDate = CDate(T.DateAdded)
  ModDate = ModLookup(AddDate)(T.Location)

  totalSeen = totalSeen + 1
  Dest = FindArchiveTrack(T.Location, ModDate)
  if Dest <> False Then
    Wscript.Echo Dest
    T.Location = Dest
    totalFound = totalFound + 1
  end if
End Sub

Function FindArchiveTrack(Location, ModDate, prefix)
  Wscript.Echo Location

  Dim Pref, Casc, path, I, NewDate
  Pref = "N:\iTunes\iTunes Media\Podcasts"
  Casc = Array(Pref, Pref & " Over", Pref & " Over Over", Pref & " Over Over Over")

  For Each path in Casc
    path = Replace(Location, prefix, path)

    If objFSO.FileExists(path) Then
      NewDate = objFSO.GetFile(path).DateCreated
      For I = -1 to +1
        If CDate(Cstr(NewDate + I/24)) = ModDate Then
          FindArchiveTrack = path
          Exit Function
        Else
          Wscript.Echo NewDate + I/24 & " <> " & ModDate
        End If
      Next
    End If
  Next
  FindArchiveTrack = False
End Function


'''
' Load table to look up Modified Date as a function of Added Date and Location
'''
Sub LoadModLookup()
  Wscript.Echo "Loading mod date lookups..."
  Dim strData, lines, count, I

  objStream.Type = 2 'text
  objStream.CharSet = "utf-8"
  objStream.Open
  objStream.LoadFromFile("addtomod.txt")
  strData = objStream.ReadText()
  objStream.Close

  lines = Split(strData, vbLf)
  count = Ubound(lines)
  For I=Lbound(lines) to count
    Wscript.Stdout.Write chr(13) & "# " & I & " of " & count & " > "
    Dim fields
    fields = Split(lines(I), vbTab)
    If Ubound(fields) = 2 Then
      AddModLookup LDate(fields(0)), fields(1), LDate(fields(2))
    End If
  Next
  Wscript.Echo ""
End Sub

Sub AddModLookup(AddDate, Location, ModDate)
  Wscript.Stdout.Write(AddDate & "     ")
  If Not ModLookup.Exists(AddDate) Then
    Dim dict
    Set dict = CreateObject("Scripting.Dictionary")
    ModLookup.Add AddDate, dict
  End If
  ModLookup(AddDate).Add Replace(Location, "/", "\"), ModDate
End Sub

'''
' Parse Zulu datestrings to local datetime
'''
Function LDate(Dstr)
  LDate = CDate(Cstr(fixmydate(Dstr) + TZOffset))
End Function

' https://stackoverflow.com/questions/2517306/does-vbscript-have-a-datetime-tryparse-equivalent'
Function fixmydate(mydate)
    Dim sday, smonth, syear
    Dim shour, sminute, ssecond
    Dim sdate

    syear = cint(Mid(mydate,1,4))
    smonth = cint(Mid(mydate,6,2))
    sday = cint(Mid(mydate,9,2))

    shour = cint(Mid(mydate,12,2))
    sminute = cint(Mid(mydate,15,2))
    ssecond = cint(Mid(mydate,18,2))

    sdate = DateSerial(syear,smonth,sday)
    sdate = dateadd("h",shour,sdate)
    sdate = dateadd("n",sminute,sdate)
    sdate = dateadd("s",ssecond,sdate)

    fixmydate = sdate
End Function

'''
' https://stackoverflow.com/questions/13980541/determine-my-time-zone-offset-using-vbscript
'''
Function GetTimeZoneOffset()
  Dim cItems, oItem
    Const sComputer = "."

    Dim oWmiService : Set oWmiService = _
        GetObject("winmgmts:{impersonationLevel=impersonate}!\\" _
                  & sComputer & "\root\cimv2")

    Set cItems = oWmiService.ExecQuery("SELECT * FROM Win32_ComputerSystem")

    For Each oItem In cItems
        GetTimeZoneOffset = oItem.CurrentTimeZone / 60
        Exit For
    Next
End Function

' https://stackoverflow.com/questions/20353072/how-to-do-a-single-line-if-statement-in-vbscript-for-classic-asp
Function IIf(bClause, sTrue, sFalse)
    If CBool(bClause) Then
        IIf = sTrue
    Else
        IIf = sFalse
    End If
End Function

' =========
' FindFiles
' =========
' Version 1.0.0.1 - July 5th 2018
' Copyright � Steve MacGuire 2011-2018
' http://samsoft.org.uk/iTunes/FindFiles.vbs
' Please visit http://samsoft.org.uk/iTunes/scripts.asp for updates

' =======
' Licence
' =======
' This program is free software: you can redistribute it and/or modify it under the terms
' of the GNU General Public License as published by the Free Software Foundation, either
' version 3 of the License, or (at your option) any later version.

' This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
' without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
' See the GNU General Public License for more details.

' Please visit http://www.gnu.org/licenses/gpl-3.0-standalone.html to view the GNU GPLv3 licence.

' Test for tracks which can be usefully updated
' Modified 2018-07-05
Function Updateable(T)
  Dim Key
  Updateable=False
  If Instr(T.KindAsString,"audio stream")=0 Then
    If T.Location="" Then
      Key=T.Size
      If Files.Exists(Key) Then
        If Files.Item(Key)<>"" Then Updateable=True               ' This script works with missing files, ignore streams
      End If
    End If
  End If
End Function

' Return the persistent object representing the track
' Keeps hold of an object that might vanish from a smart playlist as it is updated
' Modified 2014-05-15
Function PersistentObject(T)
  Dim Ext,L
  Set PersistentObject=T
  On Error Resume Next  ' Trap possible error
  L=T.Location
  If Err.Number<>0 Then
    Trace T,"Error reading location property from object."
  ElseIf L<>"" Then
    Ext=LCase(Right(L,4))
    If Instr(".ipa.ipg.m4r",Ext)=0 Then         ' Method below fails for apps, games & ringtones
      Set PersistentObject=iTunes.LibraryPlaylist.Tracks.ItemByPersistentID(iTunes.ITObjectPersistentIDHigh(T),iTunes.ITObjectPersistentIDLow(T))
    End If
  End If
End Function
