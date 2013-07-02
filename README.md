longaccess-cli
==============

Long Access: the client

Install using `python setup.py install`.


Credentials
-----------

Credentials may be configured via standard boto mechanisms (e.g. `~/.boto.cfg`)
or using the `lacreds.py` script.

Permissions
-----------

The IAM entity whose tokens are configured must have the following permissions
    
    {
        "Version":"2012-10-17",
        "Statement":[
            {
                "Effect":"Allow",
                "Action":["sts:GetFederationToken"],
                "Resource":["arn:aws:sts::xxxxx:federated-user/testuser*"]
            }
        ]
    }

