import sys
from PyQt5.QtWidgets import QDesktopWidget, QPushButton, QHBoxLayout, QGridLayout, \
    QApplication, QWidget, QLabel, QVBoxLayout, QDateTimeEdit, QLineEdit, QMessageBox
from PyQt5.QtCore import QDateTime, QEventLoop, QTimer

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.common.keys import Keys

import pyperclip
from Check_Chromedriver import Check_Chromedriver
import os, sys
from datetime import datetime, timedelta
import urllib.request
import urllib.error
import time


class MyApp(QWidget):

    def __init__(self):
        super().__init__()

        Check_Chromedriver.main()

        self.initUI()

    def initUI(self):
        m_layout = QVBoxLayout()
        self.setLayout(m_layout)

        self.input = QWidget(self)
        m_layout.addWidget(self.input)

        i_layout = QGridLayout()
        self.input.setLayout(i_layout)

        # url
        self.target_url = QLineEdit(self.input)
        i_layout.addWidget(QLabel('Target Post URL'), 0, 0)
        i_layout.addWidget(self.target_url, 0, 1)

        # comment_id
        self.target_comment_id = QLineEdit(self.input)
        i_layout.addWidget(QLabel('Target Comment id'), 1, 0)
        i_layout.addWidget(self.target_comment_id, 1, 1)

        # comment
        self.context = QLineEdit(self.input)
        i_layout.addWidget(QLabel('Context'), 2, 0)
        i_layout.addWidget(self.context, 2, 1)

        # date & time
        i_layout.addWidget(QLabel('Date/Time '), 3, 0)
        self.time = QDateTimeEdit(self.input)

        min_time = QDateTime.currentDateTime().addSecs(60)
        self.time.setDateTime(min_time)
        self.time.setDateTimeRange(min_time, QDateTime(2100, 1, 1, 00, 00, 00, 0))
        self.time.setDisplayFormat('yyyy.MM.dd hh:mm:ss.zzz')
        i_layout.addWidget(self.time, 3, 1)

        self.login_id = QLineEdit(self.input)
        i_layout.addWidget(QLabel('ID'), 4, 0)
        i_layout.addWidget(self.login_id, 4, 1)

        # pwd
        self.login_pwd = QLineEdit(self.input)
        self.login_pwd.setEchoMode(3)  # pwd echo
        i_layout.addWidget(QLabel('PWD'), 5, 0)
        i_layout.addWidget(self.login_pwd, 5, 1)

        self.submit = QWidget(self)
        s_layout = QHBoxLayout()
        self.submit.setLayout(s_layout)

        okButton = QPushButton('Submit')
        s_layout.addWidget(okButton)

        okButton.clicked.connect(self.regist_comment)
        m_layout.addWidget(self.submit)

        self.setWindowTitle('Naver Cafe Nest Comment Generator')

        self.resize(400, 200)

        self.center()
        self.show()

    def regist_comment(self):
        url = self.target_url.text()
        c_id = self.target_comment_id.text()
        context = self.context.text()

        u_id = self.login_id.text()
        u_pwd = self.login_pwd.text()

        _date = self.time.date().toPyDate()
        _time = self.time.time().toPyTime()

        ctime = datetime.now()
        if ctime.date() != _date:
            self.wrongDate()
        elif url == "" or c_id == "" or context == "" or u_id == "" or u_pwd == "":
            self.wrongInput()
        else:
            self._regist(url, c_id, context, u_id, u_pwd, _date, _time)

    def wait(self, msec=1000):
        loop = QEventLoop()
        QTimer.singleShot(msec, loop.quit)  # msec
        loop.exec_()

    def _regist(self, url, c_id, context, u_id, u_pwd, _date, _time):
        # print(url)
        # print(c_id)
        # print(context)
        # print(u_id)
        # print(u_pwd)
        # print(_date)
        # print(_time)

        def copy_paste(driver, context):
            pyperclip.copy(context)
            ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            self.wait(500)

        driver = webdriver.Chrome('./chromedriver/chromedriver.exe')
        driver.implicitly_wait(10)
        driver.get(url)

        self.wait(2000)
        driver.find_element_by_xpath('//*[@id="id"]').click()
        copy_paste(driver, u_id)
        driver.find_element_by_xpath('//*[@id="pw"]').click()
        copy_paste(driver, u_pwd)
        driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()

        driver.switch_to.frame('cafe_main')

        comment_list = driver.find_element_by_xpath(f"//ul[@class='comment_list']")
        reply = comment_list.find_element_by_xpath(f"//li[@id='{c_id}']")
        reply_btn = reply.find_element_by_xpath(
            f"//li[@id='{c_id}']/div[@class='comment_area']/div[@class='comment_box']/div[@class='comment_info_box']/a")
        reply_btn.click()

        reply_area = comment_list.find_element_by_xpath("//li[contains(@class,'CommentItem--reply')]")
        reply_area.find_element_by_xpath("//textarea").click()

        copy_paste(driver, context)

        reply_btn = reply_area.find_element_by_xpath("//a[contains(@class,'btn_register')]")

        # reply_btn.click()
        while True:
            # ctime = self.request_server_time(url)
            ctime = datetime.now()
            print(ctime.date(), ctime.time().strftime('%H:%M:%S.%f'))
            if ctime.time() >= _time:
                reply_btn.click()
                self.done(ctime)
                break
            else:
                delay = 1000 if (datetime.combine(datetime.today(), _time) - ctime).total_seconds() > 1 else 100

                self.wait(delay)

    def request_server_time(self, url):
        date = urllib.request.urlopen(url).headers['Date']
        server_datetime = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %Z')
        return server_datetime

    def done(self, ctime):
        QMessageBox.about(self, "Success", f"Add Comment at {ctime.strftime('%Y-%m-%d %H:%M:%S.%f')} ")

    def wrongInput(self):
        QMessageBox.about(self, "Wrong Input ", "empty input")

    def wrongTime(self):
        QMessageBox.about(self, "Wrong Time ", "need more than 10 sec from current time")

    def wrongDate(self):
        QMessageBox.about(self, "Wrong Date ", "Check Date")

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
