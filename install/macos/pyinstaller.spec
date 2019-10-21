# -*- mode: python -*-
import sys
import os
import inspect

# Get the version
root = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    )
)
sys.path.insert(0, root)
import flock_agent

version = flock_agent.flock_agent_version
print("Flock Agent version: {}".format(version))

a = Analysis(
    ["flock-agent"],
    pathex=["."],
    binaries=None,
    datas=[("../../share", "share")],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name="flock-agent",
    debug=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, name="flock-agent"
)

app = BUNDLE(
    coll,
    name="Flock.app",
    icon="flock-agent.icns",
    bundle_identifier="media.firstlook.flock-agent",
    info_plist={
        "LSUIElement": True,
        "NSHighResolutionCapable": True,
        "CFBundleShortVersionString": version,
    },
)
