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
a.datas.append(('srm.bat', 'srm.bat', 'DATA'))
coll = COLLECT(exe,
               a.binaries + [('msvcp110.dll', 'C:\\Windows\\System32\\msvcp110.dll', 'BINARY'),
                             ('msvcr110.dll', 'C:\\Windows\\System32\\msvcr110.dll', 'BINARY')]
                             if sys.platform == 'win32' else a.binaries,
			   a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='lacli')
