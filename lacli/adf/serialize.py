import yaml


class PrettySafeLoader(yaml.SafeLoader):
    pass


class BaseYAMLObject(yaml.YAMLObject):
    yaml_loader = PrettySafeLoader
    yaml_dumper = yaml.SafeDumper

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_mapping(cls.yaml_tag, data.__dict__)


def add_path_resolver(tag, keys):
    yaml.add_path_resolver(tag, keys, dict, Loader=PrettySafeLoader)


def load_file(f):
    try:
        return yaml.load_all(f, Loader=PrettySafeLoader,
                             tz_aware_datetimes=True)
    except TypeError:
        return yaml.load_all(f, Loader=PrettySafeLoader)
