user
请在这个文件夹下安装uv Python管理包
ai
curl -LsSf https://astral.sh/uv/install.sh | sh 
export PATH="$HOME/.local/bin:$PATH" && uv --version 

- uv init - 初始化新项目
- uv add <package> - 添加依赖包
- uv run <command> - 在虚拟环境中运行命令
- uv sync - 同步依赖

user
在shell/pyshell中测试下python是否可以在uv的python环境中顺利运行
ai
export PATH="$HOME/.local/bin:$PATH" && uv run python shell/pyshell/test_script.py 
export PATH="$HOME/.local/bin:$PATH" && uv add requests 
export PATH="$HOME/.local/bin:$PATH" && uv run python shell/pyshell/advanced_test.py 