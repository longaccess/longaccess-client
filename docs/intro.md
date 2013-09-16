# Introduction to Long Access API v1

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
* The client creates a ZIP archive with the files
* It generates a 256 bit random key
* It encrypts the archive with AES in CTR mode

### Encrypting the archive

For each archive, the client will have to generate a new random key and encrypt the archive with it before uploading it to the service.

By default the archive should be encrypted with a new random 256 bit key using [AES in CTR mode][] with an IV of zero. The key should only be used for the encryption of one archive and never be reused again.

Also, using a mature cryptography library, like [openssl][], [cryptlib][] or [BouncyCastle][] is highly recommended.

 [AES in CTR mode]: http://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#Counter_.28CTR.29
 [openssl]: https://www.openssl.org/
 [BouncyCastle]: http://bouncycastle.org/
 [cryptlib]: http://www.cs.auckland.ac.nz/~pgut001/cryptlib/
 [ADF]: adf.md 

## Uploading the archive.

Briefly the steps for the archive upload are (more details follow):

* the user selects which data capsule to upload to
* she inputs a title and free text description for the archive
* the client initializes an upload 
* it transmits the archive
* it requests confirmation of successful completion

### Preparation

So, after preparing the encrypted archive (just *archive* from now on) the user must upload it to a DataCapsule. Before actually uploading the client should use the API to verify user, get available DataCapsules, and present the user with the ones that have enough free space to hold the archive.

A `title` and `description` should also be provided by the user. This information will make it easier to navigate a user's list of archives in the future, and it's the only piece of information we (Long Access) have about the nature of the data stored (and can present to the user in the future).

### Initialization

Then the client initiates the upload using the `/upload/` call, providing the destination capsule and archive description. The API responds with all the available information about the transmission of the archive. Example of archive upload initiation request:
    
    curl -u email:password \
    --dump-header - \
    -H "Content-Type: application/json" \
    -X POST \
    --data '{\
    		"title": "test", \
    		"description": "My awesome photos", \
    		"capsule": "/api/v1/capsule/1/", \
    		"size": 10512,\
    		"checksum": "md5:d85d8251bd93decb7396e767700acb9f"\
    }' \
    http://stage.longaccess.com/api/v1/upload/

And response:

    {
        "id": "1573",
        "resource_uri": "/api/v1/upload/1",
        "bucket": "lastage",
        "prefix": "upload/1573/",
        "capsule": "/api/v1/capsule/1/", 
        "description": "My awesome photos",
        "status": "pending", 
        "title": "test",
        "token_access_key": "ASIAIBCURANIDXZJ2XYQ",
        "token_secret_key": "5cqp0qsQbtMO13HsJ5bh1DzpY0kAX8brL+I/ZZ8Z",
        "token_session": "AQoDYXdzE...TGVW6ghd68B5czR9T51svX3rkzzhFtINn/xpEF",
        "token_expiration": "2013-09-12T14:21:29Z",
        "token_uid": "stage1573"
        ]
    }

    
/upload/ will return the upload operation `id` ("1573" in this example). You will need this identifier throughout the upload process.

Using the information in the response the client can then begin uploading to S3: in particular the `bucket`, `prefix` and `token_*` values are necessary for:

* establishing a connection to S3 using:
    - `token_access_key` as the access key,
    - `token_secret_key` as the API secret, and
    - `token_session` as the secure token.
* determining the destination bucket (JSON key `bucket`) and key prefix by (JSON key `prefix`).
* determining the expiration time and date of the token (JSON key `token_expiration`).

For example, in the example response listed above the client would upload the archive to the S3 URL `s3://lastage/upload/1573/` using the access key and secret in `token`. It will also renew the token before 2:21 PM UTC on the 12th of September.

To upload the archive the client calls the appropriate AWS SDK or [API method to initiate a multipart upload][InitMultiPart] to a destination key under `prefix`. It then proceeds to upload the archive in parts of 500 MB size using the [appropriate S3 API or SDK method][UploadPart]. Since the security token will expire (typically after a few hours) the client may not be able to upload all the parts during it's lifetime. So at some point the client must finalize the current multipart upload, either before the expiration of the token or after all parts are uploaded. This should be done by calling the appropriate S3 API or SDK method to signal [completion of the MultiPart Upload][CompleteMultiPart].

Depending on the size of the archive and the duration of the token the client may need to repeat the previous operations more than once, each time uploading a subsequent portion of the archive. In this case each portion must be uploaded in order to a sequentially named key using the prefix calculated earlier. E.g.:
- `/upload/1573/1`
- `/upload/1573/2`
- `/upload/1573/3`
- etc.

After each portion is finalized, but before the next portion's upload begins, the client may request a new token from the API. This can be done by using the upload id and calling:

    GET /upload/:id/
    
The response will be identical with the response to the initial POST request, with the exception that it will contain a fresh security token, if the current one is about to expire or has expired.

Once the archive upload is complete, i.e. all portions have been uploaded, the client **MUST** call `PATCH /upload/:id/` with status "uploaded". This will notify the API to start processing the uploaded portions, assemble them into the complete archive, and verify the MD5 checksum.

    Example: 

    curl -u email:password \
    --dump-header - \
    -H "Content-Type: application/json" \
    -X PATCH \
    --data '{"id": "1", "status": "uploaded"}' \
    http://stage.longaccess.com/api/v1/upload/1

After completing the upload the client will have to wait while the server checks the integrity of the archive. To do this it should periodically call `GET /upload/:id/` (we suggest at 30 minute intervals) until the API returns with a status of `completed`. When status is `completed`, an extra JSON key is returned, called `archive_id`. Now the upload process is completed, the archive is safely stored and the client can generate the certificate.

The certificate must include the following information:

- Archive id 
- Checksum 
- AES encryption key 
- Archive title 
- Archive description
- Archive upload date
- User email
- URL to retrieve data: http://www.longaccess.com/

 [InitMultiPart]: http://docs.aws.amazon.com/AmazonS3/latest/API/mpUploadInitiate.html
 [CompleteMultiPart]: http://docs.aws.amazon.com/AmazonS3/latest/API/mpUploadComplete.html
 [UploadPart]: http://docs.aws.amazon.com/AmazonS3/latest/API/mpUploadUploadPart.html
