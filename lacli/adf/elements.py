import sys
from lacli.cipher import cipher_modes, new_key
from lacli.date import today, later
from .serialize import BaseYAMLObject, add_path_resolver
from datetime import datetime


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
    >>> import pyaml
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
    >>> from lacli.adf.persist import load_archive
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


add_path_resolver(u'!meta', ["meta"])


class Format(BaseYAMLObject):
    yaml_tag = u'!format'


add_path_resolver(u'!format', ["meta", "format"])


class Links(BaseYAMLObject):
    """
    >>> links = Links(local='http://foo.bar.com')
    >>> links.download
    >>> links.upload
    >>> links.local
    'http://foo.bar.com'
    >>> from StringIO import StringIO
    >>> out = StringIO()
    >>> from lacli.adf.persist import make_adf
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


add_path_resolver(u'!cipher', ["meta", "cipher"])


class DerivedKey(BaseYAMLObject):
    yaml_tag = u'!key'


add_path_resolver(u'!key', ["keys", None])


class Certificate(BaseYAMLObject):
    """
    >>> cert = Certificate(chr(255)*16)
    >>> import pyaml
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


add_path_resolver(u'!mac', ["mac"])


class Signature(BaseYAMLObject):
    """
    >>> sig = Signature('1', 'http://baz.com', datetime.utcfromtimestamp(0))
    >>> import pyaml
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


add_path_resolver(u'!signature', ["signature"])
