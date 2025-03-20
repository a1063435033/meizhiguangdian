import time
import json
import os
import re
import yaml
import serial
import utils.light_commands
from page.fileOperations import FileOperations
from utils.serial_data_parser import SerialDataParser
from datetime import datetime, timedelta


class PowerStripControl(FileOperations):
    def __init__(self, filepath):
        super().__init__(filepath)
        self.timeout_seconds = 7
        config_path = r"D:\meizhiguangdian\autoTest\MH_autotest\config\powerStrip_config.yaml"
        with open(config_path, 'r', encoding='utf-8') as file:
            self.config_yaml = yaml.safe_load(file)
        self.times = self.config_yaml['switch_times']
        

    def check_iHub4Set_switch_status(self, ser, start_time, ihub, on):
        while time.time() - start_time < self.timeout_seconds:
            if ser.in_waiting > 0:
                raw_data = ser.readline().decode().rstrip()
                first_json_end = raw_data.find('}{') + 1  # 找到'}{'的位置，并调整以包含第一个'}'
                # # 分割字符串
                # first_json_str = buffer[:first_json_end]
                second_json_str = raw_data[first_json_end:]
                # 解析JSON字符串为字典
                # first_dict = json.loads(first_json_str)
                second_dict = json.loads(second_json_str)
                light_data = second_dict.get('params', {}).get("iHub")[ihub]
                if light_data['on'] == on:
                    return True
                else:
                    self.write_log(f"当前发送状态为：{on}，软件上报状态为{light_data['on']}，请检查手动模式开关孔位操作", 'iHub4Set_switch_manual_mode.txt')
                    return False

    def iHub4Set_switch_manual_mode(self, ser, pid):
        ihubs = ["uv", "ir", "rb"]
        def control_socket(ihub):
            for i in range(self.times):
                sendSwitchManualCmd = utils.light_commands.get_iHub4Set_switch_manual_mode_Cmd(ser, ihub, pid, 1)
                if not sendSwitchManualCmd:
                    self.write_log("发送指令失败，请检查串口", 'iHub4Set_switch_manual_mode.txt')
                    return False  # 或者采取其他适当的操作
                start_time = time.time()
                if self.check_iHub4Set_switch_status(ser, start_time, ihub, 1):
                    print(f'第{i+1}次打开{ihub}孔位')               
                sendSwitchManualCmd = utils.light_commands.get_iHub4Set_switch_manual_mode_Cmd(ser, ihub, pid, 0)
                if not sendSwitchManualCmd:
                    self.write_log("发送指令失败，请检查串口", 'iHub4Set_switch_manual_mode.txt')
                    return False  # 或者采取其他适当的操作
                start_time = time.time()
                if self.check_iHub4Set_switch_status(ser, start_time, ihub, 0):
                    print(f'第{i+1}次关闭{ihub}孔位')
            return True
        for ihub in ihubs:
            if control_socket(ihub):
                self.write_log(f"四孔排插{ihub}位开关测试通过", 'iHub4Set_switch_manual_mode.txt')
            else:
                self.write_log(f"四孔排插{ihub}位开关测试失败", 'iHub4Set_switch_manual_mode.txt')

    def iHub4Set_switch_autoMod_mode(self, ser, pid):
        rd = 60
        ed = 60
        times = 99
        ihubs = ["uv", "ir", "rb"]
        nowTime = SerialDataParser.read_serial_data_get_nowTime(ser)
        date_time_part, tz_offset = nowTime[1].rsplit('-', 1)
        tz_offset = '-' + tz_offset  # 添加负号，确保时区偏移正确
        dt = datetime.strptime(date_time_part, '%Y-%m-%d:%H:%M:%S')
        new_dt = dt + timedelta(minutes=2)
        st = int(nowTime[0]) + 2
        for ihub in ihubs:
            sendSwitchManualCmd = utils.light_commands.get_iHub4Set_switch_autoMod_mode_Cmd(ser, pid, ihub, st, rd, ed, times)
            if not sendSwitchManualCmd:
                self.write_log("发送指令失败，请检查串口", 'iHub4Set_switch_autoMod_mode.txt')
                return False
            self.write_log(f"四孔排插{ihub}位循环测试开始，开始时间为：{new_dt}", 'iHub4Set_switch_manual_mode.txt')



                




# if __name__ == "__main__":
#     # 获取当前路径并设置日志文件夹路径
#     current_path = os.getcwd()
#     now_time = datetime.now().strftime("%Y%m%d_%H%M%S")  # 当前时间
#     result_path = os.path.join(current_path, f"4孔排插测试日志{now_time}")
#     if not os.path.exists(result_path):
#         os.makedirs(result_path)
#     log_path = result_path
#     config_path = r"D:\meizhiguangdian\autoTest\MH_autotest\config\config.yaml"
#     with open(config_path, 'r', encoding='utf-8') as file:
#         config = yaml.safe_load(file)
#     # 初始化LightControl实例
#     powerStripControl = PowerStripControl(log_path)
#     pid = config['device']['pid']
#     ser_report = config['device']['ser']
#     ser = serial.Serial(ser_report, 115200, timeout=1)
#     # powerStripControl.iHub4Set_switch_manual_mode(ser, pid)
#     powerStripControl.iHub4Set_switch_autoMod_mode(ser, pid)