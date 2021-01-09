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


def login():
    options = webdriver.ChromeOptions()
    options.binary_location = "./chrome/chrome.exe"
    options.add_argument('blink-settings=imagesEnabled=true')
    options.add_argument('--mute-audio')
    options.add_argument('--log-level=3')
    options.add_argument('--window-size=750,450')
    options.add_argument('--window-position=700,0')
    options.add_experimental_option(
        'excludeSwitches', ['enable-automation'])  # 绕过js检测
    browser = webdriver.Chrome(
        executable_path="./Chrome/chromedriver.exe", options=options)  # 声明浏览器
    browser.get("http://jw1.yzu.edu.cn")
    try:
        WebDriverWait(browser, 270).until(title_of_login())
        cookies = browser.get_cookies()
        cookie = cookies[0].get('value')
        browser.quit()
        return cookie
    except:
        print("登录超时")
        browser.quit()
        return -1


def jw_post(cookie, kcId):
    url = "http://jw1.yzu.edu.cn/xkAction.do"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
               'Cookie': 'JSESSIONID=%s' % cookie,  # 这里是Cookie，形式为JSESSIONID=xxxx
               'Content-Type': 'application/x-www-form-urlencoded'}
    body = {'kcId': kcId,  # 这里是课程号，形式为课程号_课序号.如17258011_01
            'preActionType': '3',
            'actionType': '9'}
    try:
        r = requests.post(url, headers=headers, data=body, timeout=5)
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
    elif('<font color="#990000">' not in r.text and '校任选课开课信息!' in r.text):
        # 课序号错误没有任何提示，只能先这样凑合了，待优化
        print("课程号错误，请检查后重新输入！")
        os.system("pause")
        exit(0)
    else:
        print("未知返回值！")
        return 1


def main():
    print("欢迎使用抢课助手，本程序还处于demo阶段，可能存在BUG，欢迎提issue")
    print("Designed by luoboQuQ")
    print("请选择cookie获取方式")
    choose = input("（1.自动 2.手动,推荐选择自动）:")
    if (choose == '2'):
        cookie = input("请输入cookie：")
    else:
        cookie = login()
        if(cookie == -1):
            cookie = input("Cookie获取失败，请手动输入Cookie:")
    kcId_1 = input("请输入课程号(例如17018004)：")
    kcId_2 = input("请输入课序号(例如01,0不可少)：")
    kcId = kcId_1 + '_' + kcId_2
    while jw_post(cookie, kcId):
        time.sleep(2)

    os.system('pause')


if __name__ == "__main__":
    main()
