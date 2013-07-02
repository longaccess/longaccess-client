from latvm.policy import upload_policy
import os
import boto.sts
import json

class MyTvm(object):

    credfile=os.path.expanduser('~/.latvm.json')

    def __init__(self,region='us-east-1',bucket='lastage',prefix='upload'):
        self.federation_policy=upload_policy(bucket, prefix)
        self.readcreds()
        self.connection = boto.sts.connect_to_region(
                region_name=region,aws_access_key_id=self.key,
                aws_secret_access_key=self.secret)

    def readcreds(self):
        # use boto defaults
        self.key=None
        self.secret=None
        # unless user configured other credentials
        if os.path.isfile(self.credfile):
            print "Reading TVM credentials from {}".format(self.credfile)
            with open(self.credfile) as f:
                creds=json.loads(f.read())
                self.key=creds['key']
                self.secret=creds['secret']

    @classmethod
    def storecreds(cls, key, secret):
        with open(cls.credfile, mode='w') as f:
            json.dump({'key': key, 'secret': secret}, f)

    def get_upload_token(self,uid=None,secs=3600):
        if not self.connection:
            raise Exception("No STS connection.")

        credentials=None
        if uid is None:
            credentials = self.connection.get_session_token(duration=secs)
        else:
            token = self.connection.get_federation_token(uid, 
                    duration=secs, policy=self.federation_policy)
            credentials=token.credentials
            uid = token.federated_user_id
        if not credentials:
            raise Exception("Error getting token.")

        return (credentials.access_key,
                credentials.secret_key,
                credentials.session_token,
                credentials.expiration,
                uid)

