# - *- coding: utf- 8 - *-
import telebot
import requests
from bs4 import BeautifulSoup as bs
from telebot import types
import sqlite3
import time
from config import *

def main():
    bot = telebot.TeleBot(TOKEN , parse_mode='markdown')    

    global lst, lst_src, lst_name, page, search, genres, connect, cursor, data_msg
    lst = []
    lst_src = []
    lst_name = []   
    page = 1
    search = ''
    genres = '&genres='

    connect = sqlite3.connect('base.db' , check_same_thread=False)
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS account( id INTEGER )""")

    # ======================================================================================#
    # ==================================get informations====================================#
    # ======================================================================================#

    def send_for_all(message):
        msg = bot.send_message(message.chat.id, "Отправьте сообщения для отправке: ")
        bot.register_next_step_handler(msg, send_for_all_process)

    def send_for_all_process(message):
        cursor.execute(f"SELECT id FROM account"); members_id = cursor.fetchall()
        all_msg_id = message.message_id

        for member_id in members_id:
            bot.copy_message(from_chat_id=message.chat.id , chat_id=member_id[0] , message_id=all_msg_id )
          
    bot.enable_save_next_step_handlers(delay=2)
    bot.load_next_step_handlers()

    # ======================================================================================#
    # ===========================commands check and do func=================================#
    # ======================================================================================#


    @bot.message_handler(commands=['commands'])
    def news(message):
        bot.send_message(message.chat.id, "*Команды в нашем боте: *\n\n*/start*  -  Запустить бота\n*/help*  -  Помощь как использовать бота")

    @bot.message_handler(commands=['start'])
    def start(message):
        global connect , cursor  
        id = message.chat.id
        cursor.execute(f"SELECT id FROM account WHERE id = {id}"); member_id = str(cursor.fetchone()); member_id = member_id.replace(',' , ''); member_id = member_id.replace(')' , ''); member_id = member_id.replace('(' , ''); member_id = member_id.replace("'" , '')

        if str(id) != str(member_id):
            cursor.execute(f"INSERT INTO account(id) VALUES (?)" , (id,))
            connect.commit()

        text = "🤚 Привет этот бот умеет искать *фразы* из *фильмов* и *мультфильмов* по вашему запросу.\n\n💬 Пишите *фразу* которую хотите найти\n\n~ *Пока что доступно только английский язык* ~"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        if message.chat.id in ADMINS_ID:
            markup.row("поиск по всем критериям" , "поиск по мультфильмам")
            markup.row("Получить все ID пользователей" , "Отправить всем сообщения")
            markup.row("Отправить индивидуальный сообщения")
        else:
            markup.row("поиск по всем критериям" , "поиск по мультфильмам")
    
        bot.send_message(message.chat.id, text , reply_markup = markup)


    @bot.message_handler(commands=['help'])
    def help(message):
        bot.send_message(message.chat.id, "*Как пользоваться этим ботом и зачем?*\n\n-  Это нужен для того чтобы получить видео с какой то фразом по фразу\n-  Чтобы найти видео с фразой вам нужно биверать категорию и писать фразу который ишете\n\nБольше команды можно узнать по команду */commands*" )

    # ======================================================================================#
    # ================================check text and func===================================#
    # ======================================================================================#


    @bot.message_handler(content_types=['text'])
    def text_check(message):
        global search, genres, connect, cursor, lst, lst_name, lst_src, data_msg

        if (message.text == 'Получить все ID пользователей') and (message.chat.id in ADMINS_ID):
            cursor.execute(f"SELECT id FROM account"); members_id = cursor.fetchall()
            bot.send_message(message.chat.id , f'Пользователей: {len(members_id)}')

        elif (message.text == 'Отправить всем сообщения') and (message.chat.id in ADMINS_ID):
            send_for_all(message)

        else:
            try:
                bot.delete_message(message.chat.id, data_msg.message_id)  
            except:
                pass

            search = ''
            genres = ''
            lst.clear()
            lst_src.clear()
            lst_name.clear()
            msg = bot.send_message(message.chat.id, "⏳ Обработка данных.." ) 

            search = message.text
            genres = ''
            url = f'https://getyarn.io/yarn-find?text=' + search + genres

            response = requests.get(url)
            soup = bs(response.text, 'html.parser')
            blocks = soup.find_all('div' , attrs={'class':'pure-u-1-2 pure-u-md-1-3 pure-u-lg-1-4 pure-u-xl-1-4'})

            for block in blocks:
                title = block.find('div' , attrs={'class':'title ab fw5 p05 tal'}).text
                a_href = block.find('a' , attrs={'class':'p'}).get('href')
                a_href = a_href.split('/')
                name = block.find('div' , attrs={'class':'transcript db bg-w fwb p05 tal'}).text.strip()
                lst.append(title)
                lst_src.append(a_href[-1])
                lst_name.append(name)

            try:
                try:
                    markup = types.InlineKeyboardMarkup(row_width=5)
                    item1 = types.InlineKeyboardButton("1" , callback_data='get_1')
                    item2 = types.InlineKeyboardButton("2" , callback_data='get_2')
                    item3 = types.InlineKeyboardButton("3" , callback_data='get_3')
                    item4 = types.InlineKeyboardButton("4" , callback_data='get_4')
                    item5 = types.InlineKeyboardButton("5" , callback_data='get_5')
                    item6 = types.InlineKeyboardButton("6" , callback_data='get_6')
                    item7 = types.InlineKeyboardButton("7" , callback_data='get_7')
                    item8 = types.InlineKeyboardButton("8" , callback_data='get_8')
                    item9 = types.InlineKeyboardButton("9" , callback_data='get_9')
                    item10 = types.InlineKeyboardButton("10" , callback_data='get_10')
                    previous  = types.InlineKeyboardButton("⬅️" , callback_data='previous')
                    next = types.InlineKeyboardButton("➡️" , callback_data='next')
                    markup.add(item1,item2,item3,item4,item5,item6,item7,item8,item9,item10,previous,next)

                    info = f"*Страница {page}*\n\n"

                    for i in range(10):
                        info += f"{i+1}:  `{lst[i]}`\n*Что говорится в видео:*  `{lst_name[i]}`\n\n"

                    data_msg = bot.send_message(message.chat.id, info , reply_markup=markup) 

                except:
                    markup = types.InlineKeyboardMarkup(row_width=5)
                    item1 = types.InlineKeyboardButton("1" , callback_data='get_1')
                    item2 = types.InlineKeyboardButton("2" , callback_data='get_2')
                    item3 = types.InlineKeyboardButton("3" , callback_data='get_3')
                    item4 = types.InlineKeyboardButton("4" , callback_data='get_4')
                    item5 = types.InlineKeyboardButton("5" , callback_data='get_5')
                    markup.add(item1,item2,item3,item4,item5)
                    
                    info = f"*Страница {page}*\n\n"

                    for i in range(6):
                        info += f"{i+1}:  `{lst[i]}`\n*Что говорится в видео:*  `{lst_name[i]}`\n\n"

                    data_msg = bot.send_message(message.chat.id, info , reply_markup=markup) 
            except:
                bot.send_message(message.chat.id, f"По вашему запросу `{search}` ничего не нашлось")
            finally:
                bot.delete_message(message.chat.id, msg.message_id)  


    # ======================================================================================#
    # ===============================check callback lambda==================================#
    # ======================================================================================#


    @bot.callback_query_handler(func=lambda call: True)
    def callback_check(call):
        global lst, lst_src, lst_name, page, search, data_msg

        if 'get_' in call.data:
            cld = int((call.data).replace('get_', ''))-1
            markup = types.InlineKeyboardMarkup(row_width=1)
            item = types.InlineKeyboardButton("От бота" , url='https://t.me/Find_phrase_bot')
            markup.add(item)
            bot.send_message(call.message.chat.id, "📹 Отправляется...")
            response_image = requests.get(f'https://y.yarn.co/{lst_src[cld]}.mp4').content    
            bot.send_video(call.message.chat.id , response_image , caption=f'`{lst[cld]}`\n*Что говорится в видео:*  `{lst_name[cld]}`' , reply_markup=markup)

        elif call.data == 'next':
            lst.clear()
            lst_src.clear()
            lst_name.clear()
            page = page + 1
            url = f'https://getyarn.io/yarn-find?text=' + search + genres + '&p=' + str(page)
            response = requests.get(url)
            soup = bs(response.text, 'html.parser')
            blocks = soup.find_all('div' , attrs={'class':'pure-u-1-2 pure-u-md-1-3 pure-u-lg-1-4 pure-u-xl-1-4'})

            for block in blocks:
                title = block.find('div' , attrs={'class':'title ab fw5 p05 tal'}).text
                a_href = block.find('a' , attrs={'class':'p'}).get('href')
                a_href = a_href.split('/')
                name = block.find('div' , attrs={'class':'transcript db bg-w fwb p05 tal'}).text.strip()
                lst.append(title)
                lst_src.append(a_href[-1])
                lst_name.append(name)

            try:
                try:
                    markup = types.InlineKeyboardMarkup(row_width=5)
                    item1 = types.InlineKeyboardButton("1" , callback_data='get_1')
                    item2 = types.InlineKeyboardButton("2" , callback_data='get_2')
                    item3 = types.InlineKeyboardButton("3" , callback_data='get_3')
                    item4 = types.InlineKeyboardButton("4" , callback_data='get_4')
                    item5 = types.InlineKeyboardButton("5" , callback_data='get_5')
                    item6 = types.InlineKeyboardButton("6" , callback_data='get_6')
                    item7 = types.InlineKeyboardButton("7" , callback_data='get_7')
                    item8 = types.InlineKeyboardButton("8" , callback_data='get_8')
                    item9 = types.InlineKeyboardButton("9" , callback_data='get_9')
                    item10 = types.InlineKeyboardButton("10" , callback_data='get_10')
                    previous  = types.InlineKeyboardButton("⬅️" , callback_data='previous')
                    next = types.InlineKeyboardButton("➡️" , callback_data='next')
                    markup.add(item1,item2,item3,item4,item5,item6,item7,item8,item9,item10,previous,next)

                    info = f"*Страница {page}*\n\n"

                    for i in range(10):
                        info += f"{i+1}:  `{lst[i]}`\n*Что говорится в видео:*  `{lst_name[i]}`\n\n"

                    bot.edit_message_text(chat_id=call.message.chat.id, text=info, message_id=data_msg.message_id, reply_markup=markup) 

                except:
                    markup = types.InlineKeyboardMarkup(row_width=5)
                    item1 = types.InlineKeyboardButton("1" , callback_data='get_1')
                    item2 = types.InlineKeyboardButton("2" , callback_data='get_2')
                    item3 = types.InlineKeyboardButton("3" , callback_data='get_3')
                    item4 = types.InlineKeyboardButton("4" , callback_data='get_4')
                    item5 = types.InlineKeyboardButton("5" , callback_data='get_5')
                    markup.add(item1,item2,item3,item4,item5)
                    
                    info = f"*Страница {page}*\n\n"

                    for i in range(6):
                        info += f"{i+1}:  `{lst[i]}`\n*Что говорится в видео:*  `{lst_name[i]}`\n\n"

                    bot.edit_message_text(chat_id=call.message.chat.id, text=info, message_id=data_msg.message_id, reply_markup=markup) 
            except:
                bot.send_message(call.message.chat.id, f"Страницу под номером `{page}` не нашлось")


        elif call.data == 'previous':
            if page > 1:
                lst.clear()
                lst_src.clear()
                lst_name.clear()
                page = page - 1
                url = f'https://getyarn.io/yarn-find?text=' + search + genres + '&p=' + str(page)
                response = requests.get(url)
                soup = bs(response.text, 'html.parser')
                blocks = soup.find_all('div' , attrs={'class':'pure-u-1-2 pure-u-md-1-3 pure-u-lg-1-4 pure-u-xl-1-4'})

                for block in blocks:
                    title = block.find('div' , attrs={'class':'title ab fw5 p05 tal'}).text
                    a_href = block.find('a' , attrs={'class':'p'}).get('href')
                    a_href = a_href.split('/')
                    name = block.find('div' , attrs={'class':'transcript db bg-w fwb p05 tal'}).text.strip()
                    lst.append(title)
                    lst_src.append(a_href[-1])
                    lst_name.append(name)

                try:
                    markup = types.InlineKeyboardMarkup(row_width=5)
                    item1 = types.InlineKeyboardButton("1" , callback_data='get_1')
                    item2 = types.InlineKeyboardButton("2" , callback_data='get_2')
                    item3 = types.InlineKeyboardButton("3" , callback_data='get_3')
                    item4 = types.InlineKeyboardButton("4" , callback_data='get_4')
                    item5 = types.InlineKeyboardButton("5" , callback_data='get_5')
                    item6 = types.InlineKeyboardButton("6" , callback_data='get_6')
                    item7 = types.InlineKeyboardButton("7" , callback_data='get_7')
                    item8 = types.InlineKeyboardButton("8" , callback_data='get_8')
                    item9 = types.InlineKeyboardButton("9" , callback_data='get_9')
                    item10 = types.InlineKeyboardButton("10" , callback_data='get_10')
                    previous  = types.InlineKeyboardButton("⬅️" , callback_data='previous')
                    next = types.InlineKeyboardButton("➡️" , callback_data='next')
                    markup.add(item1,item2,item3,item4,item5,item6,item7,item8,item9,item10,previous,next)

                    info = f"*Страница {page}*\n\n"

                    for i in range(10):
                        info += f"{i+1}:  `{lst[i]}`\n*Что говорится в видео:*  `{lst_name[i]}`\n\n"

                    bot.edit_message_text(chat_id=call.message.chat.id, text=info, message_id=data_msg.message_id, reply_markup=markup) 

                except:
                    markup = types.InlineKeyboardMarkup(row_width=5)
                    item1 = types.InlineKeyboardButton("1" , callback_data='get_1')
                    item2 = types.InlineKeyboardButton("2" , callback_data='get_2')
                    item3 = types.InlineKeyboardButton("3" , callback_data='get_3')
                    item4 = types.InlineKeyboardButton("4" , callback_data='get_4')
                    item5 = types.InlineKeyboardButton("5" , callback_data='get_5')
                    markup.add(item1,item2,item3,item4,item5)
                    
                    info = f"*Страница {page}*\n\n"

                    for i in range(6):
                        info += f"{i+1}:  `{lst[i]}`\n*Что говорится в видео:*  `{lst_name[i]}`\n\n"

                    bot.edit_message_text(chat_id=call.message.chat.id, text=info, message_id=data_msg.message_id, reply_markup=markup) 
            else:
                bot.send_message(call.message.chat.id, f"Нет страницы чтобы вернутся назад")  

    # ======================================================================================#
    # ======================================================================================#
    # ======================================================================================#

    bot.polling(non_stop=True)

if __name__ =='__main__':
    main()