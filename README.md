# ctf-cicd

Program to deploy automatically CTF challenges in CTFD. 
This tool tries to answer the limitations of ctfcli, when you use it for continuos deployment. The settings are passed to the program using environment variables and there is no need to have config files in the repository.

The majority of the features are implemented using ctfcli and also inpired by the blogpost from [Rohan Mukherjee](https://medium.com/csictf/automate-deployment-using-ci-cd-eeadd3d47ca7).


## Running and configure this tool

`ctf-cicd` deploys all challenges (challenge.yml) that are detected in the current directory or any of its subfolders. To define challenges, they must respect the [ctfcli specification](https://github.com/CTFd/ctfcli#challenge-specification).

### Installation

``
$ pip3 install .
``

### Running
``
$ ctfcicd
``

### Settings

`CTFD_TOKEN`: CTFd Admin Access Token (ex. d41d8cd98f00b204e9800998ecf8427e)

`CTFD_URL`: CTFd instance URL (ex. https://demo.ctfd.io)

`DEPLOY_HOST`: URI of the method that you want to use to deploy your dockerized challenge ([More info](https://github.com/CTFd/ctfcli/blob/226036fba901ac93a5dd0dab20233cd2168eeacb/ctfcli/spec/challenge-example.yml#L27)).

`DEPLOY_NETWORK`: Optional variable to specify to which network you want the container attached.
