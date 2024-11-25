# 开发指南

## 开发环境设置

### 安装依赖

1. 创建并激活虚拟环境
```bash
conda create -n ckgcus python=3.10
conda activate ckgcus
```

2. 安装依赖
```bash
# 进入后端目录
cd backend

# 安装开发依赖
pip install -e ".[dev]"

# 或使用镜像源加速安装
pip install -e .[dev] -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
```

### 常见安装问题

1. 未切换到虚拟环境
```bash
# 检查当前环境是否正确激活
conda env list
```

2. Polygon3 安装失败
```bash
# 尝试使用 conda 安装
conda install polygon3
```

## Git 工作流

### 准备工作

1. Fork 仓库
- 点击 GitHub 仓库右上角的 Fork 按钮
- 这将复制仓库的文件、提交历史和 Issues 到你的账户
2. 配置 SSH
- 生成 SSH 密钥
```bash
# 生成 SSH 密钥
ssh-keygen -t rsa -C "your.email@example.com"

# 查看公钥
cd ~/.ssh
cat id_rsa.pub

# 创建或编辑配置文件
nano ~/.ssh/config

# 添加以下内容
Host github.com
    HostName ssh.github.com
    User git
    Port 443
```
- 进入 `GitHub Settings` > `SSH and GPG keys`
- 添加复制的 SSH 公钥

### 日常开发流程
1. 同步拉取代码
```bash
# 同步 Fork
# 在 GitHub Fork 页面点击 "Sync fork"

# 克隆仓库
git clone <your_ssh_url>

# Git 配置
git config --global user.email "you@example.com"
git config --global user.name "Your Name"

#拉取代码
git pull
```
2. 更改代码
3. 提交代码
```bash
# 在新分支上提交代码
git pull
git checkout -b new-feature
git add .
git commit -m "描述你的修改内容"
git push origin new-feature
```
- 返回 GitHub，切换到 `new-feature` 分支
- 点击 `Contribute` > `Open pull request`

## 代码规范
[编码规范、提交规范...]

## 测试指南
[测试相关内容...] 
