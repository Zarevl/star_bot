#!/usr/bin/env python
# coding: utf-8

# In[11]:


import discord
import os
import requests
import json
import random
#from keep_alive import keep_alive
import pandas as pd
import numpy as np
import re


#get app token
token_file = open("token.txt", "r")
token = token_file.readline()

#pulling questions database 
questions = pd.read_csv('db.csv', encoding='utf-8')
types = list(questions["type_id"].unique())
sessions = pd.read_csv("sessions.csv", encoding="utf-8")

flag = False

#function to pick a question for the user
def get_question(user_id):
    
    global questions, sessions, flag
    
    type_id = random.choice(types)
    
    if flag == False:         
        if type_id in list(sessions.loc[sessions["user_id"] == user_id, "type_id"]):
            while type_id in list(sessions.loc[sessions["user_id"] == user_id, "type_id"]):
                type_id = random.choice(types)
    
    #get question's row index
    row_id = random.choice(list(questions.loc[questions["type_id"] == type_id].index.values))
    
    #update user's history
    sessions = sessions.append([{"user_id": user_id, "type_id":type_id, "question_id": row_id}],ignore_index=True) 
    
    if len(sessions.loc[sessions["user_id"] == user_id]) >= 4:
        old = min(list(sessions.loc[sessions["user_id"] == user_id].index.values))
        sessions = sessions.drop(old)
        sessions = sessions.reset_index(drop=True)
    
    flag = False
    
    #Update database of questions 
    questions.iloc[row_id, 3] = questions.iloc[row_id, 3] +1
    
    return questions.iloc[row_id, 2], row_id        


#bot initialization
client = discord.Client()
print(client)

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))
  #await message.channel.send('The bot is online ')


@client.event
async def on_message(message):
  if message.author == client.user:
    return

  msg = message.content
  
    #if any(word in msg for word in sad_words):
      #await message.channel.send(random.choice(options))
  
  if msg.startswith('$ask'):     

    user_id = message.author
    if user_id not in list(sessions["user_id"]): 
        flag = True #True = new user
        
    question, row_id = get_question(user_id)   
    
    await message.channel.send(question)

  if msg.startswith('$dislike'): 

    bot_message = 'Noted'
    user_id = message.author
    last_user_session = max(list(sessions.loc[sessions["user_id"] == user_id].index.values))
    last_question_index = sessions.iloc[last_user_session, 2]
    questions.iloc[last_question_index, 4] = questions.iloc[last_question_index, 4] +1

    await message.channel.send(bot_message)

  if msg.startswith('$add'): 

    bot_message = 'Please pick a category or add a new one by typing **$new *category_name***. \nCurrently, I have:\n' + '\n'.join(types) + '.'

    #here I need to save the question 
    await message.channel.send(bot_message)

  if msg not in ['$ask', '$add', '$dislike']:
    
    bot_message = 'Hi ' + str(message.author) + ',\n' + 'I can ask you behavioral questions, just type **$ask**. If you do not like the question, just type **$dislike** after it. If you have the question you want to add then type **$add *question itself***.'
  
    await message.channel.send(bot_message)

  questions.to_csv('db.csv', index=False)
  sessions.to_csv('sessions.csv', index=False)

#keep_alive()
client.run(token)


# In[5]:





# In[ ]:





# In[ ]:




