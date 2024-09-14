import os
import cv2
import argparse
from poe_api_wrapper import PoeApi
import numpy as np
from scipy.stats import mode
import csv

# Tokens for Poe API (update with actual tokens if needed)
tokens = {
    'p-b': "i7JZq6B4feBIrYx2Ao8ewQ==", 
    'p-lat': "cuHNeEA7iTTHDGTzlgzdCa1b6niVntYU6vSQmOqr5g==",
    'formkey': 'c045ce1e4e5ba81ffa20da079984c515',
}

tokens_jlc = {
    'p-b': "iG6CkxM-wGYwbqiYIkFDrA==", 
    'p-lat': "moQLC5Bz/NR66fad6mHHR8kQ9Vtecv492PW5a8c6AQ==",
    'formkey': 'c8ceeb7e8b2c67b13aceb888ddbfa20d',
}

def get_data(client):
    # Get chat data of all bots (this will fetch all available threads)
    # print(client.get_chat_history("gpt4_o_128k")['data'])
    # Get chat data of a bot (this will fetch all available threads)
    # print(client.get_chat_history("gpt4_o")['data'])
    data = client.get_settings()
    print(data)
    # print(client.get_botInfo(handle="gpt4_o"))
    # print(client.get_available_creation_models())
    # print(client.get_available_bots())

def send_message(image_path, client,info):
    fixed_msg = f"""
    I have uploaded a series of frames, each representing a video chunk of 2 seconds. The original video title is {info}. 
    Based on the title background, the image content and the presented subtitles (if there are any), sort all the frames that higher number means higher interestingness score regarding the title.
    Answer in the following json format: (frame i, rating j), show with frame number ascending. The frame number i should correspond with the uploaded image file name. Different frames can yield the same score. Explain your answer.
    """
    message = fixed_msg
    frame = ["temp2.png"]
    if image_path is not None:
        frame = image_path
    bot = "gpt4_o_128k"
    for chunk in client.send_message(bot, message, file_path=frame, chatId=649712483):
        pass
    res = chunk["text"]
    return res

def extract_chunks(video_path, chunk_duration, frame_path):
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    print(f"{video_path} Video FPS: {fps}")
    os.system("rm -rf " + frame_path+"/*")
    fps=np.ceil(fps)
    frames_per_chunk = int(fps * chunk_duration)
    res = []
    chunk_index = 0
    while True:
        chunk_frames = []
        for _ in range(frames_per_chunk):
            success, frame = video.read()
            if not success:
                break
            chunk_frames.append(frame)

        if not chunk_frames:
            break
        if (len(chunk_frames) < frames_per_chunk):
            break
        key_frame = chunk_frames[0]
        res.append(key_frame)
    video.release()
    print(f"Extracted {len(res)} chunks from the video.")
    os.makedirs(frame_path, exist_ok=True)
    for i in range(len(res)):
        cv2.imwrite(os.path.join(frame_path, f"{i}.png"), res[i])
    return res

def read_score(file_path):
    res={}
    with open(file_path, 'r', newline='', encoding='utf-8') as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        for row in reader:
            identifier = row[0]  # 第一列
            category = row[1]    # 第二列
            values = row[2]
            values_list = values.split(',') if values else []  # 分割字符串
            values_list=np.array(values_list,dtype=int)
            if (identifier not in res):
                res[identifier]={"type":category,"values":values_list}
            else:
                res[identifier]["values"]=np.vstack((res[identifier]["values"],values_list))
    return res

def read_info(file_path,res):
    with open(file_path, 'r', newline='', encoding='utf-8') as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        for row in reader:
            identifier = row[1]  # 第一列
            category = row[0]    # 第二列
            info = row[2]
            if (category=="category"): continue
            res[identifier]["info"]=info
    return res

def save_info(res,video_name,duration):
    video_path = os.path.join("./dataset", video_name, f"{video_name}.mp4")
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    fps=np.ceil(fps)
    fpc=fps*duration
    fpc=int(fpc)
    score=res[video_name]["values"]
    info=res[video_name]["info"]
    print(f"{video_name} Video FPS: {fps} Score: {score.shape} Info: {info}")
    # for i in range (score.shape[1]):
    #     print(f"{i+1} {score[0,i]}")
    chunk_num=score.shape[1]/(fpc)
    chunk_num=int(chunk_num)
    final_score=np.zeros((score.shape[0],chunk_num))
    for i in range (chunk_num):
        # tmp=np.mean(score[:,i*fpc:(i+1)*fpc],axis=1)
        tmp, _ = mode(score[:,i*fpc:(i+1)*fpc], axis=1)
        final_score[:,i]=tmp.flatten()
        # for j in (score[0,i*fpc:(i+1)*fpc]):
        #     print(j)
        # print(score[0,i*fpc:(i+1)*fpc],tmp[0],"\n")

    print(f"Final Score: {final_score.shape} {final_score}")
    print(chunk_num*fpc,score.shape[1])
    np.save(f"./dataset/{video_name}/score.npy",final_score)
    return final_score

def eval_llm(chunk_score,info,frame_path,client):
    chunk_num=chunk_score.shape[1]
    image_path=[]
    for i in range(chunk_num):
        cur_path = os.path.join(frame_path, f"{i}.png")
        image_path.append(cur_path)
        if len(image_path) == 20:
            res = send_message(image_path=image_path, client=client,info=info)
            print(res)
            image_path = []
        print(i+1,np.mean(chunk_score[:,i]))
        if i >= 19:
            break

def main():
    parser = argparse.ArgumentParser(description="Extract frames from videos and process them.")
    parser.add_argument("-video_folder",type=str, default="./dataset/", help="Folder containing videos to process.")
    parser.add_argument("-chunk_duration", type=int,default=2, help="Duration of each chunk in seconds.")
    args = parser.parse_args()

    video_folder = args.video_folder
    chunk_duration = args.chunk_duration

    client = PoeApi(tokens=tokens_jlc)  # Adjust this to use the correct tokens if necessary
    get_data(client=client)
    
    all_score=read_score("./tvsum/data/ydata-tvsum50-anno.tsv")
    all_score=read_info("./tvsum/data/ydata-tvsum50-info.tsv",all_score)
    
    video_list = os.listdir(video_folder)
    for video in video_list:
        video_name = video
        video_path = os.path.join(video_folder, video_name, f"{video_name}.mp4")
        frame_path = os.path.join(video_folder, video_name, "frames")
        # video_frames = extract_chunks(video_path=video_path, chunk_duration=chunk_duration, frame_path=frame_path)
        # chunk_score=save_info(all_score,video_name,chunk_duration)

        chunk_score=np.load(f"./dataset/{video_name}/score.npy")
        info=all_score[video_name]["info"]
        print(f"Processing {video_name} with title {info}")
        eval_llm(chunk_score,info,frame_path,client)
        exit(0)
        

if __name__ == "__main__":
    main()