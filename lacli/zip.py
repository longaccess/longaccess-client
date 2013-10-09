from zipfile import ZipFile, ZIP_DEFLATED


def zip_writer(out, files, cache):
    zpf = ZipFile(out, 'w', ZIP_DEFLATED, True)
    for f in files:
        zpf.write(f)
        yield f
    zpf.close()
