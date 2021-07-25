from joblib import load
from datetime import datetime
from bs4 import BeautifulSoup as bs
from text_preprocess import preprocess_text
from vkbottle.bot import Bot, Message


import requests as req
import random as rnd
import pandas as pnd
import string
import re

vk_token = 'токен сообщества вк здесь'
genius_token = 'токен разработчика с genius api здесь'
bot = Bot(vk_token)

#answer generators
async def generate_greetings(user_name: str):
    greetings = ["Хэй", "Привет", "♂ FUCK YOU ♂", "Приветствую", "Здорово", "Хай", "Нихао", "Конишуа", "Бонжур, епта", "Хэллоу"]
    gachi_greetings = ["fuckin' slave", "dungeon master", "leatherman", "boss of this gym", "boy next door", "jabroni"]
    main_part = ["Посмотрим что за ♂ deep dark fantasy ♂ ты прислал", 
                 "Опять шлешь свои ♂ deep dark fantasys ♂ ?", 
                 "Ну и что ты прислал ? Небось свои ♂ deep dark fantasys ♂ ?", 
                 "Ты опять шлешь свои ♂ deep dark fantasys ♂, мудила ?",
                 "♂ Without further inturptions lets celebrate and suck some dick ♂ Ой, то есть посмотрим что ты прислал"]



    return rnd.choice(greetings) + ", ♂ " + rnd.choice(gachi_greetings) + " ♂ \n" + rnd.choice(main_part)
    
async def generate_outocome(user_name: str, outcome: int):
    labels = ["не сексисткий", "сексисткий"]
    sexism_answers = ["ОГО! ♂ that turns me on ♂", 
                      "♂ It's so fuckin' deep ♂ and meaningful.", 
                      "♂ Six hot loads ♂ автору этого текста внутривенно !!!",
                      "♂ We must pull off our pants ♂, ♂ fisting ass ♂, заснять это и отправить автору присланного текста.",
                      "Отослал это произведение искусства на локальный ♂ bondage gay web site ♂ твоего города."]
    
    nonsexism_answers = ["♂ Get your ass back here ♂, это же обычная ваниль !!",
                         "♂ Oh shit i'm sorry ♂ Я не нашел проявлений мускулинности в этом тексте.",
                         "♂ Enjoy lush of the spanking ♂, но только не под эту песню.",
                         "♂ I am a performance artist ♂, но под эту песню даже у меня бы не встал.",
                         "Заплачу ♂ 300 bucks ♂, чтобы это не читать это вновь."]

    main_part =  ["Конечно это же",
    "Неужели я прочитал",
    "Это определенно",
    "Да неужели, блэт, это", 
    "Если ты еще не догадался, это"]

    answ = rnd.choice(sexism_answers) if outcome == 1 else rnd.choice(nonsexism_answers)

    return answ + '\n' + rnd.choice(main_part) + ' ' + labels[outcome] + " текст."

async def generate_refusal(user_name: str):
    sorry_part = ["Извини", "Ссорян", "Ты охирел", "С ума сошел", "Иди в пень", "Ты в своем уме", "Ага, конечно"]
    gachi_greetings = ["fuckin' slave", "dungeon master", "leatherman", "boss of this gym", "boy next door", "jabroni"]
    main_part = ["этот текст слишком большой", "этот текст огроменный", "слишком большой текст", "больше 1500 символ, дружок-пирожок", "it' so fuckin' big и вообще больше 1500 символов"]

    return rnd.choice(sorry_part) + ", ♂ " + rnd.choice(gachi_greetings) + " ♂, " + rnd.choice(main_part)

async def generate_error_refuse():
    gachi_greetings = ["fuckin' slave", "dungeon master", "leatherman", "boss of this gym", "boy next door", "jabroni"]
    return "Извини, ♂ " + rnd.choice(gachi_greetings) + " ♂, этот сервис не работает " 


#additional functions
# sexism classification model
async def classify_sexism(text: str):
    model = load('./sexism model/model.joblib')
    vectorize = load('./sexism model/vectorizer.joblib')

    return model.predict(vectorize.transform([preprocess_text(text)]))[0]
 
# if last user activity was 24 hours ago or user is not in db - return True, else False
# i use this for controling greetings part
async def check_user_activity_time(user_id: int):
    # settings
    path = './users/user_list.xlsx' #path to file
    time_threshold = 86423          #time threshold ~24 hours

    df = pnd.read_excel(path)
    user = df.loc[df['user_id'] == user_id]
    current_time = datetime.now()
    answer = False

    if user.empty:
        df = df.append({'user_id':user_id, 
                        'last_active_time':current_time}, 
                        ignore_index=True)
        answer = True

    else:
        user_last_time =  datetime.fromisoformat(user['last_active_time'].to_string(index=False))
        if (current_time.timestamp() - user_last_time.timestamp()) > time_threshold:
            answer = True
        df.update(pnd.DataFrame({'last_active_time':current_time}, index=user.index))
    
    df.to_excel(path, index=False)
    return answer

# to purify text
def clean_text(text):
    text = text.lower()
    text = re.sub('\[.*?\]', '',text)
    text = re.sub("\\W"," ",text) 
    text = re.sub('https?://\S+|www\.\S+', '',text)
    text = re.sub('<.*?>+', '',text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '',text)
    text = re.sub('\n', '',text)
    text = re.sub('\w*\d\w*', '',text)

    return text

#sexism classificators
#sexism in music
async def get_music_classification(user_name:str, audio):
    artist = audio.artist
    song_name = audio.title
    lyrics = ''
    answer = ''

    response = req.get('https://api.genius.com/search?' , 
        headers = {
            "Accept": "application'/json",
            "Authorization": "Bearer " + genius_token
        },
        params = {
            'q': artist + ' ' + song_name
    })

    if response.status_code != 200:
        return generate_error_refuse()
    
    response_content = response.json()
    seach_res = response_content['response']['hits']
        
    if len(seach_res) == 0:
        #TODO: add to generate error refuse some error cases
        return 'К сожалению, этой песни не нашлось в базе данных Genius =('
    
    for song in seach_res:
        song_artist = song['result']['primary_artist']['name']
        song_title =  song['result']['title']
        
        if artist.lower() in song_artist.lower() and song_name.lower() in song_title.lower():
            responce = req.get("https://genius.com" + song['result']['path'])
            
            if responce.status_code == 200:
                text = bs(responce.text, features="html5lib")
                for div in text.find_all("div", {"class":"lyrics"}):
                    if div.text:
                        lyrics = lyrics + div.text
        
        if lyrics:
            break

    answer = lyrics + '\n' + await generate_outocome(user_name, await classify_sexism(lyrics))
    
    return answer

#sexism in text
async def get_text_classification(text:str, user_name:str, user_id:int):
    if len(text) > 1500:
        return await generate_refusal(user_name)
    
    answer = ''
        
    answer = await generate_outocome(user_name, await classify_sexism(text))
    return answer   

#message handler
@bot.on.message()
async def message_handler(message: Message):
    users_info = await bot.api.users.get(message.from_id)

    universal_refusal_message = "Так не пойдет, дружок пирожок ! \n Либо шлешь трэк, либо текст, либо клуб кожевенного мастерства двумя этажами выше !"
    message_text = message.text
    message_attachments = message.attachments

    if message_text and len(message_attachments) > 0:
        await message.answer(message=universal_refusal_message)
        return

    if await check_user_activity_time(users_info[0].id):
        await message.answer(message= await generate_greetings(users_info[0].first_name))


    #handmade switch (since python doesnt have a switch case construction)
    #switches beetwen text and music and one text command
    if message_text:
        answer = await get_text_classification(message_text, users_info[0].first_name, users_info[0].id)
        await message.answer(message=answer)
    elif clean_text(message_text) == "отправь гачимикс":
        audio_ids = open('songs.txt', 'r').read().split('\n')
        await message.answer(message='', attachment='audio' + rnd.choice(audio_ids))  
    elif len(message_attachments) > 0:
        for attach in message_attachments:
            if attach.audio:
                answer = await get_music_classification(users_info[0].first_name, attach.audio)
                await message.answer(message=answer)
            else: 
                await message.answer(message=universal_refusal_message)

bot.run_forever()