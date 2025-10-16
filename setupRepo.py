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
import subprocess
from pathlib import Path
from argparse import ArgumentParser
from argparse import Namespace
import inspect
import platform
from typing import Tuple
import logging

from envSetup import *

# ############################################################################
# ## Variables
# ############################################################################
AGS_SCRIPT_URL = "ssh://git@miller.amer.dell.com/cdc/ags_scripts.git"
AGS_SCRIPT_BRANCH = "main"
PY_VERSION = "Python312_v1"
PY_DIR = os.path.join(os.getenv("BUILDTOOLS_PATH_OVERRIDE"), PY_VERSION)
PY_VER_PATH = os.path.join(BASE_BUILDTOOLS_PATH, f".{PROJECT_ID}_pyver")
PY_VENV_DIR = os.path.join(os.getenv("BUILDTOOLS_PATH_OVERRIDE"), f".{PROJECT_ID}_{PY_VERSION}.venv")
INCLUDE_FILES = {__name__}
logger = logging.getLogger(__name__)

#
# @brief     cloneUpdateAgSScripts
# @details   Clone or update ags_scritps to manage platform build management.
#
def cloneUpdateAgSScripts():
    funcName = inspect.currentframe().f_code.co_name + '()'
    # Create the DevTools dir if it does not exist
    devToolsDir = os.path.join(BASE_BUILDTOOLS_PATH, "DevTools")
    os.makedirs(name = devToolsDir, exist_ok = True)

    scriptsDir = os.path.join(devToolsDir, "ags_scripts")
    print(f"scriptsDir: {scriptsDir}")

    # Clone the ags_scripts repo to {BASE_BUILDTOOLS_PATH}/DevTools/Scripts
    if os.path.exists(scriptsDir):
        clCmd = f"cd {scriptsDir} && git checkout {AGS_SCRIPT_BRANCH} && git pull origin {AGS_SCRIPT_BRANCH}"
    else:
        clCmd = f"git clone --branch {AGS_SCRIPT_BRANCH} {AGS_SCRIPT_URL} {scriptsDir}"
    print(clCmd)
    retVal = os.system(clCmd)
    if retVal != 0:
        print(f"Cloning Ags-Scripts failed with, returncode={retVal}, bailing out...")
        sys.exit(1)
    print(f"{funcName}: Ags-Scripts cloned and copied successfully...")


# Call to clone/update the ags_script download
cloneUpdateAgSScripts()

############################################################################
## Imports from agsscripts
############################################################################
from biosCommonDefs import biosEnvSettings, artifactSettings
import biosCommonFuncs
import configSupport
import credSupport
import prepare_tools
import transferHelper

from DellPkgs.BuildTools.DellTools.envSupport import InitializeWsEnv
from DellPkgs.BuildTools.DellTools.platformSupport import DownloadDpfBinPackages

############################################################################
## Function Implementation
############################################################################

#
# @brief     initEnv
# @details   Initialize the environment for the script
#
def initEnv():
    if os.getenv("BUILDTOOLS_PATH_OVERRIDE", default=None) is None:
        buildToolsPath = os.path.abspath("c:\\bea\\BuildTools")
        if not os.path.exists(buildToolsPath):
            raise Exception(f"{buildToolsPath} does not exist. Exiting ...")
        os.environ["BUILDTOOLS_PATH_OVERRIDE"] = buildToolsPath

    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(message)s",
        filename=os.path.join(os.getenv("BUILDTOOLS_PATH_OVERRIDE"), "setupRepoPython.log"), filemode='w')
    logger.setLevel(logging.INFO)
    return buildToolsPath


def trace_statements(frame, event, arg):
    if event == 'line':
        # Get filename and line number
        filename = os.path.basename(frame.f_code.co_filename)
        lineno = frame.f_lineno
        # Get the name of the function currently being executed
        func_name = frame.f_code.co_name

        # Optionally, get the line of code itself (requires reading the file)
        # For simplicity, we'll just print filename, line number, and function name
        print(f"[{filename}:{lineno}] - {func_name}() - Executing line.")
    return trace_statements

def custom_trace(frame, event, arg):
    filename = os.path.basename(frame.f_code.co_filename)
    lineno = frame.f_lineno
    func_name = frame.f_code.co_name

    # Optional: Filter by file
    if INCLUDE_FILES and filename not in INCLUDE_FILES:
        return custom_trace # Continue tracing, but ignore this file

    # Log based on event type
    if event == 'line':
        logger.info(f"LINE: [{filename}:{lineno}] - {func_name}()")
    elif event == 'call':
        logger.info(f"CALL: [{filename}:{lineno}] - Entering {func_name}()")
    elif event == 'return':
        logger.info(f"RETURN: [{filename}:{lineno}] - Exiting {func_name}() (Returned: {arg})")
    elif event == 'exception':
        exc_type, exc_value, _ = arg
        logger.error(f"EXCEPTION: [{filename}:{lineno}] - In {func_name}() - {exc_type.__name__}: {exc_value}")

    return custom_trace


#
# @brief     deployVirtualEnv
# @details   Setup and/or update the Python virtual environment and install dependencies
# @param pydir: Python Install Path

def deployVirtualEnv(pydir: str) -> str:
    funcName = inspect.currentframe().f_code.co_name + '()'

    venvPath = os.path.join(os.getenv("BUILDTOOLS_PATH_OVERRIDE"), f".{PROJECT_ID}_{os.path.basename(pydir)}.venv")
    pypath = os.path.join(pydir, "python")
    requirementsPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "py_requirements.txt")

    if not os.path.exists(venvPath):
        subprocess.run([pypath, "-m", "venv", venvPath])
        print(f"{funcName}: Python virtual environment created at {venvPath}")

    if biosEnvSettings['ServerEnv'] == False:    
        subprocess.run([os.path.join(venvPath, "Scripts", "python"), "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.run([os.path.join(venvPath, "Scripts", "python"), "-m", "pip", "install", "-r", requirementsPath])
        subprocess.run([os.path.join(venvPath, "Scripts", "python"), "-m", "pip", "list"])

    print(f"{funcName}: Python module requirements installed...")

    print(f"[NOTE] {funcName}: !!!!! Use the virtual environment @{venvPath} for activation for all your future build sessions !!!!!")


def isPythonVenvExists() -> Tuple[bool, str]:

    # Check if python version file exists
    if not os.path.exists(PY_VER_PATH):
        return False, ""

    # Check if python virtual environment exists
    with open(PY_VER_PATH, "r") as pyVerFd:
        storedPyDir = pyVerFd.readline().strip()

    venvPath = os.path.join(os.getenv("BUILDTOOLS_PATH_OVERRIDE"), f".{PROJECT_ID}_{os.path.basename(storedPyDir)}.venv")
    if not os.path.exists(venvPath):
        return False, ""

    # Check if DevTools/ags_scripts exists
    agsScriptsPath = os.path.join(os.getenv("BUILDTOOLS_PATH_OVERRIDE"), "DevTools", "ags_scripts")
    if not os.path.exists(agsScriptsPath):
        return False, ""

    return True, storedPyDir

#
# @brief     setUpPythonEnv
# @details   Setup the Python virtual environment and install dependencies
# @param pydir: Python Install Path
#
def setUpPythonEnv(pydir: str) -> None:
    funcName = inspect.currentframe().f_code.co_name + '()'

    # Check if the Python install path exists
    if not os.path.exists(pydir):
        print(f"{funcName}: Python doesn't exist under {pydir}, please install base Python312_v1 version under {os.getenv('BUILDTOOLS_PATH_OVERRIDE')} and try again...")
        sys.exit(1)

    if not os.path.exists(os.path.join(pydir, "python.exe")):
        print(f"{funcName}: Python install path {pydir} doesn't contain python.exe, please install base Python312 version and try again...")
        sys.exit(1)

    # Setup the python virtual environment and install dependencies
    print(f"{funcName}: Deploying a Python virtual environment and installing dependencies...")
    deployVirtualEnv(pydir)

    # Create python version file as per user input
    buildToolsPath = os.getenv("BUILDTOOLS_PATH_OVERRIDE")
    with open(PY_VER_PATH, "w") as pyVerFd:
        pyVerFd.write(pydir)

    # Add agslib.pth file to site-packages to be available in the virtual environment
    libpth = os.path.join(PY_VENV_DIR, "Lib", "site-packages", "agslib.pth")
    if not os.path.exists(libpth):
        with open(libpth, "w") as libpthFd:
            libpthFd.write(os.path.join(os.getenv("BUILDTOOLS_PATH_OVERRIDE"), "DevTools", "ags_scripts", "python"))

    print(f"{funcName}: Activate your virtual environment by running {os.path.join(PY_VENV_DIR, 'Scripts', 'activate')}")


#
# @brief UpdateSysPath
# @details Update the sys.path to include the BuildTools path and ags-scripts subdirectories
#
def UpdateSysPath():
    buildToolsPath = os.getenv("BUILDTOOLS_PATH_OVERRIDE")
    if not os.path.exists(buildToolsPath) and not os.path.exists(os.path.join(buildToolsPath, "DevTools", "ags-scripts")):
        print(f"{buildToolsPath} or {os.path.join(buildToolsPath, 'DevTools', 'ags-scripts')} does not exist. Exiting ...")
        sys.exit(1)
    else:
        sys.path.insert(0, os.path.join(buildToolsPath, "DevTools", "ags_scripts", "python"))
#
# @brief setGpgCredentials
# @details Set GPG credentials for the build process
#
def setGpgCredentials():
    prepare_tools.setCredentials()

def is_in_venv() -> bool:
    # sys.prefix: The virtual environment/site-packages directory that runs this python script
    # sys.base_prefix: Set during Python startup, points where system wide site-packages live.
    # If sys.base_prefix == sys.prefix, then the virtual environment is not active
    return sys.prefix != sys.base_prefix

#
# @brief    SetupGitTemplates
# @details  Configures git templates and hooks based on the batch script provided.
#
# @param WsDir (str): Workspace path
# @param PythonToolPath (str): The Python command to use for running scripts.
#
def SetupGitTemplates(WsDir, PythonToolPath):
    # Copy everything from GitFiles to the .git directory
    print("SetupGitTemplates() Start")

    if os.path.exists(biosEnvSettings['DevToolsDir']):
        repoGitDir = os.path.join(WsDir, '.git')
        repoGitHooksDir = os.path.join(repoGitDir, 'hooks')
        gitTemplateDir = os.path.join(biosEnvSettings['DevToolsDir'], 'ags_scripts', 'python', 'GitFiles')

        # Copy the commit template file
        biosCommonFuncs.CopyFile2(os.path.join(gitTemplateDir, 'Commit-Template.txt'), os.path.join(repoGitDir, 'Commit-Template.txt'))

        # Set the template for the superproject's commit log
        if os.path.exists(os.path.join(gitTemplateDir, 'Commit-Template.txt')):
            subprocess.run(['git', 'config', '--local', 'commit.template', os.path.join(repoGitDir, 'Commit-Template.txt')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Copy the pre-push hook to every hooks directory in .git/modules
        for file in os.listdir(os.path.join(gitTemplateDir, 'hooks')):
            biosCommonFuncs.CopyFile2(os.path.join(gitTemplateDir, 'hooks', file), os.path.join(repoGitHooksDir, file))

        # Replace strings in commit-msg and pre-push files
        if platform.system() == 'Windows':
            PythonToolPath = PythonToolPath.replace('\\', '\\\\')
        print(f"PythonToolPath: {PythonToolPath}")

        for file in os.listdir(repoGitHooksDir):
            if file in ['commit-msg', 'pre-push']:
                file_path = os.path.join(repoGitHooksDir, file)
                with open(file_path, 'r') as f:
                    file_content = f.read()
                replaced_content = file_content.replace('PYTHON_PATH', PythonToolPath)
                with open(file_path, 'w') as f:
                    f.write(replaced_content)
    else:
        print("Error: DevToolsPath does not exist")

#
# @brief     DownloadCompilersTools
# @details   Download compilers and tools defined in repoConfig.yaml
#
# @param RootDir    Edk2 package directory
# @param Override   True: Download the tools and override the old onces
#                   False: Default. Skips downloading the tools, if the output directory exist
#
def DownloadCompilersTools(RootDir: str, Override: bool = False) -> bool:
    RootBuild = os.getenv("ROOT_BUILD", default=os.path.join(os.getenv("BUILDTOOLS_PATH_OVERRIDE"), "temp"))
    retVal = False

    # Get compilers binaries
    repoConfigData = configSupport.LoadYamlData(os.path.join(RootDir, 'repoConfig.yaml'))
    print(f"Compilers to Download: {repoConfigData['COMPILERS']}")
    for compiler in repoConfigData['COMPILERS']:
        print(f"compiler: {compiler}")
        retVal = transferHelper.DownloadWithCurl(RootBuild,
                        f"{artifactSettings['CPG_BIOS_DEV_COMPILERS_URL']}/{compiler['ver']}.7z",
                        f"{os.path.join(biosEnvSettings['BuildToolsDir'], compiler['out'])}",
                        Override)
        # In case of failure exit download 
        if retVal == False:
            break
    return retVal


# @brief     setupRepoInit
# @details   Process the command line arguments
# @param args: Command line arguments

def setupRepoInit(args: Namespace) -> None:
    funcName = inspect.currentframe().f_code.co_name + '()'
    repoRootDir = f"{WORKSPACE_ROOT}"
    os.environ['REPO_ROOT'] = repoRootDir  ## Use local repo root
    repoConfigData = {}
    retVal = False

    print(f"{funcName}: Repo Root: {repoRootDir}")

    if args.env:
        exists, pydir = isPythonVenvExists()
        if not exists:
            pydir = os.path.join(os.getenv("BUILDTOOLS_PATH_OVERRIDE"), PY_VERSION)
            setUpPythonEnv(pydir)
        else:
            print(f"{funcName}: Python virtual environment already exists at {pydir}.venv, checking for updates...")
            deployVirtualEnv(pydir)

            if is_in_venv(): # if this script is running in the virtual environment
                if not prepare_tools.hasValidCredentials():
                    print(f"{funcName}: Credentials not set, please set up the credentials with -c option and try again...")
                    sys.exit(1)
                    # retVal = credSupport.CreateNetrc()
                    # if retVal == 0:
                    #     prepare_tools.downloadDefaultTools(args.force)
                    #     credSupport.DeleteNetrc()

    if args.setup:
        setUpPythonEnv(args.pydir)

    repoConfigData = configSupport.ReadConfigFile(os.path.join(repoRootDir, 'repoConfig.yaml'))
    repoConfigMtime = os.path.getmtime(os.path.join(repoRootDir, 'repoConfig.yaml'))

    recreate = False
    if os.path.exists(WS_ENV_VAR_PATH):
        envVarMtime = os.path.getmtime(WS_ENV_VAR_PATH)
        if (repoConfigMtime > envVarMtime):
            recreate = True

    envVarList = InitializeWsEnv(repoRootDir, ROOT_BUILD, repoConfigData, recreate)
    # print(f"envVarList: {envVarList}")
    if os.path.exists(PY_VER_PATH):
        with open(PY_VER_PATH, "r") as pyVerFd:
            envVarList['LATEST_PYPATH'] = pyVerFd.readline().strip()
    
    SetupGitTemplates(repoRootDir, os.getenv('PYTHON_PATH', default=PY_DIR))

    if args.credentials:
        prepare_tools.setCredentials()
        print(f"{funcName}: Credentials set successfully...")

    if args.download:
        # Download compilers and tools
        try:
            retVal = prepare_tools.downloadDefaultTools(args.force)
            if retVal:
                retVal = credSupport.CreateNetrc()
                if retVal == 0:
                    retVal = DownloadCompilersTools(repoRootDir, args.force)
                    if retVal:
                        retVal = DownloadDpfBinPackages(envVarList)
                    credSupport.DeleteNetrc()
        except subprocess.CalledProcessError as e:
            print(f"Downloading compilers and tools failed with error: {retVal}, bailing out...")
            sys.exit(1)
        print(f"{funcName}: Compilers and tools downloaded successfully...")

    if args.upload:
        prepare_tools.uploadArtifact(args.upload[0], args.upload[1])


############################################################################
## Entry Point Function
############################################################################
if __name__ == "__main__":

    # Enable tracing (not now, but in case we need it later)
    #sys.settrace(trace_statements)

    parser = ArgumentParser(description="Setup the AGS repo for build management")
    group = parser.add_mutually_exclusive_group(required=True)

    # Setup mutually exclusive arguments first
    group.add_argument("-e", "--env", dest="env", action="store_true", required=False, default=False, help="Check and setup the python virtual environment")
    group.add_argument("-p", "--pydir", dest="pydir", type=str, required=False, help="Python Install Path")
    group.add_argument("-c", "--credentials", dest="credentials", action="store_true", required=False, default=False, help="Set credentials for Artifactory downloads")
    group.add_argument("-u", "--upload", dest="upload", nargs=2, required=False, default=None, help="Upload artifacts to Artifactory: <srcPath> <relative dstPath")

    parser.add_argument("-s", "--setup", dest="setup", action="store_true", required=False, default=False, help="Setup python virtual environment and install dependencies")
    parser.add_argument("-d", "--download", dest="download", action="store_true", required=False, default=False, help="Download compilers and tools")
    parser.add_argument("-f", "--force", dest="force", action="store_true", required=False, default=False, help="Forces the tools and compiler download")

    args = parser.parse_args()
    if not any([args.setup, args.download, args.credentials]) and args.pydir:
        print("One of the options -s, -d, is required along with -p. Exiting ...")
        sys.exit(1)

    setupRepoInit(args)

    # Disable tracing
    sys.settrace(None)