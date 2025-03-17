from datetime import datetime
import time
import yaml

# 正确指定配置文件的路径
config_path = r"D:\meizhiguangdian\autoTest\MH_autotest\config\config.yaml"

try:
    # 使用正确的路径和编码打开文件
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
        print(config)  # 打印读取的内容以验证是否正确加载
except FileNotFoundError as e:
    print(f"无法找到文件: {e}")
except UnicodeDecodeError as e:
    print(f"编码解码错误: {e}")
except Exception as e:
    print(f"发生了一个错误: {e}")