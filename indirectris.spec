# -*- mode: python -*-

block_cipher = None


a = Analysis(['indirectris.py'],
             pathex=['/home/morozov/minor_projects/indirectris'],
             binaries=[],
             datas=[('cp437_12x12.png', '.'), ('indirectris.xp', '.'), ('indirectris.json', '.'), ('/usr/local/lib/python3.6/site-packages/bearlibterminal/libBearLibTerminal.so', '.'), ('Fail.wav', '.'), ('Fly.wav', '.'), ('Connect.wav', '.'), ('Explosion.wav', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='indirectris',
          debug=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='indirectris')
