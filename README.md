This a project for Udacity's Full Stack Web Developer Nanodegree and tutorial is inspired from one of courses.
# Prerequisites

- VirtualBox, see [VirtualBox](#install-virtualbox) section
- Vagrant, see [Vagrant](#install-vagrant) section
- VM configuration, see [Download the VM configuration](#download-the-vm-configuration) section

# How to run the code

- Clone the repository `git clone https://github.com/adityamehra/catalog.git` or download the repository.
- Install the prerequisites
- Move the repository to the directry called __vagrant__, see [Download the VM configuration](#download-the-vm-configuration) section
- Run the following command:
 1. `python database_setup`, to create sqlite database catalog with Category and Item tables
 2. `python fill_catalog.py`, to fill the tables with some values
 3. `python server.py`, to get the website up and running
- Go to http://localhost:8000/

## Install VirtualBox
VirtualBox is the software that actually runs the virtual machine. [You can download it from virtualbox.org, here](https://www.virtualbox.org/wiki/Downloads). Install the platform package for your operating system. You do not need the extension pack or the SDK. You do not need to launch VirtualBox after installing it; Vagrant will do that.

__Ubuntu users__: If you are running Ubuntu 14.04, install VirtualBox using the Ubuntu Software Center instead. Due to a reported bug, installing VirtualBox from the site may uninstall other software you need.

## Install Vagrant
Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem. [Download it from vagrantup.com](https://www.vagrantup.com/downloads.html). Install the version for your operating system.

__Windows users__ The Installer may ask you to grant network permissions to Vagrant or make a firewall exception. Be sure to allow this.

- If Vagrant is successfully installed, you will be able to run `vagrant --version` in your terminal to see the version number.
- The shell prompt in your terminal may differ. Here, the `$` sign is the shell prompt.

## Download the VM configuration

You can use Github to fork and clone the repository https://github.com/udacity/fullstack-nanodegree-vm or download the repository.

You will end up with a new directory containing the VM files. Change to this directory in your terminal with `cd`. Inside, you will find another directory called __vagrant__. Change directory to the __vagrant__ directory.

## Start the virtual machine

From your terminal, inside the vagrant subdirectory, run the command vagrant up. This will cause Vagrant to download the Linux operating system and install it. This may take quite a while (many minutes) depending on how fast your Internet connection is.
- Starting the Ubuntu Linux installation with `vagrant up`.

When `vagrant up` is finished running, you will get your shell prompt back. At this point, you can run `vagrant ssh` to log in to your newly installed Linux VM!
