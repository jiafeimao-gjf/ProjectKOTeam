#!/usr/bin/env python3
import random
import sys, os, json, base64, subprocess
from pathlib import Path

workdir = "/Users/jiafei/PycharmProjects/{}"


# ---------- 工具函数 ----------
def run_cmd(cmd, cwd=None):
    """执行 shell 命令，返回 stdout；抛异常时终止"""
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}\n{result.stdout}")
    return result.stdout.strip()


def read_content(lines_iter):
    """读取 CONTENT 块，直到 END_CONTENT"""
    content_lines = []
    for line in lines_iter:
        if line.strip() == "END_CONTENT":
            break
        content_lines.append(line.rstrip("\n"))
    return "\n".join(content_lines)


# ---------- 操作实现 ----------
def create_file(params, content):

    path = Path(params["path"])
    write_path = Path(workdir) / path
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(write_path, "w", encoding="utf-8") as f:
        f.write(content[:-1])
    run_cmd(f"cd {workdir} && git add {path}")


def update_file(params, content):
    path = Path(params["path"])
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    run_cmd(f"cd {workdir} && git add {path}")


def delete_file(params):
    path = Path(params["path"])
    if path.exists():
        run_cmd(f"cd {workdir} && git rm {path}")


def commit(params):
    msg = params["message"]
    author_name = params.get("author_name", "AI Bot")
    author_email = params.get("author_email", "ai@example.com")
    run_cmd(f'cd {workdir} && git commit -m "{msg}" --author="{author_name} <{author_email}>"')


def pull(params):
    remote = params.get("remote", "origin")
    branch = params.get("branch", "main")
    run_cmd(f"cd {workdir} && git pull {remote} {branch}")


def create_branch(params):
    branch = params["branch_name"]
    start_point = params.get("start_point", "HEAD")
    run_cmd(f"cd {workdir} && git branch {branch} {start_point}")
    run_cmd(f"cd {workdir} && git checkout {branch}")


def push(params):
    remote = params.get("remote", "origin")
    branch = params.get("branch", "HEAD")
    run_cmd(f"cd {workdir} && git push {remote} {branch}")


# ---------- 主解析 ----------
def parse_cop(text, logger):
    lines = iter(text.split('\n'))
    actions = []

    for line in lines:
        if line.strip() != "BEGIN COP":
            continue
        # 进入 COP 块
        while True:
            # StopIteration 判断
            line = next(lines, None)
            if line is None:
                logger.info("COP 解析结束")
                break
            line = line.strip()
            # logger.info(f"line = {line}")
            if line.startswith("ACTION:"):
                action_type = line.split(":", 1)[1].strip()
            elif line.startswith("PARAMS:"):
                # 读取 JSON/YAML
                param_lines = []
                content_flag = False
                for p in lines:
                    if p.strip() == "":
                        continue
                    if p.strip().startswith("CONTENT:"):
                        # 预读 CONTENT 标记，后面会处理
                        content_flag = True
                        break
                    if p.strip().startswith("ACTION:") or p.strip() == "END COP":
                        # 结束当前 action
                        content_flag = False
                        break
                    param_lines.append(p)
                params_text = "\n".join(param_lines).strip()
                # 先尝试解析 JSON
                try:
                    params = json.loads(params_text)
                except Exception:
                    # 解析 YAML
                    import yaml
                    params = yaml.safe_load(params_text)
                if content_flag:
                    # 跳过已读的 CONTENT: 行
                    next(lines)  # skip "CONTENT:"
                    content = read_content(lines)
                else:
                    content = None
                actions.append((action_type, params, content))
            elif line == "END COP":
                break
    return actions


def main():
    # 读取输入：文件或 stdin
    if len(sys.argv) > 1:
        cop_text = Path(sys.argv[1]).read_text(encoding="utf-8")
    else:
        cop_text = sys.stdin.read()

    do_code_parser(cop_text, None)


def do_code_parser(cop_text, logger):
    actions = parse_cop(cop_text, logger=logger)
    global workdir
    workdir = workdir.format("tmp")
    logger.info(f"workdir = {workdir}")
    run_cmd(f"cd {workdir} && git init")
    # 执行
    for action, params, content in actions:
        if action == "CREATE_FILE":
            create_file(params, content)
        elif action == "UPDATE_FILE":
            update_file(params, content)
        elif action == "DELETE_FILE":
            delete_file(params)
        elif action == "COMMIT":
            commit(params)
        elif action == "PULL":
            pull(params)
        elif action == "CREATE_BRANCH":
            create_branch(params)
        elif action == "PUSH":
            push(params)
        else:
            raise ValueError(f"Unknown action: {action}")


if __name__ == "__main__":
    main()
