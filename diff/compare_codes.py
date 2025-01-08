def compare_strings(str1, str2):
    # 将字符串转换为set，每行一个code
    codes1 = {
        code.strip().strip('",') for code in str1.strip().split("\n") if code.strip()
    }
    codes2 = {
        code.strip().strip('",') for code in str2.strip().split("\n") if code.strip()
    }

    # 找出差异
    not_in_str1 = codes2 - codes1
    not_in_str2 = codes1 - codes2
    common_codes = codes1 & codes2

    # 生成一个包含时间戳的文件名
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"shipping_codes_diff_{timestamp}.txt"

    # 输出结果到控制台和文件
    result = []
    result.append(f"对比结果:")
    result.append(f"字符串1中共有 {len(codes1)} 个codes")
    result.append(f"字符串2中共有 {len(codes2)} 个codes")
    result.append(f"两个字符串共同存在的codes数量: {len(common_codes)}\n")

    result.append(f"在字符串2中存在但在字符串1中不存在的codes ({len(not_in_str1)}):")
    result.extend(sorted(not_in_str1))
    result.append("")

    result.append(f"在字符串1中存在但在字符串2中不存在的codes ({len(not_in_str2)}):")
    result.extend(sorted(not_in_str2))

    # 打印到控制台
    print("\n".join(result))

    # 保存到文件
    with open(result_file, "w") as f:
        f.write("\n".join(result))

    print(f"\n结果已保存到 {result_file}")


def get_input_strings():
    print("请输入第一段字符串 (输入完成后按Ctrl+D或Ctrl+Z结束):")
    str1 = []
    while True:
        try:
            line = input()
            str1.append(line)
        except EOFError:
            break

    print("\n请输入第二段字符串 (输入完成后按Ctrl+D或Ctrl+Z结束):")
    str2 = []
    while True:
        try:
            line = input()
            str2.append(line)
        except EOFError:
            break

    return "\n".join(str1), "\n".join(str2)


if __name__ == "__main__":
    str1, str2 = get_input_strings()
    compare_strings(str1, str2)
