# _*_coding : utf-8 _*_
# @Time : 2024/3/23 13:19
# @Author : shui
# @File : ytdown.py
# @Project : pythonProject

import json
import yt_dlp
import configparser
import os


def get_url():
    with open('./temp/new_video_dict.json', 'r') as file:
        url_dict = json.load(file)
    if not url_dict:
        print('下载列表为空，结束任务')
    else:
        for value in url_dict.values():
            url = value
            download_video(url)
    print('视频下载完成')


def rename_video(save_path, old_title, new_title):
    old_file_path = os.path.join(save_path, f"{old_title}.mp4")
    new_file_path = os.path.join(save_path, f"{new_title}.mp4")
    print(old_file_path)
    print(new_file_path)
    if os.path.exists(old_file_path):
        os.rename(old_file_path, new_file_path)
        print(f"视频文件重命名为 {new_title}.mp4")


# def title_illegal(video_title):
#     illegal_str = ['<', '>', ':', '"', '/', '|', '?', '*']
#     for char in illegal_str:
#         if char in video_title:
#             # 将video_title中的对应i的字符修改为'_'
#             video_title = video_title.replace(char, '_')
#     # 去掉空格
#     video_title = video_title.replace(" ", "")
#     return video_title


def download_video(url):
    config = configparser.ConfigParser()
    with open('config.ini', encoding='utf-8') as f:
        config.read_file(f)
    save_path = config.get('Crawlers', 'save_path')

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    ydl_opts = {
        'format': 'best',  # 下载最佳质量的视频
        'outtmpl': save_path + '/%(title)s.%(ext)s'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)  # 提取视频信息，不下载视频

        # 整理视频信息
        # 提取字典中的description和tags部分，写入到info字典
        extract = ['title', 'description', 'tags']
        info = {}
        for key in extract:
            if key in info_dict:
                info[key] = info_dict[key]

        # # 对文件名进行检查，排除特殊字符
        title = info.get('title')
        illegal_str = ['<', '>', ':', '"', '/', '|', '?', '*']
        for char in illegal_str:
            if char in title:
                print('该视频title中包含非法字符，取消下载')
                return
            else:
                info['video_path'] = save_path

                # 保存视频信息
                filename = f"{save_path}/{title}.json"
                print(filename)
                with open(filename, 'w') as file:
                    json.dump(info, file, indent=4)

        # 下载视频
        ydl.download([url])

        print(f'{title}下载完成')





