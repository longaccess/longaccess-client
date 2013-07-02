from lacli.config import BOTO_DEFAULT_REGION, BOTO_ACCESS_KEY, BOTO_SECRET, BOTO_BUCKET, BOTO_UPLOAD_PREFIX

__version__="0.1a1.dev1"

import policy


_defaultallow=['s3:ListAllMyBuckets','s3:ListBucket','s3:ListBucketMultipartUploads', 's3:ListMultipartUploadParts']
_bucketarn='arn:aws:s3:::'+BOTO_BUCKET
_uploadfolder=BOTO_UPLOAD_PREFIX #+"/${aws:userid}"

BOTO_UPLOAD_POLICY=policy.make([
    policy.allow_statement(_defaultallow, _bucketarn),
    policy.allow_statement(['s3:PutObject'], _bucketarn+"/*") #, _uploadfolder)
])

