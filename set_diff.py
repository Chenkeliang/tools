def compare_sets(set1, set2):
    """
    比较两个集合的差异

    参数:
    set1 (set): 第一个集合
    set2 (set): 第二个集合

    返回:
    tuple: 包含以下三个元素的元组
        - 仅在 set1 中的元素
        - 仅在 set2 中的元素
        - 两个集合的交集
    """
    # 计算 set1 和 set2 的差集
    only_in_set1 = set1 - set2
    only_in_set2 = set2 - set1

    # 计算 set1 和 set2 的交集
    intersection = set1 & set2

    return only_in_set1, only_in_set2, intersection


if __name__ == "__main__":
    # 示例用法
    set1 = {
        "6934411310793102548A",
    }

    set2 = {
        "6934411310793102548A",
    }

    # print(set1)
    # items = []
    #
    # # 将列表转换为集合，这将自动移除重复项
    # unique_items = len(set(items))
    #
    # # 找出那些在原始列表中出现超过一次的元素
    # duplicates = [item for item in items if items.count(item) > 1]
    #
    diff_set1, diff_set2, common_set = compare_sets(set1, set2)
    #
    print("仅在 set1 中的元素:", diff_set1)
    print("仅在 set2 中的元素:", diff_set2)
    # print("两个集合的交集:", common_set)
    # print("重复数据：", duplicates)  # 输出重复的元素
    # print("长度：", unique_items)  # 输出重复的元素
    # print("长度1：", len(set1))  # 输出重复的元素
    # print("长度2：", len(set2))  # 输出重复的元素
