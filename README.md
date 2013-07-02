longaccess-cli
==============

Long Access: the client

Install using `python setup.py test`.

Don't forget to copy `lacli/config.py.sample` to `lacli/config.py` and edit accordingly:

Permissions
-----------

The IAM entity whose tokens are specified in `config.py` must have the following permissions
    
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

