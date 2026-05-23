name: Feature Request
description: Suggest an idea for this project
title: "[FEATURE] "
labels: ["enhancement"]
assignees: []
body:
  - type: markdown
    attributes:
      value: |
        Thanks for your interest in improving Research OS!
  - type: textarea
    id: feature-description
    attributes:
      label: Describe the feature
      description: A clear and concise description of what you want to happen.
    validations:
      required: true
  - type: textarea
    id: use-cases
    attributes:
      label: Use Cases
      description: In what situations would this feature be useful?
