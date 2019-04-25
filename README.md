# Hephaestus

A rudimentary configuration management tool

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Architecture](#architecture)
- [What can be improved](#improvements)

## Installation
Make sure that the following sofware is installed:
- `python` (tested with verision `2.7.10`)
- `pip` (tested with version `18.1`)

```sh
git https://github.com/olarudan/hephaestus.git
cd hephaestus
pip install .
```

## Usage
`hep -c config.yml -i examples/hosts examples/manifests/manifest.yml`

This command will run tasks included in the manifest.yml file on `hosts` declared in `hosts file` using the `config.yml` configuration file

## Architecture
Hephaestus (hep) is a rudimentary configuration management tool capable of executing various tasks on remote hosts through the `ssh` protocol.

### Modules
Hep has a modular architecture which can be extended easily. Currently there are three modules that can perform idempotent actions on remote hosts:
- file (copy local files to remote hosts and change owner/group/mod of the file)
- apt (install or remove apt packages)
- service (restart System V init scripts (services))

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

For modules' available options check the corresponding    class documentation (`hephaestus/modules`)

### Manifests
A `manifest` is a collection of tasks that can be applied to a remote host (examples/manifests/manifest.yml)

### hosts
A `hosts` file is a list of hostnames (or ips) that the manifests are going to be applied to (examples/hosts)
 
### Task runner
The TaskRunner class is responsible for running manifests on each node in the hosts file.
It is capable of parsing the YAML manifest file and instantiating corresponding Class objects for each task. Tasks are run sequentially. Same goes for hosts.

### SSH
The `hep` engine uses the `paramiko` library to manage `ssh` connections through which commands are executed. If any command fails, `hep` will exit with an exit status code of `1`. So, in short, failures are handled by the `SSH` class.

## What can be improved
The list of improvements that could be implemented for `hep`:

- Decrease the number of ssh execute_command calls
- A separate class would be desirable to validate each module's YAML declaration syntax 
- Parallel execution of tasks on multiple hosts (multi-threading or multiple processes)
- The way commands are executed on remote hosts is not ideal. THe preferred way would be to execute as much as possible through python code by copying modules to the remote hosts and then deleting them after the task_runner finishes executing the tasks.
- If a task fails the program exists. An `ignore_error` option could be added to ignore a task that fails
- Error handling is done in the ssh class. This could be improved on.
- The assumption made about stderr and stdout returned by commands executed on remote hosts should be revisited and potentially edge cases be identified.
- `Notify` functionality: one task could trigger another tasks execution (i.e. server restarts after config changes)
- `Iteration functionality` for modules: i.e one task using the apt module could install a list of packages rather than one (limitation)
- Polish module functionality to make some parameters optional (i.e. if not specifying 'src' for the file module then it will not copy the local file to the remote host, it will ony change its mod)




