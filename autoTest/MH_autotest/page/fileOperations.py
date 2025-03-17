import time,datetime


class FileOperations:
    def __init__(self,filepath):
        self.filepath = filepath

    #清空文件
    def vEmptyFile(self,strFileName="log.txt"):
        with open(str(strFileName), 'w+') as fl:
            strInfo = fl.read()
            if strInfo != '':
                fl.write('')
        return  True

    # 写文件并选择方式和是否打印写入信息
    def write_log(self, log_info="", logname="log.txt", writeway='a+',time_mark=True):
        try:
            with open(self.filepath+"\\"+logname, writeway) as fl:
                if time_mark:
                    fl.write("[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "]" + (str(log_info) + "\n").replace("\r", ""))
                else:
                    fl.write(str(log_info))
                print(str(log_info).strip())
            return True
        except:
            return False