<!--
Copyright (C) Pipin Fitriadi - All Rights Reserved

Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 22 May 2025
-->

<!-- omit in toc -->
# Python

[![License](https://img.shields.io/badge/license-Proprietary-red)](LICENSE)
[![PyPI - Python Version](https://img.shields.io/badge/python-3.13%2B-blue?logo=Python&logoColor=white)](https://www.python.org/downloads/release/python-3131/)

- [Setup](#setup)
- [CI/CD](#cicd)

This repository serves as a centralized Python's workspace,
providing structure and resources to support development activities.
It may include configuration files, environment setup, shared utilities
and documentation that help maintain consistency and streamline workflows
across projects or teams.

## Setup

Follow these steps *only if* your WSL have trouble to connect same network
with Windows:

> **Enable Mirrored Networking mode (WSL 2 Global Fix)**
>
> If you want WSL and Windows to completely share the same network ports
> (meaning `localhost` on Windows is exactly the same as `localhost` on WSL),
> you can turn on **Mirrored Networking**.
>
> After that, any port forwarding you run normally in PowerShell will
> automatically be available at `localhost` inside WSL.

1. In Windows, press <kbd>Win</kbd> + <kbd>r</kbd>, type `%USERPROFILE%`,
   and press <kbd>enter</kbd>
2. Create or open a file named _`.wslconfig`_ (make sure it doesn't end in _`.txt`_)
3. Paste the following configuration inside it:

    ```ini
    [wsl2]
    networkingMode=mirrored
    ```

4. Open **PowerShell** and restart WSL to apply the changes

    ```powershell
    wsl --shutdown
    ```

Follow these steps the first time you use VS Code after cloning this git repository:

1. Change `name` value in [pyproject.toml](pyproject.toml) to your project name
2. Create a _`.env`_ file based on [_`.env.template`_](.env.template)
   and set your environment values
3. Use the command <kbd>f1</kbd>, select `Tasks: Run Task`, and then choose `Preparation`
4. Use the command <kbd>f1</kbd>, select `Python: Select Interpreter`,
    and then choose _`./.venv/bin/python`_
5. Use the command <kbd>f1</kbd>, select `Tasks: Run Task`,
    and then choose `Python: Preparation`

## CI/CD

If you encounter a Code Quality error during the CI/CD process,
use the command <kbd>f1</kbd>, select `Tasks: Run Task`,
choose `CI/CD: Code Quality - Fixing`, and then run `git commit` and `git push`.
