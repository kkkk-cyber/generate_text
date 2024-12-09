import sqlite3

# 连接到数据库
conn = sqlite3.connect('portraits.db')

# 创建游标对象
cursor = conn.cursor()

# 查询所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("数据库中的表:")
for table in tables:
    print(table[0])

# 查看 `portraits` 表中的数据
print("\n'portraits' 表中的数据:")
cursor.execute("SELECT * FROM portraits")
rows = cursor.fetchall()

for row in rows:
    print(row)

# 关闭连接
conn.close()
