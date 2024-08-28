#!/usr/bin/env python

import requests
import urllib.parse
import subprocess

MODEL = "llama3.1:8b-instruct-q6_K"
SPEAKER = "1"

def is_process_running(process_name):
    return True

def play(text):
    encoded_text = urllib.parse.quote(text)
    audio_query_response = requests.post(f"http://localhost:50021/audio_query?speaker={SPEAKER}&text={encoded_text}")
    if audio_query_response.status_code != 200:
        print("Failed to get audio query.")
        print(audio_query_response)
        return False

    audio_query_response = audio_query_response.json()
    audio_query_response['speedScale'] *= 1.4

    response = requests.post(f"http://localhost:50021/synthesis?speaker={SPEAKER}", json=audio_query_response)
    if response.status_code != 200:
        print("Failed to get WAV.")
        print(response)
        return False

    process = subprocess.Popen(["aplay"], stdin=subprocess.PIPE)
    process.communicate(input=response.content)

    return True

def main():
    while True:
        if not is_process_running('voicevox') or not is_process_running('ollama'):
            print("Required processes are not running.")
            return

        user_input = input(">>> ")

        ollama_request = {
            "model": MODEL,
            "stream": False,
            "messages": [
                { "role": "user", "content": user_input }
            ]
        }
        response = requests.post("http://localhost:11434/api/chat", json=ollama_request)
        if response.status_code != 200:
            print("Failed to get response from the chat server.")
            print(response)
            continue

        reply = response.json().get("message", {}).get("content")
        if not reply:
            print("No 'message.content' found in the response.")
            print(response.json())
            continue

        play(reply)

if __name__ == "__main__":
    main()
