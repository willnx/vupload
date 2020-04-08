# -*- coding: UTF-8 -*-
import os
import sys
import argparse
from getpass import getpass


def printerr(message):
    """Like print(), but to stderr

    :Returns: None

    :param message: **Required** What to print to standard error
    :type message: String
    """
    sys.stderr.write('{}\n'.format(message))
    sys.stderr.flush()


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
    parser.add_argument('-f', '--file', default=None,
        help='The file to upload to the VM')
    parse.add_argument('-v', '--the-vm', required=True,
        help="The name of the Virtual Machine to upload a file to")
    parse.add_argument('-t', '--upload-dir', required=True,
        help='The directory on the VM to upload the file to')
    parser.add_argument('--no-upload', action='store_true',
        help='Skip the file upload, and simply generate the upload URL')

    args = parser.parse_args(cli_args)
    if args.file is None and not args.no_upload:
        doh = 'Must provide the file to upload, or supply the "--no-upload" flag'
        raise argparse.ArgumentTypeError(doh)
    elif args.file is not None:
        if not os.path.isfile(args.file):
            doh = 'No such file: {}'.format(args.file)
            raise argparse.ArgumentTypeError(doh)

    if args.vcenter_password or args.password:
        msg = 'WARNING: Supplying passwords via an argument is a security risk!\n'
        msg += 'Avoid that risk and omit those arguments, and the tool will interactively prompt you for them.'
        printerr(msg)

    if args.vcenter_password is None:
        args.vcenter_password = getpass(prompt='Please enter the vCenter user password: ')
    if args.password is None:
        args.password = getpass(prompt='Please enter the VM user password: ')
    return args



def main(cli_args=None):
    """Entry point for script"""
    if cli_args is None:
        cli_args = sys.argv[1:]

    try:
        args = parse_cli(cli_args)
    except argparse.ArgumentTypeError as doh:
        printerr(doh)
        sys.exit(1)
    print(args)


if __name__ == '__main__':
    main()
