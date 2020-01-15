# Copyright 2019 Beads Land-Trujillo

import re
import datetime
import urlparse
import HTMLParser

HTMLParser = HTMLParser.HTMLParser()

class LibraryException(Exception): pass

class Database:
  def __init__(self, path):
    self._path = path

  def __iter__(self):
    self._fp = open(self._path, 'r')
    self._skip_to("<dict>")
    self._state = self._parse_dict("<key>Tracks</key>")
    self._read_as("<dict>", "dict expected")
    return self

  def next(self):
    line = self._next_line()
    if line == "</dict>": return self._skip_playlists()
    if not re.match(r"<key>(.*)</key>", line):
      raise LibraryException("key expected: %s" % line)
    self._read_as("<dict>", "dict expected")

    value = self._parse_dict()
    value['iTunes Library'] = self._state
    return value

  def _next_line(self):
    return self._fp.readline().strip()

  def _skip_to(self, text):
    while True:
      if self._next_line() == text: break

  def _read_as(self, text, err):
    line = self._next_line()
    if line != text: raise LibraryException("%s: %s" % (err, line))

  def _skip_playlists(self):
    self.read_as("<key>Playlists</key>", "unexpected section")
    self._read_as("<dict>", "dict expected")
    self._read_as("<array>", "array expected")
    self._plists = {p['Name']: p for p in self._parse_array()}
    self._read_as("</dict>", "dict closure expected")
    self._read_as("</array>", "array closure expected")
    self._read_as("</dict>", "dict closure expected")
    self._read_as("</plist>", "property list closure expected")
    raise StopIteration

  def _parse_dict(self, next="</dict>"):
    dict = {}
    while True:
      line = self._next_line()
      if line == next: break

      k, v = self._parse_key_value(line)
      if k in dict:
        if type(dict[k]) is not list: dict[k] = [dict[k]]
        dict[k].append(v)
      else:
        dict[k] = v
    return dict

  def _parse_array(self):
    arr = []
    while True:
      line = self._next_line()
      if line == "</array>": break
      if line != "<dict>": raise LibraryException("expected dict: %s" % line)

      arr.append(self._parse_dict())
    return arr

  def _parse_key_value(self, line):
    m = re.match(r"<key>(.*)</key>(.*)", line)
    if not m: raise LibraryException("excpected key: %s" % line)

    (key, value) = m.group(1, 2)
    if value == "<true/>": return key, True
    if value == "<false/>": return key, False

    while not re.search("</[^>]+>", value):
      more = self._next_line()
      if more == "<array>": return key, self._parse_array()
      if more == "<data>": return key, self._parse_data()
      value = "%s\n%s" % (value, more)

    n = re.match(r"^<([^>]+)>([^<]+)</[^>]+>$", value)
    if n is None:
      raise LibraryException("expected container tag: %s"
                             % value.replace("\n", "\\n"))
    (type, value) = n.group(1, 2)
    if type == "date": return key, value
#    if type == "date":
#      dt = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
#      return key, savvy.common.Datetime(dt)
    if type == "string":
      return key, urlparse.unquote(HTMLParser.unescape(value.decode('utf-8')))
    if type == "integer": return key, int(value)
    if type == "float": return key, float(value)
    raise LibraryException("unknown type: %s: %s" \
                           % (type, value.replace("\n", "\\n")))

  def _parse_data():
    value = ""
    while not re.search("</data>", value):
      more = self._next_line()
      value = "%s\n%s" % (value, more)
    n = re.match(r"<data>([^<]+)</data>", value)
    return "data(%s)" % n.group(1).strip()
