# _*_coding : utf-8 _*_
# @Time : 2024/3/21 14:16
# @Author : shui
# @File : main
# @Project : pythonProject

import configparser
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from ytdown import GetVideoInfo
import get_cookies
import pre_upload
import asyncio
import os


def crawler():
    keyword = config.get('Crawlers', 'search_keyword')
    page = int(input('请输入爬取页数'))
    url = 'https://www.youtube.com'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/122.0.0.0 Safari/537.36'
               }
    proxy = 'http://127.0.0.1:10809'

    chrome_options = webdriver.ChromeOptions()
    for key, value in headers.items():
        chrome_options.add_argument(f'--header={key}: {value}')
    chrome_options.add_argument(f'--proxy-server={proxy}')

    # 无界面模式
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

    # 爬取窗口是否保持打开状态
    # chrome_options.add_experimental_option('detach', True)

    browser = webdriver.Chrome(options=chrome_options)
    browser.get(url)

    # 模拟浏览器操作
    WebDriverWait(browser, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//div[@id="search-input"]/input[@id="search"]'))
    ).send_keys(keyword)
    time.sleep(2)
    WebDriverWait(browser, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//button[@id="search-icon-legacy"]'))).click()

    time.sleep(5)

    for i in range(page+1):
        browser.execute_script("document.documentElement.scrollTop=100000")
        time.sleep(2)

    # 获取视频地址
    print('开始获取视频地址')
    videos_url_list = browser.find_elements(By.XPATH, '//*[@id="video-title"]')
    for video_urls in videos_url_list:
        video_url = video_urls.get_attribute('href')
        if video_url != None:
            return video_url



def delete_files_in_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")


def mode(value):
    if value == 1:
        download_url = input('请输入需要下载的页面网址:')
        videos_get = GetVideoInfo()
        videos_get.get_video_info(download_url)
    elif value == 2:
        download_url = crawler()
        print('正在爬取中....')
        videos_get = GetVideoInfo()
        videos_get.get_video_info(download_url)
    elif value == 3:
        get_cookies.main()
        print('抖音cookie更新完成')
        print('====================')
        print('“1”手动模式：输入视频地址进行爬取')
        print('“2”自动模式：以config.ini文件中的配置自动爬取')
        mode_code = int(input('请输入模式代码：'))
        mode(mode_code)
    else:
        print('**请选择正确的模式**')
        print('请检查config.ini配置文件')


async def preup():
    await pre_upload.pre_upload()


if __name__ == '__main__':
    # 读取配置文件
    config = configparser.ConfigParser()
    with open('config.ini', encoding='utf-8') as f:
        config.read_file(f)
    mode_type = int(config.get('Crawlers', 'mode_type'))
    save_path = config.get('Crawlers', 'save_path')

    mode(mode_type)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(preup())

    # 上传完成后删除所有下载视频文件
    delete_files_in_directory(save_path)
