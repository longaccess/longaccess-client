# Introduction to longaccess API v1

## Getting started

Visit [stage.longaccess.com](http://stage.longaccess.com/) and create a new user. You will need this user's credentials to test your client. 

Verify user (users are identified by their email) using the API:

    curl -u email:password \
    --dump-header - \
    -H "Accept: application/json" \
    http://stage.longaccess.com/api/v1/account/

While at it, you should also create at least one DataCapsule. Use the following (dummy) credit card (provided by braintree sandbox):

    Credit Card Number: 4111111111111111
    CVV: 111 
    Expiration Date: 11/2015

Verify that the DataCapsule was created using the API:

    curl -u email:password \
    --dump-header - \
    -H "Accept: application/json" \
    http://stage.longaccess.com/api/v1/capsule/
   
## Preparing the archive.

There are two steps here, preparing the archive and encrypting the archive. There are many options for each step which will be detailed in the next two sections. However the following is a quick, recommended, example:

* The user selects the files to add
* The client creates a TAR archive with the files
* It compresses the archive with the [XZ][] library
* It generates a 256 bit random key 
* It encrypts the archive with AES in CTR mode
* It calculates an authenticating code with HMAC-SHA512
* It transmits to the service:
    - the encrypted archive
    - the authenticating code
    - the archive description

### Archiving and compressing the files
The archive is assembled and encrypted locally on the user's computer. 

Once the user indicates the files that he wants to upload, the client will create an archive containing them. If the archive format chosen, e.g. TAR, does not compress it's contents the client can optionally apply a compression algorithm on top of the archived data. For example a TAR archive could be compressed to an [XZ][] file, e.g. `archive.tar.xz`.

Another possibility is using an archive format that handles compression itself, preferably with an open specification and as widely implemented as possible. E.g. something based on [LZMA2][], like [7z][], could be used. More simply one could use ZIP (which uses the DEFLATE algorithm).

### Encrypting and authenticating the archive

For each archive, the client will have to generate a new random key and encrypt the archive with it before uploading it to the service. Additionally the client should provide for the calculation of an authentication code (MAC) that will permit the user to later check the archive's authenticity and integrity.

For encryption we recommend a 256 bit key size with AES in CTR mode. Special considerations for this mode must be dealt seriously, as described in the [relevant NIST Standard][NIST SP 800-38A]. Alternatively CBC, EAX, CCM or GCM mode may be used. For the MAC we recommend either using a HMAC, based on a SHA-2 digest algorithm, such as HMAC-SHA512, or using the code calculated during encryption by an AEAD mode of AES, like AES-GCM. 
 
In all cases using a mature cryptography library, like [openssl][], [cryptlib][] or [BouncyCastle][] is highly recommended.

## Uploading the archive.

Once the encrypted archive is ready (we will refer to it ar the *archive* from now on), the client should use the API to verify user, get available DataCapsules, and present the user with the ones that have enough free space to hold the archive.

An optional (but it is highly recomended to so so) `title` and `description` should also be provided by the user. This information will make it easier to navigate a user's list of archives in the future, and it's the only piece of information we (longaccess) have about the nature of the data stored (and can present to the user in the future).

Then the client initiates the upload using the `/upload/` call. This will return 

Example of archive upload initiation:
    
    curl -u email:password \
    --dump-header - \
    -H "Content-Type: application/json" \
    -X POST \
    --data '{"title": "test", "description": "blah blah", "capsule": "/api/v1/capsule/1/", "status": "pending"}' http://stage.longaccess.com/api/v1/upload/


 [LZMA2]: https://en.wikipedia.org/wiki/Lempel%E2%80%93Ziv%E2%80%93Markov_chain_algorithm#LZMA2_format
 [7z]: http://7-zip.org/7z.html
 [XZ]: http://tukaani.org/xz/format.html
 [openssl]: https://www.openssl.org/
 [BouncyCastle]: http://bouncycastle.org/
 [cryptlib]: http://www.cs.auckland.ac.nz/~pgut001/cryptlib/
