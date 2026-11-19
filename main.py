import telebot
import sqlite3 as sq
import random
import json
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import os
import perks_class




API_TOKEN = BOT_TOKEN

min_pis = -5
max_pis = 10


pisun_update_t = 23

player_dict = {"id": -1, "name": "null", "pisun": 0, "last_game": "0-0-0-0-0", "pisun_delta": 0, "perk": "none", "last_perk": None, "perk_ready": False}


def sort_users_by_pis(users):
    users_l_sorted = sorted(users, key=lambda x: x["pisun"])
    users_l_sorted.reverse()
    return users_l_sorted



def vadat_perk_q(message, new_json, user_in_json, group_id):
    last_perk = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    random_prk = perks_class.get_random_perk()
    r_prk_id = perks_class.get_perk_id(random_prk)



    match r_prk_id:
        case 7:
            random_user = random.choice(new_json["users"])
            random_prk.value = random_user["id"]
            random_prk.desc = f"Если после прокрутки вашего писюнчика игрок *{random_user["name"]}* будет на первом месте в топе, то ваш писюнчик увеличится на *{random_prk.const_val} см.*"
        case 6:
            pass
        case 5:
           users_no_perk = [us for us in new_json["users"]]
           users_no_perk.remove(new_json["users"][user_in_json])
           random_user = random.choice(users_no_perk)
           random_prk.value = random_user["id"]
           random_prk.desc = f"В следующей прокрутке писюнчика вам выпадет такое же значение как у *{random_user["name"]}*"
        case 4:
           random_prk = perks_class.rand_x(random_prk) 
        case 3:
            random_prk = perks_class.rand_minus_pis(random_prk) 
            markup = telebot.types.InlineKeyboardMarkup(resize_keyboard=True)
            users_l_sorted = sort_users_by_pis(new_json["users"])
            for i in users_l_sorted:
                us_name = i["name"]
                us_id = i["id"]
                if i["id"] != message.from_user.id:
                    butn = telebot.types.InlineKeyboardButton(text=f"{us_name} | {i["pisun"]} см", callback_data=f'min_pis:{us_id}:{new_json["users"][user_in_json]["id"]}:{random_prk.value}')
                    markup.add(butn)
            bot.send_message(message.chat.id, f"*{new_json["users"][user_in_json]["name"]}*, выбери игрока, которому ты хочешь уменьшить писюнчик на {random_prk.value} см:", reply_markup=markup, parse_mode="Markdown")
        case 2:
            new_json["users"][user_in_json]["perk"] = "none"
            last_game = new_json["users"][user_in_json]["last_game"]
            prokrutka_pisun_q(message, new_json, user_in_json, group_id, new_json["users"][user_in_json]["name"], last_game)

    if not random_prk.instant_use:
        new_json["users"][user_in_json]["perk"] = random_prk.dict_perk()
    new_json["users"][user_in_json]["last_perk"] = last_perk           
    

    write_json(new_json, f"data/{group_id}")
    bot.reply_to(message, f'''Ты активировал случайный перк *"{random_prk.name}"*.
{random_prk.desc}''', parse_mode='Markdown')
    


def get_perk_from_ind(ind, value=0):
    perk = perks_class.registered_perks[ind]
    perk.value = value
    return perk



def prokrutka_pisun_q(message, new_json, user_in_json, group_id, username, date_now, time_msg=""):
    razmer_pisun = new_json["users"][user_in_json]["pisun"]
    #date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #pisun_plus = random.randrange(min_pis, max_pis+1)
    razmer_range = list(range(min_pis, max_pis+1))
    razmer_range.remove(0)
    pisun_plus = random.choice(razmer_range)
    first_value_pis = pisun_plus
    lolik = "вырос"

    perk_dict = new_json["users"][user_in_json]["perk"]


    perk = None
    if perk_dict != "none":
        perk = get_perk_from_ind(perk_dict["id"], perk_dict["value"])
        if not perk.imunitet:
            new_json["users"][user_in_json]["perk"] = "none"


    #perk_dict = new_json["users"][user_in_json]["perk"] 
    #if perk_dict != "none":
        #if not perk_dict["imunitet"]:
            #new_json["users"][user_in_json]["perk"] = "none"

    comment = ""

    if perk_dict != "none":
        match perk.id:
            case 0:
                pisun_plus = random.randrange(1, max_pis)
            case 1:
                pisun_plus = random.randrange(min_pis, 0)
            case 3:
                pass
            case 4:
                comment = f"\n(Писюн изменился бы без прибавки на *{first_value_pis} см)*" 
                pisun_plus += perk.value
            case 5:
                player_id = perk.value
                player_pisun_delta = new_json["users"][find_user_ind(player_id, f"data/{str(group_id)}")]["pisun_delta"]
                pisun_plus = player_pisun_delta
            case 6:
                pisun_plus = new_json["users"][user_in_json]["pisun_delta"]
            case 7:
                player_id = perk.value
                player = new_json["users"][find_user_ind(player_id, f"data/{str(group_id)}")]
                if sort_users_by_pis(new_json["users"]).index(player) == 0:
                    pisun_plus += 10
                    comment = f"""\n(*{player["name"]}* оказался королем.
Твой писюн дополнительно изменился на *{perk.const_val} см.*)"""
                else:
                    comment = f"""(*{player["name"]}* не оказался королем.
Твой писюн дополнительно не изменился)"""                    



    if pisun_plus < 0: lolik = "сократился"
    else: "вырос"
    new_json["users"][user_in_json]["pisun_delta"] = pisun_plus
    new_json["users"][user_in_json]["pisun"] += pisun_plus
    new_json["users"][user_in_json]["last_game"] = date_now
    write_json(new_json, f"data/{str(group_id)}")
    bot.reply_to(message, f"""
*{username}*, Твой писюн *{lolik}* на *{abs(pisun_plus)} см*. 
Сейчас он составляет *{razmer_pisun + pisun_plus} cм*.{comment}
Следующая попытка завтра!{time_msg}
""", parse_mode='Markdown')    



only_group_msg = """
Данная команда работает только в группах. 
Добавь бота в группу, чтобы команда работала.
"""

bot = telebot.TeleBot(API_TOKEN)


def read_json(file='user_data'):
    with open(f'{file}.json', 'r', encoding='utf-8') as user_data_json:
        return json.load(user_data_json)
    
def write_json(new_json, file_name='user_data'):
    with open(f'{file_name}.json', 'w', encoding='utf-8') as user_data_json:
        json.dump(new_json, user_data_json, indent=4, ensure_ascii=False)

def find_user_ind(userid, file_name='user_data'):
    with open(f'{file_name}.json', 'r', encoding='utf-8') as user_data_json:
        dict = json.load(user_data_json)
        for user in dict["users"]:
            if user["id"] == userid:
                return dict["users"].index(user)
        return "none"


# Handle '/start' and '/help'   
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, f"""
Привет, я Пиписька Бот Redux.
Напиши команду /dick и увеличь свой писюн в диапазоне *[{min_pis}, {max_pis}] см* раз в 24 часа.
Напиши команду /perk, чтобы получить случайный перк.
""", parse_mode='Markdown')

@bot.message_handler(commands=['dick'])
def izmenit_pisun(message):
    if message.chat.type in ["group", "supergroup"]:
        group_id = message.chat.id
        user = message.from_user
        userid = user.id
        username = user.first_name
        f_path = f"data/{str(group_id)}.json"
        if not Path(f_path).is_file():
            write_json({"users": []}, f"data/{str(group_id)}")
        json_f: dict = read_json(f"data/{str(group_id)}")
        user_in_json = find_user_ind(userid, f"data/{str(group_id)}")
        print(user_in_json)
        if user_in_json != "none":
            new_json = json_f.copy()
            razmer_pisun = new_json["users"][user_in_json]["pisun"]
            last_game = new_json["users"][user_in_json]["last_game"]
            date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            diff_now = datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S")
            diff_last = ''
            if last_game != "0-0-0-0-0":
                diff_last = datetime.strptime(last_game, "%Y-%m-%d %H:%M:%S")
                seconds = (diff_now - diff_last).total_seconds()
                hours = seconds // 3600

                remaining_hours = (pisun_update_t-1) - hours
                remaining_secs = 59 - (seconds % 60)
                remaining_mins = 59 - ((seconds % 3600) // 60)

                time = f"{int(remaining_hours)} ч. {int(remaining_mins)} мин. {int(remaining_secs)} с."

            if last_game == "0-0-0-0-0" or (hours >= pisun_update_t) or (username == "Maze" and group_id == -4927323046):
                prokrutka_pisun_q(message, new_json, user_in_json, group_id, username, date_now,)
            else:
                bot.reply_to(message, f"""
*{username}*, Ты уже играл.
Сейчас твой писюн составляет *{razmer_pisun} cм*.
Следующая попытка через *{time}*
""", parse_mode='Markdown')            
        elif user_in_json == "none":
            new_json = json_f.copy()
            updated_user = player_dict.copy()
            updated_user["id"] = userid
            updated_user["name"] = username
            new_json["users"].append(updated_user)
            write_json(new_json, f"data/{str(group_id)}")
            izmenit_pisun(message)
    else:
        bot.reply_to(message, only_group_msg)

@bot.message_handler(commands=['top'])           
def top(message):
    if message.chat.type in ["group", "supergroup"]:
        group_id = message.chat.id
        f_path = f"data/{str(group_id)}.json"
        if not Path(f_path).is_file():
            write_json({"users": []}, f"data/{str(group_id)}")
        json_f: dict = read_json(f"data/{str(group_id)}")
        users = [a for a in json_f["users"]]
        users_sorted = sorted(users, key=lambda x: x["pisun"])
        users_sorted.reverse()
        bot_message = ""
        count = 1
        for i in users_sorted:
            smile = ""
            if count == 1:
                smile = "🍆"
            elif count == len(users_sorted):
                smile = "🤥"
            
            plr_name = i["name"]
            if len(plr_name) >= 10:
                plr_name = plr_name[:10]+"..."
            
            pisun_dlt = str(i["pisun_delta"])
            if i["pisun_delta"] > 0:
                pisun_dlt = "+"+pisun_dlt

            msg = f"\n*{count}|{plr_name}{smile} — {i['pisun']} см.| {pisun_dlt}*"
            bot_message+=msg
            count+=1
        bot.reply_to(message, f"""
        {bot_message}
        """, parse_mode='Markdown')
    else:        
        bot.reply_to(message, only_group_msg)


@bot.message_handler(commands=['stats'])   
def create_img(message):
    if message.chat.type in ["group", "supergroup"]:
        img = Image.new('RGB', (600, 550), color=(0, 0, 3))
        idraw = ImageDraw.Draw(img)


        group_title = ImageFont.truetype('RussoOne-Regular.ttf', size = 35)
        group_title2 = ImageFont.truetype('RussoOne-Regular.ttf', size = 25)
        group_title3 = ImageFont.truetype('RussoOne-Regular.ttf', size = 20)


        group_id = message.chat.id
        f_path = f"data/{str(group_id)}.json"
        if not Path(f_path).is_file():
            write_json({"users": []}, f"data/{str(group_id)}")
        json_f: dict = read_json(f"data/{str(group_id)}")
        users = [a for a in json_f["users"]]
        users_sorted = sorted(users, key=lambda x: x["pisun"])
        users_sorted.reverse()
        count = 1
        x = 15
        y = 75
        for i in users_sorted:
            color = 'white'
            if count == 1:
                color = (240, 210, 0)
            if count == 2:
                color = 'gray'
            if count == 3:
                color = (125, 60, 0)

            pisun_delta = str(i["pisun_delta"])
            color_pis = 'white'
            if i["pisun_delta"] > 0:
                pisun_delta = "+"+pisun_delta
                color_pis = 'lime'
            elif i["pisun_delta"] < 0:
                color_pis = 'red'
            
            player_name = i["name"]
            if i["id"] == 5837854157: player_name = "Лжеваня"
            if i["id"] == 1164658241: player_name = "Ваня"
            if len(player_name) >= 17:
                player_name=player_name[:17]+"..."
            idraw.text((10, y), f'{count}', font=group_title2, fill=color)
            idraw.text((40, y), player_name, font=group_title, )
            idraw.text((455, y), f'{i["pisun"]} см', font=group_title3, fill="white")
            idraw.text((555, y), pisun_delta, font=group_title3, fill=color_pis)
            y+=50
            count+=1

        group_name = message.chat.title
        if len(group_name) > 16:
            group_name = group_name[:14]+"..."
        idraw.text((10, 10), f'Топ чата:', font=group_title, )
        idraw.text((185, 10), f'{group_name}', font=group_title, fill=(240, 210, 0))


        img_path = f'{group_id}.png'
        img.save(img_path)
        with open(img_path, "rb") as image:
            bot.send_photo(group_id, image)
        os.remove(img_path)
    else:
        bot.reply_to(message, only_group_msg)


        


@bot.message_handler(commands=['perk'])   
def vidat_perk(message):
    if message.chat.type in ["group", "supergroup"]:
        print(1)
        group_id = message.chat.id
        user = message.from_user
        userid = user.id
        username = user.first_name
        f_path = f"data/{str(group_id)}.json"
        if not Path(f_path).is_file():
            write_json({"users": []}, f"data/{str(group_id)}")
        json_f: dict = read_json(f"data/{str(group_id)}")
        user_in_json = find_user_ind(userid, f"data/{str(group_id)}")
        print(user_in_json)
        if user_in_json != "none":
        
            new_json = json_f.copy()
            #start_json = json_f.copy()
            if not new_json["users"][user_in_json].get("perk"): 
                new_json["users"][user_in_json]["perk"] = "none"
            #if new_json["users"][user_in_json]["perk"] != "none":
             
                #bot.reply_to(message, f"""У тебя уже есть активный перк *"{get_perk_from_ind(new_json["users"][user_in_json]["perk"]["id"]).name}"*.
#Прокрути свой писюнчик еще раз, чтобы активировать новый.""", parse_mode="Markdown")
            print(5)
            if new_json["users"][user_in_json].get("last_perk"):
                print(6)
                last_perk = new_json["users"][user_in_json]["last_perk"]
                date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                diff_now = datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S")
                diff_last = datetime.strptime(last_perk, "%Y-%m-%d %H:%M:%S")
                seconds = (diff_now - diff_last).total_seconds()
                hours = seconds // 3600

                pisun_update_t = 23
                remaining_hours = (pisun_update_t-1) - hours
                remaining_secs = 59 - (seconds % 60)
                remaining_mins = 59 - ((seconds % 3600) // 60)

                time = f"{int(remaining_hours)} ч. {int(remaining_mins)} мин. {int(remaining_secs)} с."
                perk = None
                if new_json["users"][user_in_json]["perk"] != "none":
                    perk = get_perk_from_ind(new_json["users"][user_in_json]["perk"]["id"])                


                if hours >= pisun_update_t:
                    if new_json["users"][user_in_json].get("perk_ready") or not perk:
                        new_json["users"][user_in_json]["perk_ready"] = False
                        vadat_perk_q(message, new_json, user_in_json, group_id)
                    else:
                        new_json["users"][user_in_json]["perk_ready"] = True
                        write_json(new_json, f"data/{str(group_id)}")
                        bot.reply_to(message, f'''! Сейчас у тебя активирован перк *"{perk.name}"* !
*Пропиши команду снова, чтобы сделать реролл перка.*''', parse_mode="Markdown")                          

                else:
                    info = ""
                    if perk:
                        info = f'Сейчас у тебя активирован перк *"{perk.name}"*.\n'
                    bot.reply_to(message, f"""{info}Время для повторной прокрутки перка не прошло.
Следующая попытка через *{time}*""", parse_mode="Markdown")                        
            else:
                vadat_perk_q(message, new_json, user_in_json, group_id)

        elif user_in_json == "none":
            new_json = json_f.copy()
            updated_user = player_dict.copy()
            updated_user["id"] = userid
            updated_user["name"] = username
            new_json["users"].append(updated_user)
            write_json(new_json, f"data/{str(group_id)}")
            vidat_perk(message)
    else:
        bot.reply_to(message, only_group_msg)        


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])





@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
  if "min_pis" in call.data:
    chat_id = call.message.chat.id
    call_data: str = call.data
    splited_data_list = call_data.split(":")
    user_to_min_pis = splited_data_list[1]
    caller_user_id = splited_data_list[2]
    minus_pis = int(splited_data_list[3])
    if str(call.from_user.id) == caller_user_id:
        json_f: dict = read_json(f"data/{str(chat_id)}")
        caller_ind = find_user_ind(int(caller_user_id), f"data/{str(chat_id)}")
        caller_name = json_f["users"][caller_ind]["name"]
        if json_f["users"][caller_ind]["perk"] != "none" and json_f["users"][caller_ind]["perk"]["id"] == 3:
            json_f["users"][caller_ind]["perk"] = "none"
            user_to_min_pis_ind = find_user_ind(int(user_to_min_pis), f"data/{str(chat_id)}")
            user_to_min_pis_name = json_f["users"][user_to_min_pis_ind]["name"]
            json_f["users"][user_to_min_pis_ind]["pisun"] -= minus_pis
            json_f["users"][user_to_min_pis_ind]["pisun_delta"] = minus_pis
            write_json(json_f, f"data/{str(chat_id)}")
            bot.send_message(chat_id, f'''*{caller_name}* уменьшил писюнчик игроку *{user_to_min_pis_name}* на *{abs(minus_pis)} см.*''', parse_mode="Markdown")      
        else:
            bot.send_message(chat_id, f'''*{caller_name}*, у тебя нет перка на уменьшение писюнчик другу((.''', parse_mode="Markdown")   





bot.infinity_polling()
