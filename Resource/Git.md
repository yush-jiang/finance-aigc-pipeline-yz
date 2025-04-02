# Git


## 1. 安装 Git
首先，确保你已经在你的电脑上安装了 Git。你可以从 Git 的官方网站下载并安装：[Git 官方下载地址](https://git-scm.com/)
    
安装完成后，可以在命令行（或终端）中输入以下命令来检查 Git 是否安装成功：`git --version` 如果安装成功，终端会显示 Git 的版本号。
    
## 2. 配置 Git

安装 Git 后，先进行一些基本配置，特别是设置你的用户名和邮箱。这是因为每次提交时，Git 会记录提交者的信息。

- `git config --global user.name <你的名字>`
- `git config --global user.email <你的邮箱>`
    
## 3. 创建一个新的 Git 仓库

如果你已经有一个项目文件夹，并希望开始使用 Git，你可以在该文件夹中初始化一个 Git 仓库。首先，进入你的项目文件夹：`cd <code path>`
        
然后使用以下命令初始化 Git 仓库：`git init`

执行过后在你的项目文件夹中创建一个 `.git` 文件夹，表示这是一个 Git 仓库。
    
## 4. 检查 Git 状态

每次进行修改后，你可以使用 `git status` 命令来查看当前 Git 仓库的状态，了解哪些文件已修改、哪些文件被暂存或未跟踪。`git status`
    
## 5. 添加修改到暂存区
在进行提交之前，你需要将修改添加到 Git 的暂存区。假设你修改了一个文件 `example.txt`，可以使用以下命令：`git add example.txt`
    
如果你想将所有已修改的文件添加到暂存区，可以使用：`git add .`
    
## 6. 提交修改
将文件添加到暂存区后，你可以通过 `git commit` 命令提交修改。每次提交时，写一个简洁的提交信息，描述这次提交的内容。`git commit -m "添加了新的功能"`
    
## 7. 查看提交历史
如果你想查看项目的提交历史，可以使用 `git log` 命令,这将显示提交的详细信息，包括提交的 SHA-1 哈希值、作者、日期和提交信息。
    
## 8. 与远程仓库进行交互
如果你有一个远程仓库（比如 GitHub、GitLab 或 Bitbucket），你可以将本地仓库与远程仓库进行连接。
- 设置远程仓库：

    `git remote add origin https://github.com/yourusername/yourrepository.git`
        
- 将本地提交推送到远程仓库：

    `git push origin master`/ `git push`
        
- 从远程仓库拉取最新的修改：
    
    `git pull origin master` / `git pull`
