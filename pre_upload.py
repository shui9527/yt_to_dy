import os
import json
import asyncio
from douyin_upload import upload_video


async def pre_upload():
    folder_path = './videos_download'
    # 通过视频文件名找到同名的记录视频信息的json文件获取视频信息
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.mp4') or file_name.endswith('.avi') or file_name.endswith('.mkv'):
            json_name = os.path.splitext(file_name)[0]
            print(json_name)
            with open(folder_path + '/' + os.path.splitext(file_name)[0]+'.json', 'r', encoding='utf-8') as info:
                info_content = info.read()
                info_dict = json.loads(info_content)
                video_path = info_dict.get('video_save_path')
                video_path = video_path + os.path.splitext(file_name)[1]
                video_name = info_dict.get('title')
                description = info_dict.get('description')
                tags = info_dict.get('tags')

                # 调用抖音上传函数
                if video_path:
                    await upload_video(video_path=video_path, video_name=video_name, description=description, tags=tags,
                                       storage_state=None, headless=False)


if __name__ == '__main__':
    asyncio.run(pre_upload())
