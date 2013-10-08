# Archive Description Files, v0.1

This document describes the structure and
semantics of Archive Description Files (ADF). 

---

## Purpose

The purpose of an Archive Description File is to collect all the relevant structural and descriptive metadata about an archive, as well as to be somewhat extensible. The base format is [YAML][]. See [a minimal example](minimal.adf) of this format and [here](sample.adf) for a full example.

Relevant structural metadata include information about:
   
* the plaintext archive format / media type
* the cipher used for confidentiality
* the storage service signature
* the Message Authentication Code used for integrity

Relevant descriptive metadata include information about:

   * the software that created the archive
   * the circumstances of the archive creation
   * the actual contents of the archive

Binary values are base64 encoded and tagged with the `!!binary` tag.

## Basic Structure

The basic structure of an ADF file is a typical YAML 2.0 file with a header and up to 4 different documents. These documents are tagged as follows:

* `archive` - description of the contents and the format of the archive
* `auth` (optional) - authentication data (to verify authenticity)
* `certificate` - confidential data that provide access to the data stored in the service
* `links` - a list of URL's where the archive can be found

### Archive

The document is a mapping with the following keys:

* `title` - the title the user gave to this archive
* `description` - the description the user gave to this archive
* `meta` - other metadata
    - `platform` - a description of the computing platform that the archive was produced on.
    - `creator` - a description of the person or organization who created the archive
    - `created` - a timestamp for the time of the archive creation, in ISO format (e.g. 2013-06-07T10:45:01Z)
    - `format` - the id of the container format or a mapping with the following keys:
        + `type` - the id of the container format
        + `compression` - the id of an additional compressed container format
    - `cipher` - a scalar with the encryption algorithm id, or a mapping that contains the following keys:
        + `mode` - an id (E.g. `aes-256-ctr`) which determines the cipher algorithm, key-size and mode of operation.
        + `key` (optional) - the key id (a plain number), defaults to the first key
        + `input` (optional) - optional, a binary value with any IV/nonce used.

#### Example container format names

* `[ustar][]` - standard TAR format, widely implemented
* `[cpio][]` - standard CPIO format, mostly Unix
* `[zip][]` - standard ZIP format, widely implemented
* `[7z][]` - 7zip format, mostly Windows
* `[xz][]` - XZ format, mostly Unix 

Please note that the ZIP format does not in it's historical form support files larger than 2 GB.
Additionally it does not mandate Unicode filenames. Many clients support both
large files and Unicode names as extensions. These however are not standard. We
propose that archives that are created with these extensions specify a
different container format than `zip` like for example: 

* `[ziputf][]` - standard ZIP format with Unicode filenames, not so widely implemented
* `[zip64][]` - standard ZIP format for large files, not so widely implemented
* `[zip64utf][]` - standard ZIP format for large files with Unicode filenames, not so widely implemented


#### Example compression algorithm names

* `[deflate][]` - widely available, low compression, ok performance
* `[bzip2][]` - less available, good compression, poor performance
* `[lzma][]` - widely available, high compression, ok performance
* `[lzma2][]` - not widespread, highest compression, good performance
* `[Snappy][]` - not widespread, low compression,  extreme performance

#### Example cipher id's

* `aes-256-cbc` - 256-bit AES in CBC mode.
* `aes-256-gcm` - 256-bit AES in GCM mode.
* `aes-256-ctr` - 256-bit AES in CTR mode.

### Certificate

The optional document contains the keys used to encrypt the archive as well as the optional signatures of any storage services. It is a mapping with one of the following keys:

* `key`: - a binary value with the encryption key
* `keys`: - a sequence of keys used in the archive. Each member is either a binary value with an encryption key or a mapping with the folowing keys:
    - `key` - an integer index to another member of this list which should be used as the input key material of a key derivation function
    - `method` - the id of a key derivation function
    - `input` - a binary value with any input data that was used with the KDF algorithm (e.g. for `scrypt` a value in [the ASN.1 schema `scrypt-params`](http://tools.ietf.org/html/draft-josefsson-scrypt-kdf-01#section-6)).

Additionally the document mapping may contain a key `signature` which contains another mapping with the following keys:

* `originator` - a plain text identifying the creator of the signature
* `data` - the digital signature itself
* `type` - the type of signature (e.g. S/MIME)

#### Examples of Key Derivation Functions

* `HKDF-SHA256` - [HKDF (RFC 5869)]() with SHA256 hash
* `PBKDF2` - [RFC 2898]()
* `scrypt` - [scrypt (Internet Draft)]()

#### Examples of Signature Types

* `S/MIME`
* `OpenPGP`
* etc.

### Links

The optional document is a mapping with any of the following keys:

* `download` - a URL from where to download the archive
* `local` - a local `file://` URL where the archive is located on the local host

### Auth

The optional document is a mapping with the following keys:

* `sha512` (optional) - a binary value with the SHA512 checksum of the archive
* `mac` (optional) - a mapping that contains the following keys:
    - `mode` - the id of the algorithm that produced the MAC
    - `key` (optional) - the key id (a plain number), defaults to the first key
    - `output` - a binary value with the MAC

#### Example MAC algorithm id's

* `HMAC-SHA512` - HMAC (RFC 2104) with SHA-512 digest
* `GCM` - the GHASH value from the GCM cipher, assuming an archive encrypted with AES in GCM mode.


 [YAML]: http://www.yaml.org "YAML"
 [deflate]: https://en.wikipedia.org/wiki/DEFLATE#Stream_format "Deflate stream format"
 [Snappy]: http://code.google.com/p/snappy/source/browse/trunk/README
 [lzma]: https://en.wikipedia.org/wiki/LZMA#Compressed_format_overview "LZMA compressed format"
 [bzip2]: https://en.wikipedia.org/wiki/Bzip2#File_format "Bzip2"
 [zip]: https://en.wikipedia.org/wiki/ZIP_(file_format) "Zip file format"
 [7z]: http://www.7-zip.org/7z.htmla "7z file format"
 [xz]: http://tukaani.org/xz/xz-file-format.txt "XZ file format"
 [ustar]: http://pubs.opengroup.org/onlinepubs/9699919799/utilities/pax.html#tag_20_92_13_06 "ustar file format"
 [cpio]: http://pubs.opengroup.org/onlinepubs/9699919799/utilities/pax.html#tag_20_92_13_07 "cpio file format"
 [HKDF (RFC 5869)]: http://tools.ietf.org/html/rfc5869 "HKDF"
 [RFC 2898]: http://tools.ietf.org/html/rfc2898 "PBKDF"
 [scrypt (Internet Draft)]: http://tools.ietf.org/html/draft-josefsson-scrypt-kdf-01 "draft-josefsson-scrypt-kdf-01"
