name: Bug Report
description: Use this template if something is not working correctly
#title: ""
labels: [needs-triage]
#assignees:
#  -

body:
  - type: markdown
    attributes:
      value: |
        We appreciate you taking your time to report an issue with ctfcicd. The more details you can provide, the most likely we will be able to assist you.

        Before raising a bug/issue please check that it has not already been reported by searching [GitHub Open or Closed Issues](https://github.com/MrSuicideParrot/ctf-cicd/issues).
        
  - type: textarea
    id: bug_description
    attributes:
      label: Describe the bug
      description: A clear and concise description of what the bug is. Try to be very factual in the description.
      placeholder: |
        
        What is the issue? What causes the bug?
    validations:
      required: true

  - type: textarea
    id: reproduce
    attributes:
      label: Steps to reproduce
      description: A clear sequence of steps to recreate the issue.

    validations:
      required: true

  - type: input
    id: expected
    attributes:
      label: Expected behavior
      placeholder: 'ctfcicd should...'

  - type: input
    id: commit
    attributes:
      label: Commit
      description: |
        - Which commit introduced the error?

  - type: dropdown
    id: source
    attributes:
      label: Where did you obtain ctfcicd from?
      options:
        - 'downloaded using pip'
        - 'cloned from github directly'
        - 'other'
    validations:
     required: true
      
  - type: dropdown
    id: OS
    attributes:
      label: What OS are you using?
      options:
        - 'Linux'
        - 'Mac'
        - 'Windows'
    validations:
      required: true

  - type: textarea
    id: additional_info
    attributes:
      label: Please provide additional context if applicable. You can attach files too, but might need to rename to .txt or .zip

  - type: markdown
    attributes:
      value: Thanks for filling out this form completely. It saves us a lot of time.
