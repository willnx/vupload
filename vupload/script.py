# -*- coding: UTF-8 -*-
import os
import sys
import time
import argparse
from getpass import getpass

import requests
from vlab_inf_common.vmware import vCenter, vim


def printerr(message):
    """Like print(), but to stderr

    :Returns: None

    :param message: **Required** What to print to standard error
    :type message: String
    """
    sys.stderr.write('{}\n'.format(message))
    sys.stderr.flush()


def check_file(a_file):
    """For validating CLI input, and ensuring the supplied file is real.

    :Returns: String

    :param a_file: The value passed to the CLI
    :type a_file: String
    """
    a_file = os.path.abspath(a_file) # for better error messages
    if not os.path.isfile(a_file):
        raise argparse.ArgumentTypeError('No such file: {}'.format(a_file))
    return a_file


def parse_cli(cli_args):
    """Handles parsing the CLI, and gives us --help for (basically) free

    :Returns: argparse.Namespace

    :param cli_args: **Required** The arguments passed to the script
    :type cli_args: List
    """
    parser = argparse.ArgumentParser(description='Upload a file to a VMware VM')

    parser.add_argument('-s', '--vcenter', required=True,
        help='The IP/FQDN of the vCenter server')
    parser.add_argument('-a', '--vcenter-user', required=True,
        help='The name of the user to login to vCenter as')
    parser.add_argument('-c', '--vcenter-password', default=None,
        help='The password for the vCenter user')
    parser.add_argument('-u', '--username', required=True,
        help='The user to login to the VM as')
    parser.add_argument('-p', '--password', default=None,
        help='The password for the VM user')
    parser.add_argument('-f', '--file', required=True, type=check_file,
        help='The file to upload to the VM')
    parser.add_argument('-v', '--the-vm', required=True,
        help="The name of the Virtual Machine to upload a file to")
    parser.add_argument('-t', '--upload-dir', required=True,
        help='The directory on the VM to upload the file to')
    parser.add_argument('--no-upload', action='store_true',
        help='Skip the file upload, and simply generate the upload URL')

    args = parser.parse_args(cli_args)
    if args.vcenter_password or args.password:
        msg = 'WARNING: Supplying passwords via an argument is a security risk!\n'
        msg += 'Avoid that risk and omit those arguments, and the tool will interactively prompt you for them.'
        printerr(msg)

    if args.vcenter_password is None:
        args.vcenter_password = getpass(prompt='Please enter the vCenter user password: ')
    if args.password is None:
        args.password = getpass(prompt='Please enter the VM user password: ')
    return args


def get_upload_url(vcenter, vcenter_user, vcenter_password, the_vm, username, password,
                   file, upload_dir):
    """Call VMware's InitiateFileTransferToGuest API for an upload URL

    :Returns: String

    :param vcenter: **Required** The IP/FQDN of the vCenter server
    :type vcenter: String

    :param vcenter_user: **Required** The name of the user to login to vCenter with
    :type vcenter_user: String

    :param vcenter_password: The password for the vCenter user
    :type vcetner_password: String

    :param the_vm: **Required** The name of the VM to upload the file to
    :type the_vm: String

    :param username: **Required** The user to login to the VM with
    :type username: String

    :param password: **Required** The password for the VM user
    :type password: String

    :param file: **Required** The local file to upload to the VM
    :type file: String

    :param upload_dir: **Required** The directory on the VM to upload the file to
    :type upload_dir: String
    """
    creds = vim.vm.guest.NamePasswordAuthentication(username=username, password=password)
    upload_path = '{}/{}'.format(upload_dir, os.path.basename(file))
    file_size = os.stat(file).st_size
    with vCenter(host=vcenter, user=vcenter_user, password=vcenter_password) as vcenter:
        vm = vcenter.get_by_name(name=the_vm, vimtype=vim.VirtualMachine)
        return _get_url(vcenter, vm, creds, upload_path, file_size)


def _get_url(vcenter, vm, creds, upload_path, file_size):
    """Mostly to deal with race between a VM powering on, and all of VMwareTools being ready.

    :Returns: String

    :param vcenter: **Required** The instantiated connection to vCenter
    :type vcenter: vlab_inf_common.vmware.vCenter

    :param vm: **Required** The new DataIQ machine
    :type vm: vim.VirtualMachine

    :param creds: **Required** The username & password to use when logging into the new VM
    :type creds: vim.vm.guest.NamePasswordAuthentication

    :param file_size: **Required** How many bytes are going to be uploaded
    :type file_size: Integer
    """
    # If the VM just booted the service can take some time to be ready
    for retry_sleep in range(10):
        try:
            url = vcenter.content.guestOperationsManager.fileManager.InitiateFileTransferToGuest(vm=vm,
                                                                                                 auth=creds,
                                                                                                 guestFilePath=upload_path,
                                                                                                 fileAttributes=vim.vm.guest.FileManager.FileAttributes(),
                                                                                                 fileSize=file_size,
                                                                                                 overwrite=True)
        except vim.fault.GuestOperationsUnavailable:
            time.sleep(retry_sleep)
        else:
            return url
    else:
        error = 'Unable to upload file. Timed out waiting on VMware Tools to become available.'
        raise ValueError(error)


def main(cli_args=None):
    """Entry point for script"""
    if cli_args is None:
        cli_args = sys.argv[1:]
    args = parse_cli(cli_args)
    try:
        upload_url = get_upload_url(vcenter=args.vcenter,
                                    vcenter_user=args.vcenter_user,
                                    vcenter_password=args.vcenter_password,
                                    the_vm=args.the_vm,
                                    username=args.username,
                                    password=args.password,
                                    file=args.file,
                                    upload_dir=args.upload_dir)
    except vim.fault.InvalidGuestLogin:
        printerr('Invalid password for VM user {}'.format(args.username))
        sys.exit(1)
    except vim.fault.CannotAccessFile:
        printerr('VM user {} lacks permission to write to {}'.format(args.username, args.upload_dir))
        sys.exit(1)

    if args.no_upload:
        print('Upload URL is: {}'.format(upload_url))
        print('To upload the file with curl, the syntax would be:')
        print("curl -k --fail -X PUT -d @{} {}".format(args.file, upload_url.replace('&', '\&')))
    else:
        with open(args.file) as the_file:
            stime = time.time()
            resp = requests.put(upload_url, data=the_file, verify=False)
            delta = time.time() - stime
        if not resp.ok:
            printerr('Upload failure')
            printerr('HTTP Response: {}'.format(resp.status))
            printerr('Response body: {}'.format(resp.content))
            sys.exit(1)
        print('Uploade {} bytes in {} seconds'.format(os.stat(args.file).st_size, delta))


if __name__ == '__main__':
    main()
