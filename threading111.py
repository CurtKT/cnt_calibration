import sys
import serial
import serial.tools.list_ports
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QMainWindow, QApplication
from untitled import Ui_MainWindow
import binascii
import threading
import time
import re


class Pyqt5_Serial(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.stop_flag = 1  # 时间停止标识符
        self.com_port_flag = 1  # 线程关闭标识符
        self.isstar = False  # 是否测量标识符
        self.setupUi(self)
        self.setWindowTitle("EasyCounter")
        self.setWindowIcon(QtGui.QIcon("./icon/图标"))
        self.widget.setHidden(True)
        self.init()
        self.read_text()
        self.ser = serial.Serial()
        t_3 = threading.Thread(target=self.port_check)  # 串口检测设置为自动检测！
        t_3.start()

    def read_text(self):
        """读取文件中的指令和配置信息"""
        # 读取指令
        with open("./data/order.txt") as f:
            text = f.read()
            text_split = text.split()
        self.text_join = " ".join(text_split)
        self.ret = re.sub(r"<[^>]*>", "", self.text_join)
        self.text_init = re.match(r".*//初始化指令(.*)//初始化指令", self.ret).group(1)
        self.text_time = re.match(r".*//设置时间(.*)//设置时间", self.ret).group(1)
        self.text_voltage = re.match(r".*//设置高压(.*)//设置高压", self.ret).group(1)
        self.text_threshold = re.match(r".*//设置阈值(.*)//设置阈值", self.ret).group(1)

        # 读取配置
        with open("./data/calibration.txt") as f:
            test = f.read()
            self.hv_k = re.match(r"[\S\s]*HV-K<(.*?)>", test).group(1)
            self.hv_b = re.match(r"[\S\s]*HV-b<(.*?)>", test).group(1)
            self.th_k = re.match(r"[\S\s]*TH-K<(.*?)>", test).group(1)
            self.th_b = re.match(r"[\S\s]*TH-b<(.*?)>", test).group(1)

        with open("./bin/set_message.bat") as f:
            set_text = f.read()
            if len(set_text) == 0:
                self.spinBox.setValue(100)
                self.spinBox_2.setValue(800)
                self.spinBox_3.setValue(850)
            else:
                print(set_text)
                test = re.match(r".*//设置时间：(.*)//设置时间", set_text).group(1)
                test_2 = re.match(r".*//设置高压：(.*)//设置高压", set_text).group(1)
                test_3 = re.match(r".*//设置阈值：(.*)//设置阈值", set_text).group(1)
                self.spinBox.setValue(int(test))
                self.spinBox_2.setValue(int(test_2))
                self.spinBox_3.setValue(int(test_3))

        with open("./bin/max_voltage.bat") as f:
            max_voltage = f.read()
            self.lineEdit_2.setText(max_voltage)
            self.spinBox_3.setMaximum(int(self.lineEdit_2.text()))

    def closeEvent(self, QCloseEvent):
        """关闭时关闭多线程"""
        self.reset()
        self.port_close()
        self.com_port_flag = 0
        self.isstar = False
        with open("./bin/set_message.bat", "w") as f:
            f.write("//设置时间：%d//设置时间  //设置高压：%d//设置高压  //设置阈值：%d//设置阈值"
                    % (self.spinBox.value(), self.spinBox_2.value(), self.spinBox_3.value()))

    def resizeEvent(self, evt):
        """窗口变化重整控件"""
        self.refactor_x_y(self.lcdNumber, 0, 30)
        self.refactor_x_y(self.lcdNumber_2, 681, 220)
        self.refactor_x_y(self.spinBox, 680, 30)
        self.refactor_x_y(self.spinBox_2, 680, 420)
        self.refactor_x_y(self.spinBox_3, 680, 610)
        self.refactor_x_y(self.checkBox, 690, 620)
        self.refactor_x_y(self.label_2, 690, 40)
        self.refactor_x_y(self.label_4, 690, 440)
        self.refactor_x_y(self.label, 10, 40)
        self.refactor_x_y(self.label_3, 690, 240)
        self.refactor_x_y(self.label_5, 0, 430)
        self.refactor_x_y(self.textBrowser, 0, 460)
        self.refactor_size(self.lcdNumber, 681, 391)
        self.refactor_size(self.lcdNumber_2, 307, 201)
        self.refactor_size(self.spinBox, 411, 191)
        self.refactor_size(self.spinBox_2, 411, 191)
        self.refactor_size(self.spinBox_3, 411, 191)
        self.refactor_size(self.checkBox, 141, 21)
        self.refactor_size(self.label_2, 181, 31)
        self.refactor_size(self.label_4, 141, 21)
        self.refactor_size(self.label, 61, 31)
        self.refactor_size(self.label_3, 131, 31)
        self.refactor_size(self.label_5, 91, 31)
        self.refactor_size(self.textBrowser, 681, 341)
        self.refactor_x_y(self.pushButton_5, 990, 30)
        self.refactor_x_y(self.pushButton_6, 990, 124)
        self.refactor_x_y(self.pushButton_7, 990, 420)
        self.refactor_x_y(self.pushButton_8, 990, 516)
        self.refactor_x_y(self.pushButton_9, 990, 610)
        self.refactor_x_y(self.pushButton_10, 990, 705)
        self.refactor_size(self.pushButton_5, 111, 91)
        self.refactor_size(self.pushButton_6, 111, 91)
        self.refactor_size(self.pushButton_7, 111, 91)
        self.refactor_size(self.pushButton_8, 111, 91)
        self.refactor_size(self.pushButton_9, 111, 91)
        self.refactor_size(self.pushButton_10, 111, 91)
        self.refactor_x_y(self.widget, 420, 280)
        self.refactor_x_y(self.label_6, 0, 401)
        self.refactor_size(self.label_6, 681, 20)

    def refactor_x_y(self, widget, x, y):
        """重构widget位置"""
        widget.move(x/1090*self.width(), y/802*self.height())

    def refactor_size(self, widget, width, height):
        """重构widget大小"""
        widget.resize(self.width()*width/1090, self.height()*height/802)

    def init(self):
        """"连接信号与槽"""
        # 打开串口按钮
        self.pushButton.clicked.connect(self.port_open)
        # 开始测量按钮
        self.pushButton_2.clicked.connect(self.star)
        # 暂停测量按钮
        self.pushButton_3.clicked.connect(self.stop)
        # 复位按钮
        self.pushButton_4.clicked.connect(self.reset)
        # 设置测量时间
        self.spinBox.valueChanged.connect(self.set_time)
        # 设置测量阈值
        self.spinBox_2.valueChanged.connect(self.set_threshold)
        # 测量高压勾选
        self.checkBox.stateChanged.connect(self.set_voltage)
        # 帮助文档按钮
        self.pushButton_15.clicked.connect(self.help)
        # 设定高压上限
        self.pushButton_11.clicked.connect(lambda: self.widget.setHidden(False))
        self.pushButton_13.clicked.connect(self.ok)
        self.pushButton_14.clicked.connect(self.cancel)
        self.pushButton_12.clicked.connect(self.check_pwd)
        # 按钮步长设置
        self.pushButton_5.clicked.connect(lambda: self.spinBox.setValue(self.spinBox.value() + 10))
        self.pushButton_6.clicked.connect(lambda: self.spinBox.setValue(self.spinBox.value() - 10))
        self.pushButton_7.clicked.connect(lambda: self.spinBox_2.setValue(self.spinBox_2.value() + 1))
        self.pushButton_8.clicked.connect(lambda: self.spinBox_2.setValue(self.spinBox_2.value() - 1))
        self.pushButton_9.clicked.connect(lambda: self.spinBox_3.setValue(self.spinBox_3.value() + 10))
        self.pushButton_10.clicked.connect(lambda: self.spinBox_3.setValue(self.spinBox_3.value() - 10))
        self.pushButton_5.setAutoRepeat(True)
        self.pushButton_6.setAutoRepeat(True)
        self.pushButton_7.setAutoRepeat(True)
        self.pushButton_8.setAutoRepeat(True)
        self.pushButton_9.setAutoRepeat(True)
        self.pushButton_10.setAutoRepeat(True)
        # 添加图标
        self.pushButton_2.setIcon(QtGui.QIcon("./icon/开始"))
        self.pushButton_3.setIcon(QtGui.QIcon("./icon/暂停"))
        self.pushButton_4.setIcon(QtGui.QIcon("./icon/复位"))
        size = QtCore.QSize(80, 80)
        self.pushButton_5.setIcon(QtGui.QIcon("./icon/上"))
        self.pushButton_5.setIconSize(size)
        self.pushButton_7.setIcon(QtGui.QIcon("./icon/上"))
        self.pushButton_7.setIconSize(size)
        self.pushButton_9.setIcon(QtGui.QIcon("./icon/上"))
        self.pushButton_9.setIconSize(size)
        self.pushButton_6.setIcon(QtGui.QIcon("./icon/下"))
        self.pushButton_6.setIconSize(size)
        self.pushButton_8.setIcon(QtGui.QIcon("./icon/下"))
        self.pushButton_8.setIconSize(size)
        self.pushButton_10.setIcon(QtGui.QIcon("./icon/下"))
        self.pushButton_10.setIconSize(size)

    def port_check(self):
        """ 串口检测与连接"""
        while True:
            if self.com_port_flag == 0:  # 线程关闭标识符
                break
            # 检测所有存在的串口，将信息存储在字典中
            port_name = None
            self.Com_Dict = {}
            port_list = list(serial.tools.list_ports.comports())
            for port in port_list:
                self.Com_Dict["%s" % port[0]] = "%s" % port[1]
            for test in self.Com_Dict:
                try:
                    port_name = re.match(".*CP210.*", self.Com_Dict[test]).group()
                    self.com_port = test
                except:
                    pass

            if self.ser.is_open:
                self.pushButton.setEnabled(False)
            else:
                if port_name:
                    self.pushButton.setEnabled(True)
                else:
                    self.pushButton.setEnabled(False)
            time.sleep(0.3)
        print("T3")

    def twinkle(self):
        """运行闪烁"""
        while True:
            if not self.isstar:
                self.label_6.setStyleSheet("background-color: rgb(255, 0, 0);")
                break
            self.label_6.setStyleSheet("background-color: rgb(0, 255, 0);")
            self.label_6.setHidden(True)
            time.sleep(0.5)
            self.label_6.setHidden(False)
            time.sleep(0.5)
        print("T4")

    def port_open(self):
        """定标器连接"""
        self.ser.port = self.com_port
        self.ser.baudrate = 256000
        self.ser.bytesize = 8
        self.ser.stopbits = 1
        self.ser.parity = "N"
        self.com_port_flag = 0
        try:
            self.ser.open()
        except:
            QMessageBox.critical(self, "Port Error", "此串口不能被打开！")
            return None
        if self.ser.isOpen():
            self.data_receive()
            self.pushButton.setEnabled(False)
            self.pushButton_2.setEnabled(True)
            self.checkBox.setEnabled(True)
            self.spinBox.setEnabled(True)
            self.spinBox_2.setEnabled(True)
            self.spinBox_3.setEnabled(True)
            self.pushButton_4.setEnabled(True)
            self.pushButton_5.setEnabled(True)
            self.pushButton_6.setEnabled(True)
            self.pushButton_7.setEnabled(True)
            self.pushButton_8.setEnabled(True)
            self.pushButton_9.setEnabled(True)
            self.pushButton_10.setEnabled(True)
            self.textBrowser.append("定标器状态（已连接）")
            self.input_s = self.text_init  # 发送初始化指令
            self.send()
            self.set_time()  # 设置测量时间
            self.set_threshold()  # 设置测量阈
            self.get_num()  # 接收计数值
            t_5 = threading.Thread(target=self.overtime)  # 检测串口连接状态
            t_5.start()

    def port_close(self):
        """关闭串口"""
        try:
            self.ser.close()
        except:
            pass

    def star(self):
        """开始测量"""
        self.isstar = True
        self.input_s = "12 34 0f 00 06 24 00 00 00 ab cd"  # 开始指令
        self.send()
        self.textBrowser.append("开始测量")
        self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(True)
        self.checkBox.setEnabled(False)
        self.spinBox.setEnabled(False)
        self.spinBox_2.setEnabled(False)
        # self.spinBox_3.setEnabled(False)
        t_4 = threading.Thread(target=self.twinkle)
        t_4.start()

    def stop(self):
        """停止测量"""
        self.isstar = False
        self.label_6.setStyleSheet("background-color: rgb(255, 0, 0);")
        self.label_6.setHidden(False)
        self.input_s = "12 34 0f 00 06 20 00 00 00 ab cd"  # 暂停指令
        self.send()
        self.textBrowser.append("暂停测量")
        self.pushButton_2.setEnabled(True)
        self.pushButton_3.setEnabled(False)
        self.pushButton_4.setEnabled(True)
        self.spinBox.setEnabled(True)
        self.spinBox_2.setEnabled(True)
        # self.spinBox_3.setEnabled(True)

    def reset(self):
        """复位"""
        self.stop()
        time.sleep(0.2)
        self.input_s = "12 34 0f 00 06 28 00 00 00 ab cd"  # reset指令
        self.send()
        self.textBrowser.append("复位成功")
        self.pushButton_2.setEnabled(True)
        self.pushButton_3.setEnabled(False)
        self.spinBox_2.setEnabled(True)
        self.spinBox.setEnabled(True)
        self.checkBox.setEnabled(True)
        # 复位还原显示界面
        self.lcdNumber.display(0)
        self.lcdNumber_2.display(0)
        # 复位后发送已设置参数
        self.stop_flag = 1
        self.set_time()

    def send(self):
        """单次发送数据"""
        try:
            msg = bytes.fromhex(self.input_s)
            self.ser.write(msg)
        except:
            pass

    def circul_send(self):
        """循环发送数据"""
        self.textBrowser.append("通信成功！")
        self.textBrowser.append("正在接收中...")
        while self.ser.isOpen():
            try:
                msg = bytes.fromhex("12 34 0f 00 06 38 00 00 01 ab cd")
                self.ser.write(msg)
            except:
                pass
            time.sleep(0.1)
        print("T2")

    def get_num(self):
        """循环接收信息"""
        t_2 = threading.Thread(target=self.circul_send)
        t_2.start()

    def receive(self):
        """接收并解码数据"""
        while True:
            if self.ser.isOpen():
                time.sleep(0.05)
                try:
                    if self.ser.in_waiting:
                        # 接收16进制数据并转化为字符串
                        self.msg = str(binascii.b2a_hex(self.ser.read(self.ser.in_waiting)))[2:-1]
                        # 字符串切片并转化为10进制时间
                        msg_time = self.msg[16:28]
                        time_ns = int(msg_time, 16)*25  # time_ns单位纳秒
                        time_s = int(time_ns/10**9)  # 纳秒转化为秒
                        self.lcdNumber_2.display(time_s)
                        # 字符串切片并转化为10进制粒子数
                        msg_num = self.msg[40:48]
                        num = int(msg_num, 16)
                        self.lcdNumber.display(num)
                        if self.lcdNumber_2.value() == self.spinBox.value() and self.stop_flag == 1:
                            self.isstar = False
                            self.pushButton_2.setEnabled(False)
                            self.pushButton_3.setEnabled(False)
                            self.stop_flag = 0
                            self.textBrowser.append("测量成功！")
                            self.textBrowser.append("")
                            self.textBrowser.append(time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time())))
                            self.textBrowser.append("测量时间%d秒" % self.spinBox.value())
                            self.textBrowser.append("测量阈值%d毫伏" % self.spinBox_2.value())
                            if self.checkBox.isChecked():
                                self.textBrowser.append("设定高压%d伏" % self.spinBox_3.value())
                            else:
                                self.textBrowser.append("未设定高压")
                            self.textBrowser.append("计数值为%d" % self.lcdNumber.value())
                            self.textBrowser.append("")
                            with open("./data/data.txt", "a") as f:
                                f.write("\r\n")
                                f.write(time.strftime('%Y-%m-%d  %H:%M:%S\r\n', time.localtime(time.time())))
                                f.write("    测量时间%d秒\r\n" % self.spinBox.value())
                                f.write("    测量阈值%d毫伏\r\n" % self.spinBox_2.value())
                                if self.checkBox.isChecked():
                                    f.write("    设定高压%d伏\r\n" % self.spinBox_3.value())
                                else:
                                    f.write("    未设定高压\r\n")
                                f.write("    计数值为%d\r\n" % self.lcdNumber.value())
                                f.write("\r\n")
                except Exception as result:
                    # 状态栏显示异常提示
                    self.textBrowser.append("错误为%s" % result)
                if self.isstar:
                    self.textBrowser.moveCursor(self.textBrowser.textCursor().End)
            else:
                break

        print("T")
        # self.isstar = False
        # self.textBrowser.append("串口连接超时")

    def overtime(self):
        time.sleep(0.5)
        while True:
            if self.isstar:
                over_flag = self.msg
                time.sleep(0.5)
                if over_flag == self.msg:
                    self.isstar = False
                    self.textBrowser.append("串口连接超时")
            else:
                print("..........")
                break
        print("T5")

    def data_receive(self):
        """接收数据多线程"""
        t = threading.Thread(target=self.receive)
        t.start()

    def set_time(self):
        """设置测量时间"""
        hex_time = hex(self.spinBox.value()*10)  # 设置时间转化为16进制
        str_time = str(hex_time)[2:]
        x_index = self.text_time.find("X")
        x_r_index = self.text_time.rfind("X")
        if len(str_time) == 1:
            # send_time = "12 34 0f 00 06 14 00 00 0" + str_time + " ab cd"
            send_time = self.text_time[1:x_index] + "00 0" + str_time + self.text_time[x_r_index+1:-1]
        elif len(str_time) == 2:
            # send_time = "12 34 0f 00 06 14 00 00 " + str_time + " ab cd"
            send_time = self.text_time[1:x_index] + "00 " + str_time + self.text_time[x_r_index+1:-1]
        elif len(str_time) == 3:
            # send_time = "12 34 0f 00 06 14 00 0" + str_time[0:1] + " " + str_time[1:] + " ab cd"
            send_time = self.text_time[1:x_index] + "0" + str_time[0:1] + " " + str_time[1:] \
                        + self.text_time[x_r_index+1:-1]
        elif len(str_time) == 4:
            # send_time = "12 34 0f 00 06 14 00 " + str_time[0:2] + " " + str_time[2:] + " ab cd"
            send_time = self.text_time[1:x_index] + str_time[0:2] + " " +\
                        str_time[2:] + self.text_time[x_r_index+1:-1]
        self.input_s = send_time  # 发送指令
        print("设置时间>>>>>", send_time)
        self.send()
        self.textBrowser.append("测量时间：%d秒" % (self.spinBox.value()))

    def set_voltage(self):
        """设置高压"""
        if self.checkBox.isChecked():
            x_index = self.text_voltage.find("X")
            x_r_index = self.text_voltage.rfind("X")
            self.spinBox_3.setStyleSheet("background-color: red;"
                                         "font: 75 100pt 'Adobe Arabic';"
                                         "color: rgb(255, 255, 0);")
            # hex_voltage = hex(int(self.spinBox_3.value()*43.7))  # 设置电压转化为16进制
            hex_voltage = hex(int(self.spinBox_3.value() * float(self.hv_k) + float(self.hv_b)))  # 设置电压转化为16进制
            str_voltage = str(hex_voltage)[2:]
            if len(str_voltage) == 1:
                # send_voltage = "12 34 0f 00 6f 00 00 00 0" + str_voltage + " ab cd"
                send_voltage = self.text_voltage[1:x_index] + "00 0" + str_voltage + self.text_voltage[x_r_index+1:-1]
            elif len(str_voltage) == 2:
                # send_voltage = "12 34 0f 00 6f 00 00 00 " + str_voltage + " ab cd"
                send_voltage = self.text_voltage[1:x_index] + "00 " + str_voltage + self.text_voltage[x_r_index+1:-1]
            elif len(str_voltage) == 3:
                # send_voltage = "12 34 0f 00 6f 00 00 0" + str_voltage[0:1] + " " + str_voltage[1:] + " ab cd"
                send_voltage = self.text_voltage[1:x_index] + "0" + str_voltage[0:1] + " " + str_voltage[1:] \
                                + self.text_voltage[x_r_index+1:-1]
            elif len(str_voltage) == 4:
                # send_voltage = "12 34 0f 00 6f 00 00 " + str_voltage[0:2] + " " + str_voltage[2:] + " ab cd"
                send_voltage = self.text_voltage[1:x_index] + str_voltage[0:2] + " " + str_voltage[2:] +\
                               self.text_voltage[x_r_index+1:-1]
            self.input_s = send_voltage  # 发送指令
            print("设置高压>>>>>", send_voltage)
            self.send()
            self.textBrowser.append("设置高压：%d伏" % (self.spinBox_3.value()))
            self.spinBox_3.setEnabled(False)
            self.pushButton_7.setEnabled(False)
            self.pushButton_8.setEnabled(False)
        else:
            self.spinBox_3.setStyleSheet("background-color: rgb(0, 0, 127);"
                                         "font: 75 100pt 'Adobe Arabic';"
                                         "color: rgb(255, 255, 0);")
            self.textBrowser.append("未设置高压")
            self.spinBox_3.setEnabled(True)
            self.pushButton_7.setEnabled(True)
            self.pushButton_8.setEnabled(True)

    def set_threshold(self):
        """设置阈值"""
        x_index = self.text_threshold.find("X")
        x_r_index = self.text_threshold.rfind("X")
        # hex_threshold = hex(int(self.spinBox_2.value() * float(1)))  # 设置阈值转化为16进制
        hex_threshold = hex(int(self.spinBox_2.value() * float(self.th_k) + float(self.th_b)))  # 设置阈值转化为16进制
        str_threshold = str(hex_threshold)[2:]
        if len(str_threshold) == 1:
            # send_threshold = "12 34 0f 00 04 01 00 00 01 ab cd 12 34 0f 00 11 06 00 00 0" \
            #                  + str_threshold \
            #                  + " ab cd 12 34 0f 00 04 01 00 00 00 ab cd"
            send_threshold = self.text_threshold[1:x_index] + "00 0" + str_threshold + self.text_threshold[x_r_index+1:-1]
        elif len(str_threshold) == 2:
            # send_threshold = "12 34 0f 00 04 01 00 00 01 ab cd 12 34 0f 00 11 06 00 00 "\
            #                  + str_threshold \
            #                  + " ab cd 12 34 0f 00 04 01 00 00 00 ab cd"
            send_threshold = self.text_threshold[1:x_index] + "00 " + str_threshold + self.text_threshold[x_r_index+1:-1]
        elif len(str_threshold) == 3:
            # send_threshold = "12 34 0f 00 04 01 00 00 01 ab cd 12 34 0f 00 11 06 00 0" \
            #                  + str_threshold[0:1] + " " + str_threshold[1:] \
            #                  + " ab cd 12 34 0f 00 04 01 00 00 00 ab cd"
            send_threshold = self.text_threshold[1:x_index] + "0" + str_threshold[0:1] + " " + str_threshold[1:] \
                             + self.text_threshold[x_r_index+1:-1]
        elif len(str_threshold) == 4:
            # send_threshold = "12 34 0f 00 04 01 00 00 01 ab cd 12 34 0f 00 11 06 00 "\
            #                  + str_threshold[0:2] + " " + str_threshold[2:] \
            #                  + " ab cd 12 34 0f 00 04 01 00 00 00 ab cd"
            send_threshold = self.text_threshold[1:x_index] + str_threshold[0:2] + " " + str_threshold[2:] \
                             + self.text_threshold[x_r_index+1:-1]
        self.input_s = send_threshold  # 发送指令
        print("设置阈值>>>>>", send_threshold)
        self.send()
        self.textBrowser.append("设置阈值：%dmV" % (self.spinBox_2.value()))

    def check_pwd(self):
        """验证密码"""
        with open("./data/admin.txt") as f:
            pwd = f.read()
        if self.lineEdit.text() == pwd:
            self.lineEdit_2.setEnabled(True)
            self.lineEdit.setEnabled(False)
            self.pushButton_12.setEnabled(False)
            self.label_9.setText("密码正确！")
        else:
            self.label_9.setText("密码错误请重新输入！")
        pass

    def ok(self):
        """确认按钮"""
        self.cancel()
        with open("./bin/max_voltage.bat", "w") as f:
            f.write(self.lineEdit_2.text())
        self.spinBox_3.setMaximum(int(self.lineEdit_2.text()))

    def cancel(self):
        """取消按钮"""
        self.label_9.setText("")
        self.lineEdit.setText("")
        self.widget.setHidden(True)
        self.lineEdit.setEnabled(True)
        self.pushButton_12.setEnabled(True)
        self.lineEdit_2.setEnabled(False)

    def help(self):
        """提示帮助信息"""
        with open("./data/help.txt") as f:
            text = f.read()
        self.textBrowser.append(text)
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myshow = Pyqt5_Serial()
    # 主窗口退出机制
    myshow.show()
    sys.exit(app.exec_())