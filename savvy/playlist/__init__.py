def repr_array(arr, plus=None):
  if not len(arr):
    out = "[]"
  elif len(arr) < 4:
    out = str(arr[:3])
  else:
    out = "%s, ... of %d]" % (str(arr[:3]).rstrip("]"), len(arr))

  if plus:
    return "%s + %s" % (out, plus)
  else:
    return out
