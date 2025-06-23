import re

def text_analyze(msg):
    nums = re.findall(r"([\d\.]+)%|(\d+)", msg)
    flat = [x for pair in nums for x in pair if x]
    return "文字分析結果：\n" + "\n".join(flat)