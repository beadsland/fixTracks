Option Explicit

Wscript.Echo "Setting up objects..."
Dim iTunes, Tracks
Set iTunes=CreateObject("iTunes.Application")
Set Tracks=iTunes.LibraryPlaylist.Tracks

Dim objStream, ModLookup
Set objStream = CreateObject("ADODB.Stream")
Set ModLookup = CreateObject("Scripting.Dictionary")

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
  Dim I, Location, count
  count = Tracks.Count
  For I = 1 to count
    Wscript.Stdout.Write "# " & I & " of " & count & "> " & chr(13)
    Location = Tracks(I).Location
    If InStr(Location, "Archived Podcasts") Then
      FixArchiveTrack(Tracks(I))
    End If
  Next
End Sub

Sub FixArchiveTrack(T)
  Wscript.Echo T.AddDate & " " & T.Location
  Wscript.Quit
End Sub

'''
' Load table to look up Modified Date as a function of Added Date and Location
'''
Sub LoadModLookup()
  Wscript.Echo "Loading mod date lookups..."
  Dim strData, lines, count

  objStream.CharSet = "utf-8"
  objStream.Open
  objStream.LoadFromFile("addtomod.txt")
  strData = objStream.ReadText()
  objStream.Close

  lines = Split(strData, vbCrLf)
  count = Ubound(lines)
  For I=1 to count
    Wscript.Stdout.Write "# " & I & " of " & count & "> " & chr(13)
    Dim fields
    fields = Split(line, vbTab)
    AddModLookup CDate(fields(1)), Location, CDate(fields(3))
  Next
End Sub

Sub AddModLookup(AddDate, Location, ModDate)
  If Not ModLookup.Exists(AddDate) Then
    ModLookup.Add(AddDate)
  End If
  ModLookup(AddDate).Add Location, ModDate
End Sub
