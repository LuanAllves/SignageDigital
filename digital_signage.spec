# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 1. Análise do projeto (onde o PyInstaller encontra os arquivos e pacotes)
a = Analysis(['main.py'],
             pathex=['.'],
             binaries=[],
             datas=[
                ('gui', 'gui'),  # Inclui a pasta 'gui' e seu conteúdo
                ('utils', 'utils'), # Inclui a pasta 'utils' e seu conteúdo
             ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

# 2. Reúne os arquivos e cria o executável principal
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

# 3. Define as informações do executável
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='digital_signage',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False, # Use True para ver o console de debug, False para não
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )

# 4. Cria o instalador ou pacote (opcional)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='digital_signage')