import re

# 从字符串中提取数字
totalCount = "b'0,{0.054489,-0.419880,-64.224762,0.098824,0.000000,0.000000},GetPose(2,0);'"
count = re.findall('-?\d+.?\d+', totalCount)
print(count)
