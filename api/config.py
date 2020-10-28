import json
import os


def get(config: str, key: str):
    if not os.path.exists("./config/"):
        os.mkdir("./config/")
    if not os.path.exists(f"./config/{config}.json"):
        return None
    with open(f"./config/{config}.json") as file:
        data = json.load(file)

    prevLayer = data
    for layer in key.split("."):
        newLayer = prevLayer.get(layer)
        if newLayer is None: return None
        prevLayer = newLayer

    return prevLayer


def set(config: str, key: str, value):
    if not os.path.exists("./config/"):
        os.mkdir("./config/")
    if not os.path.exists(f"./config/{config}.json"):
        with open(f"./config/{config}.json", 'w') as file:
            file.write("{}")
    with open(f"./config/{config}.json", 'r') as file:
        data = json.load(file)

    lastLayer = key.split(".")
    lastLayer = lastLayer[len(lastLayer) - 1]

    prevLayer = data
    for layer in key.split("."):
        if layer == lastLayer:
            newLayer = prevLayer.get(layer)
            if newLayer is None:
                prevLayer[layer] = value
            else:
                prevLayer.update({lastLayer: value})
        else:
            newLayer = prevLayer.get(layer)
            if newLayer is None: prevLayer[layer] = {}
            prevLayer = prevLayer.get(layer)

    with open(f"./config/{config}.json", 'w') as file:
        json.dump(data, file)
