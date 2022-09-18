from ast import parse
from ctfcicd import CiCd
from sys import argv
from os import getenv
from argparse import ArgumentParser, BooleanOptionalAction

def main():
    parser = ArgumentParser(description='Deploy challenges in ctfd')
    parser.add_argument('--insecure-tls-verification', action=BooleanOptionalAction, default=False)
    parser.add_argument('--testing', action=BooleanOptionalAction, default=False)
    parser.add_argument('--commits', action='extend', nargs='*', type=str)
    args = parser.parse_args()

    if args.commits is not None and len(args.commits) == 2:
        CiCd(not args.testing, not args.insecure_tls_verification).sync_folder_with_git(*args.commits)
    else:
        CiCd(not args.testing, not args.insecure_tls_verification).deploy_current_folder()

if __name__ == "__main__":
    main()
