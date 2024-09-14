import cv2
import numpy as np
import torch
from transformers import CLIPProcessor, CLIPModel

# 加载CLIP模型和处理器
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# 视频帧提取
video_path = "./Open-Sora-Plan/Some people playing football and then celebrating the goal..mp4"
cap = cv2.VideoCapture(video_path)
frames = []
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frames.append(frame)
cap.release()

# 文本输入
text = "shooting the football"
text = "celebrating the goal"
text="Drone shot along the Hawaii jungle coastline, sunny day. Kayaks in the water."
text="Some people playing football and then celebrating the goal."
inputs = processor(text=[text], return_tensors="pt", padding=True)

# 计算每帧的相似度得分
scores = []
for i in range (len(frames)):
    frame = frames[i]
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = processor(images=image, return_tensors="pt")
    outputs = model(**inputs, **image)
    similarity = outputs.logits_per_image.item()  # 获取相似度得分
    scores.append(similarity)
    print(f"Frame {i}: Similarity Score = {similarity}")

import matplotlib.pyplot as plt

# 将帧转换为秒
fps = 25  # 每秒帧数
seconds = [i / fps for i in range(len(scores))]

# 绘制曲线图
plt.plot(seconds, scores)
plt.xlabel('Time (seconds)')
plt.ylabel('Similarity Score')
plt.title('Similarity Score over Time')
plt.savefig('similarity_score_'+text+'.pdf')