# _*_coding : utf-8 _*_
# @Time : 2024/3/21 14:16
# @Author : shui
# @File : main
# @Project : pythonProject

import configparser
import json
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
import data_collation
import ytdown
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
    chrome_options.add_experimental_option('detach', True)

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

    time.sleep(2)

    # 获取视频标题和地址
    video_dict = {}

    videos_title_list = browser.find_elements(By.XPATH, '//*[@id="video-title"]')
    for video_title in videos_title_list:
        titles = video_title.get_attribute('title')

        hrefs = video_title.get_attribute('href')

        video_dict[titles] = hrefs

    # 去除字典中value为None的键值
    new_video_dict = {key: value for key, value in video_dict.items() if value is not None}

    print('已获取视频信息：')
    for key in new_video_dict.keys():
        print(key)

    # 将数据保存到JSON文件
    file_name = './temp/new_video_dict.json'

    with open(file_name, 'w') as file:
        json.dump(new_video_dict, file, indent=4)


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
        down_url = input('请输入需要下载的页面网址:')
        ytdown.download_video(down_url)
    elif value == 2:
        crawler()
        data_collation.data_collation()
        ytdown.get_url()
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
    # 在协程中调用另一个协程时，使用await关键字
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
    delete_files_in_directory(save_path)
