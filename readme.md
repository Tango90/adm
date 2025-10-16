# AGS_2025

## System Requirements
- Git
- 7-zip
- Python 3.12
- VS2019
- CLang
- SSH
- GPG

__NOTE:__ For detailed tools information https://confluence.cpg.dell.com/display/CDC/System+Setup

## Project Setup
### Environment Variables
1. Create a tools directory where the compilers and tools will be stored (e.g. __C:\bea\BuilTools__ or a path of your choice).
2. Press `WINDOWS + s` to open the windows search option.
3. Type 'environment vairable', this will show an option *'Edit the system environment variables'*. Selecting this option will open 'System Properties' window.
4. Click on the *'Environment Variables...'* button.
5. Under the 'System variables' section, select *'New...'* button.
6. Fill the variable name box with __BUILDTOOLS_PATH_OVERRIDE__
7. For value type the directory path to the tools (e.g. __C:\bea\BuilTools__). Or use 'Browse Directory...' to locate the directory path.
8. Select *OK* for all the previously open windows.

### User Credentials
User credentials for artifactory downloads will use GPG encryption. User credentials such as corporate username and password shall be obtained during the setup process and encrypted credentials shall be saved onto the disk.

### GIT
Since the project will use command line version of GIT client, make sure the system has GIT installed. Otherwise, down it from https://git-scm.com/ to install it. Follow the GIT client and SSH configuration setup used for AgS repos.

### 7-zip
It is useful to download 7zip from web. 7zip shall also be available under DevTools folder of $BUILDTOOLS_PATH_OVERRIDE(default:C:\bea\BuildTools)

### VS2019
  VS2019 shall be downloaded automatically when a first build is done on a machine and it is availble under $BUILDTOOLS_PATH_OVERRIDE

### Python
For this project, Python3.12 is used. A prepackaged version is available in the artifactory. Follow the steps below to set up python,
1. Download the package from https://artifactory.cpg.dell.com/artifactory/dellcorebinary-gen-prod-local/com/dell/cpg/firmware/bios/compilers/Python/Python312_v1.7z
2. Extract the file content to __C:\bea\BuilTools\Python312_v1__

### SSH
To setup SSH to be used with Git, follow the instructions at: https://confluence.cpg.dell.com/display/~tony_chen5/Setup+SSH+on+Git

### GPG
To setup GPG to be used with Git and AGS builds, follow the instructions at: https://confluence.cpg.dell.com/display/CSGSD/GPG+Signing

### Repo Download
Use command line or GUI GIT to clone the POC repo to a directory of you choosing. It is advisable to use shorter path length to the clone the repo.

```
git clone --progress --recursive https://git.cpg.dell.com/scm/cdc/ags_2025.git

git clone --progress --recursive ssh://git@git.cpg.dell.com/cdc/ags_2025.git
```


## Key Script Information
There are a few important files are in the project

### *Repository Config Files*
- __repoConfig.yaml:__ This file resides in the root directory of the project / repo. It contains AgS repo generational information.
- __siConfig.yaml:__ This file resides in the `<Root Directory>/DellPkgs/DellSiPkgs/<Silicon Directory>` (e.g. *C:\bea\poc_ags_2025\DellPkgs\DellSiPkgs\LunarLake\siConfig.yaml*)
- __platConfig.yaml:__ This file resides in the respective platform directory (e.g. *C:\bea\poc_ags_2025\DellPkgs\DellPlatformPkgs\NB\TributoLnlPkg\platConfig.yaml*)

### *Maven Config Files*
- `<Root Directory>/pom.xml`:
- `<Root Directory>/DellPkgs/pom.xml`:
- `<Root Directory>/DellPkgs/DellPlatformPkgs/pom.xml`:
- `<Root Directory>/DellPkgs/DellPlatformPkgs/<DT/NB/PW>/pom.xml`:
- `<Root Directory>/DellPkgs/DellPlatformPkgs/<DT/NB/PW>/<Platform Pkg>/pom.xml`:

### *Package Manager and Helper Scripts*
- [buildManager.py](DellPkgs/BuildTools/DellTools/buildManager.py)
- [envDefs.py](DellPkgs/BuildTools/DellTools/envDefs.py)
- [envSupport.py](DellPkgs/BuildTools/DellTools/envSupport.py)
- [prepare_tools.py](DellPkgs/BuildTools/DellTools/prepare_tools.py)
- [platformPkgManager.py](DellPkgs/BuildTools/DellTools/platformPkgManager.py)
- [platformSupport.py](DellPkgs/BuildTools/DellTools/platformSupport.py)

__NOTE:__ For more details on these scripts checkout the [DellTools/Readme.md](DellPkgs/BuildTools/DellTools/readme.md) (*Under construction*)


## How to run the build
- Open up a Windows Command terminal and go to your workspace root directory.
- If you are running the setupRepo.py for the first time, and run *setupRepo -p <Python_Installation_Path> -s -c -d*. E.g.
`setupRepo.py -p C:\bea\BuildTools\Python312_v1 -s -c -d` This will setup a Python virtual environment for the specified Python version with necessary python packages, accepts user credentials and saves encrypted credentials onto the disk and downloads necessary tools and compiler for the supported SI platforms.
- Else if your password is changed run `setupRepo.py -p C:\bea\BuildTools\Python312_v1 -c`
- Else if your platform tools/compilers are updated in the SI configuration, run `setupRepo.bat -p C:\bea\BuildTools\Python312_v1 -d`
- The '-s' option sets up Python virtual environment by downloading necessary python packages and setup common python scripts on a subfolder under __BUILDTOOLS_PATH_OVERRIDE__
- The '-p' option specifies where Python312_v1 is installed (usally under __BUILDTOOLS_PATH_OVERRIDE__) and sets up Python virtual environment for that Python version and activates that version for future use in the Windows Command terminal session
- The '-c' option gets user credentials and save encrypted credentials to be used later when downloading dependent tools and binaries during the build process
- The '-d' option downloads essential tools and compilers to enable build process
- The virtual environment is created under __BUILDTOOLS_PATH_OVERRIDE__/.ags2025_<PythonVer>_v1.env. When a windows command terminal is open, activate the Virtual environment using __BUILDTOOLS_PATH_OVERRIDE__/.ags2025_<PythonVer>_v1.env/activate.bat
- Go to a platform directory (e.g. DellPkgs\DellPlatformPkgs\NB\TarokoPtlOnePkg) and run build from a command prompt with __-nou__. E.g.
`DellPkgs\DellPlatformPkgs\NB\TarokoPtlOnePkg> builda -nou`
