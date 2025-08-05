import json
import os
import subprocess
import sys
from typing import Dict

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Add current dir for importing api_client
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from api_client import MultiModelAPIClient

# Global API client instance
api_client: MultiModelAPIClient | None = None


def get_api_client() -> MultiModelAPIClient:
    """Return cached API client (singleton)."""
    global api_client
    if api_client is None:
        api_client = MultiModelAPIClient()
    return api_client


def tool_executor(instruction: str) -> str:
    """Main CLI tool executor.

    Parameters
    ----------
    instruction: str
        User instruction.
    """
    prompt_path = os.path.join(project_root, "prompt", "CLI工具执行引擎.md")
    with open(prompt_path, "r", encoding="utf-8") as f:
        system_prompt_content = f.read()

    result_json = make_llm_api_call(system_prompt=system_prompt_content, user_instruction=instruction)

    try:
        result_data = json.loads(result_json)
        if result_data.get("status") == "execute_command":
            command = result_data.get("command")
            working_dir = result_data.get("working_directory", ".")
            if command:
                try:
                    cmd_parts = command.split()
                    result = subprocess.run(
                        cmd_parts,
                        capture_output=True,
                        text=True,
                        cwd=os.path.join(project_root, working_dir),
                    )
                    if result.returncode == 0:
                        return json.dumps(
                            {
                                "status": "success",
                                "log": f"命令执行成功: {command}\n输出:\n{result.stdout}",
                            },
                            ensure_ascii=False,
                            indent=2,
                        )
                    return json.dumps(
                        {
                            "status": "failure",
                            "error": f"命令执行失败: {command}\n错误:\n{result.stderr}",
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
                except Exception as exc:  # noqa: BLE001
                    return json.dumps(
                        {
                            "status": "failure",
                            "error": f"执行命令时发生异常: {exc}",
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
            return json.dumps({"status": "failure", "error": "未找到要执行的命令"}, ensure_ascii=False, indent=2)
        return result_json
    except json.JSONDecodeError:
        return result_json


def make_llm_api_call(system_prompt: str, user_instruction: str) -> str:
    """Invoke real LLM API using MultiModelAPIClient."""
    print("\n--- [API CALL] ---")
    print(f"  System Prompt: {system_prompt[:50]}...")
    print(f"  User Instruction: {user_instruction}")
    print("--- [LLM is processing...] ---\n")
    client = get_api_client()
    result_json = client.call_api(system_prompt, user_instruction)
    return result_json


def call_agent_multi_turn(agent_name: str, instruction: str) -> str:
    """Multi-turn agent invocation."""
    agents_config_path = os.path.join(project_root, "cli-lib", "agents.json")
    main_json_path = os.path.join(project_root, "cli-lib", "main.json")
    try:
        with open(agents_config_path, "r", encoding="utf-8") as f:
            agents = json.load(f)
    except FileNotFoundError:
        return json.dumps({"status": "failure", "error": f"Agent registry not found at {agents_config_path}"})

    agent_info: Dict[str, str] | None = agents.get(agent_name)
    if not agent_info:
        return json.dumps({"status": "failure", "error": f"Agent '{agent_name}' is not defined in agents.json."})

    system_prompt_path = os.path.join(project_root, os.path.normpath(agent_info["system_prompt_path"]))
    try:
        with open(system_prompt_path, "r", encoding="utf-8") as f:
            system_prompt_content = f.read()
    except FileNotFoundError:
        return json.dumps({"status": "failure", "error": f"System prompt for agent '{agent_name}' not found at {system_prompt_path}"})

    try:
        with open(main_json_path, "r", encoding="utf-8") as f:
            main_json_content = f.read()
    except FileNotFoundError:
        return json.dumps({"status": "failure", "error": f"main.json not found at {main_json_path}"})

    first_round_instruction = f"""
    以下是可用工具的注册表内容:
    ```json
    {main_json_content}
    ```

    用户指令:{instruction}

    请根据main.json中的工具信息,选择合适的工具并告诉我需要查看哪个工具的详细文档.
    
    **重要:在选择工具后,你需要先快速检查用户指令中是否包含了该工具可能需要的关键参数.**
    
    请返回JSON格式:
    - 如果工具选择成功且用户指令看起来完整:{{"status": "request_doc", "tool_name": "工具名", "doc_path": "文档路径"}}
    - 如果选择了工具但怀疑缺少关键参数:{{"status": "need_params_check", "tool_name": "工具名", "doc_path": "文档路径"}}
    """

    print("\n--- [第一轮对话] ---")
    first_result_json = make_llm_api_call(system_prompt=system_prompt_content, user_instruction=first_round_instruction)

    try:
        first_result = json.loads(first_result_json)
        if first_result.get("status") == "need_params_check":
            tool_name = first_result.get("tool_name")
            doc_path = first_result.get("doc_path")
            if not tool_name or not doc_path:
                return json.dumps({"status": "failure", "error": "LLM未正确返回工具名或文档路径"})
            full_doc_path = os.path.join(project_root, os.path.normpath(doc_path))
            try:
                with open(full_doc_path, "r", encoding="utf-8") as f:
                    doc_content = f.read()
            except FileNotFoundError:
                return json.dumps({"status": "failure", "error": f"工具文档未找到: {full_doc_path}"})
            param_check_instruction = f"""
            以下是 {tool_name} 工具的详细文档:
            ```markdown
            {doc_content}
            ```

            原始用户指令:{instruction}

            请仔细检查用户指令是否包含了工具文档中标记为 "required: yes" 的所有必须参数.

            **参数识别规则:**
            1. 参数可能以多种格式出现:"-name value"、"--datapath value"、"参数:-name value --datapath value"等
            2. 参数值可能包含中文、英文、特殊字符
            3. 如果用户指令中明确提到了参数名和对应的值,就认为该参数已提供
            4. 特别注意:如果指令中包含类似"参数:-name DivineInsight --datapath 【神躯】"这样的格式,说明参数已经完整提供

            **当前用户指令分析:**
            请逐一检查文档中每个required参数是否在用户指令中有对应的值.
            
            请返回JSON格式:
            - 如果所有必须参数都已提供:{{"status": "params_complete"}}
            - 如果缺少必须参数:{{"status": "missing_params", "missing_params": ["参数1", "参数2"], "param_descriptions": {{"参数1": "参数1的描述", "参数2": "参数2的描述"}}}}
            """

            print("\n--- [参数检查] ---")
            param_check_result_json = make_llm_api_call(system_prompt=system_prompt_content, user_instruction=param_check_instruction)
            try:
                param_check_result = json.loads(param_check_result_json)
                if param_check_result.get("status") == "missing_params":
                    missing_params = param_check_result.get("missing_params", [])
                    param_descriptions = param_check_result.get("param_descriptions", {})
                    return json.dumps(
                        {
                            "status": "need_user_input",
                            "message": f"执行 {tool_name} 工具需要额外的必须参数",
                            "missing_params": missing_params,
                            "param_descriptions": param_descriptions,
                            "tool_name": tool_name,
                            "original_instruction": instruction,
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
                if param_check_result.get("status") != "params_complete":
                    print(f"警告: 参数检查返回了意外状态: {param_check_result.get('status')}")
            except json.JSONDecodeError:
                print("警告: 无法解析参数检查结果,继续正常流程")
            first_result["status"] = "request_doc"

        if first_result.get("status") == "request_doc":
            tool_name = first_result.get("tool_name")
            doc_path = first_result.get("doc_path")
            if not tool_name or not doc_path:
                return json.dumps({"status": "failure", "error": "LLM未正确返回工具名或文档路径"})
            full_doc_path = os.path.join(project_root, os.path.normpath(doc_path))
            try:
                with open(full_doc_path, "r", encoding="utf-8") as f:
                    doc_content = f.read()
            except FileNotFoundError:
                return json.dumps({"status": "failure", "error": f"工具文档未找到: {full_doc_path}"})
            second_round_prompt_path = os.path.join(project_root, "prompt", "CLI命令生成器.md")
            try:
                with open(second_round_prompt_path, "r", encoding="utf-8") as f:
                    second_round_system_prompt = f.read()
            except FileNotFoundError:
                second_round_system_prompt = system_prompt_content
                print("警告: 未找到CLI命令生成器提示词,使用原始提示词")
            second_round_instruction = f"""
            以下是 {tool_name} 工具的详细文档:
            ```markdown
            {doc_content}
            ```

            原始用户指令:{instruction}

            请根据工具文档和用户指令,生成具体的执行命令.
            """

            print("\n--- [第二轮对话] ---")
            second_result_json = make_llm_api_call(system_prompt=second_round_system_prompt, user_instruction=second_round_instruction)
            try:
                second_result = json.loads(second_result_json)
                if second_result.get("status") == "execute_command":
                    command = second_result.get("command")
                    working_dir = second_result.get("working_directory", ".")
                    if command:
                        return execute_command(command, working_dir, project_root)
                    return json.dumps({"status": "failure", "error": "未找到要执行的命令"})
                if second_result.get("status") == "error":
                    error_msg = second_result.get("error", "未知错误")
                    missing_params = second_result.get("missing_params", [])
                    if missing_params:
                        return json.dumps(
                            {
                                "status": "need_user_input",
                                "message": f"执行 {tool_name} 工具需要额外的必须参数",
                                "missing_params": missing_params,
                                "error_details": error_msg,
                                "tool_name": tool_name,
                                "original_instruction": instruction,
                            },
                            ensure_ascii=False,
                            indent=2,
                        )
                    return json.dumps({"status": "failure", "error": f"CLI命令生成失败: {error_msg}"})
                return json.dumps({"status": "failure", "error": f"第二轮对话返回了意外的状态: {second_result.get('status')}"})
            except json.JSONDecodeError:
                return json.dumps({"status": "failure", "error": f"无法解析第二轮对话结果: {second_result_json}"})
        return json.dumps({"status": "failure", "error": f"第一轮对话返回了意外的状态: {first_result.get('status')}"})
    except json.JSONDecodeError:
        return json.dumps({"status": "failure", "error": f"无法解析第一轮对话结果: {first_result_json}"})


def execute_command(command: str, working_dir: str, project_root: str) -> str:
    """Helper to execute shell command."""
    try:
        cmd_parts = command.split()
        result = subprocess.run(
            cmd_parts,
            capture_output=True,
            text=True,
            cwd=os.path.join(project_root, working_dir),
        )
        if result.returncode == 0:
            return json.dumps(
                {"status": "success", "log": f"命令执行成功: {command}\n输出:\n{result.stdout}"},
                ensure_ascii=False,
                indent=2,
            )
        return json.dumps(
            {"status": "failure", "error": f"命令执行失败: {command}\n错误:\n{result.stderr}"},
            ensure_ascii=False,
            indent=2,
        )
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"status": "failure", "error": f"执行命令时发生异常: {exc}"}, ensure_ascii=False, indent=2)


def call_agent(agent_name: str, instruction: str) -> str:
    """Call a specific sub-agent to perform task."""
    agents_config_path = os.path.join(project_root, "cli-lib", "agents.json")
    try:
        with open(agents_config_path, "r", encoding="utf-8") as f:
            agents = json.load(f)
    except FileNotFoundError:
        return json.dumps({"status": "failure", "error": f"Agent registry not found at {agents_config_path}"})

    agent_info = agents.get(agent_name)
    if not agent_info:
        return json.dumps({"status": "failure", "error": f"Agent '{agent_name}' is not defined in agents.json."})

    system_prompt_path = os.path.join(project_root, os.path.normpath(agent_info["system_prompt_path"]))
    try:
        with open(system_prompt_path, "r", encoding="utf-8") as f:
            system_prompt_content = f.read()
    except FileNotFoundError:
        return json.dumps({"status": "failure", "error": f"System prompt for agent '{agent_name}' not found at {system_prompt_path}"})

    result_json = make_llm_api_call(system_prompt=system_prompt_content, user_instruction=instruction)
    try:
        result_data = json.loads(result_json)
        if result_data.get("status") == "execute_command":
            command = result_data.get("command")
            working_dir = result_data.get("working_directory", ".")
            if command:
                try:
                    cmd_parts = command.split()
                    result = subprocess.run(
                        cmd_parts,
                        capture_output=True,
                        text=True,
                        cwd=os.path.join(project_root, working_dir),
                    )
                    if result.returncode == 0:
                        return json.dumps(
                            {
                                "status": "success",
                                "log": f"命令执行成功: {command}\n输出:\n{result.stdout}",
                            },
                            ensure_ascii=False,
                            indent=2,
                        )
                    return json.dumps(
                        {
                            "status": "failure",
                            "error": f"命令执行失败: {command}\n错误:\n{result.stderr}",
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
                except Exception as exc:  # noqa: BLE001
                    return json.dumps(
                        {
                            "status": "failure",
                            "error": f"执行命令时发生异常: {exc}",
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
            return json.dumps({"status": "failure", "error": "未找到要执行的命令"}, ensure_ascii=False, indent=2)
        return result_json
    except json.JSONDecodeError:
        return result_json
