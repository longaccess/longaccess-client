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
The archive is assembled and encrypted locally on the user's computer. 

Once the user indicates the files that he wants to upload, the client will create a ZIP archive containing them. 

Then, the client will have to generate a random 256bit key that will be used to encrypt the ZIP file using AES256. Great care should be taken in choosing a random Initialisation Vector and a random Encryption Key.
 
## Uploading the archive.
Once the AES-encrypted ZIP archive is ready (we will refer to it ar the *archive* from now on), the client should use the API to verify user, get available DataCapsules, and present the user with the ones that have enough free space to hold the archive.

An optional (but it is highly recomended to so so) `title` and `description` should also be provided by the user. This information will make it easier to navigate a user's list of archives in the future, and it's the only piece of information we (longaccess) have about the nature of the data stored (and can present to the user in the future).

Then the client initiates the upload using the `/upload/` call. This will return 

Example of archive upload initiation:
    
    curl -u email:password \
    --dump-header - \
    -H "Content-Type: application/json" \
    -X POST \
    --data '{"title": "test", "description": "blah blah", "capsule": "/api/v1/capsule/1/", "status": "pending"}' http://stage.longaccess.com/api/v1/upload/
