import argparse
import json
import os

from shell.pyshell.agent_framework import call_agent_multi_turn
from shell.pyshell.ai_os import AIOSRuntime


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="多代理 CLI 入口")
    parser.add_argument("--agent", default="task_planner", help="要调用的 agent 名称")
    parser.add_argument("--instruction", required=True, help="用户指令")
    parser.add_argument(
        "--runtime",
        default="ai_os",
        choices=["ai_os", "legacy"],
        help="执行模式：ai_os 为状态驱动闭环，legacy 为原始两轮执行",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.runtime == "ai_os":
        runtime = AIOSRuntime(os.path.dirname(os.path.abspath(__file__)))
        result = runtime.run_once(args.agent, args.instruction, call_agent_multi_turn)
    else:
        result = call_agent_multi_turn(args.agent, args.instruction)

    try:
        print(json.dumps(json.loads(result), ensure_ascii=False, indent=2))
    except json.JSONDecodeError:
        print(result)


if __name__ == "__main__":
    main()
