import json
from datetime import datetime


def read_file1_data(file_path):
    """读取第一个文件的数据（WXSP格式）"""
    data_dict = {}
    try:
        with open(file_path, "r") as f:
            for line_number, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                # 分割订单号和SKU列表
                parts = line.split(",", 1)
                if len(parts) != 2:
                    print(f"行 {line_number}: 格式不正确: {line}")
                    continue

                order_id = parts[0].replace("WXSP", "")  # 移除WXSP前缀
                # 处理SKU列表，移除引号并分割
                sku_list = parts[1].strip('"').split(",")
                sku_list = [sku.strip() for sku in sku_list]

                # 打印调试信息
                print(f"文件1处理: 原始订单号={parts[0]}, 处理后订单号={order_id}")

                data_dict[order_id] = {"order_id": order_id, "sku_list": sku_list}

    except Exception as e:
        print(f"读取文件1 {file_path} 时出错: {str(e)}")

    print(f"文件1成功读取了 {len(data_dict)} 条记录")
    # 打印前几个订单号示例
    print("文件1的前5个订单号示例:", list(data_dict.keys())[:5])
    return data_dict


def clean_order_id(order_id):
    """清理订单号中的引号"""
    return order_id.strip().strip('"')


def clean_waybill_id(waybill_id):
    """清理运单号中的引号和空格"""
    return waybill_id.strip().strip('"').strip()


def read_file2_data(file_path):
    """读取第二个文件的数据（快递信息格式）"""
    data_dict = {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            # 跳过标题行（如果有）
            first_line = f.readline()
            if "订单号" in first_line or "物流公司" in first_line:
                pass  # 跳过标题行
            else:
                f.seek(0)  # 如果第一行不是标题，重新回到文件开头

            for line_number, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    # 使用制表符分割
                    parts = line.split("\t")
                    if len(parts) < 3:
                        print(f"行 {line_number}: 格式不正确: {line}")
                        continue

                    order_id = clean_order_id(parts[0])
                    waybill_id = clean_waybill_id(parts[2])

                    if not waybill_id:  # 如果运单号为空，跳过该记录
                        print(f"行 {line_number}: 运单号为空，跳过: {line}")
                        continue

                    data_dict[order_id] = {
                        "order_id": order_id,
                        "delivery_id": "JD",
                        "waybill_id": waybill_id,
                    }

                except Exception as e:
                    print(f"行 {line_number} 处理出错: {line}")
                    print(f"错误信息: {str(e)}")
                    continue

    except Exception as e:
        print(f"读取文件2 {file_path} 时出错: {str(e)}")

    print(f"文件2成功读取了 {len(data_dict)} 条记录")
    # 打印前几个订单号和运单号示例
    sample_records = list(data_dict.items())[:5]
    print("文件2的前5个记录示例:")
    for order_id, data in sample_records:
        print(f"订单号: {order_id}, 运单号: {data['waybill_id']}")
    return data_dict


def match_and_generate_requests(file1_path, file2_path):
    """匹配两个文件的数据并生成请求数据"""
    # 读取两个文件的数据
    data1 = read_file1_data(file1_path)
    data2 = read_file2_data(file2_path)

    print(f"\n文件1中有 {len(data1)} 条数据")
    print(f"文件2中有 {len(data2)} 条数据")

    # 找出共同的订单号
    common_orders = set(data1.keys()) & set(data2.keys())
    # 只在文件1中的订单号
    only_in_file1 = set(data1.keys()) - set(data2.keys())
    # 只在文件2中的订单号
    only_in_file2 = set(data2.keys()) - set(data1.keys())

    print(f"\n共同订单数: {len(common_orders)}")
    if common_orders:
        print("共同订单号示例:", list(common_orders)[:5])
    print(f"只在文件1中的订单数: {len(only_in_file1)}")
    print(f"只在文件2中的订单数: {len(only_in_file2)}")

    # 生成请求数据文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    request_file = f"request_data_{timestamp}.txt"

    with open(request_file, "w") as f:
        # 写入共同的订单
        for order_id in sorted(common_orders):
            # 合并两个文件中的数据
            merged_data = {
                "order_id": order_id,
                "sku_list": data1[order_id]["sku_list"],
                "waybill_id": data2[order_id]["waybill_id"],
                "delivery_id": data2[order_id]["delivery_id"],
            }
            f.write(json.dumps(merged_data, ensure_ascii=False) + "\n")

    # 生成差异数据文件
    diff_file = f"diff_data_{timestamp}.txt"
    with open(diff_file, "w") as f:
        f.write("=== 只在文件1中的订单 ===\n")
        for order_id in sorted(only_in_file1):
            f.write(f"{order_id}: {json.dumps(data1[order_id], ensure_ascii=False)}\n")

        f.write("\n=== 只在文件2中的订单 ===\n")
        for order_id in sorted(only_in_file2):
            f.write(f"{order_id}: {json.dumps(data2[order_id], ensure_ascii=False)}\n")

    return request_file, diff_file


if __name__ == "__main__":
    print("请输入两个数据文件的路径：")
    file1_path = input("文件1路径 (包含WXSP和SKU的文件): ").strip()
    file2_path = input("文件2路径 (包含快递信息的文件): ").strip()

    request_file, diff_file = match_and_generate_requests(file1_path, file2_path)

    print(f"\n请求数据已保存到: {request_file}")
    print(f"差异数据已保存到: {diff_file}")
    print("\n您可以使用 send_requests.py 脚本处理 request_data 文件中的数据")
