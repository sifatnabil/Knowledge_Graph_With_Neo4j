import wikipedia

topics = ["convolutional neural network", "neural network", "yann le", "neural network", "recurrent neural network"]

text = ""

for topic in topics: 
    text += wikipedia.summary(topic)
    text += " "

with open("corpus.txt", "w", encoding="utf-8") as f:
    f.write(text)