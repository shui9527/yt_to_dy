import json


def data_collation():
    with open('./temp/finish_download_dict.json', 'r') as file:
        finish_dict = json.load(file)

    with open('./temp/new_video_dict.json', 'r') as file:
        new_dict = json.load(file)

    # 找出不重复的内容
    unique_data = [item for item in new_dict if item not in finish_dict]

    # 合并去重后的数据
    merged_data = finish_dict.copy()  # 复制原始字典
    merged_data.update({k: v for k, v in new_dict.items() if k in unique_data})

    # 将不重复内容保存到一个文件中
    new_data_dict = {k: v for k, v in new_dict.items() if k in unique_data}
    with open('./temp/new_video_dict.json', 'w') as file:
        json.dump(new_data_dict, file, indent=4)

    # 将合并后的数据保存到原有的另一个文件中
    with open('./temp/finish_download_dict.json', 'w') as file:
        json.dump(merged_data, file, indent=4)
