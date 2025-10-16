"""
############################################################################
Copyright (c) 2024 - 2025 Dell Inc. All rights reserved.
This software and associated documentation (if any) is furnished
under a license and may only be used or copied in accordance
with the terms of the license. Except as permitted by such
license, no part of this software or documentation may be
reproduced, stored in a retrieval system, or transmitted in any
form or by any means without the express written consent of
Dell Inc.
############################################################################
"""
############################################################################
## Includes
############################################################################
import os 
import sys
import platform

from pathlib import Path

############################################################################
## Variables
############################################################################
PROJECT_ID = "ags_2025"

WORKSPACE_ROOT = os.getenv('WORKSPACE_ROOT', default=Path(__file__).resolve().parent)
ROOT_BUILD = os.path.join(WORKSPACE_ROOT, 'Build')
if not os.path.exists(ROOT_BUILD):
    print(f'Creating: {ROOT_BUILD}')
    os.makedirs(ROOT_BUILD)
    os.environ['ROOT_BUILD'] = ROOT_BUILD
WS_ENV_VAR_PATH = os.path.join(ROOT_BUILD, 'envVars.json')

############################################################################
## Function Implementation
############################################################################
#
# Initialize sys path
#

def InitializeSysPath():
    buildToolsPath = os.getenv('BUILDTOOLS_PATH_OVERRIDE', default = None)
    if buildToolsPath is None:
        if platform.system() == 'Windows':
            buildToolsPath = os.path.join('C:', 'bea', 'BuildTools')
        else:
            buildToolsPath = os.path.join('/', 'bea', 'BuildTools')
        os.environ["BUILDTOOLS_PATH_OVERRIDE"] = buildToolsPath
    os.makedirs(name = buildToolsPath, exist_ok = True)
    if not os.path.exists(buildToolsPath):
        raise Exception(f"{buildToolsPath} does not exist. Exiting ...")
        sys.exit(1)

    
    # delltoolsPath = os.path.join(WORKSPACE_ROOT, 'DellPkgs','BuildTools', 'DellTools')

    # print(f"buildToolsPath: {buildToolsPath}")
    sys.path.insert(0, buildToolsPath)
    sys.path.insert(0, os.path.join(buildToolsPath, "DevTools"))
    sys.path.insert(0, os.path.join(buildToolsPath, "DevTools", "ags_scripts", "python"))
    return buildToolsPath

############################################################################
## Variables
############################################################################
# Calling to Initialize the environment
BASE_BUILDTOOLS_PATH = InitializeSysPath()

#
# 
#
print(f"BASE_BUILDTOOLS_PATH    : {BASE_BUILDTOOLS_PATH}")
print(f"PROJECT_ID              : {PROJECT_ID}")
print(f"WORKSPACE_ROOT          : {WORKSPACE_ROOT}")
print(f"ROOT_BUILD              : {ROOT_BUILD}")
print(f"WS_ENV_VAR_PATH         : {WS_ENV_VAR_PATH}")
# print(f"sys.path: {sys.path}")