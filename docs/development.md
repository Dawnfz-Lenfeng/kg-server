# 开发指南

## 开发环境设置
1. 创建并激活虚拟环境：
```bash
conda create -n ckgcus python=3.10
conda activate ckgcus
```
2. 安装依赖：
```bash
cd backend
pip install -e ".[dev]"  # 安装开发依赖
```
也可以使用镜像源
```
pip install -e .[dev] -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple 
```

在安装过程中可能会遇到以下错误：  

1. 没有切换到虚拟环境：可以通过下面的命令检查当前所在环境
```bash
conda env list
```
2. 安装库Polygon3时可能出现问题，这时可以试着通过conda安装来解决此问题  
```
conda install polygon3
```

## 代码贡献流程（git 操作）
### 第一次进行本项目代码开发
1. 点击GitHub仓库右上角fork标识的按钮，将这个仓库的文件、提交历史、issues和其余东西的仓库复制到自己的github仓库中
2. 配置SSH协议教程
```bash
# 将 "xxx@xxx.com" 替换为你自己GitHub的邮箱地址
ssh-keygen -t rsa -C "xxx@xxx.com"  
# 进入ssh目录
cd ~/.ssh
# 查看ssh 公钥  进行复制
cat id_rsa.pub
```  
进入GitHub设置你的SSH  
找到SSH的配置文件，它的路径一般是~/.ssh/config，如果这个文件不存在的话也可以创建一个。然后，在其中增加以下内容：
```bash
Host github.com
  HostName ssh.github.com
  User git
  Port 443
```

### 每次进行代码的贡献流程
1. 在自己的GitHub fork上点击Sync fork按钮确保及时更新了最新版本
2. 将pycharm或者vscode切换至搭建好的本项目虚拟环境，可以通过终端的头文件名验证是否切换成功
3. git clone 操作 （这里推荐使用ssh，配置方法见上一部分“第一次进行本项目开发”）
```bash
git clone yoursshkey
#yoursshkey 部分填写你在GitHub上点开code按钮，选择ssh后可粘贴的一行文字
```
4. 进行代码修改
5. 代码提交与审批  

```bash
git config --global user.email"you@example.com"
#或者
git config --global user.name "Your Name"
```
提交代码，这里建议创建一个分支来避免跟主支冲突
```bash
git pull
git checkout -b new
git add .
git commit -m .
git push origin new
```
在终端操作结束后，返回GitHub，切换到new分支，在Contribute按钮下提交你的修改

## 代码规范
[编码规范、提交规范...]

## 测试指南
[测试相关内容...] 
