def generate_update_sql(input_file, batch_size=3000):
    # 读取shipping codes
    with open(input_file, "r") as f:
        # 去除引号和逗号，并过滤空行
        codes = [line.strip().strip('",') for line in f if line.strip()]

    # 按batch_size分组处理
    for i in range(0, len(codes), batch_size):
        batch = codes[i : i + batch_size]
        # 生成SQL语句
        sql = "UPDATE mp_shipping SET status = 110 WHERE shipping_code IN (\n"
        sql += ",\n".join(f"'{code}'" for code in batch)
        sql += "\n);"

        # 将SQL语句写入文件
        output_file = f"update_batch_{i//batch_size + 1}.sql"
        with open(output_file, "w") as f:
            f.write(sql)
        print(f"Generated {output_file}")


if __name__ == "__main__":
    generate_update_sql("./shipping_codes.txt")
