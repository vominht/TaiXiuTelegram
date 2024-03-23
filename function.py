from telegram import Update
from telegram.ext import ContextTypes
import json
from telegram import ChatPermissions

auto_sessions = {}
betting_sessions = {}

admin_ids = []

def load_config():
    global admin_ids
    with open('config.json', 'r') as file:
        config = json.load(file)
        admin_ids = config.get("admin_ids", []) 
    return config

config = load_config()

slot_min_bet = config['slot_machine']['min_bet']
three_of_a_kind_multiplier = config['slot_machine']['multipliers']['three_of_a_kind']
double_seven_multiplier = config['slot_machine']['multipliers']['double_seven']
jackpot_multiplier = config['slot_machine']['multipliers']['jackpot']
taixiu_min_bet = config['taixiu']['min_bet']
taixiu_multiplier = config['taixiu']['multipliers']['tai_xiu']
chanle_min_bet = config['chanle']['min_bet']
chanle_multiplier = config['chanle']['multipliers']['chan_le']
doanso_min_bet = config['doanso']['min_bet']
doanso_multiplier = config['doanso']['multiplier']

def read_data(file_path):
  with open(file_path, 'r', encoding='utf-8') as file:
      return json.load(file)

def write_data(file_path, data):
  with open(file_path, 'w', encoding='utf-8') as file:
      json.dump(data, file, ensure_ascii=False, indent=4)

def format_currency(amount):
  return "<b>{:,} VNĐ</b>".format(amount)

def update_user_info(user_id: int, new_balance: int):
  file_path = 'data.json'  
  with open(file_path, 'r', encoding='utf-8') as file:
      users = json.load(file)
  for user in users:
      if user['user_id'] == user_id:
          user['balance'] = new_balance
          break
  with open(file_path, 'w', encoding='utf-8') as file:
      json.dump(users, file, ensure_ascii=False, indent=4)

def get_user_info(user_id):
  with open('data.json', 'r') as f:
      users = json.load(f)
      for user in users:
          if user['user_id'] == user_id:
              return user
  return None

def translate_bet_type(bet_type):
  if bet_type == "T":
      return "Tài"
  elif bet_type == "X":
      return "Xỉu"
  return bet_type

def is_user_admin(user_id):
  return user_id in admin_ids

async def lock_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
  chat_id = update.effective_chat.id
  permissions = ChatPermissions(can_send_messages=False)  
  await context.bot.set_chat_permissions(chat_id=chat_id, permissions=permissions)

async def unlock_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
  chat_id = update.effective_chat.id
  permissions = ChatPermissions(can_send_messages=True)  
  await context.bot.set_chat_permissions(chat_id=chat_id, permissions=permissions)