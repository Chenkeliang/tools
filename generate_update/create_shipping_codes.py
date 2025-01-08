# 创建一个新文件来保存shipping codes
shipping_codes = [
    "SH250101AMDHECJS",
]

# 将codes写入文件，每行一个code
with open("shipping_codes.txt", "w") as f:
    for code in shipping_codes:
        f.write(f'"{code}"\n')

print(f"已生成shipping_codes.txt文件，包含 {len(shipping_codes)} 个shipping codes")
