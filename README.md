# vUpload
(v-up-load, noun)

A CLI tool for uploading files to a VM via VMware's InitiateFileTransferToGuest.

The InitiateFileTransferToGuest is really handy for uploading files to VMs
when your machine can route to the ESXi host, but not the specific virtual
machine.


## Installation
The easiest way to install the ``vupload`` tool is with pip:

    pip install vupload

If you're behind a corporate firewall, you might have to explicitly trust the
TLS cert for PyPi:

    pip install --trusted-host=pypi.org vupload

## Examples
Here's an example of uploading a file in your local directory to a virtual machine
named ``test123``:

    vupload --vcenter 10.1.1.5 --vcenter-user Administrator@vsphere.local --username root --file somefile.txt --the-vm test123 --upload-dir /tmp

To avoid being prompted for multiple passwords (handy if you want to script usage)
you can pass the ``--vcenter-password`` and ``--password`` arguments.

Most of the arguments have shorter versions too! The output of this command will
help you match up the long argument with their shorter version:

    vupload -h

You can even use ``vupload`` to just generate the URL to for uploading a file.
Just pass the ``--no-upload`` flag:

    vupload -s 10.1.1.5 -a Administrator@vsphere.local -u root -f somefile.txt -v test123 -t /tmp --no-upload


## Dev notes
These notes are specifically intended for devs. If you installed vupload via
``pip``, ignore this whole section.

To build on a local dev box, you'll need header files for your version of Python,
a compiler and the ``make`` command. For CentOS you can run this command to install
those dependencies:

    sudo yum -y install python3-devel make gcc

Once you have those dependencies installed, run this command to build and install
vupload:

    make install

Running this command will delete build artifacts:

    make clean

To remove the vupload Python package, run:

    make uninstall
