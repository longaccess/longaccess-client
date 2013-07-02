import boto.sts
import json
from botofun import BOTO_DEFAULT_REGION, BOTO_ACCESS_KEY, BOTO_SECRET, BOTO_UPLOAD_POLICY, BOTO_UPLOAD_PREFIX
import botofun.policy

class MyTvm(object):

    def __init__(self,region=BOTO_DEFAULT_REGION):
        self.connection = boto.sts.connect_to_region(region_name=region,aws_access_key_id=BOTO_ACCESS_KEY, aws_secret_access_key=BOTO_SECRET)

    def get_upload_token(self,uid,secs):
        if not self.connection:
            raise Exception("No STS connection.")

        token = self.connection.get_federation_token(uid, secs, policy=json.dumps(BOTO_UPLOAD_POLICY))
        if not token:
            raise Exception("Error getting token.")

        return (token.credentials.access_key,
                token.credentials.secret_key,
                token.credentials.session_token,
                token.credentials.expiration,
                token.federated_user_id)
