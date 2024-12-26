import sys
import pyperclip
import re
import argparse


def clean_item(item):
    # 移除所有引号、逗号和多余的空白
    cleaned = re.sub(r'["\',]+$', "", item.strip())  # 移除尾部的引号和逗号
    cleaned = re.sub(r'^["\']', "", cleaned)  # 移除开头的引号
    cleaned = re.sub(r'["\']$', "", cleaned)  # 移除结尾的引号
    return cleaned.strip()


def format_text(text, format_type=0):
    try:
        # 移除空行和首尾空白，同时处理可能的特殊字符
        text = text.replace("\r", "").strip()

        # 分割行，并清理每一行
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # 处理混合分隔符的情况（逗号和空格）
        if len(lines) == 1:
            # 先按逗号分割，然后对每个部分按空格分割
            items = []
            # 使用正则表达式处理可能的特殊分隔符
            parts = re.split(r"[,\s]+", lines[0])
            for part in parts:
                if part.strip():
                    items.append(part.strip())
        else:
            items = lines

        # 清理每一项
        items = [clean_item(item) for item in items if clean_item(item)]

        # 根据format_type选择不同的格式化方式
        if format_type == 1:  # 横排带引号
            return '","'.join(items).join(['"', '"'])
        elif format_type == 2:  # 竖排不带引号
            return ",\n".join(items)
        elif format_type == 3:  # 竖排不带引号和逗号
            return "\n".join(items)
        else:  # 默认：竖排带引号
            formatted_items = [f'"{item}"' for item in items]
            return ",\n".join(formatted_items)
    except Exception as e:
        print(f"处理文本时出错: {str(e)}")
        return text


def get_input():
    """获取用户输入，确保等待Enter键"""
    print("请粘贴文本，然后按Enter键确认：")
    lines = []
    while True:
        try:
            line = input()
            if not line and lines:  # 如果是空行且已经有输入内容，则结束输入
                break
            lines.append(line)
        except EOFError:
            break
    return "\n".join(lines)


if __name__ == "__main__":
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(
        description="文本格式化工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  1. 默认格式（竖排带引号）:
     输入: A1,A2
     输出:
     "A1",
     "A2"

  2. 横排格式 (-v 1):
     输入: A1,A2
     输出: "A1","A2"

  3. 竖排不带引号 (-v 2):
     输入: "A1","A2"
     输出:
     A1,
     A2

  4. 竖排不带引号和逗号 (-v 3):
     输入: "A1","A2"
     输出:
     A1
     A2
""",
    )
    parser.add_argument(
        "-v",
        "--vertical",
        type=int,
        default=0,
        help="输出格式：0为竖排带引号（默认），1为横排带引号，3为竖排不带引号，4为竖排不带引号和逗号",
    )
    parser.add_argument("file", nargs="?", help="输入文件路径（可选）")

    args = parser.parse_args()

    try:
        # 获取输入文本
        if args.file:
            try:
                with open(args.file, "r", encoding="utf-8") as f:
                    text = f.read()
            except Exception as e:
                print(f"读取文件错误: {e}")
                sys.exit(1)
        else:
            text = get_input()

        result = format_text(text, format_type=args.vertical)
        print("\n处理结果：")
        print(result)

        # 复制到剪贴板
        pyperclip.copy(result)
        print("\n结果已复制到剪贴板！")
    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n发生错误: {str(e)}")
        sys.exit(1)
