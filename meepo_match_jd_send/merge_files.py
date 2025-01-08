def process_line(line):
    """处理每一行数据，返回单号和其他信息"""
    parts = line.strip().split("\t")
    if len(parts) >= 1:
        # 处理第一个字段中的订单号，去除引号和逗号
        order_id = parts[0].strip().strip('"').strip(",")
        # 如果有其他字段，获取快递公司和运单号
        delivery_id = parts[1].strip() if len(parts) > 1 else ""
        waybill_id = parts[2].strip().strip('"') if len(parts) > 2 else ""
        return order_id, delivery_id, waybill_id
    return None, None, None


def merge_files():
    # 读取第一个文件（包含订单号和SKU信息）
    print(
        "请输入第一个文件的内容 (包含订单号和SKU列表，输入完成后按Ctrl+D或Ctrl+Z结束):"
    )
    sku_data = {}
    while True:
        try:
            line = input()
            if line.strip():
                # 处理类似 WXSP3725078054219682816"L1733994510201" 的格式
                parts = line.strip().split('"')
                if len(parts) >= 2:
                    # 去除订单号开头的WXSP和末尾的逗号
                    order_id = parts[0].strip().strip(",")
                    if order_id.startswith("WXSP"):
                        order_id = order_id[4:]  # 去除前4个字符 "WXSP"
                    sku_list = [
                        sku.strip() for sku in parts[1].split(",") if sku.strip()
                    ]
                    sku_data[order_id] = sku_list
        except EOFError:
            break

    # 读取第二个文件（包含快递信息）
    print("\n请输入第二个文件的内容 (包含快递信息，输入完成后按Ctrl+D或Ctrl+Z结束):")
    delivery_data = {}
    while True:
        try:
            line = input()
            if line.strip():
                order_id, delivery_id, waybill_id = process_line(line)
                if order_id:
                    delivery_data[order_id] = {
                        "delivery_id": delivery_id,
                        "waybill_id": waybill_id,
                    }
        except EOFError:
            break

    # 合并数据并生成JSON格式
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"merged_data_{timestamp}.go"

    with open(result_file, "w") as f:
        f.write("package main\n\n")
        f.write("var dataMap = map[string]interface{}{\n")

        # 合并两个文件的数据
        all_orders = set(sku_data.keys()) | set(delivery_data.keys())
        for order_id in sorted(all_orders):
            sku_list = sku_data.get(order_id, [])
            delivery_info = delivery_data.get(
                order_id, {"delivery_id": "", "waybill_id": ""}
            )

            # 生成合并后的JSON格式
            merged_info = {
                "delivery_id": delivery_info["delivery_id"],
                "order_id": order_id,
                "sku_list": sku_list,
                "waybill_id": delivery_info["waybill_id"],
            }

            # 写入Go map格式
            import json

            f.write(f'\t"{order_id}": {json.dumps(merged_info, ensure_ascii=False)},\n')

        f.write("}\n")

    print(f"\n结果已保存到 {result_file}")


if __name__ == "__main__":
    merge_files()
