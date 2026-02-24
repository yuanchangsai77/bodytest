import argparse
import json

from shell.pyshell.agent_framework import call_agent_multi_turn


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="多代理 CLI 入口")
    parser.add_argument("--agent", default="task_planner", help="要调用的 agent 名称")
    parser.add_argument("--instruction", required=True, help="用户指令")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    result = call_agent_multi_turn(args.agent, args.instruction)
    try:
        print(json.dumps(json.loads(result), ensure_ascii=False, indent=2))
    except json.JSONDecodeError:
        print(result)


if __name__ == "__main__":
    main()
