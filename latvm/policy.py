import random
import json

def random_statement_id():
    return "statement{}".format(random.randrange(1000,2000))

def allow_statement(actions, arn, prefix=None):
    st={}
    st['Action']=actions
    st['Resource']=arn
    st['Effect']='Allow'
    st['Sid']=random_statement_id()
    if prefix is not None:
        st['Condition']=prefix_condition(prefix)
    return st

def prefix_condition(prefix):
    return {'StringLike': {"s3:prefix": prefix+"/*"}}

def upload_policy(bucket='lastage',prefix='upload'):
    _defaultallow=['s3:ListAllMyBuckets',
                   's3:ListBucket',
                   's3:ListBucketMultipartUploads',
                   's3:ListMultipartUploadParts']
    _bucketarn='arn:aws:s3:::{}'.format(bucket)
    _uploadfolder=prefix #+"/${aws:userid}"
    return json.dumps({'Statement': [
                allow_statement(_defaultallow, _bucketarn),
                allow_statement(['s3:PutObject'], _bucketarn+"/*") #, _uploadfolder)
            ], 'Version':"2012-10-17"})

