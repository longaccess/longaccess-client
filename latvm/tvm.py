from latvm.policy import BOTO_DEFAULT_REGION, BOTO_ACCESS_KEY, BOTO_SECRET, BOTO_UPLOAD_POLICY
import boto.sts
import json

class MyTvm(object):

    def __init__(self,region=BOTO_DEFAULT_REGION):
        self.connection = boto.sts.connect_to_region(region_name=region,aws_access_key_id=BOTO_ACCESS_KEY, aws_secret_access_key=BOTO_SECRET)

    def get_upload_token(self,uid=None,secs=3600):
        if not self.connection:
            raise Exception("No STS connection.")

        credentials=None
        if uid is None:
            credentials  = self.connection.get_session_token(duration=secs, force_new=True)
        else:
            token = self.connection.get_federation_token(uid, secs, policy=json.dumps(BOTO_UPLOAD_POLICY))
            credentials=token.credentials
            uid = token.federated_user_id
        if not credentials:
            raise Exception("Error getting token.")

        return (credentials.access_key,
                credentials.secret_key,
                credentials.session_token,
                credentials.expiration,
                uid)
