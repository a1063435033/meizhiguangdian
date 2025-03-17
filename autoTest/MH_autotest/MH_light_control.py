import serial
import time
import json
import re
import utils.light_commands
from datetime import datetime
from page.fileOperations import FileOperations

class LightControl(FileOperations):
    def __init__(self, filepath):
        super().__init__(filepath)
        self.timeout_seconds = 7

    def manual_light_adjust_mode(self, ser, pid, on, dim):
          # 设置读取时间窗口为6秒
        data_received = False
        start_time = time.time()  # 记录开始时间
          # 标志变量，表示是否已接收到数据
        commands = utils.light_commands.get_manual_light_adjust_mode_command(pid, on, dim)
        ser.write(commands.encode('utf-8'))
        time.sleep(0.5)
        while time.time() - start_time < self.timeout_seconds and not data_received:  # 在6秒内持续读取
            if ser.in_waiting > 0:
                raw_data = ser.readall()
                if isinstance(raw_data, bytes):
                    serial_data = raw_data.decode(errors='ignore')#.rstrip()
                    match = re.search(r'{.*?}', serial_data)
                    first_json_str = match.group(0)
                    try:
                        buffer = json.loads(first_json_str)
                    except:
                        matches = re.findall(r'\{.*?\}', serial_data)
                        first_json_str = matches[-1]
                        buffer = json.loads(first_json_str)
                data_received = True
                    
        if data_received:
            data_received = False
            try:
                if buffer["code"] == 200:
                    self.write_log(f"发送手动调节灯光模式命令成功: {commands}")
                else:
                    self.write_log(f"6S内没有接受到指令响应，发送失败")
                    return None
            except:
                matches = re.findall(r'\{.*?\}', serial_data)
                first_json_str = matches[-1]
                buffer = json.loads(first_json_str)
                if buffer["code"] == 200:
                    self.write_log(f"发送手动调节灯光模式命令成功: {commands}")
                else:
                    self.write_log(f"6S内没有接受到指令响应，发送失败")
                    return None
        start_time1 = time.time()
        while time.time() - start_time1 < self.timeout_seconds and not data_received:  # 在6秒内持续读取
            if ser.in_waiting > 0:
                raw_data = ser.readline().decode().rstrip()
                # 读取一行数据
                data_received = True
        if data_received:     
            first_json_end = raw_data.find('}{') + 1  # 找到'}{'的位置，并调整以包含第一个'}'
            # # 分割字符串
            # first_json_str = buffer[:first_json_end]
            second_json_str = raw_data[first_json_end:]
            # 解析JSON字符串为字典
            # first_dict = json.loads(first_json_str)
            second_dict = json.loads(second_json_str)
            light_data = second_dict.get('params', {}).get('light')
            if light_data['dim'] == dim:
                self.write_log(f"调节亮度成功, 亮度dim值为：{light_data['dim']}")
                ser.close()
                return second_dict['params']['sensor']['ppfd']
                
            else:
                self.write_log(f"调节亮度失败, 亮度dim值为：{light_data['dim']}")
        return None

    def auto_light_adjust_mode(self, ser, pid, st, et, dim, darkenT, offT, sunTime):
        ppfd_list = []
        current_time_list = []
        data_received = False
        start_time = time.time()  # 记录开始时间
        # 标志变量，表示是否已接收到数据
        commands = utils.light_commands.get_auto_light_adjust_mode_command(pid, st, et, dim, darkenT, offT, sunTime)
        ser.write(commands.encode('utf-8'))
        time.sleep(0.5)
        while time.time() - start_time < self.timeout_seconds and not data_received:  # 在6秒内持续读取
            if ser.in_waiting > 0:
                raw_data = ser.readall()
                if isinstance(raw_data, bytes):
                    serial_data = raw_data.decode(errors='ignore')#.rstrip()
                    match = re.search(r'{.*?}', serial_data)
                    first_json_str = match.group(0)
                    try:
                        buffer = json.loads(first_json_str)
                    except:
                        matches = re.findall(r'\{.*?\}', serial_data)
                        first_json_str = matches[-1]
                        buffer = json.loads(first_json_str)
                data_received = True
        if data_received:
            data_received = False
            if buffer["code"] == 200:
                self.write_log(f"发送自动调节灯光模式命令成功: {commands}", 'auto_light_adjust_mode_log.txt')
            else:
                self.write_log(f"6S内没有接受到指令响应，发送失败", 'auto_light_adjust_mode_log.txt')
                return False
        while True:
            if ser.in_waiting > 0:
                # 读取一行数据
                raw_data = ser.readall().decode().rstrip() 
                first_json_end = raw_data.find('}{') + 1  # 找到'}{'的位置，并调整以包含第一个'}'
                # # 分割字符串
                first_json_str = raw_data[:first_json_end]
                second_json_str = raw_data[first_json_end:]
                # 解析JSON字符串为字典
                first_dict = json.loads(first_json_str)
                second_dict = json.loads(second_json_str)
                minutes_since_midnights = first_dict['params']['device_info']['timeinfo']
                dt = datetime.strptime(minutes_since_midnights.rsplit('-', 1)[0], '%Y-%m-%d:%H:%M:%S')
                # 计算从当天开始到现在经过了多少分钟
                midnight = dt.replace(hour=0, minute=0, second=0, microsecond=0)
                minutes_passed = (dt - midnight).total_seconds() / 60

                if minutes_passed >= st:
                    self.write_log(second_dict['params']['sensor']['ppfd'], 'auto_light_adjust_mode_log.txt')
                    self.write_log(minutes_since_midnights.rsplit('-', 1)[0], 'auto_light_adjust_mode_log.txt')
                    ppfd_list.append(second_dict['params']['sensor']['ppfd'])

                    current_time_list.append(minutes_since_midnights.rsplit('-', 1)[0])
                    if second_dict['params']['sensor']['ppfd'] == 0 and minutes_passed >= et:
                        self.write_log(second_dict['params']['sensor']['ppfd'], 'auto_light_adjust_mode_log.txt')
                        self.write_log(minutes_since_midnights.rsplit('-', 1)[0], 'auto_light_adjust_mode_log.txt')
                        return ppfd_list, current_time_list
                    
                if minutes_passed >= et and second_dict['params']['sensor']['ppfd'] != 0:
                    ppfd = second_dict['params']['sensor']['ppfd']
                    self.write_log(f'当前时间以超过{et}，PPFD：{ppfd}，灯光未关闭', 'auto_light_adjust_mode_log.txt')
                    return None

    def ppfd_light_adjust_mode(self, ser, pid, st, et, dim_min, dim_max, ppfd, darkenT, offT, sunTime):
        commands = utils.light_commands.get_ppfd_light_adjust_mode_command(pid, st, et, dim_min, dim_max, ppfd, darkenT, offT, sunTime)
        ser.write(commands.encode('utf-8'))
        data_received = False
        time.sleep(0.5)
        start_time = time.time()  # 记录开始时间
        while time.time() - start_time < self.timeout_seconds and not data_received: # 在6秒内持续读取
            if ser.in_waiting > 0:
                raw_data = ser.readall()
                if isinstance(raw_data, bytes):
                    serial_data = raw_data.decode(errors='ignore')#.rstrip()
                    match = re.search(r'{.*?}', serial_data)
                    first_json_str = match.group(0)
                    try:
                        buffer = json.loads(first_json_str)
                    except:
                        matches = re.findall(r'\{.*?\}', serial_data)
                        first_json_str = matches[-1]
                        buffer = json.loads(first_json_str)
                data_received = True
        if data_received:
            print(buffer)
            data_received = False
            if buffer["code"] == 200:
                self.write_log(f"发送自动调节灯光模式命令成功: {commands}")
            else:
                self.write_log(f"6S内没有接受到指令响应，发送失败")
                return False
        while True:
            if ser.in_waiting > 0:
                # 读取一行数据
                raw_data = ser.readall().decode().rstrip() 
                first_json_end = raw_data.find('}{') + 1  # 找到'}{'的位置，并调整以包含第一个'}'
                # # 分割字符串
                first_json_str = raw_data[:first_json_end]
                second_json_str = raw_data[first_json_end:]
                # 解析JSON字符串为字典
                first_dict = json.loads(first_json_str)
                second_dict = json.loads(second_json_str)
                minutes_since_midnight = first_dict['params']['device_info']['timeinfo']
                dt = datetime.strptime(minutes_since_midnight.rsplit('-', 1)[0], '%Y-%m-%d:%H:%M:%S')
                # 计算从当天开始到现在经过了多少分钟
                midnight = dt.replace(hour=0, minute=0, second=0, microsecond=0)
                minutes_passed = (dt - midnight).total_seconds() / 60
                dim = second_dict['params']['light']['dim']
                ppfd = second_dict['params']['sensor']['ppfd']
                if minutes_passed >= st and  minutes_passed <= st + 1:
                    if second_dict['params']['light']['dim'] == dim_min:
                        self.write_log(f'设备dim值为:{dim},自定义dim_min值为{dim_min}', 'ppfd_light_adjust_mode.txt')

                    else:
                        self.write_log(f'一分钟内，设备dim值不等于dim_min值，{dim}、{dim_min}', 'ppfd_light_adjust_mode.txt')
                        return False
                elif minutes_passed > st + 1:
                    self.write_log(second_dict['params']['sensor']['ppfd'], 'ppfd_light_adjust_mode.txt')
                    self.write_log(second_dict['params']['light']['dim'], 'ppfd_light_adjust_mode.txt')
                    if second_dict['params']['sensor']['ppfd'] > dim_max + 3:
                        self.write_log(f'当前ppfd超过最大值，ppfd值为：{ppfd}，最大值为：{dim_max}', 'ppfd_light_adjust_mode.txt')
                        return False
                    # elif second_dict['params']['sensor']['ppfd']
                elif minutes_passed >= et:
                    print('测试结束')
                    return True




                


                


                        
                
        



                        

                    
# # 调用方法
# if __name__ == "__main__":
#     a = lightControl()
#     a.manual_light_adjust_mode()