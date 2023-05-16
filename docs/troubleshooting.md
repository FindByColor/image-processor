![Find By Color Logo](https://findbycolor-github.s3.amazonaws.com/logo.png 'Find By Color Logo')

**[↤ BACK](../README.md)**

# Troubleshooting

This document will contain a list of known issues, and how to solve them.

## SSH Keys

VS Code Remove Developer Containers require that SSH Keys installed on the host computer be added to the `ssh-agent` so VS Code can access them from the Docker Virtual Machine. When this goes wrong, you can see a few errors.

## GitHub

```
git@github.com: Permission denied (publickey)
```

If you are seeing this kind of error, you'll need to make sure you review the steps covered in our WIKI:

[![Up Next](https://img.shields.io/badge/WIKI-Git_Credentials-blue.svg?style=for-the-badge&logo=github&logoColor=ffffff&logoWidth=16)](https://github.com/FindByColor/.github/wiki/Git-Credentials)

## Docker

Having Docker issues? It happens to the best of us. I find going nuclear is the best option sometimes. This command will clean everything and allow you to do a clean install ( without it trying to use some random hidden cache ).

**WARNING:** If you are using docker for anything else, maybe don't use this and contact someone for help.

```bash
docker system prune -a
```

## Live Share

The quickest way to tell if Live Share is broken ( sadly, it happens more than it should ), you can check your status bar in the footer of VS Code. If you do not see `Live Share` in the status bar, then it broke.

### Here is how to fix the issue:

1. Press <kbd>F1</kbd> to open the Command Palette
2. Select `Live Share: Repair Installation` and let it run
