import serial
from datetime import datetime, timedelta
import struct
import pandas as pd
import threading
import keyboard
import os
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class DeviceInfo:
    """Data class to store device information"""
    timestamp: str
    address: int
    func_code: int
    registers: Tuple[int, ...]
    device_type: str
    device_id: List[str]
    hardware_version: str
    firmware_version: str
    temperature: float
    humidity: float
    light_sensor: int
    is_daytime: bool
    day_ppfd_threshold: int
    night_ppfd_threshold: int
    sampling_stable_time: int
    interval_hold_count: int

class SerialReader:
    """Class to handle serial communication and data parsing"""
    
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 0.2):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.running = False
        
    def __enter__(self):
        self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.ser and self.ser.is_open:
            self.ser.close()
            
    @staticmethod
    def calculate_crc16(data: bytes) -> bytes:
        """Calculate CRC16 for the given data"""
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
    
    def parse_response(self, response_bytes: bytes, timestamp: str) -> Optional[DeviceInfo]:
        """Parse the response bytes into a DeviceInfo object"""
        try:
            addr, func_code, byte_count = struct.unpack('>BBB', response_bytes[:3])
            expected_length = 3 + byte_count + 2
            
            if len(response_bytes) != expected_length:
                logger.error(f"Data length mismatch: expected {expected_length} bytes, got {len(response_bytes)} bytes")
                return None
                
            registers = struct.unpack(f'>{byte_count // 2}H', response_bytes[3:-2])
            
            return DeviceInfo(
                timestamp=timestamp,
                address=addr,
                func_code=func_code,
                registers=registers,
                device_type=f"{registers[1]:04X}",
                device_id=[f"{reg:04X}" for reg in registers[2:6]],
                hardware_version=f"{registers[6] >> 8}.{registers[6] & 0xFF}",
                firmware_version=f"{registers[7] >> 8}.{registers[7] & 0xFF}",
                temperature=registers[10] / 10,
                humidity=registers[11] / 10,
                light_sensor=registers[12],
                is_daytime=bool(registers[15]),
                day_ppfd_threshold=registers[16],
                night_ppfd_threshold=registers[17],
                sampling_stable_time=registers[18],
                interval_hold_count=registers[19]
            )
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return None

    def read_data(self, commands: bytes) -> List[bytes]:
        """Read data from serial port"""
        self.ser.write(commands)
        data = bytearray()
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < 2:
            if self.ser.in_waiting > 0:
                chunk = self.ser.read(self.ser.in_waiting or 1)
                if chunk:
                    data.extend(chunk)
                    
        if not data:
            return []
            
        results = []
        start_index = 0
        
        # 根据不同的命令使用不同的匹配模式
        if commands == bytes.fromhex('0A 03 00 00 00 19 85 7B'):
            pattern = bytes.fromhex("0A0332000A")
            data_length = 49
        else:  # 02 03 00 00 00 16 C4 37
            pattern = bytes.fromhex("02032c0002")
            data_length = 55
            
        while True:
            start_index = data.find(pattern, start_index)
            if start_index == -1:
                break
                
            if start_index + data_length <= len(data):
                extracted_part = data[start_index:start_index + data_length]
                received_crc = extracted_part[-2:]
                computed_crc = self.calculate_crc16(extracted_part[:-2])
                
                if received_crc == computed_crc:
                    results.append(extracted_part)
                start_index += data_length
            else:
                break
                
        return results

class DataCollector:
    """Class to handle data collection and Excel file generation"""
    
    def __init__(self, headers: List[str], excel_file_path: str):
        self.headers = headers
        self.excel_file_path = excel_file_path
        self.sheets_data: Dict[str, pd.DataFrame] = {}
        self.data_list: List[Dict] = []
        
    def process_device_info(self, device_info: DeviceInfo) -> Dict:
        """Convert DeviceInfo to dictionary format"""
        return {
            '时间': device_info.timestamp,
            '设备地址': device_info.address,
            '功能码': device_info.func_code,
            '寄存器数据': device_info.registers,
            '设备类型代码': device_info.device_type,
            '设备ID': device_info.device_id,
            '硬件版本': device_info.hardware_version,
            '固件版本': device_info.firmware_version,
            '温度': device_info.temperature,
            '湿度': device_info.humidity,
            '光敏传感器': device_info.light_sensor,
            '是否白天': device_info.is_daytime,
            'RW 白天PPFD阀值': device_info.day_ppfd_threshold,
            'RW 夜晚PPFD阀值': device_info.night_ppfd_threshold,
            'RW 采样稳定时间': device_info.sampling_stable_time,
            '区间保持计数': device_info.interval_hold_count
        }
        
    def save_to_excel(self):
        """Save collected data to Excel file"""
        for device_info in self.data_list:
            if device_info is None:
                continue
                
            row_df = pd.DataFrame([device_info], columns=self.headers)
            device_address = device_info['设备ID'][3]
            
            if device_address not in self.sheets_data:
                self.sheets_data[device_address] = pd.DataFrame(columns=self.headers)
                
            if not row_df.empty:
                self.sheets_data[device_address] = pd.concat(
                    [self.sheets_data[device_address], row_df],
                    ignore_index=True,
                    join='inner'
                )
                
        with pd.ExcelWriter(self.excel_file_path, engine='openpyxl') as writer:
            for sheet_name, df in self.sheets_data.items():
                df.to_excel(writer, sheet_name=str(sheet_name), index=False)
                
        return self.excel_file_path

def run_auto_test(headers: List[str], excel_file_path: str, serial_port: str, end_test_time: int) -> str:
    """Main function to run the auto test"""
    start_time = datetime.now()
    logger.info(f"开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    end_time = start_time + timedelta(minutes=end_test_time)
    
    # 定义两个设备的命令
    commands = [
        bytes.fromhex('0A 03 00 00 00 19 85 7B'),  # 第一个设备
        bytes.fromhex('02 03 00 00 00 16 C4 37')   # 第二个设备
    ]
    
    collector = DataCollector(headers, excel_file_path)
    reader = SerialReader(serial_port)
    
    def check_key():
        while reader.running:
            if keyboard.is_pressed('esc'):
                reader.running = False
                logger.info("准备退出...")
                break
                
    listener_thread = threading.Thread(target=check_key, daemon=True)
    listener_thread.start()
    logger.info("按下 'Esc' 键以提前退出循环...")
    
    with reader as reader:
        reader.running = True
        device_count = 1
        
        while reader.running and datetime.now() < end_time:
            # 依次读取两个设备的数据
            for cmd in commands:
                results = reader.read_data(cmd)
                
                for result in results:
                    try:
                        device_info = reader.parse_response(result, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        if device_info:
                            collector.data_list.append(collector.process_device_info(device_info))
                            logger.info(f'设备{device_count}，温度值：{device_info.temperature}，湿度值：{device_info.humidity}')
                            device_count += 1
                    except ValueError as e:
                        logger.error(f"Error processing device info: {e}")
                        
                logger.info('-' * 100)
            
    return collector.save_to_excel()

def demo(headers: List[str], serial_port: str, output_file_path: str):
    """Demo function to run the test and process results"""
    file_path = run_auto_test(headers, 'file3.xlsx', serial_port, 100)
    logger.info(f"Generated file: {file_path}")
    
    file_path = reExcel.process_excel(file_path)
    logger.info(f"Processed file: {file_path}")
    
    xls, sheets = outputFeil.read_excel_sheets(file_path)
    if not sheets:
        return
        
    processed_sheets = {}
    for sheet_name in sheets:
        logger.info(f"正在处理Sheet: {sheet_name}")
        df = pd.read_excel(xls, sheet_name=sheet_name)
        processed_sheets[sheet_name] = outputFeil.process_sheet(df)
        
    outputFeil.write_processed_sheets_to_excel(processed_sheets, output_file_path)

if __name__ == "__main__":
    headers = [
        '时间', '设备地址', '功能码', '寄存器数据', '设备类型代码', '设备ID', '硬件版本', '固件版本',
        '温度', '湿度', '光敏传感器', '是否白天', 'RW 白天PPFD阀值', 'RW 夜晚PPFD阀值',
        'RW 采样稳定时间', '区间保持计数'
    ]
    demo(headers, 'COM3', '湿度测试数据表.xlsx') 