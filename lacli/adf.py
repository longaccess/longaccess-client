import yaml
from lacli.cipher import modes as cipher_modes


class Archive(yaml.YAMLObject):
    yaml_tag = u'!archive'

    def __init__(self, title, meta, description=None, tags=[]):
        self.title = title
        self.description = description
        self.tags = tags
        self.meta = meta


class Auth(yaml.YAMLObject):
    yaml_tag = u'!auth'


class Format(yaml.YAMLObject):
    yaml_tag = u'!format'


class Links(yaml.YAMLObject):
    yaml_tag = u'!links'


class Cipher(yaml.YAMLObject):
    yaml_tag = u'!cipher'

    modes = {
        'aes-256-ctr': None
    }

    def __setstate__(self, d):
        assert d['mode'] in cipher_modes
        self.__dict__.update(d)


class DerivedKey(yaml.YAMLObject):
    yaml_tag = u'!key'


class Certificate(yaml.YAMLObject):
    yaml_tag = u'!certificate'


class MAC(yaml.YAMLObject):
    yaml_tag = u'!mac'


class Signature(yaml.YAMLObject):
    yaml_tag = u'!signature'


yaml.add_path_resolver(u'!format', ["meta", "format"], dict)
yaml.add_path_resolver(u'!cipher', ["meta", "cipher"], dict)
yaml.add_path_resolver(u'!mac', ["mac"], dict)
yaml.add_path_resolver(u'!signature', ["signature"], dict)
yaml.add_path_resolver(u'!key', ["keys", None], dict)


def load_all(f):
    return yaml.load_all(f)


def make_adf(archive=None, canonical=False):
    return yaml.dump(archive, default_flow_style=False, canonical=canonical)
