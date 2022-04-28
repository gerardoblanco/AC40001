import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

import numpy
import tflearn
import tensorflow
import random
import json
import pickle
import os
import telebot
import requests
import subprocess
import RPi.GPIO as GPIO
import envAutomation
import envControlFuncs
import detect

tokenStr = ""

for ele in token: 
        tokenStr += str(ele)

API_KEY = tokenStr

testAPI = "https://api.telegram.org/bot{}/getMe".format(API_KEY)

r = requests.head(testAPI)
print(r.status_code)
code = r.status_code
print(code)


# set GPIO numbering mode and define output pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(20,GPIO.OUT) 
GPIO.setup(26,GPIO.OUT)
GPIO.setup(21,GPIO.OUT) 

# Relay HAT
GPIO.output(20,True) # solenoid valve
GPIO.output(26,True) # DC Motor
GPIO.output(21,True) # water pump

if code == 404 or code == 401:
    # force an exception
    print(ThisWillThrowAnException)
if tried == True:
    
    # start the greenhouse automated controls
    cmd = 'python3 envAutomation.py'
    p = subprocess.Popen(cmd, shell=True)
    
    
    with open("intents.json") as file:
        data = json.load(file)

    try:
        # check for existing trained model
        with open("UpdatedModel.pickle", "rb") as f:
            words, labels, training, output = pickle.load(f)
        
    except:
        words = []
        labels = []
        docs_x = []
        docs_y = []

        for intent in data["intents"]:
            for pattern in intent["patterns"]:
                wrds = nltk.word_tokenize(pattern)
                words.extend(wrds)
                docs_x.append(wrds)
                docs_y.append(intent["tag"])

            if intent["tag"] not in labels:
                labels.append(intent["tag"])

        words = [stemmer.stem(w.lower()) for w in words if w != "?"]
        words = sorted(list(set(words)))

        labels = sorted(labels)

        training = []
        output = []

        out_empty = [0 for _ in range(len(labels))]

        for x, doc in enumerate(docs_x):
            bag = []

            wrds = [stemmer.stem(w.lower()) for w in doc]

            for w in words:
                if w in wrds:
                    bag.append(1)
                else:
                    bag.append(0)

            output_row = out_empty[:]
            output_row[labels.index(docs_y[x])] = 1

            training.append(bag)
            output.append(output_row)


        training = numpy.array(training)
        output = numpy.array(output)
        
        with open("UpdatedModel.pickle", "wb") as f:
            pickle.dump((words, labels, training, output), f)

    tensorflow.compat.v1.reset_default_graph()

    net = tflearn.input_data(shape=[None, len(training[0])])
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
    net = tflearn.regression(net)

    model = tflearn.DNN(net)

    try:
        model.load("mymain.tflearn")
    except:
        model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
        model.save("mymain.tflearn")
        
    def bag_of_words(s, words):
        global nltk
        global stemmer
        global numpy
        bag = [0 for _ in range(len(words))]

        s_words = nltk.word_tokenize(s)
        s_words = [stemmer.stem(word.lower()) for word in s_words]

        for se in s_words:
            for i, w in enumerate(words):
                if w == se:
                    bag[i] = 1
                
        return numpy.array(bag)

    bot = telebot.TeleBot(API_KEY)

    @bot.message_handler(func=lambda message: True)
    def userInput(message):
        global bot
        global model
        global bag_of_words
        global words
        global labels
        global numpy
        global data
        global random
        global GPIO
        
        userInput = message.text.casefold()
        results = model.predict([bag_of_words(userInput, words)])
        results_index = numpy.argmax(results)
        maxValue = numpy.amax(results)
        
        tag = labels[results_index]
        
        if userInput == "/help":
            tag == "Help"
            
        elif userInput == "/temperature":
            tag == "QueryTemp"
        
        elif userInput == "/moisture":
            tag == "QuerySoil"
        
        elif userInput == "/tank":
            tag == "QueryTank"
        
        if maxValue > 0.7:
            for tg in data["intents"]:
                if tg['tag'] == tag:
                    responses = tg['responses']
                    
            bot.send_message(message.chat.id, random.choice(responses))
            
            if tag == "IrrigationON":
                if envControlFuncs.soilMoisture() == True:
                    envAutomation.irrigation()
                else:
                    bot.send_message(message.chat.id, "Sorry, seems like the crops don't need watering! Try again soon!")
               
            if tag == "IrrigationOFF":
                if envControlFuncs.soilMoisture() == False:
                    envAutomation.irrigation()
                else:
                    bot.send_message(message.chat.id, "Sorry, the crops still need watering! Try again soon!")
                
            if tag == "VentilationON":
                interior, exterior = envControlFuncs.greenhouseTemp()
                
                if interior > exterior and interior > 25:
                    envAutomation.ventilation()
                else:
                    bot.send_message(message.chat.id, "Sorry, I can't open the window yet, it's too cold!")
            
            if tag == "VentilationOFF":
                interior, exterior = envControlFuncs.greenhouseTemp()
                
                if interior < exterior and interior < 25:
                    envAutomation.ventilation()
                else:
                    bot.send_message(message.chat.id, "Sorry, I can't close the window yet, it's too warm!")  
            
            if tag == "ValveON":
                if envControlFuncs.waterTankDepth() < 0.7:
                    envAutomation.fillTank()
                else:
                    bot.send_message(message.chat.id, "Sorry, the water level is already high!")
            
            if tag == "ValveOFF":
                if envControlFuncs.waterTankDepth() < 0.3:
                    envAutomation.fillTank()
                else:
                    bot.send_message(message.chat.id, "Sorry, the water level is too low!")
            
            if tag == "QuerySoil":
                if envControlFuncs.soilMoisture() == True:
                    bot.send_message(message.chat.id, "The soil is dry")
                else:
                    bot.send_message(message.chat.id, "The soil is wet")
            
            if tag == "QueryTemp":
                interior, exterior = envControlFuncs.greenhouseTemp()
                bot.send_message(message.chat.id, "The internal temperature is: {}°C".format(interior))
                bot.send_message(message.chat.id, "The external temperature is: {}°C".format(exterior))
            
            if tag == "QueryWeed":
                if detect.main() == "Nothing":
                    bot.send_message(message.chat.id, "No weeds found!")
                else:
                    bot.send_message(message.chat.id, "I think I see weeds in your greenhouse!")
            
            if tag == "QueryTank":
                bot.send_message(message.chat.id, "The water tank depth is: {}m".format(1.3 - (envControlFuncs.waterTankDepth())))
            
            if tag == "Help":
                bot.send_message(message.chat.id, "Hey!\nYou can query the state of any environmental control feature by asking me about its current condition.") 
                bot.send_message(message.chat.id, "If you wish to use commands, these are the ones I can currently understand:")
                bot.send_message(message.chat.id, "/help\n/temperature\n/moisture\n/tank")
                bot.send_message(message.chat.id, "If you wish to override the automated features, you can ask to turn on or off the irrigation, solenoid valve or window DC motor by simply mentioning one of these features and the state you wish for it to be in")
                
        else:
            bot.send_message(message.chat.id, "I didn't catch that, sorry!")
            
    bot.polling()



