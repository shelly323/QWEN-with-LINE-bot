import json
import os
import dashscope
from dashscope import MultiModalConversation
from openai import OpenAI
from encode import encode_file

dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'

api_key = 'sk-3cc213f25b2d4ebb9c0bb9e6a878f8e0'

def image_edit(image):
    #animation()
    prompt = image_segestion(image)
    # The model supports one to three input images.
    messages = [
        {
            "role": "user",
            "content": [
                {"image": image},
                {"text": f"請依以下建議修飾圖片：{prompt}"}
            ]
        }
    ]
    response = MultiModalConversation.call(
        api_key=api_key,
        model="qwen-image-edit-plus",
        messages=messages,
        stream=False,
        n=1,
        watermark=False,
        negative_prompt=" "
    )
    if response.status_code == 200:
        os.system('cls')
        # To view the full response, uncomment the following line.
        # print(json.dumps(response, ensure_ascii=False))
        return response.output.choices[0].message.content[0]['image']
    else:
        print(f"HTTP status code: {response.status_code}")
        print(f"Error code: {response.code}")
        print(f"Error message: {response.message}")
        print("For more information, see the documentation: https://www.alibabacloud.com/help/en/model-studio/error-code")
def aigeneration(image):
    
    #animation()
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    )

    completion = client.chat.completions.create(
        model="qwen3-vl-plus",
        messages=[
            {"role": "system", "content": "你是一位圖像真實性鑑定專家"},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url", "image_url": {"url": f"{image}"},
                    },
                    {"type": "text", "text": ("請判斷這張圖是否為AI生成，並依照以下格式回答：""""
                                              'result': 'AI生成' 或 '真實照片'
                                              'confidence': '數值'
                                              'reason': '簡述'
                                              """
                                              "禁止使用任何 Markdown、符號標註或程式碼框，所有輸出皆為純文字格式"

                    )},
                ],
            }
        ],
    )
    return completion.choices[0].message.content
def image_segestion(image):
    #animation()
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    )

    completion = client.chat.completions.create(
        model="qwen3-vl-plus",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"{image}"},
                    },
                    {"type": "text", "text": "請分析這張圖片，列出幾項可以改善外觀的修圖建議"
                                             "例如該調整亮度為多少、對比多少、色調多少、飽和度多少、構圖等"
                                             "請以條列方式輸出，但禁止使用任何 Markdown、符號標註或程式碼框"
                                             "條列格式請採用：1）建議內容 2）建議內容 3）建議內容"
                                             "請僅輸出純文字，不要加上任何多餘說明"
                    },
                ],
            }
        ],
    )
    return completion.choices[0].message.content


# while True:
#     print('1.image edit')
#     print('2.is ai generate?')
#     print('3.image segestion')
#     print('4.exit')
#     choice = input()
#     if choice == '1':
#         image_edit(get_image())
#     elif choice == '2':
#         aigeneration(get_image())
#     elif choice == '3':
#         print(image_segestion(get_image()))
#     elif choice == '4':
#         break
#     else:
#         print('invalid choice')