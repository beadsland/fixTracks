class ReprArray:
  def __init__(self, arr, max=3):
    if len(arr) > max:
      str = "+:%d" % (len(arr) - max)
      arr = arr[:max]
      arr.append(ReprLiteral(str))
    self.arr = arr

  def __repr__(self):
    return repr(self.arr)

class ReprLiteral:
  def __init__(self, str):
    self.str = str

  def __repr__(self):
    return self.str
