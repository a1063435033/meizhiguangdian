import serial
from datetime import datetime, timedelta
import struct
import pandas as pd
import threading

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
        '设备ID': [f"{reg:04X}" for reg in registers[2:6]],
        '硬件版本': f"{registers[6] >> 8}.{registers[6] & 0xFF}",
        '固件版本': f"{registers[7] >> 8}.{registers[7] & 0xFF}",
        '温度': round(registers[10] / 10),
        '湿度': round(registers[11] / 10),
        '光敏传感器': registers[12],
        '是否白天': registers[15],
        'RW 白天PPFD阀值': registers[16],
        'RW 夜晚PPFD阀值': registers[17],
        'RW 采样稳定时间': registers[18],
        '区间保持计数': registers[19]
    }
    
    return device_info

def listen_for_exit():
    """监听用户输入，如果输入为'exit'，则设置running为False"""
    global running
    while running:
        exit_signal = input("输入 'exit' 以提前退出循环: ")
        if exit_signal.strip().lower() == 'exit':
            running = False
            print("准备退出...")
            break

def run_auto_test(headers, excel_file_path, serial_port, endTestTime):
    # 获取当前时间
    start_time = datetime.now()
    print("开始时间:", start_time.strftime("%Y-%m-%d %H:%M:%S"))
    # 设置结束时间
    end_time = start_time + timedelta(minutes=endTestTime)
    # 标志位，用于控制循环
    global running
    running = True
    # 用于存储不同设备地址的DataFrame
    sheets_data = {}
    data_list = []
    commands = bytes.fromhex('02 03 00 00 00 16 C4 37')
    ser = serial.Serial(serial_port, 115200, timeout=1)

    # 在另一个线程中启动监听函数
    threading.Thread(target=listen_for_exit, daemon=True).start()

    while running and datetime.now() < end_time:
        ser.write(commands)
        data = ser.readall().hex()
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        results = []
        start_index = 0
        fixed_length = 98   
        while True:
            start_index = data.find("02032c0002", start_index)
            if start_index == -1:
                break
            end_index = min(start_index + fixed_length, len(data))
            extracted_part = data[start_index:end_index]
            results.append(extracted_part)
            start_index += 10

        for result in results:
            data1 = bytes.fromhex(result)
            devicesInfo = parse_response(data1, formatted_time)
            # if devicesInfo:
            data_list.append(devicesInfo)

    # 处理并保存数据到Excel文件
    for device_info in data_list:
        device_info['温度'] = int(device_info['温度'])
        device_info['湿度'] = int(device_info['湿度'])
        row_df = pd.DataFrame([device_info], columns = headers)
        device_address = device_info['设备ID'][3]
        if device_address not in sheets_data:
            sheets_data[device_address] = pd.DataFrame(columns = headers)
        if not row_df.empty:
            sheets_data[device_address] = pd.concat(
                [sheets_data[device_address], row_df],
                ignore_index=True,
                join='inner'
            )
        else:
            print(f"Skipping empty DataFrame for device {device_address}")

    with pd.ExcelWriter(excel_file_path, engine = 'openpyxl') as writer:
        for sheet_name, df in sheets_data.items():
            df.to_excel(writer, sheet_name=str(sheet_name), index=False)

if __name__ == "__main__":
    headers = [
        '时间', '设备地址', '功能码', '寄存器数据', '设备类型代码', '设备ID', '硬件版本', '固件版本',
        '温度', '湿度', '光敏传感器', '是否白天', 'RW 白天PPFD阀值', 'RW 夜晚PPFD阀值',
        'RW 采样稳定时间', '区间保持计数'
    ]
    excel_file_path = 'outlog.xlsx'  # 定义Excel文件路径
    endTestTime = 30  # 定义测试时长，单位为分钟
    serial_port = 'COM3'  # 定义串口号
    run_auto_test(headers, excel_file_path, serial_port, endTestTime)