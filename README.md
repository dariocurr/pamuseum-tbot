# Try Out Development Containers: Python

A **development container**, from now on _dev container_, is a running
[Docker](https://www.docker.com) container with a well-defined tool/runtime
stack and its prerequisites.

> You can try out development containers with
> **[GitHub Codespaces](https://github.com/features/codespaces)** or
> **[Visual Studio Code Remote - Containers](https://aka.ms/vscode-remote/containers)**

This is a template project that using a _dev container_, automatically
configures a **Python** development environment with few easy steps.

> Check out others
> [_dev container_ template projects](https://github.com/dariocurr?tab=repositories&q=devcontainer)

This template includes a
**[GitHub Action](https://github.com/features/actions)** which ensures that any
changes made to the `dev` branch still allow Docker to build the _dev container_
correctly. If so, then the `main` branch is merged with the `dev` oen.

> You should never directly push on the `main` branch as
> **[Git best practices](https://git-scm.com/book)** recommend

Feel free to dive into configuration files and modify them to suit your needs.

## Setting up the development container

### GitHub Codespaces

Follow these steps to open this sample in a Codespace:

1. Click the Code drop-down menu and select the **Open with Codespaces** option

2. Select **+ New codespace** at the bottom on the pane

> For more info, check out the
> [GitHub documentation](https://docs.github.com/en/free-pro-team@latest/github/developing-online-with-codespaces/creating-a-codespace#creating-a-codespace).

### VS Code Remote - Containers

Follow these steps to open this sample in a container using the _VS Code
Remote - Containers_ extension:

1. If this is your first time using a _dev container_, please ensure your system
   meets the pre-reqs (i.e. have Docker installed)

2. Clone this repository to your local filesystem

3. Press <kbd>F1</kbd> and select the **Remote-Containers: Reopen in
   Container...** command

> For more info, check out the
> [VS Code documentation](https://aka.ms/vscode-remote/containers).
