import random
 
# 定义包含英文字母的字符串

def GetRandomWorld():
    letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    number = random.randint(30, 31)  # 生成1到10之间的随机整数
    # 生成随机英文字符
    word = ""
    for i in range(0,32):
        random_letter = random.choice(letters)
        word = word + random_letter
    setstr = str(word).lower()
    return setstr


if __name__=="__main__":
    print(GetRandomWorld())
