# -*- mode: python -*-
a = Analysis(['lacli-script.py'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='lacli.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True )
a.datas.append(('cacert.pem', 'cacert.pem', 'DATA'))
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='lacli')
