Boto Fun
========

Just some code to test boto, using `python setup.py test`.

Don't forget to copy `botofun/config.py.sample` to `botofun/config.py` and edit accordingly:

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


