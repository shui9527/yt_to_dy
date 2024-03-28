# _*_coding : utf-8 _*_
# @Time : 2024/3/23 13:19
# @Author : shui
# @File : ytdown.py
# @Project : pythonProject

import json
import yt_dlp
import configparser
import subprocess
import re


class GetVideoInfo:

    config = configparser.ConfigParser()
    with open('config.ini', encoding='utf-8') as f:
        config.read_file(f)
    video_save_path = config.get('Crawlers', 'save_path')
    db_path = config.get('Crawlers', 'db_path')
    new_down_path = config.get('Crawlers', 'new_down_path')
    video_title = ''
    video_url = ''
    video_description = ''
    video_tags = ''


    def get_video_info(self, url):
        # 爬取视频信息
        print('开始爬取视频信息')
        ydl_opts = {
            'format': 'best',  # 下载最佳质量的视频
            'outtmpl': self.video_save_path + '/%(title)s.%(ext)s'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)

        # 提取字典中的tittle，description和tags部分
        self.video_title = info_dict['title']
        self.video_description = info_dict['description']
        self.video_tags = info_dict['tags']
        self.video_url = url
        print('已获取视频信息')
        print(f'title：\n{self.video_title}')
        # print(f'description：\n{self.video_description}')

        # 修正标题
        self.video_title = self.check_fix_title(self.video_title)
        # 对照数据库去重 并加入数据库
        self.data_collation(self.video_title)
        # 下载视频文件
        self.download_video(self.video_title, self.video_url, self.video_save_path)
        # 视频信息修正
        self.video_description = self.fix_description(self.video_description)
        self.video_tags = self.fix_tags(self.video_tags)
        # 保存视频信息
        self.save_video_info(self.video_save_path, self.video_title, self.video_description, self.video_tags)

    def check_fix_title(self, video_title):
        illegal_str = ['<', '>', ':', '"', '/', '|', '*', "'"]
        for char in illegal_str:
            if char in video_title:
                # 将video_title中的对应i的字符修改为'_'
                video_title = video_title.replace(char, '_')
        # 去掉空格
        video_title = video_title.replace(" ", "")

        return video_title

    def fix_description(self, video_description):
        pattern = r'(http|https)://\S+'  # 匹配以 http 或 https 开头的链接
        matches = re.finditer(pattern, video_description)
        for match in matches:
            if match is not None:
                video_description = video_description.replace(match.group(0), '')

        return video_description

    def fix_tags(self, video_tags):

        # 去除非中英文tags
        video_tags = [tag for tag in video_tags if not bool(re.search(r'[^\u4e00-\u9fa5a-zA-Z]', tag))]

        return video_tags

    def data_collation(self, video_title):
        # 打开数据库json，读取数据
        with open(self.db_path, 'r') as file:
            finish_dict = json.load(file)

        # 对比数据库，如果不存在，添加到数据库中，且保存到新下载目标的json
        if video_title not in finish_dict:
            finish_dict[video_title] = self.video_url


        # 把已更新的数据库数据重新写入
        with open(self.db_path, 'w') as file:
            json.dump(finish_dict, file, indent=4)

    def download_video(self, video_title, video_url, video_save_path):
        command = f'yt-dlp -o "{video_save_path}/{video_title}.%(ext)s" {video_url}'
        subprocess.run(command, shell=True)

    def save_video_info(self, video_save_path, video_title, video_description, video_tags,):

        info = {'title': video_title,
                'description': video_description,
                'tags': video_tags,
                'video_save_path': video_save_path + '/' + video_title
                }

        filename = f"{video_save_path}/{video_title}.json"

        with open(filename, 'w') as file:
            json.dump(info, file, indent=4)




