# ctf-cicd

`ctf-cicd` is a tool designed to automate the deployment of CTF challenges in [CTFd](https://ctfd.io/). It aims to address the limitations of `ctfcli` for continuous deployment making use of environment variables, eliminating the need for config files in the repository.

This tool leverages the features of `ctfcli` and is inspired by a blog post from [Rohan Mukherjee](https://medium.com/csictf/automate-deployment-using-ci-cd-eeadd3d47ca7).


## Getting Started

### Prerequisites

Ensure you have the following installed:
- Python 3.x
- `pip`

## Running and configure this tool

`ctf-cicd` deploys all challenges (challenge.yml) that are detected in the current directory or any of its subfolders. To define challenges, they must respect the [ctfcli specification](https://github.com/CTFd/ctfcli#challenge-specification).

### Step 1: Installation

You can either clone the repository or install it directly using `pip`:

```bash
# Alternative 1: Cloning the repository
$ git clone https://github.com/MrSuicideParrot/ctf-cicd.git

# Alternative 2: Using pip
$ python -m pip install ctfcicd

# After having the source code you should install the project requirements
$ pip install .
```

`Note:` You can (and should) make use of [virtual environments](https://docs.python.org/3/library/venv.html).



### Step 2: Configuration

Set the following environment variables to configure ctf-cicd:

- `CTFD_TOKEN`: CTFd Admin Access Token (ex. d41d8cd98f00b204e9800998ecf8427e)

- `CTFD_URL`: CTFd instance URL (ex. https://demo.ctfd.io)

- `DEPLOY_HOST`: URI of the method that you want to use to deploy your dockerized challenge ([More info](https://github.com/CTFd/ctfcli/blob/226036fba901ac93a5dd0dab20233cd2168eeacb/ctfcli/spec/challenge-example.yml#L27)).

- `DEPLOY_NETWORK`: (Optional) variable to specify to which network you want the container attached.

Example configuration:

```bash
export CTFD_TOKEN="your_ctfd_token"
export CTFD_URL="https://your_ctfd_instance"
export DEPLOY_HOST="ssh://your_deploy_host"
export DEPLOY_NETWORK="your_network"
```

### Step 3: Running
```bash
# Alternative 1: Deploying all challenges
$ ctfcicd

# Alternative 2: Deploy a list of challenges
$ ctfcicd --chalenges chall1 chall2 chall3
```

## Contributing

Contributions from the community are welcome! To contribute:

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature-branch`)
6. Create a new Pull Request

## Usage Examples

This project can be used to automate the deployment of challenges either locally or using github actions. An example of how to do so can be seen in [here](examples/).

If you come up with other usages of this project, feel free to [open a Pull Request](https://github.com/MrSuicideParrot/ctf-cicd/pulls).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

This tool was inspired by a blog post from [Rohan Mukherjee](https://medium.com/csictf/automate-deployment-using-ci-cd-eeadd3d47ca7). Special thanks to the `ctfcli` community for their foundational work.
