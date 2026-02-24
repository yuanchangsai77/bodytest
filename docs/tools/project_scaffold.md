# project_scaffold

用于根据用户要求搭建项目结构。

## 必填参数
- `project_name`: 项目名
- `tech_stack`: 技术栈（如 python-fastapi / node-express）

## 推荐命令模板
```bash
mkdir -p <project_name>/{src,tests,docs}
```

## 输出约定
当参数齐全时返回 `execute_command`。
当参数缺失时返回 `error` 并在 `missing_params` 给出字段名。
