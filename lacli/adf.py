import yaml

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
    yaml_tag = u'!archive'

    def __init__(self, title, meta, description=None, tags=[]):
        self.title = title
        self.description = description
        self.tags = tags
        if not hasattr(meta, 'format'):
            raise ValueError("invalid meta: " + str(meta))
        self.meta = meta


class Auth(BaseYAMLObject):
    yaml_tag = u'!auth'

    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)


class Meta(BaseYAMLObject):
    yaml_tag = u'!meta'

    def __init__(self, format, cipher):
        self.format = format
        self.cipher = cipher


class Format(BaseYAMLObject):
    yaml_tag = u'!format'


class Links(BaseYAMLObject):
    yaml_tag = u'!links'

    def __init__(self, download=None, local=None):
        if download:
            self.download = download
        if local:
            self.local = local


class Cipher(BaseYAMLObject):
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
    yaml_tag = u'!certificate'

    def __init__(self):
        self.key = new_key(256)


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


def load_all(f):
    return yaml.load_all(f, Loader=PrettySafeLoader)


def load_archive(f):
    for o in load_all(f):
        if hasattr(o, 'meta'):
            return o
    raise InvalidArchiveError()


def make_adf(archive=None, canonical=False, out=None):
    if not hasattr(archive, '__getitem__'):
        archive = [archive]
    return yaml.safe_dump_all(archive, out, canonical=canonical)
