import os
import pkg_resources

from mypylib.mypylib import MyPyClass
from myioncore.myioncore import MyTonCore

from mypylib.mypylib import (
    run_as_root
)

from typing import Optional


def migrate_to_version_1(local: MyPyClass, ion: MyTonCore):
    # get script path
    migrate_script_path = pkg_resources.resource_filename('myionctrl', 'migrations/migration_001.sh')
    args = ["/bin/bash", migrate_script_path]
    exit_code = run_as_root(args)
    if exit_code != 0:
        raise RuntimeError(f'Failed to run migration error. Exit code: {exit_code}')
    return


def migrate(version: 0, local: MyPyClass, ion: MyTonCore):
    restart = False
    if version < 1:
        local.add_log(f'Running migration {version} -> 1', 'info')
        restart_required = migrate_to_version_1(local, ion)
        restart = restart or restart_required
    return 1, restart


def run_migrations(local: Optional[MyPyClass]=None, ion: Optional[MyTonCore]=None):
    if local is None:
        local = MyPyClass('myionctrl.py')
    if ion is None:
        ion = MyTonCore(MyPyClass('myioncore.py'))

    # migrations    
    version = 0
    
    workdir = local.buffer.my_work_dir
    version_file_path = os.path.join(workdir, 'VERSION')
    if os.path.exists(version_file_path):
        with open(version_file_path, 'r') as f:
            version = int(f.read())
    
    new_version, restart = migrate(version, local, ion)
    
    with open(version_file_path, 'w') as f:
        f.write(f'{new_version}')
    return restart
#end define
