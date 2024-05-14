import os
from dotenv import load_dotenv
import argparse
import time
from gtts import gTTS
from openai import OpenAI
import subprocess

class ChatGPTSession:
    def __init__(self, model='gpt-3.5-turbo'):
        # self.API_KEY = os.getenv("API_KEY")
        self.model = model
        self.messages = [{"role": "system", "content": "You are an assistant"}]
        # self.client = OpenAI(api_key=self.API_KEY)

    def get_ans(self, question=''):
        if not question:
            return ''
        
        self.messages.append({"role": "user", "content": question})
        chat = self.client.chat.completions.create(model=self.model, messages=self.messages)
        reply = chat.choices[0].message.content
        self.messages.append({"role": "assistant", "content": reply})

        return reply

class AudioGenerator:
    def textToWav(self, text):
        tts = gTTS(text=text, lang='en')
        tts.save('results/audio.wav')


def main():
    chatgptSession = ChatGPTSession()
    question = input("User: ")

    t1 = time.time()
    ans = chatgptSession.get_ans(question)
    print(ans)
    t2 = time.time()

    print(f"Answer fetched from GPT in {round(t2-t1, 2)} seconds")

    # t3 = time.time()
    # audioGen = AudioGenerator()
    # audioGen.textToWav(ans)
    # t4 = time.time()

    # print(f"Audio Generated in {round(t4-t3, 2)} seconds")

    # Uncomment this section if you want to generate video
    # t5 = time.time()
    # videoGen = VideoGenerator(args.image_path, args.model_path)
    # videoGen.generateVideo()
    # t6 = time.time()

    # print(f"Video Generated in {round(t6-t5, 2)} seconds")

    # print(f"Text-Video Time: {round(t6-t5+t4-t3, 2)} seconds")

    # print(f"\n\nTime taken for pipeline: {round(t6-t1)} seconds")

if __name__ == '__main__':
    main()
