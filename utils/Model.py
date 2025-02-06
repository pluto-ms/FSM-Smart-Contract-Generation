import requests
import json
from colorama import Fore
import random
from data_utils import data_utils


class Model:
    def __init__(self, config: str) -> None:
        config = data_utils.load_config('../config/llm_api.config')['config']
        self.base_url = config['base_url']
        self.model = config['model']
        self.key = config['key']
    

    # Single round dialogue in openai format
    def single_dialogue(self, content: str, random_parameters: bool=False, temperature: float=0.6, top_p: float=0.9) -> str:
        
        if random_parameters:
            temperature = round(random.uniform(0.6, 1.0), 2)
            top_p = round(random.uniform(0.9, 1.0), 2)

        headers = {"Content-Type": "application/json"}
        if self.key != '':
            headers['Authorization'] = f"Bearer {self.key}"

        res = requests.post(url=self.base_url,
                            headers=headers,
                            json={"model": self.model,
                                  "temperature": temperature,
                                  "top_p": top_p,
                                  "messages": [
                                      {
                                          "role": "system",
                                          "content": "You are an expert in smart contract programming."
                                      },
                                      {
                                          "role": "user",
                                          "content": content
                                      }
                                  ]}
                            )
        json_dict = json.loads(res.text)
        # print(res.text)
        response = json_dict['choices'][0]['message']['content']
        print(Fore.GREEN + response)

        return response
    

    # Multi round dialogue in openai format
    def multiple_dialogue(self, content: str, conversation: list, random_parameters: bool=False, temperature: float=0.6, top_p: float=0.9) -> str:

        if random_parameters:
            temperature = round(random.uniform(0.6, 1.0), 2)
            top_p = round(random.uniform(0.9, 1.0), 2)

        if len(conversation) == 0:
            conversation = [
                        {
                            "role": "system",
                            "content": "You are an expert in smart contract programming."
                        }
                    ]
        

        conversation.append({
                        "role": "user",
                        "content": content
                    })

        headers = {"Content-Type": "application/json"}
        if self.key != '':
            headers['Authorization'] = f"Bearer {self.key}"

        res = requests.post(url=self.base_url,
                            headers=headers,
                            json={"model": self.model,
                                  "temperature": temperature,
                                  "top_p": top_p,
                                  "messages": conversation})
        
        # print(res.text)
        
        json_dict = json.loads(res.text)
        response = json_dict['choices'][0]['message']['content']
        print(Fore.GREEN + response)

        conversation.append({
                        "role": "assistant",
                        "content": response
                    })

        return response, conversation