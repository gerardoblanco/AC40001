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
        patternList = []
        patternTagIndicator = []

        for intent in data["intents"]:
            for pattern in intent["patterns"]:
                processedWord = nltk.word_tokenize(pattern)
                words.extend(processedWord)
                patternList.append(processedWord)
                # each entry in patternList[] will correspond to the tag at the same index in patternTagIndicator[]
                patternTagIndicator.append(intent["tag"])

            if intent["tag"] not in labels:
                labels.append(intent["tag"])
        
        # stem all words in words[] list and remove duplicate entries to obtain vocabulary size
        words = [stemmer.stem(w.lower()) for w in words if w != "?"]
        words = sorted(list(set(words))) # remove duplicate entries and convert back to list

        labels = sorted(labels)

        training = []
        output = []
        
        # list used for the 1-hot encoding using a bag of words for the output tag
        out_empty = [0 for _ in range(len(labels))]

        # create the bags of words
        for x, pattern in enumerate(patternList):
            bag = []
            
            # stem the words in the patters
            processedWord = [stemmer.stem(w.lower()) for w in pattern]
            
            # for every word in the vocabulary
            for w in words:
                # if it exists in the current pattern
                if w in processedWord:
                    # represent the existance of this word
                    bag.append(1)
                else:
                    bag.append(0)
            
            # make a copy of the out_empt list
            output_row = out_empty[:]
            # set the output to 1 for the corresponding tag to the pattern in the patternTagIndicator list
            output_row[labels.index(patternTagIndicator[x])] = 1
            
            
            training.append(bag)
            output.append(output_row)

        # TFLearn works with numpy arrays
        training = numpy.array(training)
        output = numpy.array(output)
        
        # save the pre-processed data
        with open("UpdatedModel.pickle", "wb") as f:
            pickle.dump((words, labels, training, output), f)
    
    # resetting underlying graph data and settings
    tensorflow.compat.v1.reset_default_graph()
    
    # first layer of Neural Network, with number of neurons equal to the vocabulary size
    neuralNet = tflearn.input_data(shape=[None, len(training[0])])
    # two fully connected hidden layers with 10 neurons each
    neuralNet = tflearn.fully_connected(net, 10)
    neuralNet = tflearn.fully_connected(net, 10)
    # last layer with number of neurons equal to the number of tags in the vocabulary.
    neuralNet = tflearn.fully_connected(net, len(output[0]), activation="softmax")
    neuralNet = tflearn.regression(neuralNet)
    
    # train the model
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
        
        userInput = message.text.casefold()
        results = model.predict([bag_of_words(userInput, words)])
        results_index = numpy.argmax(results)
        maxValue = numpy.amax(results)
        
        tag = labels[results_index]
        
        ''' As soon as chat is initiated, save the chat ID so that the system can communicate the
            existence of weeds without having to poll for commands or queries and then reply to the user's
            message. This way the bot can contact the user automatically,
            providing proactive customer interaction'''
        
        if userInput == "/start":
            with open('botChatID.txt', "w") as myfile:
                myfile.write(str(message.chat.id))
        
        elif userInput == "/help":
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
                
                with open ("irrigationTime.txt", "r") as myfile:
                    irTime = str(myfile.read().splitlines())
                bot.send_message(message.chat.id, "The irrigation was last used at {}".format(irTime))
            
            if tag == "QueryTemp":
                interior, exterior = envControlFuncs.greenhouseTemp()
                bot.send_message(message.chat.id, "The internal temperature is: {}°C".format(interior))
                bot.send_message(message.chat.id, "The external temperature is: {}°C".format(exterior))
                
                with open ("ventilationTime.txt", "r") as myfile:
                    ventTime = str(myfile.read().splitlines())
                bot.send_message(message.chat.id, "The ventilation was last activated at {}".format(ventTime))
            
            if tag == "QueryWeed":
                if detect.main() == "Nothing":
                    bot.send_message(message.chat.id, "No weeds found!")
                else:
                    bot.send_message(message.chat.id, "I think I see {} in your greenhouse!".format(detect.main()))
            
            if tag == "QueryTank":
                bot.send_message(message.chat.id, "The water tank depth is: {}m".format(1.3 - (envControlFuncs.waterTankDepth())))
                
                with open ("tankTime.txt", "r") as myfile:
                    tankTime = str(myfile.read().splitlines())
                bot.send_message(message.chat.id, "The tank was last filled at {}".format(tankTime))
                
            if tag == "Help":
                bot.send_message(message.chat.id, "Hey!\nYou can query the state of any environmental control feature by asking me about its current condition.") 
                bot.send_message(message.chat.id, "If you wish to use commands, these are the ones I can currently understand:")
                bot.send_message(message.chat.id, "/help\n/temperature\n/moisture\n/tank")
                bot.send_message(message.chat.id, "If you wish to override the automated features, you can ask to turn on or off the irrigation, solenoid valve or window DC motor by simply mentioning one of these features and the state you wish for it to be in")
                
        else:
            bot.send_message(message.chat.id, "I didn't catch that, sorry!")
            
    bot.polling()



