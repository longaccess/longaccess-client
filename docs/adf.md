# Archive Description Files, v0.1

This document describes the structure and
semantics of Archive Description Files (ADF). 

---

## Purpose

The purpose of an Archive Description File is to
collect all the relevant structural and
descriptive metadata about an archive, as well as
to be somewhat extensible. The base format is
[YAML][].

Relevant structural metadata include information about:
   
* the cipher used for confidentiality
* the Message Authentication Code used for integrity
* the plaintext archive format / media type

Relevant descriptive metadata include information about:

   * the software that created the archive
   * the circumstances of the archive creation
   * the actual contents of the archive

### Example

The following is an example of an ADF file, the
parts of which are described in the rest of this
document:

    %YAML 1.2
    %TAG !a! tag:longaccess.com,2013-09-11/archive
    --- !a!adf
    href: http://download.longaccess.com/x0fs8907494875
    crypto:
        !a!cipher: aes-256-ctr
        init: !!binary "GKrtCB10XLbtA9qHnyoZj67dgk1f1uLuHBF6xCBAvhI="
        !a!mac: HMAC-MD5
        auth: !!binary "J+0wGQKFm/ZnqFXtJGxMzQ==" 
        auth_extra: Y
    format:
        !a!compression: bz2
        !a!container: tar
    description:
        platform: Windows XP
        creator: Long Access Client v0.7
        extra: |
            This archive contains pictures from my
            vacation in 2013, organized by location.
            I went to: Corfu, Kefalonia and Zakynthos

## Basic Structure

The basic structure of an ADF file is a typical YAML 2.0
file with a header and a top level mapping. The mapping 
shall contain the following keys:

* `crypto` - for cryptographic information
* `format` - for archive format information
* `description`  - optional, for descriptive metadata
* `href` - optional, for providing a link to a copy of the archive available for downloading

### Header

The document header shall be as follows:

    %YAML 1.2
    %TAG !! tag:longaccess.com,2013-09-11/app
    --- !!adf

### crypto

This key contains any necessary information to be
able to decrypt and, optionally, authenticate the
archive. This includes a description of the
cipher used, any required initialization data
and, optionally, a description of the message authentication
used.

The key is a mapping with the following keys:

* `cipher` - a mapping that contains the following keys:
    - `name` - a name that determines the cipher algorithm, key-size and mode of operation.
    - `init` - optional, a binary value (tagged) with any IV/nonce used.
* `mac` - a mapping that contains the following keys:
    - `algorithm` - the name of the algorithm that produced the MAC
    - `data` - a binary value (tagged) with the MAC
    - `include_extra` - a boolean value (tagged) to indicate that the MAC covers the `description/extra` data in ADF file.

Example cipher names:

* `aes-256-cbc` - 256-bit AES in CBC mode.
* `aes-256-gcm` - 256-bit AES in GCM mode.
* `aes-256-ctr` - 256-bit AES in CTR mode.

Example MAC algorithms:

* `HMAC-SHA512` - HMAC with SHA-512 digest
* `GCM` - the GHASH value from the GCM cipher. Requires `cipher` to be `aes-256-gcm`.

### `format`

This key contains any necessary information to be
able to decompress and unpack the archive into any individual 
files that it contains.

The key is a mapping with the following keys:

* `compression` - the name of the compression algorithm applied 
* `container` - the name of the archive format used

Example compression algorithm names:

* `[deflate][]` - widely available, low compression, ok performance
* `[bzip2][]` - less available, good compression, poor performance
* `[lzma][]` - widely available, high compression, ok performance
* `[lzma2][]` - not widespread, highest compression, good performance
* `[Snappy][]` - not widespread, low compression,  extreme performance

Example container format names:

* `[ustar][]` - standard TAR format, widely implemented
* `[cpio][]` - standard CPIO format, mostly Unix
* `[zip][]` - standard ZIP format, widely implemented
* `[7z][]` - 7zip format, mostly Windows
* `[xz][]` - XZ format, mostly Unix 

### Description

This key, if it exists, contains any descriptive
metadata. The key is a mapping with one or more
of the following keys:

* `platform` - a description of the computing platform that the archive was produced on.
* `created` - a timestamp for the time of the archive creation, in ISO format 
* `creator` - a description of the person or organization who created the archive
* `extra` - an arbitrary block of text that was supplied during the creation of the archive.

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
