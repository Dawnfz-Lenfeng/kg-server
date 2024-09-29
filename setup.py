from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="ckgcus",
    version="0.1.0",
    author="Dawnfz",
    author_email="2912706234@qq.com",
    description="中文知识图谱",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Dawnfz-Lenfeng/CKG_CUS",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.10",
)
