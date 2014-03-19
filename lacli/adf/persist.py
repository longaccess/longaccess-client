import yaml
import json
import sys
import re
import mmap

try:
    import pyaml
except ImportError:
    pyaml = None

from lacli.exceptions import InvalidArchiveError
from lacli.date import parse_timestamp, format_timestamp
from datetime import datetime
from base64 import b64encode, b64decode
from .elements import (Archive, Meta, Certificate, Auth,
                       Cipher, Links, Signature)
from .serialize import load_file


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
        for o in load_file(f):
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
