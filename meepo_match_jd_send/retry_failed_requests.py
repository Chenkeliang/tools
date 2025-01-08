import asyncio
import aiohttp
import json
from datetime import datetime


def clean_order_id(order_id):
    """清理订单号中的引号"""
    return order_id.strip().strip('"')


def clean_waybill_id(waybill_id):
    """清理运单号中的引号和空格"""
    return waybill_id.strip().strip('"').strip()


def read_data2_file(file_path):
    """读取data2.txt格式的文件"""
    request_data = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            # 跳过标题行（如果有）
            first_line = f.readline()
            if "订单号" in first_line or "物流公司" in first_line:
                pass  # 跳过标题行
            else:
                f.seek(0)  # 如果第一行不是标题，重新回到文件开头

            for line in f:
                line = line.strip()
                if not line:
                    continue

                # 使用制表符分割
                parts = line.split("\t")
                if len(parts) >= 3:
                    order_id = clean_order_id(parts[0])
                    waybill_id = clean_waybill_id(parts[2])

                    if order_id and waybill_id:
                        data = {
                            "order_id": order_id,
                            "delivery_id": "JD",
                            "waybill_id": waybill_id,
                            "sku_list": [],  # 如果需要SKU列表，需要从其他地方获取
                        }
                        request_data.append(data)

        print(f"成功读取 {len(request_data)} 条数据")
    except Exception as e:
        print(f"读取文件出错: {str(e)}")
    return request_data


async def send_request(session, data):
    """发送单个请求"""
    url = "http://hermes-go.prod.svc.luojilab.dc/wxsp/delivery-physical/dedao"
    headers = {"Content-Type": "application/json"}
    try:
        async with session.post(url, json=data, headers=headers) as response:
            result = await response.text()
            status = response.status
            print(f"订单 {data['order_id']} 请求完成，状态码: {status}")
            if status < 200 or status >= 300:
                return False, data, f"状态码: {status}, 响应: {result}"
            return True, data, result
    except Exception as e:
        print(f"订单 {data['order_id']} 请求失败: {str(e)}")
        return False, data, str(e)


async def process_batch(request_data, concurrency=10):
    """处理一批请求"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        semaphore = asyncio.Semaphore(concurrency)

        async def bounded_send(data):
            async with semaphore:
                return await send_request(session, data)

        for data in request_data:
            task = asyncio.create_task(bounded_send(data))
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        return results


def read_failed_requests(file_path):
    """读取失败的请求数据"""
    request_data = []
    try:
        with open(file_path, "r") as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    # 从记录中提取原始请求数据
                    request_data.append(record["request_data"])
        print(f"成功读取 {len(request_data)} 条失败的请求数据")
    except Exception as e:
        print(f"读取文件出错: {str(e)}")
    return request_data


def save_failed_requests(failed_data, error_messages):
    """保存失败的请求到文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    failed_file = f"retry_failed_{timestamp}.txt"

    with open(failed_file, "w") as f:
        for data, error_msg in zip(failed_data, error_messages):
            record = {"request_data": data, "error_message": error_msg}
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return failed_file


async def main():
    print("请输入数据文件路径（可以是data2.txt或failed_requests_*.txt）：")
    file_path = input().strip()

    # 根据文件名判断使用哪种读取方式
    if "data2.txt" in file_path:
        request_data = read_data2_file(file_path)
    else:
        request_data = read_failed_requests(file_path)

    if not request_data:
        print("没有有效的请求数据")
        return

    print(f"\n总共有 {len(request_data)} 个请求待处理")

    # 设置并发数为10
    concurrency = 10
    print(f"使用 {concurrency} 个并发进行请求")

    # 记录开始时间
    start_time = datetime.now()

    # 执行请求
    results = await process_batch(request_data, concurrency)

    # 记录结束时间
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # 处理结果
    success_count = 0
    failed_requests = []
    error_messages = []

    for success, data, message in results:
        if success:
            success_count += 1
        else:
            failed_requests.append(data)
            error_messages.append(message)

    # 保存失败的请求
    if failed_requests:
        failed_file = save_failed_requests(failed_requests, error_messages)
        print(f"\n失败的请求信息已保存到: {failed_file}")

    # 输出统计信息
    print(f"\n执行完成:")
    print(f"总耗时: {duration:.2f} 秒")
    print(f"成功: {success_count} 个")
    print(f"失败: {len(failed_requests)} 个")


if __name__ == "__main__":
    asyncio.run(main())
