import latvm.tvm
import lacli.pool
import multiprocessing as mp
from itertools import repeat

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

