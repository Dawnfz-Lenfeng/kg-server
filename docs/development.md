# 开发指南

## 开发环境设置

1. **创建并激活虚拟环境**：
```bash
conda create -n ckgcus python=3.10
conda activate ckgcus
```

2. **安装依赖**：

```bash
cd backend
pip install -e ".[dev]"  # 安装开发依赖
```

也可以使用镜像源加速安装：

```bash
pip install -e .[dev] -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
```

**安装过程中可能会遇到以下错误：**

1. **未切换到虚拟环境**：可以通过以下命令检查当前环境是否正确激活：

    ```bash
    conda env list
    ```

2. **安装库 `Polygon3` 时出现问题**：可以尝试通过 `conda` 安装该库：

    ```bash
    conda install polygon3
    ```

## 代码贡献流程（Git 操作）
### 第一次进行本项目代码开发

1. **Fork 仓库**：
    - 点击 GitHub 仓库右上角的 Fork 按钮，将该仓库的文件、提交历史、Issues 等复制到自己的 GitHub 仓库中。

2. **配置 SSH 协议**：

    ```bash
    # 将 "xxx@xxx.com" 替换为你的 GitHub 邮箱地址
    ssh-keygen -t rsa -C "xxx@xxx.com"
    ```

    ```bash
    # 进入 SSH 目录
    cd ~/.ssh
    ```

    ```bash
    # 查看并复制 SSH 公钥
    cat id_rsa.pub
    ```

    - 登录 GitHub，进入 **Settings > SSH and GPG keys**，添加复制的 SSH 公钥。

    - 配置 SSH 配置文件（如果不存在，则创建一个）：

        ```bash
        nano ~/.ssh/config
        ```

        添加以下内容：

        ```
        Host github.com
          HostName ssh.github.com
          User git
          Port 443
        ```

### 每次进行代码贡献流程

1. **同步 Fork 仓库**：
    - 在自己的 GitHub Fork 上点击 **Sync fork** 按钮，确保本地仓库与上游仓库保持同步。

2. **切换 IDE 虚拟环境**：
    - 在 PyCharm 或 VSCode 中，将项目的 Python 解释器切换到之前创建的虚拟环境 `ckgcus`。可以通过终端提示符验证是否切换成功。

3. **克隆仓库**（推荐使用 SSH，参考上一步的 SSH 配置）：

    ```bash
    git clone your_ssh_url
    ```

    > **注意**：`your_ssh_url` 部分请在 GitHub 仓库页面点击 **Code** 按钮，选择 SSH 后复制的链接。

4. **进行代码修改**。

5. **提交代码与发起 Pull Request**：

    ```bash
    git config --global user.email "you@example.com"
    # 或者
    git config --global user.name "Your Name"
    ```

    建议创建一个新分支以避免与主分支冲突：

    ```bash
    git pull
    git checkout -b new-feature
    git add .
    git commit -m "描述你的修改内容"
    git push origin new-feature
    ```

    - 在终端操作完成后，返回 GitHub。
    - 切换到新创建的 `new-feature` 分支。
    - 点击 **Contribute** 按钮，选择 **Open pull request**，提交你的修改。



## 代码规范
[编码规范、提交规范...]

## 测试指南
[测试相关内容...] 
