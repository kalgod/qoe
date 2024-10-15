import os
import shutil

def copy_and_rename_files(base_dir, dest_dir, keyword):
    # 检查目标目录是否存在，如果不存在则创建它
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # 获取 base_dir 下的所有子文件夹
    subdirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]

    # 遍历每个子文件夹
    for subdir in subdirs:
        folder_path = os.path.join(base_dir, subdir)
        
        # 遍历该子文件夹中的所有文件
        for file in os.listdir(folder_path):
            if keyword in file:
                # 获取文件的完整路径
                source_file = os.path.join(folder_path, file)

                # 设定目标文件路径，重命名为 A.mp4
                dest_file = os.path.join(dest_dir, subdir)
                os.makedirs(dest_file, exist_ok=True)
                dest_file=os.path.join(dest_file, f"{subdir}.mp4")
                # 复制并重命名文件
                shutil.copy2(source_file, dest_file)
                print(f"Copied and renamed: {source_file} to {dest_file}")

# 定义基目录（即 compressed 目录）、目标目录和关键词
base_directory = './sqoe3/compressed/compressed/'
destination_directory = './dataset/sqoe3/'
search_keyword = '1050k'

# 调用函数
copy_and_rename_files(base_directory, destination_directory, search_keyword)