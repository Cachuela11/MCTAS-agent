# 输出1到300之间的所有水仙花数
def is_narcissistic(num):
    # 将数字转换为字符串，便于取各位数字
    digits = [int(d) for d in str(num)]
    # 计算各位数字的立方和
    sum_of_cubes = sum(d ** 3 for d in digits)
    # 判断是否等于原数
    return sum_of_cubes == num

# 遍历1到300
for i in range(1, 301):
    if is_narcissistic(i):
        print(i)