import yaml
import pyaml
import sys

from lacli.cipher import cipher_modes, new_key
from yaml import SafeLoader
from yaml import SafeDumper
from lacli.exceptions import InvalidArchiveError


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
    >>> meta = Meta('zip', 'aes-256-ctr', size=1024)
    >>> archive = Archive('title', meta, tags=['foo', 'bar'])
    >>> archive.title
    'title'
    >>> archive.description
    >>> archive.meta.cipher
    'aes-256-ctr'
    >>> archive.meta.size
    1024
    >>> archive.tags[1]
    'bar'
    >>> archive.description = 'what a wonderful dataset'
    >>> archive.description
    'what a wonderful dataset'
    >>> Archive('title', meta, description='worthless junk').description
    'worthless junk'
    >>> pyaml.dump(Archive('foo', Meta('zip', 'xor')), sys.stdout)
    !archive
    meta: !meta
      cipher: xor
      format: zip
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
    'd34a686c5c'
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

    def __init__(self, format, cipher, size=None):
        self.format = format
        self.cipher = cipher
        if size:
            self.size = size


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
    >>> make_adf(links, out=out)
    >>> print out.getvalue()
    !links {local: 'http://foo.bar.com'}
    <BLANKLINE>
    """
    yaml_tag = u'!links'
    download = None
    local = None
    upload = None

    def __init__(self, download=None, local=None):
        if download:
            self.download = download
        if local:
            self.local = local


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
    yaml_tag = u'!signature'


def add_path_resolver(tag, keys):
    yaml.add_path_resolver(tag, keys, dict, Loader=PrettySafeLoader)

add_path_resolver(u'!format', ["meta", "format"])
add_path_resolver(u'!cipher', ["meta", "cipher"])
add_path_resolver(u'!meta', ["meta"])
add_path_resolver(u'!mac', ["mac"])
add_path_resolver(u'!signature', ["signature"])
add_path_resolver(u'!key', ["keys", None])


def load_archive(f):
    d = {}
    for o in yaml.load_all(f, Loader=PrettySafeLoader):
        if isinstance(o, Archive):
            d['archive'] = o
        elif isinstance(o, Auth):
            d['auth'] = o
        elif isinstance(o, Certificate):
            d['cert'] = o
        elif isinstance(o, Links):
            d['links'] = o
    if 'archive' in d:
        return d
    raise InvalidArchiveError()


def make_adf(archive=None, canonical=False, out=None, pretty=False):
    """
    >>> archive = Archive('title', Meta('zip', 'aes-256-ctr'))
    >>> cert = Certificate(chr(255)*16)
    >>> make_adf([archive, cert], out=sys.stdout, pretty=True)
    !archive
    meta: !meta
      cipher: aes-256-ctr
      format: zip
    title: title
    ---!certificate
    key: !!binary |
      /////////////////////w==
    >>> make_adf([archive, cert], out=sys.stdout)
    !archive
    meta: !meta {cipher: aes-256-ctr, format: zip}
    title: title
    --- !certificate
    key: !!binary |
      /////////////////////w==
    """

    if not hasattr(archive, '__getitem__'):
        archive = [archive]
    if pretty:
        out.write("---".join(map(pyaml.dump, archive)))
        return
    return yaml.safe_dump_all(archive, out, canonical=canonical)
