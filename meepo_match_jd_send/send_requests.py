import asyncio
import aiohttp
import json
from datetime import datetime


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


def read_request_data(file_path):
    """读取请求数据文件"""
    request_data = []
    try:
        with open(file_path, "r") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    request_data.append(data)
        print(f"成功读取 {len(request_data)} 条请求数据")
    except Exception as e:
        print(f"读取文件出错: {str(e)}")
    return request_data


def save_failed_requests(failed_data, error_messages):
    """保存失败的请求到文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    failed_file = f"failed_requests_{timestamp}.txt"

    with open(failed_file, "w") as f:
        for data, error_msg in zip(failed_data, error_messages):
            # 保存失败的请求数据和错误信息
            record = {"request_data": data, "error_message": error_msg}
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return failed_file


async def main():
    print("请输入request_data文件路径：")
    file_path = input().strip()

    # 读取数据
    request_data = read_request_data(file_path)
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
