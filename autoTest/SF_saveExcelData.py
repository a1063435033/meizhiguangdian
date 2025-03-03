import struct
from datetime import datetime
import pandas as pd

def calculate_crc16(data):
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            if (crc & 0x0001) != 0:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return bytes([crc & 0xFF, crc >> 8])
    
def filter_hex_data(line):
    # 去除时间戳和前缀部分，假设格式是 "[时间戳]收←◆数据"
    if '◆' not in line:
        return None

    # 提取数据部分
    data = line.split('◆')[-1].strip()
    
    # 去除所有空白字符，得到连续的十六进制字符串
    hex_data = ''.join(data.split())
    
    # print(f"Hex data: {hex_data}")
    # print(f"Length of hex data: {len(hex_data)}")

    # 查找是否存在 "AA02"
    if 'AA02' in hex_data:
        # print(f'11111:{hex_data}')
        aa02_index = hex_data.index('AA02')
        # print(aa02_index)
        
        # 确保总长度为 92 个字符
        start_index = max(0, aa02_index - (98 - len(hex_data[aa02_index:])))
        corrected_hex_data = hex_data[start_index:start_index + 98]

        if len(corrected_hex_data) == 98:
            formatted_hex_data = ' '.join([corrected_hex_data[i:i+2] for i in range(0, len(corrected_hex_data), 2)])
            # print(f"Corrected hex data: {formatted_hex_data}")
            # print(f"Length of corrected hex data: {len(corrected_hex_data)}")
            return f"[{line.split(']')[0]}]收←◆{formatted_hex_data}"
        else:
            pass
            # # 如果仍然不满足 46 字节，则尝试找到最近的前导字节边界
            # while len(corrected_hex_data) > 98:
            #     corrected_hex_data = corrected_hex_data[2:]
            # if len(corrected_hex_data) == 98:
            #     formatted_hex_data = ' '.join([corrected_hex_data[i:i+2] for i in range(0, len(corrected_hex_data), 2)])
            #     # print(f"Final corrected hex data: {formatted_hex_data}")
            #     # print(f"Length of final corrected hex data: {len(corrected_hex_data)}")
            #     return f"[{line.split(']')[0]}]收←◆{formatted_hex_data}"
            # else:
            #     # print(f"Data cannot be corrected to 46 bytes after adjusting from AA02.")
            #     return None
    return None

def parse_response(response_bytes, timestamp):
    addr, func_code, byte_count = struct.unpack('>BBB', response_bytes[:3])
    
    # 提取寄存器数据
    registers = struct.unpack(f'>{byte_count // 2}H', response_bytes[3:-2])
    
    # 将寄存器转换为字节串以查找特定序列
    register_bytes = bytearray()
    for reg in registers:
        register_bytes.extend(struct.pack('>H', reg))
    
    # 检查是否包含目标字节序列
    target_sequence = bytes.fromhex("AA02")
    if target_sequence not in register_bytes:
        print("未找到目标字节序列 AA 02")
        return None
    
    # 根据设备信息解析具体数据
    device_info = {
        '时间': timestamp,
        '设备地址': addr,
        '功能码': func_code,
        '寄存器数据': registers,
        '设备类型代码': f"{registers[1]:04X}",
        '设备ID': [f"{registers[2]:04X}", f"{registers[3]:04X}", f"{registers[4]:04X}", f"{registers[5]:04X}"],
        '硬件版本': f"{registers[6] >> 8}.{registers[6] & 0xFF}",
        '固件版本': f"{registers[7] >> 8}.{registers[7] & 0xFF}",
        '温度': (registers[10] / 10),
        '湿度': (registers[11] / 10),
        '光敏传感器': registers[12],
        '是否白天': registers[15],
        'RW 白天PPFD阀值': registers[16],
        'RW 夜晚PPFD阀值': registers[17],
        'RW 采样稳定时间': registers[18],
        '区间保持计数': registers[19]
    }
    
    # 打印详细信息
    for key, value in device_info.items():
        print(f"{key}: {value}")
    return device_info

def read_and_parse_file(file_path):
    # 创建表头
    headers = [
            '时间', '设备地址', '功能码', '寄存器数据', '设备类型代码', '设备ID', '硬件版本', '固件版本',
            '温度', '湿度', '光敏传感器', '是否白天', 'RW 白天PPFD阀值', 'RW 夜晚PPFD阀值',
            'RW 采样稳定时间', '区间保持计数'
        ]
    df = pd.DataFrame(columns=headers)  # 初始化DataFrame
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            a = filter_hex_data(line)
            # print(f'方法a数据：{a}')
            # print(f'方法b数据：{line}')
            if a is not None:
                parts = a.split('收←◆')
                if len(parts) != 2:
                    continue
                timestamp = parts[0].strip()[1:-1]  # 去掉方括号
                hex_data = parts[1].strip()
                try:
                    # 将十六进制字符串转换为字节数组
                    response_bytes = bytes.fromhex(hex_data.replace(" ", ""))
                    
                    # 验证CRC
                    received_crc = response_bytes[-2:]
                    calculated_crc = calculate_crc16(response_bytes[:-2])
                    if received_crc == calculated_crc:
                        # print(f"时间: {timestamp}, CRC校验通过！")
                        data_list = parse_response(response_bytes, timestamp)
                        row_df = pd.DataFrame([data_list], columns=headers)
                        df = pd.concat([df, row_df], ignore_index=True)
                        excel_file_path = 'people.xlsx'
                        df.to_excel(excel_file_path, index=False)
                    else:
                        print(f"时间: {timestamp}, CRC校验失败！")
                except Exception as e:
                    print(f"处理数据时发生错误: {e}")
            else:
                print(f'{line}:不符合数据类型')
                pass

if __name__ == "__main__":
    file_path = r'D:\autoTest\SaveWindows2025_3_3_16-09-05.TXT'  # 替换为你的文件路径
    read_and_parse_file(file_path)