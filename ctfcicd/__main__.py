from ctfcicd import CiCd
from sys import argv
from os import getenv


def main():
    if len(argv) == 3 :
        prod =  not bool(getenv("TESTING_DEPLOYMENT"))
        CiCd().sync_folder_with_git(argv[1], argv[2], prod)
    else:
        CiCd().deploy_current_folder()


if __name__ == "__main__":
    main()
