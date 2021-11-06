from ctfcicd import CiCd
from sys import argv


def main():
    if len(argv) == 3 :
        CiCd().sync_folder_with_git(argv[1], argv[2])
    else:
        CiCd().deploy_current_folder()


if __name__ == "__main__":
    main()
