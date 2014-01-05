#
# Autogenerated by Thrift Compiler (0.9.0)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py:twisted,new_style
#

from thrift.Thrift import TType, TMessageType, TException, TApplicationException

from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol, TProtocol
try:
  from thrift.protocol import fastbinary
except:
  fastbinary = None


class ErrorType(object):
  NoError = 0
  Server = 1
  Network = 2
  Authentication = 3
  Validation = 4
  Other = 5
  NotImplemented = 6
  FileNotFound = 7

  _VALUES_TO_NAMES = {
    0: "NoError",
    1: "Server",
    2: "Network",
    3: "Authentication",
    4: "Validation",
    5: "Other",
    6: "NotImplemented",
    7: "FileNotFound",
  }

  _NAMES_TO_VALUES = {
    "NoError": 0,
    "Server": 1,
    "Network": 2,
    "Authentication": 3,
    "Validation": 4,
    "Other": 5,
    "NotImplemented": 6,
    "FileNotFound": 7,
  }

class ArchiveStatus(object):
  Completed = 0
  InProgress = 1
  Paused = 2
  Stopped = 3
  Failed = 4
  Local = 5

  _VALUES_TO_NAMES = {
    0: "Completed",
    1: "InProgress",
    2: "Paused",
    3: "Stopped",
    4: "Failed",
    5: "Local",
  }

  _NAMES_TO_VALUES = {
    "Completed": 0,
    "InProgress": 1,
    "Paused": 2,
    "Stopped": 3,
    "Failed": 4,
    "Local": 5,
  }

class CertExportFormat(object):
  HTML = 0
  YAML = 1
  PDF = 2

  _VALUES_TO_NAMES = {
    0: "HTML",
    1: "YAML",
    2: "PDF",
  }

  _NAMES_TO_VALUES = {
    "HTML": 0,
    "YAML": 1,
    "PDF": 2,
  }


class InvalidOperation(TException):
  """
  Attributes:
   - what
   - why
   - filename
  """

  thrift_spec = (
    None, # 0
    (1, TType.I32, 'what', None, None, ), # 1
    (2, TType.STRING, 'why', None, None, ), # 2
    (3, TType.STRING, 'filename', None, None, ), # 3
  )

  def __init__(self, what=None, why=None, filename=None,):
    self.what = what
    self.why = why
    self.filename = filename

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.I32:
          self.what = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.why = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.STRING:
          self.filename = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('InvalidOperation')
    if self.what is not None:
      oprot.writeFieldBegin('what', TType.I32, 1)
      oprot.writeI32(self.what)
      oprot.writeFieldEnd()
    if self.why is not None:
      oprot.writeFieldBegin('why', TType.STRING, 2)
      oprot.writeString(self.why)
      oprot.writeFieldEnd()
    if self.filename is not None:
      oprot.writeFieldBegin('filename', TType.STRING, 3)
      oprot.writeString(self.filename)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __str__(self):
    return repr(self)

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class DateInfo(object):
  """
  Attributes:
   - Day
   - Month
   - Year
   - Hour
   - Minutes
   - Seconds
  """

  thrift_spec = (
    None, # 0
    (1, TType.I32, 'Day', None, None, ), # 1
    (2, TType.I32, 'Month', None, None, ), # 2
    (3, TType.I32, 'Year', None, None, ), # 3
    (4, TType.I32, 'Hour', None, None, ), # 4
    (5, TType.I32, 'Minutes', None, None, ), # 5
    (6, TType.I32, 'Seconds', None, None, ), # 6
  )

  def __init__(self, Day=None, Month=None, Year=None, Hour=None, Minutes=None, Seconds=None,):
    self.Day = Day
    self.Month = Month
    self.Year = Year
    self.Hour = Hour
    self.Minutes = Minutes
    self.Seconds = Seconds

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.I32:
          self.Day = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.I32:
          self.Month = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.I32:
          self.Year = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.I32:
          self.Hour = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 5:
        if ftype == TType.I32:
          self.Minutes = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 6:
        if ftype == TType.I32:
          self.Seconds = iprot.readI32();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('DateInfo')
    if self.Day is not None:
      oprot.writeFieldBegin('Day', TType.I32, 1)
      oprot.writeI32(self.Day)
      oprot.writeFieldEnd()
    if self.Month is not None:
      oprot.writeFieldBegin('Month', TType.I32, 2)
      oprot.writeI32(self.Month)
      oprot.writeFieldEnd()
    if self.Year is not None:
      oprot.writeFieldBegin('Year', TType.I32, 3)
      oprot.writeI32(self.Year)
      oprot.writeFieldEnd()
    if self.Hour is not None:
      oprot.writeFieldBegin('Hour', TType.I32, 4)
      oprot.writeI32(self.Hour)
      oprot.writeFieldEnd()
    if self.Minutes is not None:
      oprot.writeFieldBegin('Minutes', TType.I32, 5)
      oprot.writeI32(self.Minutes)
      oprot.writeFieldEnd()
    if self.Seconds is not None:
      oprot.writeFieldBegin('Seconds', TType.I32, 6)
      oprot.writeI32(self.Seconds)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class TransferStatus(object):
  """
  Attributes:
   - StatusDescription
   - ETA
   - RemainingBytes
   - Progress
   - Status
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'StatusDescription', None, None, ), # 1
    (2, TType.STRING, 'ETA', None, None, ), # 2
    (3, TType.I64, 'RemainingBytes', None, None, ), # 3
    (4, TType.DOUBLE, 'Progress', None, None, ), # 4
    (5, TType.I32, 'Status', None, None, ), # 5
  )

  def __init__(self, StatusDescription=None, ETA=None, RemainingBytes=None, Progress=None, Status=None,):
    self.StatusDescription = StatusDescription
    self.ETA = ETA
    self.RemainingBytes = RemainingBytes
    self.Progress = Progress
    self.Status = Status

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.StatusDescription = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.ETA = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.I64:
          self.RemainingBytes = iprot.readI64();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.DOUBLE:
          self.Progress = iprot.readDouble();
        else:
          iprot.skip(ftype)
      elif fid == 5:
        if ftype == TType.I32:
          self.Status = iprot.readI32();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('TransferStatus')
    if self.StatusDescription is not None:
      oprot.writeFieldBegin('StatusDescription', TType.STRING, 1)
      oprot.writeString(self.StatusDescription)
      oprot.writeFieldEnd()
    if self.ETA is not None:
      oprot.writeFieldBegin('ETA', TType.STRING, 2)
      oprot.writeString(self.ETA)
      oprot.writeFieldEnd()
    if self.RemainingBytes is not None:
      oprot.writeFieldBegin('RemainingBytes', TType.I64, 3)
      oprot.writeI64(self.RemainingBytes)
      oprot.writeFieldEnd()
    if self.Progress is not None:
      oprot.writeFieldBegin('Progress', TType.DOUBLE, 4)
      oprot.writeDouble(self.Progress)
      oprot.writeFieldEnd()
    if self.Status is not None:
      oprot.writeFieldBegin('Status', TType.I32, 5)
      oprot.writeI32(self.Status)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class ArchiveInfo(object):
  """
  Attributes:
   - Title
   - Description
   - SizeInBytes
   - CreatedDate
   - Md5HexDigits
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'Title', None, None, ), # 1
    (2, TType.STRING, 'Description', None, None, ), # 2
    (3, TType.I64, 'SizeInBytes', None, None, ), # 3
    (4, TType.STRUCT, 'CreatedDate', (DateInfo, DateInfo.thrift_spec), None, ), # 4
    (5, TType.STRING, 'Md5HexDigits', None, None, ), # 5
  )

  def __init__(self, Title=None, Description=None, SizeInBytes=None, CreatedDate=None, Md5HexDigits=None,):
    self.Title = Title
    self.Description = Description
    self.SizeInBytes = SizeInBytes
    self.CreatedDate = CreatedDate
    self.Md5HexDigits = Md5HexDigits

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.Title = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.Description = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.I64:
          self.SizeInBytes = iprot.readI64();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.STRUCT:
          self.CreatedDate = DateInfo()
          self.CreatedDate.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 5:
        if ftype == TType.STRING:
          self.Md5HexDigits = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('ArchiveInfo')
    if self.Title is not None:
      oprot.writeFieldBegin('Title', TType.STRING, 1)
      oprot.writeString(self.Title)
      oprot.writeFieldEnd()
    if self.Description is not None:
      oprot.writeFieldBegin('Description', TType.STRING, 2)
      oprot.writeString(self.Description)
      oprot.writeFieldEnd()
    if self.SizeInBytes is not None:
      oprot.writeFieldBegin('SizeInBytes', TType.I64, 3)
      oprot.writeI64(self.SizeInBytes)
      oprot.writeFieldEnd()
    if self.CreatedDate is not None:
      oprot.writeFieldBegin('CreatedDate', TType.STRUCT, 4)
      self.CreatedDate.write(oprot)
      oprot.writeFieldEnd()
    if self.Md5HexDigits is not None:
      oprot.writeFieldBegin('Md5HexDigits', TType.STRING, 5)
      oprot.writeString(self.Md5HexDigits)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class Capsule(object):
  """
  Attributes:
   - Created
   - ID
   - Resource_URI
   - Title
   - User
   - ExpirationDate
   - TotalSizeInBytes
   - AvailableSizeInBytes
   - CapsuleContents
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'Created', None, None, ), # 1
    (2, TType.STRING, 'ID', None, None, ), # 2
    (3, TType.STRING, 'Resource_URI', None, None, ), # 3
    (4, TType.STRING, 'Title', None, None, ), # 4
    (5, TType.STRING, 'User', None, None, ), # 5
    (6, TType.STRUCT, 'ExpirationDate', (DateInfo, DateInfo.thrift_spec), None, ), # 6
    (7, TType.I64, 'TotalSizeInBytes', None, None, ), # 7
    (8, TType.I64, 'AvailableSizeInBytes', None, None, ), # 8
    (9, TType.LIST, 'CapsuleContents', (TType.STRUCT,(ArchiveInfo, ArchiveInfo.thrift_spec)), None, ), # 9
  )

  def __init__(self, Created=None, ID=None, Resource_URI=None, Title=None, User=None, ExpirationDate=None, TotalSizeInBytes=None, AvailableSizeInBytes=None, CapsuleContents=None,):
    self.Created = Created
    self.ID = ID
    self.Resource_URI = Resource_URI
    self.Title = Title
    self.User = User
    self.ExpirationDate = ExpirationDate
    self.TotalSizeInBytes = TotalSizeInBytes
    self.AvailableSizeInBytes = AvailableSizeInBytes
    self.CapsuleContents = CapsuleContents

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.Created = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.ID = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.STRING:
          self.Resource_URI = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.STRING:
          self.Title = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 5:
        if ftype == TType.STRING:
          self.User = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 6:
        if ftype == TType.STRUCT:
          self.ExpirationDate = DateInfo()
          self.ExpirationDate.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 7:
        if ftype == TType.I64:
          self.TotalSizeInBytes = iprot.readI64();
        else:
          iprot.skip(ftype)
      elif fid == 8:
        if ftype == TType.I64:
          self.AvailableSizeInBytes = iprot.readI64();
        else:
          iprot.skip(ftype)
      elif fid == 9:
        if ftype == TType.LIST:
          self.CapsuleContents = []
          (_etype3, _size0) = iprot.readListBegin()
          for _i4 in xrange(_size0):
            _elem5 = ArchiveInfo()
            _elem5.read(iprot)
            self.CapsuleContents.append(_elem5)
          iprot.readListEnd()
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('Capsule')
    if self.Created is not None:
      oprot.writeFieldBegin('Created', TType.STRING, 1)
      oprot.writeString(self.Created)
      oprot.writeFieldEnd()
    if self.ID is not None:
      oprot.writeFieldBegin('ID', TType.STRING, 2)
      oprot.writeString(self.ID)
      oprot.writeFieldEnd()
    if self.Resource_URI is not None:
      oprot.writeFieldBegin('Resource_URI', TType.STRING, 3)
      oprot.writeString(self.Resource_URI)
      oprot.writeFieldEnd()
    if self.Title is not None:
      oprot.writeFieldBegin('Title', TType.STRING, 4)
      oprot.writeString(self.Title)
      oprot.writeFieldEnd()
    if self.User is not None:
      oprot.writeFieldBegin('User', TType.STRING, 5)
      oprot.writeString(self.User)
      oprot.writeFieldEnd()
    if self.ExpirationDate is not None:
      oprot.writeFieldBegin('ExpirationDate', TType.STRUCT, 6)
      self.ExpirationDate.write(oprot)
      oprot.writeFieldEnd()
    if self.TotalSizeInBytes is not None:
      oprot.writeFieldBegin('TotalSizeInBytes', TType.I64, 7)
      oprot.writeI64(self.TotalSizeInBytes)
      oprot.writeFieldEnd()
    if self.AvailableSizeInBytes is not None:
      oprot.writeFieldBegin('AvailableSizeInBytes', TType.I64, 8)
      oprot.writeI64(self.AvailableSizeInBytes)
      oprot.writeFieldEnd()
    if self.CapsuleContents is not None:
      oprot.writeFieldBegin('CapsuleContents', TType.LIST, 9)
      oprot.writeListBegin(TType.STRUCT, len(self.CapsuleContents))
      for iter6 in self.CapsuleContents:
        iter6.write(oprot)
      oprot.writeListEnd()
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class Archive(object):
  """
  Attributes:
   - LocalID
   - Status
   - Info
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'LocalID', None, None, ), # 1
    (2, TType.I32, 'Status', None, None, ), # 2
    (3, TType.STRUCT, 'Info', (ArchiveInfo, ArchiveInfo.thrift_spec), None, ), # 3
  )

  def __init__(self, LocalID=None, Status=None, Info=None,):
    self.LocalID = LocalID
    self.Status = Status
    self.Info = Info

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.LocalID = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.I32:
          self.Status = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.STRUCT:
          self.Info = ArchiveInfo()
          self.Info.read(iprot)
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('Archive')
    if self.LocalID is not None:
      oprot.writeFieldBegin('LocalID', TType.STRING, 1)
      oprot.writeString(self.LocalID)
      oprot.writeFieldEnd()
    if self.Status is not None:
      oprot.writeFieldBegin('Status', TType.I32, 2)
      oprot.writeI32(self.Status)
      oprot.writeFieldEnd()
    if self.Info is not None:
      oprot.writeFieldBegin('Info', TType.STRUCT, 3)
      self.Info.write(oprot)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class Signature(object):
  """
  Attributes:
   - ArchiveID
   - DateCreated
   - UploaderName
   - UploaderEmail
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'ArchiveID', None, None, ), # 1
    (2, TType.STRUCT, 'DateCreated', (DateInfo, DateInfo.thrift_spec), None, ), # 2
    (3, TType.STRING, 'UploaderName', None, None, ), # 3
    (4, TType.STRING, 'UploaderEmail', None, None, ), # 4
  )

  def __init__(self, ArchiveID=None, DateCreated=None, UploaderName=None, UploaderEmail=None,):
    self.ArchiveID = ArchiveID
    self.DateCreated = DateCreated
    self.UploaderName = UploaderName
    self.UploaderEmail = UploaderEmail

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.ArchiveID = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRUCT:
          self.DateCreated = DateInfo()
          self.DateCreated.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.STRING:
          self.UploaderName = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.STRING:
          self.UploaderEmail = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('Signature')
    if self.ArchiveID is not None:
      oprot.writeFieldBegin('ArchiveID', TType.STRING, 1)
      oprot.writeString(self.ArchiveID)
      oprot.writeFieldEnd()
    if self.DateCreated is not None:
      oprot.writeFieldBegin('DateCreated', TType.STRUCT, 2)
      self.DateCreated.write(oprot)
      oprot.writeFieldEnd()
    if self.UploaderName is not None:
      oprot.writeFieldBegin('UploaderName', TType.STRING, 3)
      oprot.writeString(self.UploaderName)
      oprot.writeFieldEnd()
    if self.UploaderEmail is not None:
      oprot.writeFieldBegin('UploaderEmail', TType.STRING, 4)
      oprot.writeString(self.UploaderEmail)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class Certificate(object):
  """
  Attributes:
   - HexDigitsKey
   - Sig
   - RelatedArchive
   - LocalID
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'HexDigitsKey', None, None, ), # 1
    (2, TType.STRUCT, 'Sig', (Signature, Signature.thrift_spec), None, ), # 2
    (3, TType.STRUCT, 'RelatedArchive', (ArchiveInfo, ArchiveInfo.thrift_spec), None, ), # 3
    (4, TType.STRING, 'LocalID', None, None, ), # 4
  )

  def __init__(self, HexDigitsKey=None, Sig=None, RelatedArchive=None, LocalID=None,):
    self.HexDigitsKey = HexDigitsKey
    self.Sig = Sig
    self.RelatedArchive = RelatedArchive
    self.LocalID = LocalID

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.HexDigitsKey = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRUCT:
          self.Sig = Signature()
          self.Sig.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.STRUCT:
          self.RelatedArchive = ArchiveInfo()
          self.RelatedArchive.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.STRING:
          self.LocalID = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('Certificate')
    if self.HexDigitsKey is not None:
      oprot.writeFieldBegin('HexDigitsKey', TType.STRING, 1)
      oprot.writeString(self.HexDigitsKey)
      oprot.writeFieldEnd()
    if self.Sig is not None:
      oprot.writeFieldBegin('Sig', TType.STRUCT, 2)
      self.Sig.write(oprot)
      oprot.writeFieldEnd()
    if self.RelatedArchive is not None:
      oprot.writeFieldBegin('RelatedArchive', TType.STRUCT, 3)
      self.RelatedArchive.write(oprot)
      oprot.writeFieldEnd()
    if self.LocalID is not None:
      oprot.writeFieldBegin('LocalID', TType.STRING, 4)
      oprot.writeString(self.LocalID)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class Settings(object):
  """
  Attributes:
   - StoredUserName
   - StoredPassword
   - RememberMe
   - ArchivesFolder
   - CertificatesFolder
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'StoredUserName', None, None, ), # 1
    (2, TType.STRING, 'StoredPassword', None, None, ), # 2
    (3, TType.BOOL, 'RememberMe', None, None, ), # 3
    (4, TType.STRING, 'ArchivesFolder', None, None, ), # 4
    (5, TType.STRING, 'CertificatesFolder', None, None, ), # 5
  )

  def __init__(self, StoredUserName=None, StoredPassword=None, RememberMe=None, ArchivesFolder=None, CertificatesFolder=None,):
    self.StoredUserName = StoredUserName
    self.StoredPassword = StoredPassword
    self.RememberMe = RememberMe
    self.ArchivesFolder = ArchivesFolder
    self.CertificatesFolder = CertificatesFolder

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.StoredUserName = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.StoredPassword = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.BOOL:
          self.RememberMe = iprot.readBool();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.STRING:
          self.ArchivesFolder = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 5:
        if ftype == TType.STRING:
          self.CertificatesFolder = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('Settings')
    if self.StoredUserName is not None:
      oprot.writeFieldBegin('StoredUserName', TType.STRING, 1)
      oprot.writeString(self.StoredUserName)
      oprot.writeFieldEnd()
    if self.StoredPassword is not None:
      oprot.writeFieldBegin('StoredPassword', TType.STRING, 2)
      oprot.writeString(self.StoredPassword)
      oprot.writeFieldEnd()
    if self.RememberMe is not None:
      oprot.writeFieldBegin('RememberMe', TType.BOOL, 3)
      oprot.writeBool(self.RememberMe)
      oprot.writeFieldEnd()
    if self.ArchivesFolder is not None:
      oprot.writeFieldBegin('ArchivesFolder', TType.STRING, 4)
      oprot.writeString(self.ArchivesFolder)
      oprot.writeFieldEnd()
    if self.CertificatesFolder is not None:
      oprot.writeFieldBegin('CertificatesFolder', TType.STRING, 5)
      oprot.writeString(self.CertificatesFolder)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class VersionInfo(object):
  """
  Attributes:
   - version
   - description
   - uri
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'version', None, None, ), # 1
    (2, TType.STRING, 'description', None, None, ), # 2
    (3, TType.STRING, 'uri', None, None, ), # 3
  )

  def __init__(self, version=None, description=None, uri=None,):
    self.version = version
    self.description = description
    self.uri = uri

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.version = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.description = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.STRING:
          self.uri = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('VersionInfo')
    if self.version is not None:
      oprot.writeFieldBegin('version', TType.STRING, 1)
      oprot.writeString(self.version)
      oprot.writeFieldEnd()
    if self.description is not None:
      oprot.writeFieldBegin('description', TType.STRING, 2)
      oprot.writeString(self.description)
      oprot.writeFieldEnd()
    if self.uri is not None:
      oprot.writeFieldBegin('uri', TType.STRING, 3)
      oprot.writeString(self.uri)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)
