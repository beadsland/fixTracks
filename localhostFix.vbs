Option Explicit

Wscript.Echo "Setting up objects..."
Dim iTunes, Tracks
Set iTunes=CreateObject("iTunes.Application")
Set Tracks=iTunes.LibraryPlaylist.Tracks

Dim objStream, ModLookup, TZOffset
Set objStream = CreateObject("ADODB.Stream")
Set ModLookup = CreateObject("Scripting.Dictionary")
TZOffset = GetTimeZoneOffset / 24

'''
' Main program
'''
LoadModLookup
FixArchives

'''
' Relink Archived Podcasts to iTunes Media paths of media files
'''
Sub FixArchives()
  Wscript.Echo "Fixing archives..."
  Dim I, Location, count, T
  count = Tracks.Count
  For I = 1 to count
    Wscript.Stdout.Write chr(13) & "# " & I & " of " & count & " > "
    Set T = PersistentObject(Tracks(I))
    If T.Kind=1 Then
      If InStr(T.Location, "Archived Podcasts") Then
        FixArchiveTrack(Tracks(I))
      End If
    End If
  Next
  Wscript.Echo ""
End Sub

Sub FixArchiveTrack(T)
  Dim AddDate, I
  Wscript.Echo T.Location
  AddDate = CDate(T.DateAdded)

  Wscript.Echo AddDate & " " & ModLookup(AddDate)(T.Location)

End Sub

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
