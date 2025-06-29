# PyInstaller runtime hook for pkg_resources
# This hook ensures that pkg_resources and its dependencies are properly included

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all submodules of pkg_resources
hiddenimports = collect_submodules('pkg_resources')

# Add specific modules that might be missing
hiddenimports += [
    'pkg_resources.py2_warn',
    'pkg_resources.markers',
    'pkg_resources.extern',
    'pkg_resources.extern.packaging',
    'pkg_resources.extern.packaging.version',
    'pkg_resources.extern.packaging.specifiers',
    'pkg_resources.extern.packaging.requirements',
    'pkg_resources.extern.pyparsing',
    'pkg_resources._vendor',
    'pkg_resources._vendor.packaging',
    'pkg_resources._vendor.packaging.version',
    'pkg_resources._vendor.packaging.specifiers',
    'pkg_resources._vendor.packaging.requirements',
    'pkg_resources._vendor.pyparsing',
    'subprocess',
    'platform',
    'tempfile',
    'os',
    'sys',
    'threading',
    'time',
    're',
    'json',
    'pathlib',
    'urllib.request',
    'socket',
    'gc',
]

# Collect data files
datas = collect_data_files('pkg_resources') 