play2-git-auto-deploy
=====================

### Why?

To make your life easier, that's why :)

This is a good solution if you want to build your app locally and automatically deploy new version of an app after every push

### For whom?

For play2 framework users using git and compiling their app locally

### What do I need?

- Python2 with GitPython
- your play application cloned repo (on the server)
- destination directory (where your current app will be stored)

### How does it work?

The script works on a server. The script periodically checks for changes on the repo. If pull is needed, the script stops old app, unzips the new app version from target/universal dir and starts it in the new chosen directory. 

For this to work you need to add target/universal dir to your git. Deploy an app using play dist && git push.

Any comments and suggestions are welcome!

Inspired by: https://github.com/mchv/play2-jenkins-deployment
