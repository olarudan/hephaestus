# Hephaestus

A rudimentary configuration management tool

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Tests](#tests)
- [Architecture](#architecture)
- [What can be improved](#improvements)

## Installation
Make sure that the following software is installed on your system:
- `python` (tested with version `2.7.10`)
- `pip` (tested with version `18.1`)

```sh
git clone https://github.com/olarudan/hephaestus.git
cd hephaestus
pip install .
```

## Usage
The following command will run a manifest ([examples/manifests/manifest.yml](examples/manifests/manifest.yml)) against a list of hosts ([examples/hosts](examples/hosts)) using the ([config.yml.example](config.yml.example)) configuration file.

`hep -c config.yml -i examples/hosts examples/manifests/manifest.yml`

For more information on cli args use:
`hep -h`

## Tests
Make sure pytest is installed on your system: `pip install pytest`
```sh
cd hephaestus
pytest
```

## Architecture
Hephaestus (hep) is a rudimentary configuration management tool capable of executing various tasks on remote hosts by leveraging the `ssh` protocol.

### Modules
`Hep` has a modular architecture which can be extended easily. Currently there are three modules that can perform idempotent actions on remote hosts:
- `file` (copy local files to remote hosts and change owner/group/mod of the file). Here is a list of available options for this module:

> `action`: `present` or `absent`. The present action will create the file and absent will remove it.

> `src`: path to the source file

> `dest`: path to the destination (remote host) file

> `owner`: user on the remote machine

> `group`: group on the remote machine

> `mod`: mode in octal (i.e `777` read/write/execute permissions for user/group/other)


- `apt`: (install or remove apt packages). Here is a list of available options for this module:

> `package`: the package that the action is going to be performed on

> `action`: `remove` or `install`


- `service` (restart System V init scripts (services)). Here is a list of available options for this module:

> `service`: the service the action is going to be performed on

> `action`: `restart`


New modules can be added to the modules directory which will be registered automatically by the TaskRunner class.
The `apt` and `service` modules execute actions using corresponding unix programs (`apt` and `service`) while the `file` module executes its actions using python modules (i.e `os`).

### Tasks
A task is the smallest unit of functionality that can be executed on a remote host. Each task is defined through YAML syntax.

It consists of:
- task name
- module name
- module options

Here is an example (examples/manifests/manifest.yml) which installs the `apache2` apt package:
```
- name: "Install apache2 package"
  apt:
    package: "apache2"
    action: "install"
```
     
In the example above:
- task name: `Install apache2 package`
- module name: `apt`
- module options:
  - package: `apache2`
  - action: `install`

For modules' available options check the corresponding class documentation ([hephaestus/modules](hephaestus/modules))

### Manifests
A `manifest` is a collection of tasks that can be applied to a remote host ([examples/manifests/manifest.yml](examples/manifests/manifest.yml))

### hosts
A `hosts` file is a list of hostnames (or IPs) that the manifests are going to be applied to ([examples/hosts](examples/hosts))
 
### Task runner
The TaskRunner class is responsible for running manifests on each node in the hosts file.
It is capable of parsing the YAML manifest file and instantiating corresponding Class objects for each task and running the associated action. Tasks are run sequentially. Same goes for hosts.

### SSH
The `hep` engine uses the `paramiko` library to manage `ssh` connections through which commands are executed. If any command fails, `hep` will exit with an exit status code of `1`. So, in short, failures are handled by the `SSH` class.

## What can be improved
The list of improvements that could be implemented for `hep`:

- Decrease the number of ssh execute_command calls
- A separate class method for each hep module could be used to validate the module's YAML declaration.
- Parallel execution of tasks on multiple hosts (multi-threading or multiple processes)
- The way commands are executed on remote hosts is not ideal. The preferred way would be to execute as much as possible through python code by copying modules to the remote hosts and then deleting them after the task_runner finishes executing all tasks. Currently some of the actions are performed using python 'one liners' which are hard to read: `cmd = "python -c \"exec(\\\"import os\\nprint oct(os.stat('%s').st_mode)[4:]\\\")\"" % (self.dest)`
- If a task fails the program exists. An `ignore_error` option could be added to ignore a task that fails and prevent the task runner from aborting the whole thing.
- Error handling is done in the ssh class. This could be improved.
- The assumption made about stderr and stdout returned by commands executed on remote hosts should be revisited and potentially edge cases be identified and dealt with. In general validation/error/exception handling could be improved.
- `Notify` functionality: one task could trigger another tasks execution (i.e. server restarts after config changes)
- `Iteration functionality` for `hep modules` (i.e one task would install a list of packages rather than creating a separate task for each package install)
- Polish module functionality to make some parameters optional (i.e. if `scr` option is omitted from `apt` then the module will not copy the src file to the destination but still execute the other options i.e change mod of the dest file)
- A better way to handle cli args: https://github.com/google/python-fire
