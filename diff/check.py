def read_data(file_path):
    """读取文件中的数据，返回一个集合"""
    data = set()
    with open(file_path, "r") as file:
        for line in file:
            # 更严格的清理：去除所有空白字符、逗号和引号
            cleaned_line = line.strip().strip(",").strip('"').strip()
            if cleaned_line:  # 如果行不为空
                data.add(cleaned_line)
    return data


def compare_files(file1, file2):
    """比较两个文件，返回各自独有的数据"""
    data1 = read_data(file1)
    data2 = read_data(file2)

    unique_to_file1 = data1 - data2
    unique_to_file2 = data2 - data1

    return unique_to_file1, unique_to_file2


def main():
    # 指定文件路径
    file1_path = "data1.txt"
    file2_path = "data2.txt"

    # 对比文件
    unique_to_file1, unique_to_file2 = compare_files(file1_path, file2_path)

    print("Unique to file1:")
    for item in unique_to_file1:
        print(item)

    print("\nUnique to file2:")
    for item in unique_to_file2:
        print(item)


if __name__ == "__main__":
    main()
