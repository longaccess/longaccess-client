import yaml
import sys
import json
import mmap
import re
try:
    import pyaml
except ImportError:
    pyaml = None
from lacli.cipher import cipher_modes, new_key
from yaml import SafeLoader
from yaml import SafeDumper
from lacli.exceptions import InvalidArchiveError
from lacli.date import parse_timestamp, today, later, format_timestamp, epoch
from datetime import datetime
from base64 import b64encode, b64decode


class PrettySafeLoader(SafeLoader):
    pass


class BaseYAMLObject(yaml.YAMLObject):
    yaml_loader = PrettySafeLoader
    yaml_dumper = SafeDumper

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_mapping(cls.yaml_tag, data.__dict__)


class Archive(BaseYAMLObject):
    """
    >>> meta = Meta('zip', 'aes-256-ctr', size=1024, created='now')
    >>> archive = Archive('title', meta, tags=['foo', 'bar'])
    >>> archive.title
    'title'
    >>> archive.description
    >>> archive.meta.cipher
    'aes-256-ctr'
    >>> archive.meta.size
    1024
    >>> archive.meta.created
    'now'
    >>> archive.tags[1]
    'bar'
    >>> archive.description = 'what a wonderful dataset'
    >>> archive.description
    'what a wonderful dataset'
    >>> Archive('title', meta, description='worthless junk').description
    'worthless junk'
    >>> pyaml.dump(Archive('foo', meta), sys.stdout)
    !archive
    meta: !meta
      cipher: aes-256-ctr
      created: now
      format: zip
      size: 1024
    title: foo
    """
    yaml_tag = u'!archive'
    title = None
    description = None
    tags = None
    meta = None

    def __init__(self, title, meta, description=None, tags=[]):
        self.title = title
        if description:
            self.description = description
        if len(tags):
            self.tags = tags
        if not hasattr(meta, 'format'):
            raise ValueError("invalid meta: " + str(meta))
        self.meta = meta


class Auth(BaseYAMLObject):
    """
    >>> with open('t/data/home/certs/2013-10-13-foobar.adf') as f:
    ...     doc=load_archive(f)['auth']
    ...     auth = Auth(sha512=doc.sha512)
    ...     auth.sha512.encode('hex')[:10]
    'd5ad8f4cb5'
    """
    yaml_tag = u'!auth'

    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)


class Meta(BaseYAMLObject):
    """
    >>> meta = Meta('zip', 'aes-256-ctr', size=1024)
    >>> meta.format
    'zip'
    >>> meta.cipher
    'aes-256-ctr'
    >>> meta.size
    1024
    >>> meta = Meta('zip', 'aes-256-ctr')
    >>> meta.size
    >>> meta.size = 1024
    >>> meta.size
    1024
    """
    yaml_tag = u'!meta'
    size = None
    format = None
    cipher = None
    email = None
    name = None
    created = None

    def __init__(self, format, cipher, size=None, created=None,
                 email=None, name=None):
        self.format = format
        self.cipher = cipher
        if size:
            self.size = size
        if email:
            self.email = email
        if name:
            self.name = name
        if created:
            self.created = created
        else:
            self.created = today()


class Format(BaseYAMLObject):
    yaml_tag = u'!format'


class Links(BaseYAMLObject):
    """
    >>> links = Links(local='http://foo.bar.com')
    >>> links.download
    >>> links.upload
    >>> links.local
    'http://foo.bar.com'
    >>> from StringIO import StringIO
    >>> out = StringIO()
    >>> make_adf(links, out=out, pretty=True)
    >>> print out.getvalue()
    !links
    local: http://foo.bar.com
    <BLANKLINE>
    """
    yaml_tag = u'!links'
    download = None
    local = None
    upload = None
    """
    This attribute is undocumented in the ADF format, because it only makes
    sense in the context of a specific client. It contains the URL of the
    pending upload API resource.
    """

    def __init__(self, download=None, local=None, upload=None):
        if download:
            # deprecated, but for compatibility with early client
            self.download = download
        if local:
            self.local = local
        if upload:
            self.upload = upload


class Cipher(BaseYAMLObject):
    """
    >>> cipher = Cipher('aes-256-ctr', key=2, input='\1\2\3\4'*4)
    >>> cipher.mode
    'aes-256-ctr'
    >>> cipher.key
    2
    >>> cipher.input.encode('hex')
    '01020304010203040102030401020304'
    >>> Cipher('aes-256-ctr', key='foo')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "lacli/adf.py", line 70, in __init__
    ValueError: key must be integer
    >>> Cipher('wtf')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "lacli/adf.py", line 68, in __init__
    ValueError: wtf not recognized
    >>> cipher = Cipher('aes-256-ctr')
    >>> hasattr(cipher, 'key')
    False
    >>> hasattr(cipher, 'input')
    False
    >>> cipher = Cipher('aes-256-ctr', key=1)
    >>> hasattr(cipher, 'key')
    False
    """

    yaml_tag = u'!cipher'

    def __init__(self, mode, key=1, input=None):
        if mode not in cipher_modes():
            raise ValueError("{} not recognized".format(mode))
        if not isinstance(key, int):
            raise ValueError("key must be integer")
        self.mode = mode
        if key > 1:
            self.key = key
        if input:
            self.input = input

    def __setstate__(self, d):
        assert d['mode'] in cipher_modes()
        self.__dict__.update(d)


class DerivedKey(BaseYAMLObject):
    yaml_tag = u'!key'


class Certificate(BaseYAMLObject):
    """
    >>> cert = Certificate(chr(255)*16)
    >>> pyaml.dump(cert, sys.stdout)
    !certificate
    key: !!binary |
      /////////////////////w==
    """
    yaml_tag = u'!certificate'

    def __init__(self, key=None):
        if not key:
            self.key = new_key(256)
        else:
            self.key = key


class MAC(BaseYAMLObject):
    yaml_tag = u'!mac'


class Signature(BaseYAMLObject):
    """
    >>> sig = Signature('1', 'http://baz.com', datetime.utcfromtimestamp(0))
    >>> pyaml.dump(sig, sys.stdout)
    !signature
    aid: '1'
    created: 1970-01-01 00:00:00
    expires: 2000-01-01 00:00:00
    uri: http://baz.com
    """
    yaml_tag = u'!signature'
    aid = None
    uri = None
    created = None
    expires = None
    creator = None

    def __init__(self, aid, uri, created=None, expires=None, creator=None):
        self.aid = aid
        self.uri = uri
        if created:
            self.created = created
        else:
            self.created = today()

        if expires:
            self.expires = expires
        else:
            self.expires = later(self.created, years=30)

        if creator:
            self.creator = creator


def add_path_resolver(tag, keys):
    yaml.add_path_resolver(tag, keys, dict, Loader=PrettySafeLoader)

add_path_resolver(u'!format', ["meta", "format"])
add_path_resolver(u'!cipher', ["meta", "cipher"])
add_path_resolver(u'!meta', ["meta"])
add_path_resolver(u'!mac', ["mac"])
add_path_resolver(u'!signature', ["signature"])
add_path_resolver(u'!key', ["keys", None])

json_cert_re = re.compile(r"""
<template><script>var json_certificate='(.*)';</script></template>
""")


def load_archive(f):

    try:
        f = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    except Exception as e:
        raise InvalidArchiveError(e)
    match = json_cert_re.search(f)
    d = {}
    if match:  # we have a json encoded cert in this file
        try:
            d = as_adf(match.group(1))
        except Exception as e:
            raise InvalidArchiveError(e)
    else:
        try:
            os = yaml.load_all(f, Loader=PrettySafeLoader,
                               tz_aware_datetimes=True)
        except TypeError:
            os = yaml.load_all(f, Loader=PrettySafeLoader)
        for o in os:
            if isinstance(o, Archive):
                d['archive'] = o
            elif isinstance(o, Auth):
                d['auth'] = o
            elif isinstance(o, Certificate):
                d['cert'] = o
            elif isinstance(o, Links):
                d['links'] = o
            elif isinstance(o, Signature):
                d['signature'] = o
    if 'links' in d and d['links'].download:
        # fix for early client saving archive id in links section
        assert 'signature' not in d
        d['signature'] = Signature(aid=d['links'].download,
                                   uri='http://longaccess.com/a/')
        if d['links'].upload or d['links'].local:
            d['links'].download = None
        else:
            del d['links']
    if 'archive' in d:
        return d
    raise InvalidArchiveError()


def make_adf(archive=None, out=None, pretty=False):
    """
    >>> meta = Meta('zip', 'aes-256-ctr', created='now')
    >>> archive = Archive('title', meta)
    >>> cert = Certificate(chr(255)*16)
    >>> make_adf([archive, cert], out=sys.stdout, pretty=True)
    !archive
    meta: !meta
      cipher: aes-256-ctr
      created: now
      format: zip
    title: title
    --- !certificate
    key: !!binary |
      /////////////////////w==
    >>> make_adf([archive, cert], out=sys.stdout, pretty=True)
    !archive
    meta: !meta
      cipher: aes-256-ctr
      created: now
      format: zip
    title: title
    --- !certificate
    key: !!binary |
      /////////////////////w==
    """

    if not hasattr(archive, '__getitem__'):
        archive = [archive]
    if pretty and pyaml is not None:
        out.write("--- ".join(map(pyaml.dump, archive)))
        return
    return yaml.safe_dump_all(
        archive, out, canonical=True, allow_unicode=True)


def archive_size(archive):
    size = ""
    if archive.meta.size:
        kib = archive.meta.size // 1024
        mib = kib // 1024
        gib = mib // 1024

        if not kib:
            size = "{} B".format(archive.meta.size)
        elif not mib:
            size = "{} KB".format(kib)
        elif not gib:
            size = "{} MB".format(mib)
        else:
            size = "{} GB".format(gib)
    return size


class ADFEncoder(json.JSONEncoder):
    def _b64(self, v):
        return {'_base64': b64encode(v)}

    def default(self, o):
        if isinstance(o, (list, dict, str, unicode,
                          int, float, bool, type(None))):
            return super(ADFEncoder, self).default(o)
        if isinstance(o, datetime):
            return format_timestamp(o)
        if o.yaml_tag == Certificate.yaml_tag:
            return {'key': self._b64(o.key)}
        if o.yaml_tag == Auth.yaml_tag:
            return dict([(k, self._b64(v)) for k, v in o.__dict__.iteritems()])
        return o.__dict__


def _as_adf_object(dct):
    """
    May throw parse error for dates
    """
    if '_base64' in dct:
        return b64decode(dct['_base64'])
    if 'key' in dct:
        return Certificate(key=dct['key'])
    if 'md5' in dct:
        return Auth(**dct)
    if 'mode' in dct:
        return Cipher(**dct)
    if 'meta' in dct:
        return Archive(**dct)
    if 'download' in dct or 'upload' in dct or 'local' in dct:
        return Links(**dct)
    if 'created' in dct:
        dct['created'] = parse_timestamp(dct['created'])
        if 'aid' in dct:
            return Signature(**dct)
        else:
            return Meta(**dct)
    return dct


def as_json(docs):
    return ADFEncoder(ensure_ascii=False).encode(docs)


def as_adf(data):
    return json.loads(data, object_hook=_as_adf_object)


def creation(docs):
    """ return signature creation, or if not available, the archive creation.
        For sorting purposes. Invalid timestamps sort to the start of the epoch
    """
    created = docs['archive'].meta.created
    sig = docs.get('signature')
    if sig and sig.created:
        created = sig.created
    tstamp = parse_timestamp(created)
    if not tstamp:
        tstamp = epoch()
    return tstamp
