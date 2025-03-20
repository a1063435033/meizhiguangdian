import os
import unittest
from datetime import datetime
import serial
import yaml
from MH_light_control import LightControl
from power_strip_control import PowerStripControl
import time

class TestMHController(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # 获取当前路径并设置日志文件夹路径
        cls.current_path = os.getcwd()
        cls.now_time = datetime.now().strftime("%Y%m%d_%H%M%S")  # 当前时间
        cls.result_path = os.path.join(cls.current_path, f"MH控制器测试日志{cls.now_time}")
        if not os.path.exists(cls.result_path):
            os.makedirs(cls.result_path)
        cls.log_path = cls.result_path
        cls.config_path = r"D:\meizhiguangdian\autoTest\MH_autotest\config\config.yaml"
        with open(cls.config_path, 'r', encoding='utf-8') as file:
            cls.config = yaml.safe_load(file)
        cls.pid = cls.config['device']['pid']
        cls.ser_report = cls.config['device']['ser']
        cls.lightControl = LightControl(cls.log_path)
        cls.powerStripControl = PowerStripControl(cls.log_path)

    # def test_manual_light_adjust_mode(self):
    #     def perform_test(dimensions):
    #         for dim in dimensions:
    #             ser = serial.Serial(self.ser_report, 115200, timeout=1)
    #             manual_dim = self.lightControl.manual_light_adjust_mode(ser, self.pid, 1, dim)
    #             if manual_dim is not None:
    #                 ppfd_num = self.config['dimconfig'][f'dim{dim}']
    #                 difference = manual_dim - ppfd_num
    #                 status = "通过" if -self.config['margins']['margin'] <= difference <= self.config['margins']['margin'] else "失败"
    #                 log_msg = f"手动测试{status}: 设置{dim}%亮度，ppfd值为{manual_dim}, 差值为{difference}"
    #                 self.lightControl.write_log(log_msg, 'manual_light_adjust_mode_report.txt')
    #             else:
    #                 self.lightControl.write_log(f'manual_dim得值为：{manual_dim},请检查代码', 'test_report.txt')
    #             time.sleep(5)
        
    #     ascending_sequence = range(10, 110, 10)
    #     perform_test(ascending_sequence)
    #     descending_sequence = range(100, 9, -10)
    #     perform_test(descending_sequence)

    # def test_auto_light_adjust_mode(self):
    #     st = self.config['autoParams']['st']
    #     et = self.config['autoParams']['et']
    #     darkenT = self.config['autoParams']['darkenT']
    #     offT = self.config['autoParams']['offT']
    #     ser = serial.Serial(self.ser_report, 115200, timeout=1)
    #     testReport = {}
    #     for sunTime in range(1, 21): 
    #         if et >= 1430:
    #             st = 0
    #             et = st + 2 * sunTime + 1
    #         data = self.lightControl.auto_light_adjust_mode(ser, self.pid, st, et, 10, darkenT, offT, sunTime)
    #         st = et + 1
    #         et = st + 2 * (sunTime + 1) + 1
    #         testReport[f'日出日落第{sunTime}分钟时间'] = data[1]
    #         testReport[f'日出日落第{sunTime}分钟ppfd值'] = data[0]
    #         time.sleep(5)
    #     # 创建Excel文件的部分略去，因为通常我们不会在这个层级生成文件，除非是为了验证结果。

    # def test_ppfd_light_adjust_mod(self):
    #     st = self.config['ppfdParams']['st']
    #     et = self.config['ppfdParams']['et']
    #     dim_min = self.config['ppfdParams']['dim_min']
    #     dim_max = self.config['ppfdParams']['dim_max']
    #     ppfd = self.config['ppfdParams']['ppfd']
    #     darkenT = self.config['ppfdParams']['darkenT']
    #     offT = self.config['ppfdParams']['offT']
    #     sunTime = self.config['ppfdParams']['sunTime']
    #     ser = serial.Serial(self.ser_report, 115200, timeout=1)
    #     for i in range(1, 6):
    #         self.lightControl.ppfd_light_adjust_mode(ser, self.pid, st, et, dim_min, dim_max, ppfd, darkenT, offT, sunTime)
    #         ppfd -= 500
    #         st = et + 1
    #         et = st + 10
    #         time.sleep(5)

    def test_iHub4Set_light_and_awitch(self):
        ser = serial.Serial(self.ser_report, 115200, timeout=1)
        print('开始四孔排插手动开关测试')
        self.powerStripControl.iHub4Set_switch_manual_mode(ser, self.pid, 5)
        print('开始四孔排插自动循环开关测试')
        self.powerStripControl.iHub4Set_switch_autoMod_mode(ser, self.pid)
        ser.close()


if __name__ == "__main__":
    unittest.main()