# WSL Cheatsheet

## wsl Help
```powershell
wsl --help
```

## Check WSL status
```powershell
wsl --status
```

## Check WSL version
```powershell
wsl --version
```

## Update WSL
```powershell
wsl --update
```

## To list installed distributions 
(The default version of distro is explicitly mentioned in paranthesis)
```powershell
wsl -l
wsl --list
```

## See a list of the Linux distributions available through the online store
```powershell
wsl -l -o
wsl --list --online
```

## To list installed distributions along with its running status and wsl config being 1 or 2 
The default version of distro is explicitly marked with prefix `*` before its name
```powershell
wsl -l --verbose
wsl -l -v
```

## Set default WSL version
```powershell
wsl --set-default-version <Version>
```

## To run a specific distro
```powershell
wsl -d distro_name
wsl --distribution distro_name
```

## To terminate/shutdown a specific distro
```powershell
wsl -t distro_name_to_shutdown
wsl --terminate distro_name_to_shutdown
```

## To shutdown all disstros
```powershell
wsl --shutdown
```

## Set specific distro as default
```powershell
wsl -s my_default_distro
wsl --set-default my_default_distro
```

## To EXPORT a running distro as image
(Defaults to tar format)
```powershell
wsl --export distro_name_to_export windows_path\tar_file_name.tar
```

## To EXPORT a running distro as image in vhd format
(only supported using WSL 2)
```powershell
wsl --export distro_name_to_export --vhd windows_path\tar_file_name.vhd
```

## To IMPORT an image as distro
```powershell
wsl --import new_distro_name install_location_windows_path tar_file_name.tar --version wsl-version-1-or-2
wsl --import Ubuntu-20 D:\VMs\WSL\Ubuntu-20\ Ubuntu-20.04.tar --version 2 ## Setting my secondary HDD as storate loc for new distro
wsl --import Ubuntu-20 --vhd D:\VMs\WSL\Ubuntu-20\ Ubuntu-20.04.vhd --version 2 ## Importing distro in vhd format
```

## To UNREGISTER a distro
(also removes the its file storage)
```powershell
wsl --unregister distro_name_that_delete
```

## To run a WSL distro as the specified user.
```powershell
wsl -u username -d distroname
wsl -u root -d Ubuntu-20.04
```

## To change the default user for a distribution
```powershell
DistributionName config --default-user Username
ubuntu config --default-user my_default_username
ubuntu2004.exe config --default-user johndoe ## When you have Ubuntu 20.04 version installed from the Microsoft Store
```

## Identify IP address of your Linux distribution installed via WSL 2
(the WSL 2 VM address)
```powershell
wsl hostname -I
```

## Identify IP address of the Windows machine as seen from WSL 2 
(the WSL 2 VM)
```powershell
ip route show | grep -i default | awk '{ print $3}'
```

## List of deprecated WSL Commands
These commands were the original wsl syntax for configuring Linux distributions installed with WSL, but have been replaced with the wsl or wsl.exe command syntax.
```powershell
wslconfig.exe [Argument] [Options]
bash [Options]
lxrun /[Argument]
```
