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

### Archiving and compressing the files
The archive is assembled and encrypted locally on the user's computer. 

Once the user indicates the files that he wants to upload, the client will create an archive containing them. If the archive format chosen, e.g. TAR, does not compress it's contents the client can optionally apply a compression algorithm on top of the archived data. For example a TAR archive could be compressed to an [XZ][] file, e.g. `archive.tar.xz`.

Another possibility is using an archive format that handles compression itself, preferably with an open specification and as widely implemented as possible. E.g. something based on [LZMA2][], like [7z][], could be used. More simply one could use ZIP (which uses the DEFLATE algorithm).

### Encrypting and authenticating the archive

For each archive, the client will have to generate a new random key and encrypt the archive with it before uploading it to the service. Additionally the client should provide for the calculation of an authentication code (MAC) that will permit the user to later check the archive's authenticity and integrity.

For encryption we recommend a 256 bit key size with AES in CTR mode. Special considerations for this mode must be dealt seriously, as described in the [relevant NIST Standard][NIST SP 800-38A]. Alternatively CBC, EAX, CCM or GCM mode may be used. For the MAC we recommend either using a HMAC, based on a SHA-2 digest algorithm, such as HMAC-SHA512, or using the code calculated during encryption by an AEAD mode of AES, like AES-GCM. 
 
In all cases using a mature cryptography library, like [openssl][], [cryptlib][] or [BouncyCastle][] is highly recommended.

 [LZMA2]: https://en.wikipedia.org/wiki/Lempel%E2%80%93Ziv%E2%80%93Markov_chain_algorithm#LZMA2_format
 [7z]: http://7-zip.org/7z.html
 [XZ]: http://tukaani.org/xz/format.html
 [openssl]: https://www.openssl.org/
 [BouncyCastle]: http://bouncycastle.org/
 [cryptlib]: http://www.cs.auckland.ac.nz/~pgut001/cryptlib/
 [ADF]: adf.md 

## Uploading the archive.

Briefly the steps for the archive upload are (more details follow):

* the user selects which data capsule to upload to
* she inputs a title and free text description for the archive
* the client compiles an archive description file
* it initializes an upload 
* it transmits the archive
* it requests confirmation of successful completion

### Preparation

So, after preparing the encrypted archive (just *archive* from now on) the user must upload it to the archive. Before actually uploading the client should use the API to verify user, get available DataCapsules, and present the user with the ones that have enough free space to hold the archive.

An optional (but highly recommended) `title` and `description` should also be provided by the user. This information will make it easier to navigate a user's list of archives in the future, and it's the only piece of information we (longaccess) have about the nature of the data stored (and can present to the user in the future).

The client then proceeds to compile an [archive description file][ADF] with the following information:
- the archive format
- the compression method, if any,
- the encryption algorithm
- the authenticating code and type of algorithm used
- the user supplied title and description
- the archive size and other descriptive metadata

### Initialization

Then the client initiates the upload using the `/upload/` call, providing the destination capsule and archive description. The API responds with all the available information about the transmission of the archive. Example of archive upload initiation request:
    
    curl -u email:password \
    --dump-header - \
    -H "Content-Type: application/json" \
    -X POST \
    --data '{"title": "test", "description": "...", "capsule": "/api/v1/capsule/1/", "status": "pending"}' http://stage.longaccess.com/api/v1/upload/

and response:

    {
        "id": "1",
        "resource_uri": "/api/v1/upload/1",
        "bucket": "arn:aws:s3:::lastage",
        "prefix": "upload/",
        "capsule": "/api/v1/capsule/1/", 
        "description": "...",
        "status": "pending", 
        "title": "test",
        "token": [
            "ASIAIBCURANIDXZJ2XYQ",
            "5cqp0qsQbtMO13HsJ5bh1DzpY0kAX8brL+I/ZZ8Z",
            "AQoDYXdzE...TGVW6ghd68B5czR9T51svX3rkzzhFtINn/xpEF",
            "2013-09-12T14:21:29Z",
            "042584473589:stage17"
        ]
    }

### Upload

Using the information in the response the client can then begin uploading to S3: in particular the `bucket`, `prefix` and `token` values are necessary for:

* establishing a connection to S3 using:
    - `token[0]` as the access key,
    - `token[1]` as the API secret, and
    - `token[2]` as the secure token.
* determining the destination bucket (JSON key `bucket`) and key prefix by concatenating `prefix` and `token[4]`.

If the archive is less than 5GB the client simply uploads the archive to the destination key using the appropriate S3 API or SDK method.

If the archive is bigger than 5 GB the client calls the appropriate AWS SDK or [API method to initiate a multipart upload][InitMultiPart] and receives a MultiPart Upload ID. It then proceeds to upload the archive in parts of a certain size (we recommend 500 MB) using the [appropriate S3 API or SDK method][UploadPart]. Each part is uploaded to a sequentially named key using the prefix calculated earlier. After all parts are uploaded the appropriate S3 API or SDK method is called to signal [completion of the MultiPart Upload][CompleteMultiPart].

After completing the upload to S3 the client contacts the Long Access API to signal the completion like this:

    curl -u email:password \
    --dump-header - \
    -H "Content-Type: application/json" \
    -X PATCH \
    --data '{"id": "1", "status": "uploaded"}' http://stage.longaccess.com/api/v1/upload/1


 [InitMultiPart]: http://docs.aws.amazon.com/AmazonS3/latest/API/mpUploadInitiate.html
 [CompleteMultiPart]: http://docs.aws.amazon.com/AmazonS3/latest/API/mpUploadComplete.html
 [UploadPart]: http://docs.aws.amazon.com/AmazonS3/latest/API/mpUploadUploadPart.html

