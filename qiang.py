import os
import time

import requests
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class title_of_login:
    def __call__(self, browser):
        """ 用来结合webDriverWait判断出现的title """
        is_title = bool(EC.title_contains(u'选课管理')(browser))
        if is_title:
            return True
        else:
            return False


class Qiang():
    def __init__(self, choose=1):
        if choose == 0:
            self.host = "jw0.yzu.edu.cn"
        elif choose == 1:
            self.host = "jw1.yzu.edu.cn"
        elif choose == 2:
            self.host = "jw2.yzu.edu.cn"
        else:
            self.host = "jw3.yzu.edu.cn"

        self.options = webdriver.ChromeOptions()
        try:
            if os.path.exists("./chrome/chrome.exe"):  # win
                self.options.binary_location = "./chrome/chrome.exe"
            elif os.path.exists("./dist/chrome/chrome.exe"):  # 调试用
                self.options.binary_location = "./dist/chrome/chrome.exe"
            self.options.add_argument('blink-settings=imagesEnabled=true')
            self.options.add_argument('--mute-audio')
            self.options.add_argument('--log-level=3')
            self.options.add_argument('--window-size=750,450')
            self.options.add_argument('--window-position=700,0')
            self.options.add_experimental_option(
                'excludeSwitches', ['enable-automation'])  # 绕过js检测
            self.webdriver = webdriver
            if os.path.exists("./chrome/chromedriver.exe"):  # win
                self.browser = self.webdriver.Chrome(executable_path="./chrome/chromedriver.exe",
                                                     options=self.options)
            elif os.path.exists("./dist/chrome/chrome.exe"):  # 调试用
                self.browser = self.webdriver.Chrome(executable_path="./dist/chrome/chromedriver.exe",
                                                     options=self.options)
        except:
            print("=" * 120)
            print("浏览器初始化失败")
            print("=" * 120)
            raise

    def Login(self):
        self.browser.get("http://"+self.host)
        try:
            WebDriverWait(self.browser, 270).until(title_of_login())
            cookies = self.browser.get_cookies()
            self.cookie = cookies[0].get('value')
        except:
            print("登录超时")
            self.cookie = input("Cookie获取失败，请手动输入Cookie:")

    def SetkcId(self):
        '''设置课程号'''
        a = input("请输入课程号(例如17018004)：")
        b = input("请输入课序号(例如01,0不可少)：")
        self.kcId = a + '_' + b

    def Post(self):
        url = 'http://'+self.host+'/xkAction.do'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
                   'Cookie': 'JSESSIONID=%s' % self.cookie,  # 这里是Cookie，形式为JSESSIONID=xxxx
                   'Content-Type': 'application/x-www-form-urlencoded',
                   'Connection': 'keep-alive',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                   'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                   'Accept-Encoding': 'gzip, deflate',
                   'Upgrade-Insecure-Requests': '1'}
        body = {'kcId': self.kcId,  # 这里是课程号，形式为课程号_课序号.如17258011_01
                'preActionType': '3',
                'actionType': '9'}
        try:
            r = requests.post(url, headers=headers, data=body, timeout=10)
            r.raise_for_status()  # 手动抛出非200异常
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
            print('网络连接错误，3秒后重试')
            time.sleep(1)
            return 1
        except requests.exceptions.Timeout:
            print('连接超时，3秒后重试')
            time.sleep(1)
            return 1

        if("数据库忙请稍候再试" in r.text):
            print("课程冲突，请检查课程号后重试")
            os.system("pause")
            exit(0)
        elif("请您登录后再使用" in r.text):
            print("Cooike过期或错误，请检查Cookie后重试")
            os.system("pause")
            exit(0)
        elif("选课成功" in r.text):
            print("选课成功！")
            return 0
        elif("非选课阶段不允许选课" in r.text):
            print("选课系统暂未开启！")
            return 1
        elif("没有课余量" in r.text):
            print("发包成功，没有课余量")
            return 1
        # elif('<font color="#990000">' not in r.text and '校任选课开课信息!' in r.text):
        #     # 课序号错误没有任何提示，只能先这样凑合了，待优化
        #     print("课程号错误，请检查后重新输入！")
        #     os.system("pause")
        #     exit(0)
        elif("500 Servlet Exception" in r.text):
            print("服务器返回500错误！")
            return 1
        else:
            print("未知返回值！")
            return 1


def main():
    print("欢迎使用选课助手，本程序还处于demo阶段，可能存在BUG，欢迎提issue")
    print("Designed by luoboQuQ")
    a = int(input("请选择要使用的服务器(0/1/2/3):"))
    qiang1 = Qiang(a)
    qiang1.Login()
    print("=" * 50)
    print('请按以下步骤操作：')
    print('1.进入“选课管理”-“网上选课”')
    print('2.在“校任选课”里的“课程号”搜索框里输入要选的课程号')
    print('3.点击搜索，确保要选的课出现在浏览器上')
    print('当以上步骤做完后，最小化浏览器或关闭')
    print("=" * 50)
    qiang1.SetkcId()
    while qiang1.Post():
        time.sleep(2)
    os.system('pause')


if __name__ == "__main__":
    main()
