import json
import sys

def loadOpenAiApiKey ():
        with open('properties.json', 'r') as file:
             key = json.load(file)
        print(key)
        key = key["keys"]["openAi"]
        return key

#Compares the OpenAi key and changes properties if it got changed
def keyComparer (possibleNewKey): 
    if loadOpenAiApiKey() != possibleNewKey:
        with open('properties.json', 'r+') as file:
            data = json.load(file)
        print(data)
        data["keys"]["openAi"] = possibleNewKey
        with open('properties.json', 'w') as f:
            json.dump(data, f)
    print("API KEY changed")

possibleNewKey = sys.argv[1]
print(possibleNewKey)
keyComparer(possibleNewKey)