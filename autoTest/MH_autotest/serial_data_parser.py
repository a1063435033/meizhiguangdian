import re
import json
import time

class SerialDataParser:

    @staticmethod
    def read_serial_succeed_data(ser, timeout_seconds):
        """从串口读取的数据中提取第一个有效的JSON字符串"""
        for times in range(timeout_seconds):
            if ser.in_waiting > 0:
                raw_data = ser.readall() 
                if isinstance(raw_data, bytes):
                    serial_data = raw_data.decode(errors='ignore')#.rstrip()
                    match = re.findall(r'\{.*?\}', serial_data)
                    print(match)
                    print('-------------------------------')
                    first_json_str = match[0]
                    buffer = json.loads(first_json_str)
                    if 'code' in buffer.keys():
                        return buffer
                    else:
                        first_json_str = match[-1]
                        buffer = json.loads(first_json_str)
                        return buffer
            time.sleep(1)
    
    @staticmethod
    def split_json_pairs(ser):
        """分割包含多个JSON对象的字符串"""
        raw_data = ser.readall().decode().rstrip() 
        first_json_end = raw_data.find('}{') + 1  # 找到'}{'的位置，并调整以包含第一个'}'
        # # 分割字符串
        first_json_str = raw_data[:first_json_end]
        second_json_str = raw_data[first_json_end:]
        # 解析JSON字符串为字典
        first_dict = json.loads(first_json_str)
        second_dict = json.loads(second_json_str)
        return first_dict, second_dict

    @staticmethod      
    def continue_read_serial_data(ser, start_time, timeout_seconds, data_received):
        while time.time() - start_time < timeout_seconds and not data_received:  # 在6秒内持续读取
            if ser.in_waiting > 0:
                raw_data = ser.readall()
                if isinstance(raw_data, bytes):
                    serial_data = raw_data.decode(errors='ignore')#.rstrip()
                    match = re.search(r'{.*?}', serial_data)
                    first_json_str = match.group(0)
                    try:
                        return json.loads(first_json_str), serial_data
                    except:
                        matches = re.findall(r'\{.*?\}', serial_data)
                        first_json_str = matches[-1]
                        return json.loads(first_json_str), serial_data
                data_received = True