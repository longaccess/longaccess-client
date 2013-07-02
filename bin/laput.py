#!/home/kouk/code/bototest/bin/python

import sys
import argparse 
from itertools import repeat
import multiprocessing as mp
import latvm.tvm
import lacli.pool
from boto import config as boto_config
import os

def results(it, timeout):
    while True:
        yield it.next(timeout)

def upload_temp_key(poolmap, source, conn, name='archive'):
    with lacli.pool.MPUpload(conn,source,name=name) as upload:
        print "starting to upload {0} parts (timeout={1})".format(
                source.chunks, conn.timeout())
        args=enumerate(repeat(upload, source.chunks))
        rs=poolmap(lacli.pool.upload_part, args)
        successfull=[]
        try:
            for r in results(rs,conn.timeout()):
                successfull.append(r)
        except StopIteration:
            pass
        except mp.TimeoutError:
            print "timed out!"
        return upload.combineparts(successfull)

def pool_upload(user, duration, path):
    mp.util.log_to_stderr(mp.util.SUBDEBUG)
    tvm = latvm.tvm.MyTvm()
    token = tvm.get_upload_token(user, duration)
    conn = lacli.pool.MPConnection(token)
    try:
        poolsize=max(mp.cpu_count()-1,3)
        pool=mp.Pool(poolsize)
        source=lacli.pool.File(path)
        keys=[]
        seq=1
        while True:
            name="archive-{}".format(seq)
            try:
                res=upload_temp_key(pool.imap, source, conn, name=name)
                keys.append((res[0],res[1]))
                if res[2] is None:
                    break
                source=res[2]  # continue with remaining file
            except Exception as e:
                import traceback
                traceback.print_exc()
                break
        print "uploaded {} temp keys".format(len(keys))
        for key in keys:
            print "key: {0} (etag: {1})".format(key[0],key[1])
        # TODO join keys into one key
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        print "terminating all procs.."
        # complete upload
        pool.terminate()

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description='parallel upload to S3')
    argparser.add_argument('-u','--federated-user', dest='user', 
        default='testuser', help='user id of uploading user' )
    argparser.add_argument('-d','--duration',  dest='duration', 
        default=3600, help='duration of federated token in seconds')
    argparser.add_argument('-D', '--debug', dest='debug', 
        default='0', help='Enable Boto debugging (0,1 or 2)')
    argparser.add_argument('filename', nargs='*', help='filenames to upload')
    options = argparser.parse_args()
    if not boto_config.has_section('Boto'):
        boto_config.add_section('Boto')
    boto_config.set('Boto','num_retries', '0')
    boto_config.set('Boto','debug',options.debug)
    for fname in options.filename:
        if not os.path.isfile(fname):
            sys.exit('File {} not found.'.format(fname))
        print "putting {}".format(fname)
        pool_upload(options.user, options.duration, fname)
