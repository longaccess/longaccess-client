import random

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

def make(statements):
    return {'Statement': statements, 'Version':"2012-10-17"}
