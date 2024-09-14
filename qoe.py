import openai 
import base64
client = openai.OpenAI(api_key="anything", base_url="http://127.0.0.1:8000/v1/", default_headers={"Authorization": "Bearer anything"})

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def generate(client,path,message):
    # Path to your image
    image_path = path
    # Getting the base64 string
    base64_image = encode_image(image_path)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": message
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
            }
        ]
        }
    ]
    )
    res=response.choices[0].message.content
    return res

path="./temp.png"
fixed_msg = "On a scale of 1-5, based on the uploaded image and the following subtitles, rate the video chunk that attacts the most attention. The subtitles are :"
subtitles="they are about to shoot the ball."
format="answer only the rating number."
message=fixed_msg+subtitles+format
res=generate(client,path,message)
print(res)