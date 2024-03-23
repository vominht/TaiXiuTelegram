from telegram import Update, Dice
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import asyncio
import json
from datetime import datetime
import random
import pytz

auto_sessions = {}
betting_sessions = {}

YOUR_TOKEN = '6715931797:AAHd7Hg-0xYtdđJt9DsA2LE_TrEUOJg'
admin_ids = [] 

from function import load_config, format_currency, update_user_info, get_user_info, translate_bet_type, is_user_admin, lock_chat, unlock_chat, read_data, write_data

from commands import pot, help_command, leaderboard, trutien, congtien, profile, money, deleteaccount, listcode, chuyentien, taocode, giftcode, register, mini_games, description

from banking import naptien, button_handler, clean_name, remove_banking_request, update_balance, save_banking_data, check_banking_status, update_banking_status

from message import encouragements

vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')

current_time = datetime.now(vietnam_tz).strftime('%H:%M:%S %d-%m-%Y')

config = load_config()

slot_min_bet = config['slot_machine']['min_bet']
three_of_a_kind_multiplier = config['slot_machine']['multipliers']['three_of_a_kind']
double_seven_multiplier = config['slot_machine']['multipliers']['double_seven']
jackpot_multiplier = config['slot_machine']['multipliers']['jackpot']
taixiu_min_bet = config['taixiu']['min_bet']
taixiu_multiplier = config['taixiu']['multipliers']['tai_xiu']
taixiu_chanle_multiplier = config['taixiu']['multipliers']['taixiu_chanle']
chanle_min_bet = config['chanle']['min_bet']
chanle_multiplier = config['chanle']['multipliers']['chan_le']
doanso_min_bet = config['doanso']['min_bet']
doanso_multiplier = config['doanso']['multiplier']
darts_min_bet = config['darts']['min_bet']
darts_multiplier = config['darts']['multipliers']['darts']
darts_multiplier_aim = config['darts']['multipliers']['aim']

bowling_min_bet = config['bowling']['min_bet']
bowling_tai_xiu_chan_le_multiplier = config['bowling']['multipliers']['bowling_tai_xiu_chan_le']
bowling_strike_multiplier = config['bowling']['multipliers']['strike']

async def main_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  query = update.callback_query
  data = query.data

  if data.startswith("bank:"):
      await button_handler(update, context)
  elif data.startswith("desc_"):
      await description(update, context)

async def bowling(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  args = context.args
  if len(args) != 2 or not args[1].isdigit():
      await update.message.reply_text('Sử dụng lệnh sai. Cách dùng: /bowling [bc/bl/bt/bx] [tiền cược]')
      return

  choice_input = args[0].lower()
  bet_money = int(args[1])
  user_id = update.effective_user.id

  user_info = get_user_info(user_id)

  if not user_info:
    await update.message.reply_text('Thông tin của bạn chưa được đăng ký. Hãy sử dụng lệnh /register.')
    return

  if user_info['balance'] < bet_money:
    remaining_balance = format_currency(user_info['balance']) 
    await update.message.reply_text(f'Bạn chỉ còn {remaining_balance}, không thể cược số tiền lớn hơn số dư của bạn ❌',parse_mode='HTML')
    return

  if bet_money < bowling_min_bet:
    await update.message.reply_text(f"Mức cược tối thiểu là {format_currency(bowling_min_bet)}. Vui lòng gửi cược với số tiền ít nhất là {format_currency(bowling_min_bet)} ‼️",parse_mode='HTML')
    return

  user_info['balance'] -= bet_money
  update_user_info(user_id, user_info['balance'])

  message = await update.message.reply_dice(emoji=Dice.BOWLING)
  pins_knocked_down = message.dice.value
  pins_left = 7 - pins_knocked_down if pins_knocked_down in [1, 2] else 7 - (pins_knocked_down + 1)

  win_conditions = {
      'bc': lambda x: x % 2 == 0,
      'bl': lambda x: x % 2 == 1,
      'bt': lambda x: 4 <= x <= 6,
      'bx': lambda x: 1 <= x <= 3,
  }

  await asyncio.sleep(2)

  if pins_left == 6:  
      await update.message.reply_text('Lêu lêu ném hụt rồi kìa 🫣')
  else:
      if win_conditions[choice_input](pins_left):
          multiplier = bowling_strike_multiplier if pins_left == 0 else bowling_tai_xiu_chan_le_multiplier  
          winnings = int(bet_money * multiplier)
          user_info['balance'] += winnings
          await update.message.reply_text(f'<b>Chính xác</b> 💯\nSố dư: +{format_currency(winnings)} 💵\nSố dư khả dụng: {format_currency(user_info["balance"])} 🏦',parse_mode='HTML')
      else:
          await update.message.reply_text(f'Đoán sai rồi cưng 🤣\nSố dư: -{format_currency(bet_money)} 💵',parse_mode='HTML')

  update_user_info(user_id, user_info['balance'])

async def darts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  args = context.args
  user_id = update.effective_user.id
  if len(args) != 2 or not args[1].isdigit():
      await update.message.reply_text('Sử dụng lệnh sai. Cách dùng: /darts [t/d] [tiền cược]')
      return

  choice_input = args[0].lower()
  bet_money = int(args[1])

  user_info = get_user_info(user_id)

  if not user_info:
      await update.message.reply_text('Thông tin của bạn chưa được đăng ký. Hãy sử dụng lệnh /register.')
      return

  if user_info['balance'] < bet_money:
    remaining_balance = format_currency(user_info['balance'])  
    await update.message.reply_text(f'Bạn chỉ còn {remaining_balance}, không thể cược số tiền lớn hơn số dư của bạn ❌',parse_mode='HTML')
    return

  if bet_money < darts_min_bet:
    await update.message.reply_text(f"Mức cược tối thiểu là {format_currency(darts_min_bet)}. Vui lòng gửi cược với số tiền ít nhất là {format_currency(darts_min_bet)} ‼️",parse_mode='HTML')
    return

  user_info['balance'] -= bet_money
  update_user_info(user_id, user_info['balance'])

  message = await update.message.reply_dice(emoji=Dice.DARTS)
  score = message.dice.value
  await asyncio.sleep(2)

  winnings = 0
  result_message = ""

  if score == 1:
    penalty = int(bet_money / 2)
    total_loss = bet_money + penalty
    balance_loss = user_info['balance'] - total_loss
    if user_info['balance'] >= penalty:
        user_info['balance'] -= penalty
    else:
        user_info['balance'] = 0
    result_message = f"Phi tiêu ném trượt nhưng tiền được ném chính xác vào nhà cái 👉👈\nSố tiền thua: {bet_money:,} + {penalty:,} = {format_currency(total_loss)}\nSố dư: {format_currency(balance_loss)}"
  elif (choice_input == 't' and score in [3, 5]) or (choice_input == 'd' and score in [2, 4]):
    winnings = int(bet_money * darts_multiplier)
    user_info['balance'] += winnings
    result_message = f"Chính xác! Số dư: + {format_currency(winnings)} 💵"
  elif choice_input == 'd' and score == 6:
    winnings = int(bet_money * darts_multiplier_aim)
    user_info['balance'] += winnings
    result_message = f"Ném quá đẹp✨ Số dư: + {format_currency(winnings)}."
  elif choice_input == 't' and score == 6:
    user_info['balance'] += bet_money
    result_message = "10đ ném đẹp nhưng đoán sai rùi 👽"
  else:
    result_message = f"Bạn đoán sai rùi🥲\nSố dư: - {format_currency(bet_money)}"

  await update.message.reply_text(result_message,parse_mode='HTML')

  update_user_info(user_id, user_info['balance'])

async def slot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  user_id = update.effective_user.id

  if not context.args:
      await update.message.reply_text("Cú pháp không hợp lệ. Sử dụng: /S [tiền cược]")
      return

  try:
      bet_money = int(context.args[0])  
  except ValueError:
      await update.message.reply_text("Tiền cược phải là một số. Vui lòng nhập lại.")
      return

  user_info = get_user_info(user_id)

  if not user_info:
    await update.message.reply_text('Thông tin của bạn chưa được đăng ký. Hãy sử dụng lệnh /register.')
    return

  if user_info['balance'] < bet_money:
      remaining_balance = format_currency(user_info['balance'])  
      await update.message.reply_text(f'Bạn chỉ còn {remaining_balance}, không thể cược số tiền lớn hơn số dư của bạn ❌',parse_mode='HTML')
      return

  if bet_money < config['slot_machine']['min_bet']:
      await update.message.reply_text(f"Mức cược tối thiểu là {format_currency(config['slot_machine']['min_bet'])}\nVui lòng gửi cược với số tiền ít nhất là {format_currency(config['slot_machine']['min_bet'])} ‼️",parse_mode='HTML')
      return

  user_info['balance'] -= bet_money
  update_user_info(user_id, user_info['balance'])

  message = await update.message.reply_dice(emoji=Dice.SLOT_MACHINE)
  await asyncio.sleep(1.6)  
  result = message.dice.value

  with open('nohu.json', 'r') as file:
      data = json.load(file)
      pot_amount = data['slot_machine']['amount']

  win_money = 0
  if result in [1, 22, 43]:
      win_money = int(bet_money * config['slot_machine']['multipliers']['three_of_a_kind'])
      result_message = "Three of a Kind"
  elif result in [16, 32, 48]:
      win_money = int(bet_money * config['slot_machine']['multipliers']['double_seven'])
      result_message = "Double Seven"
  elif result == 64:
      win_money = int(bet_money * config['slot_machine']['multipliers']['jackpot'] + pot_amount)
      result_message = "JackPot"
      user_info['balance'] += win_money 
      update_user_info(user_id, user_info['balance'])
      data['slot_machine']['amount'] = 0

      jackpot_message = f"┏━━━━━━━━━━━━━┓\n" \
                      f"┣➤ NGƯỜI CHƠI: {update.effective_user.full_name}\n" \
                      f"┣➤ TIỀN CƯỢC: {format_currency(bet_money)}\n" \
                      f"┣➤ KẾT QUẢ: {result_message}\n" \
                      f"┣➤ THỜI GIAN: {current_time}\n" \
                      f"┗━━━━━━━━━━━━━┛\n\n" \
                      f"Chúc mừng đại gia đã nổ hũ, toàn bộ số tiền trong hũ ({format_currency(pot_amount)}) sẽ được cộng vào số dư của đại gia.\n" \
                      f"Tổng số tiền đại gia nhận được là {format_currency(win_money)}"
      await update.message.reply_text(jackpot_message,parse_mode='HTML')

      with open('nohu.json', 'w') as file:
          json.dump(data, file)

  if win_money > 0 and result != 64:
      user_info['balance'] += win_money  
      update_user_info(user_id, user_info['balance'])

      winning_message = (
          f"┏━━━━━━━━━━━━━┓\n"
          f"┣➤ NGƯỜI CHƠI: {update.effective_user.full_name}\n"
          f"┣➤ TIỀN CƯỢC: {format_currency(bet_money)}\n"
          f"┣➤ KẾT QUẢ: {result_message}\n"
          f"┣➤ TIỀN THẮNG: {format_currency(win_money)}\n"
          f"┣➤ THỜI GIAN: {datetime.now(vietnam_tz).strftime('%H:%M:%S %d-%m-%Y')}\n"
          f"┗━━━━━━━━━━━━━┛"
      )
      await update.message.reply_text(winning_message,parse_mode='HTML')

  else:
      encouragement_message = random.choice(encouragements)
      await update.message.reply_text(encouragement_message)
      with open('nohu.json', 'r+') as file:
          data = json.load(file)
          lost_amount_rounded = int(bet_money * 0.35)
          data['slot_machine']['amount'] += lost_amount_rounded
          file.seek(0)
          json.dump(data, file, indent=4)
          file.truncate()

async def taixiu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  args = context.args
  user_id = update.effective_user.id
  if len(args) != 2 or not args[1].isdigit():
      await update.message.reply_text('Sử dụng lệnh sai. Hãy nhập lại theo mẫu: /taixiu [tài/xỉu/tl/tc/xl/xc] [tiền cược]')
      return

  choice_input = args[0].lower()

  choices = {
      "tai": ("Tài", taixiu_multiplier),
      "tài": ("Tài", taixiu_multiplier),
      "xiu": ("Xỉu", taixiu_multiplier),
      "xỉu": ("Xỉu", taixiu_multiplier),
      "tc": ("Tài Chẵn", taixiu_chanle_multiplier),
      "tl": ("Tài Lẻ", taixiu_chanle_multiplier),
      "xc": ("Xỉu Chẵn", taixiu_chanle_multiplier),
      "xl": ("Xỉu Lẻ", taixiu_chanle_multiplier),
  }

  if choice_input in choices:
    choice, multiplier = choices[choice_input]
  else:
    await update.message.reply_text('Lựa chọn không hợp lệ. Hãy chọn Tài - Xỉu - TC - XC - TL - XL.')
    return

  bet_money = int(args[1])
  if bet_money < taixiu_min_bet:
      await update.message.reply_text(f'Mức cược tối thiểu là {taixiu_min_bet:,} VNĐ.')
      return

  with open("data.json", "r+", encoding="utf-8") as file:
      users = json.load(file)
      user = next((user for user in users if user["user_id"] == user_id), None)

      if user is None:
          await update.message.reply_text('Thông tin của bạn chưa được đăng ký. Hãy sử dụng lệnh /register.')
          return

      if user['balance'] < bet_money:
          remaining_balance = format_currency(user['balance'])  
          await update.message.reply_text(f'Bạn chỉ còn {remaining_balance}, không thể cược số tiền lớn hơn số dư của bạn ❌',parse_mode='HTML')
          return

      user['balance'] -= bet_money

      total_value = 0
      dice_values = []

      for _ in range(3):
          message = await update.message.reply_dice()
          await asyncio.sleep(2)
          total_value += message.dice.value
          dice_values.append(message.dice.value)

      if 11 <= total_value <= 18:
          result = "Tài"
          result_type = "Chẵn" if total_value % 2 == 0 else "Lẻ"
      else:
          result = "Xỉu"
          result_type = "Chẵn" if total_value % 2 == 0 else "Lẻ"

      result_combined = f"{result} {result_type}"

      await asyncio.sleep(1)

      result_icon = "⚪️" if result == "Tài" else "⚫️"

      if (choice == result) or (choice == result_combined):
          winnings = int(bet_money * multiplier)
          user["balance"] += winnings  
          winnings_formatted = "{:,}".format(winnings) + " VNĐ"
          message_text = (
            f"┏━━━━━━━━━━━━━┓\n"
            f"┣➤ NGƯỜI CHƠI: {update.effective_user.full_name}\n"
            f"┣➤ CƯỢC: {choice}\n"
            f"┣➤ TIỀN CƯỢC: {bet_money:,} VNĐ\n"
            f"┣➤ KẾT QUẢ: {'-'.join(map(str, dice_values))} | {result} {result_icon}\n"                       f"┣➤ TIỀN THẮNG: {winnings:,} VNĐ\n"
            f"┣➤ THỜI GIAN: {datetime.now(vietnam_tz).strftime('%H:%M:%S %d-%m-%Y')}\n"
            f"┗━━━━━━━━━━━━━┛"
          )

          await update.message.reply_text(message_text)
      else:
          message_text = (
            f"┏━━━━━━━━━━━━━┓\n"
            f"┣➤ NGƯỜI CHƠI: {update.effective_user.full_name}\n"
            f"┣➤ CƯỢC: {choice}\n"
            f"┣➤ TIỀN CƯỢC: {bet_money:,} VNĐ\n"
            f"┣➤ KẾT QUẢ: {'-'.join(map(str, dice_values))} | {result} {result_icon}\n"   
            f"┣➤ TIỀN THUA: {bet_money:,} VNĐ\n"
            f"┣➤ THỜI GIAN: {datetime.now(vietnam_tz).strftime('%H:%M:%S %d-%m-%Y')}\n"
            f"┗━━━━━━━━━━━━━┛"
          )

          await update.message.reply_text(message_text)

      file.seek(0)
      json.dump(users, file, indent=4)
      file.truncate()

async def chanle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  args = context.args
  if len(args) != 2 or args[0].lower() not in ["chan", "le", "chẵn", "lẻ"] or not args[1].isdigit():
      await update.message.reply_text('Sử dụng lệnh sai. Hãy nhập lại theo mẫu: /chanle (chan/le) (tiền cược)')
      return

  choice_input = args[0].lower()
  money = int(args[1])

  if "chan" in choice_input or "chẵn" in choice_input:
    choice = "Chẵn"
  elif "le" in choice_input or "lẻ" in choice_input:
    choice = "Lẻ"
  else:
    await update.message.reply_text('Lựa chọn không hợp lệ. Hãy chọn Chẵn hoặc Lẻ.')
    return

  with open('data.json', 'r+', encoding='utf-8') as file:
      users = json.load(file)
      user = next((u for u in users if u['user_id'] == update.effective_user.id), None)
      if user and money >= chanle_min_bet:

          if user['balance'] < money:
              remaining_balance = format_currency(user['balance'])  
              await update.message.reply_text(f'Bạn chỉ còn {remaining_balance}, không thể cược số tiền lớn hơn số dư của bạn ‼️',parse_mode='HTML')
              return

          user['balance'] -= money

          message = await update.message.reply_dice()
          await asyncio.sleep(2)  
          total_value = message.dice.value

          result = "Chẵn" if total_value % 2 == 0 else "Lẻ"
          await asyncio.sleep(1)  

          if choice == result:
              winnings = int(money * chanle_multiplier)
              user['balance'] += winnings
              message_text = (
                "┏━━━━━━━━━━━━━┓\n"
                f"┣➤ NGƯỜI CHƠI: {update.effective_user.full_name}\n"
                f"┣➤ CƯỢC: {choice}\n"
                f"┣➤ TIỀN CƯỢC: {money:,} VNĐ\n"
                f"┣➤ TỈ LỆ: {chanle_multiplier}\n"
                f"┣➤ KẾT QUẢ: {total_value} ({result})\n"
                f"┣➤ TIỀN THẮNG: {winnings:,} VNĐ\n"
                f"┣➤ THỜI GIAN: {datetime.now(vietnam_tz).strftime('%H:%M:%S %d-%m-%Y')}\n"
                "┗━━━━━━━━━━━━━┛"
              )

              await update.message.reply_text(message_text)
          else:         
              message_text = (
                "┏━━━━━━━━━━━━━┓\n"
                f"┣➤ NGƯỜI CHƠI: {update.effective_user.full_name}\n"
                f"┣➤ CƯỢC: {choice}\n"
                f"┣➤ TIỀN CƯỢC: {money:,} VNĐ\n"
                f"┣➤ TỈ LỆ: {chanle_multiplier}\n"
                f"┣➤ KẾT QUẢ: {total_value} ({result})\n"
                f"┣➤ TIỀN THUA: {money:,} VNĐ\n"
                f"┣➤ THỜI GIAN: {datetime.now(vietnam_tz).strftime('%H:%M:%S %d-%m-%Y')}\n"
                "┗━━━━━━━━━━━━━┛"
              )

              await update.message.reply_text(message_text)

          file.seek(0)
          json.dump(users, file, indent=4, ensure_ascii=False)
          file.truncate()
      else:
          if not user:
              await update.message.reply_text('Bạn cần đăng ký trước khi chơi. Sử dụng lệnh /register')
          elif money < 5000:
              await update.message.reply_text(f'Mức cược tối thiểu là {chanle_min_bet:,} VNĐ ‼️')

async def doanso(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  args = context.args
  if len(args) != 2 or not args[0].isdigit() or not args[1].isdigit():
      await update.message.reply_text('Sử dụng lệnh sai. Hãy nhập lại theo mẫu: /doanso (số bạn đoán từ 1 đến 6) (số tiền)')
      return

  guess = int(args[0])
  money = int(args[1])

  if guess < 1 or guess > 6:
      await update.message.reply_text('Số bạn đoán phải từ 1 đến 6.')
      return

  with open('data.json', 'r+', encoding='utf-8') as file:
      users = json.load(file)
      user = next((u for u in users if u['user_id'] == update.effective_user.id), None)
      if user and money >= doanso_min_bet:

          if user['balance'] < money:
              remaining_balance = format_currency(user['balance'])  
              await update.message.reply_text(f'Bạn chỉ còn {remaining_balance}, không thể cược số tiền lớn hơn số dư của bạn ❌',parse_mode='HTML')
              return

          user['balance'] -= money

          message = await update.message.reply_dice()
          await asyncio.sleep(2)  
          dice_value = message.dice.value

          await asyncio.sleep(1)  

          if guess == dice_value:
              winnings = round(money * doanso_multiplier)
              user['balance'] += winnings  

              message_text = (
                  "┏━━━━━━━━━━━━━┓\n"
                  f"┣➤ NGƯỜI CHƠI: {update.effective_user.full_name}\n"
                  f"┣➤ CƯỢC: {guess}\n"
                  f"┣➤ TIỀN CƯỢC: {money:,} VNĐ\n"
                  f"┣➤ TỈ LỆ: {doanso_multiplier}\n"
                  f"┣➤ KẾT QUẢ: {dice_value}\n"
                  f"┣➤ TIỀN THẮNG: {winnings:,} VNĐ\n"
                  f"┣➤ THỜI GIAN: {datetime.now(vietnam_tz).strftime('%H:%M:%S %d-%m-%Y')}\n"
                  "┗━━━━━━━━━━━━━┛"
              )

              await update.message.reply_text(message_text)
          else:
              message_text = (
                "┏━━━━━━━━━━━━━┓\n"
                f"┣➤ NGƯỜI CHƠI: {update.effective_user.full_name}\n"
                f"┣➤ CƯỢC: {guess}\n"
                f"┣➤ TIỀN CƯỢC: {money:,} VNĐ\n"
                f"┣➤ TỈ LỆ: {doanso_multiplier}\n"
                f"┣➤ KẾT QUẢ: {dice_value}\n"
                f"┣➤ TIỀN THUA: {money:,} VNĐ\n"
                f"┣➤ THỜI GIAN: {datetime.now(vietnam_tz).strftime('%H:%M:%S %d-%m-%Y')}\n"
                "┗━━━━━━━━━━━━━┛"
              )

              await update.message.reply_text(message_text)

          file.seek(0)
          json.dump(users, file, indent=4, ensure_ascii=False)
          file.truncate()
      else:
          if not user:
              await update.message.reply_text('Bạn cần đăng ký trước khi chơi. Sử dụng lệnh /register')
          elif money < 10000:
              await update.message.reply_text(f'Mức cược tối thiểu là <b>{doanso_min_bet:,} VNĐ</b> ‼️',parse_mode='HTML')

async def mophien(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

  chat_id = update.effective_chat.id
  args = context.args

  if not is_user_admin(update.effective_user.id):
      await update.message.reply_text('Bạn không có quyền sử dụng lệnh này.')
      return

  if args and args[0].lower() == "auto":
      auto_sessions[chat_id] = True
      await update.message.reply_text('Phiên tự động sẽ được mở.')
      await open_new_session(update, context)
  elif args and args[0].lower() == "stop":
      auto_sessions[chat_id] = False
      await update.message.reply_text('Đã dừng phiên.')
  else:
      await update.message.reply_text('Sai cú pháp! Dùng /mophien auto để bắt đầu và /mophien stop để dừng.')

async def display_session_info(update, context, session, result, total_value, dice_values):
  chat_id = update.effective_chat.id
  total_players = len(session["user_bets"])
  total_bets = sum(sum(user_info["bets"].values()) for user_info in session["user_bets"].values())
  session_id = random.randint(1111, 99999)
  result_formatted = translate_bet_type(result)
  result_icon = "⚪️" if result_formatted == "Tài" else "⚫️"

  session_info = (
      f"┏━━━━━━━━━━━━━┓\n"
      f"┣➤ PHIÊN: {session_id}\n"
      f"┣➤ SỐ NGƯỜI CHƠI: {total_players}\n"
      f"┣➤ TỔNG TIỀN CƯỢC: {format_currency(total_bets)}\n"
      f"┣➤ KẾT QUẢ: {'-'.join(map(str, dice_values))} | {result_formatted} {result_icon}\n"
      f"┣➤ THỜI GIAN: {datetime.now(vietnam_tz).strftime('%H:%M:%S %d-%m-%Y')}\n"
      f"┗━━━━━━━━━━━━━┛"
  )

  await context.bot.send_message(chat_id, session_info,parse_mode='HTML')

async def schedule_summarize(update: Update, context: ContextTypes.DEFAULT_TYPE):

  total_time =60

  notify_interval = 10
  chat_id = update.effective_chat.id
  session = betting_sessions.get(chat_id, {"user_bets": {}})

  while total_time > 0:
      await asyncio.sleep(notify_interval)  
      total_time -= notify_interval  

      num_players_T = sum(1 for bets in session["user_bets"].values() if bets["bets"]["T"] > 0)
      num_players_X = sum(1 for bets in session["user_bets"].values() if bets["bets"]["X"] > 0)
      total_bets_T = sum(bets["bets"]["T"] for bets in session["user_bets"].values())
      total_bets_X = sum(bets["bets"]["X"] for bets in session["user_bets"].values())
      total_players = len(session["user_bets"])

      if total_time > 0:  
        message = (
          f"⏳<b>Chỉ còn {total_time}s để đặt cược, bà con nhanh tay làm giàu đê !!!</b>\n\n"
          f"👥<b>Tổng người chơi:</b> {total_players}\n"
          f"⚫️<b>Theo Tài:</b> {num_players_T} người, tổng tiền: {format_currency(total_bets_T)}\n"
          f"⚪️<b>Theo Xỉu:</b> {num_players_X} người, tổng tiền: {format_currency(total_bets_X)}"
        )
        await update.message.reply_text(message, parse_mode='HTML')

  await summarize_bets(update, context)
  await check_results(update, context)

async def bet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  chat_id = update.effective_chat.id
  user_id = update.effective_user.id
  user_full_name = update.effective_user.full_name
  session = betting_sessions.get(chat_id)
  user_info = get_user_info(user_id)

  if session and session["is_recording"]:
      if not user_info:
          await update.message.reply_text('Thông tin của bạn chưa được đăng ký. Hãy sử dụng lệnh /register.')
          return
      bet_message = update.message.text.split()
      if len(bet_message) != 2 or bet_message[0].upper() not in ["T", "X"] or not bet_message[1].isdigit():
          await update.message.reply_text('Cú pháp cược không hợp lệ. Vui lòng gửi cược với cú pháp "T [số tiền]" hoặc "X [số tiền]".')
          return

      bet_type, bet_amount = bet_message[0].upper(), int(bet_message[1])

      if bet_amount < taixiu_min_bet:
          await update.message.reply_text(f'Mức cược tối thiểu là <b>{taixiu_min_bet:,} VNĐ</b>. Vui lòng gửi cược với số tiền ít nhất là <b>{taixiu_min_bet:,} VNĐ</b> ‼️',parse_mode='HTML')
          return

      if user_info['balance'] < bet_amount:
          remaining_balance = format_currency(user_info['balance'])  
          await update.message.reply_text(f'Bạn chỉ còn {remaining_balance}, không thể cược số tiền lớn hơn số dư của bạn ❌',parse_mode='HTML')
          return

      user_bets = session["user_bets"].get(user_id, {"name": user_full_name, "bets": {"T": 0, "X": 0}})

      if (bet_type == "T" and user_bets["bets"]["X"] > 0) or (bet_type == "X" and user_bets["bets"]["T"] > 0):
          await update.message.reply_text('Chỉ đặt cược 1 cửa trong cùng 1 phiên ‼️')
          return

      user_info['balance'] -= bet_amount
      update_user_info(user_id, user_info['balance'])

      result_formatted = translate_bet_type(bet_type)
      user_bets["bets"][bet_type] += bet_amount
      session["user_bets"][user_id] = user_bets
      formatted_amount = format_currency(user_bets["bets"][bet_type])
      await update.message.reply_text(f'Đã ghi nhận cược: {result_formatted} - {formatted_amount}',parse_mode='HTML')

async def summarize_bets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  chat_id = update.effective_chat.id
  session = betting_sessions.get(chat_id)

  if session and session["is_recording"]:
      session["is_recording"] = False
      all_bets = session["user_bets"]
      if all_bets:
          summary_messages = []
          for user_id, user_info in all_bets.items():
              user_name = user_info["name"] 
              for bet_type, amount in user_info["bets"].items():
                  if amount > 0:
                      formatted_amount = format_currency(amount)
                      result_formatted = translate_bet_type(bet_type)
                      summary_messages.append(f'{user_name}: {result_formatted} - {formatted_amount}')      

          summary_text = "\n".join(summary_messages)
          await update.message.reply_text('Tiến hành đóng phiên cược, chuẩn bị cho kết quả...')
          await asyncio.sleep(1)
          await lock_chat(update, context)
          await asyncio.sleep(1)
          await update.message.reply_text(f'Cược đã ghi nhận:\n{summary_text}',parse_mode='HTML')
          await asyncio.sleep(2.5)
          await update.message.reply_text('Bắt đầu lắc xúc xắc')
          await asyncio.sleep(1)
      else:
          await update.message.reply_text('Không có cược nào được ghi nhận.')
  else:
      await update.message.reply_text('Ghi nhận cược chưa được bắt đầu hoặc đã kết thúc.')

async def check_results(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  chat_id = update.effective_chat.id
  session = betting_sessions.get(chat_id)
  if session:
      total_value = 0
      dice_values = []

      for _ in range(3):
          message = await context.bot.send_dice(chat_id)
          await asyncio.sleep(2)
          total_value += message.dice.value
          dice_values.append(message.dice.value)

      if 11 <= total_value <= 18:
          result = "T"
      else:
          result = "X"

      await asyncio.sleep(1)

      await display_session_info(update, context, session, result, total_value, dice_values)
      await announce_results(update, context, session["user_bets"], result)

async def announce_results(update: Update, context: ContextTypes.DEFAULT_TYPE, user_bets, result) -> None:
  chat_id = update.effective_chat.id
  data_path = 'data.json'
  user_data = read_data(data_path)
  winners = []
  losers = []

  for user_id, user_info in user_bets.items():
      user_name = user_info["name"]
      bet_type = None
      bet_amount = 0
      for type, amount in user_info["bets"].items():
          if amount > 0:
              bet_type = type
              bet_amount = amount
              break

      for user in user_data:
          if user['user_id'] == user_id:
              if bet_type == result:

                  win_amount = int(bet_amount * taixiu_multiplier)
                  user['balance'] += win_amount
                  formatted_win_amount = format_currency(win_amount)
                  winners.append(f'{user_name}: +{formatted_win_amount}')
              else:
                  formatted_loss_amount = format_currency(bet_amount)
                  losers.append(f'{user_name}: -{formatted_loss_amount}')
              break

  write_data(data_path, user_data)

  result_formatted = translate_bet_type(result)
  if winners:
      winners_text = "\n".join(winners)
      await update.message.reply_text(f'Người thắng cược ({result_formatted}):\n{winners_text}',parse_mode='HTML')
  if losers:
      losers_text = "\n".join(losers)
      await update.message.reply_text(f'Người thua cược:\n{losers_text}',parse_mode='HTML')
  await asyncio.sleep(1)
  await unlock_chat(update, context)
  if auto_sessions.get(chat_id):
    await context.bot.send_message(chat_id, "10s sau sẽ mở phiên tiếp theo.")
    await asyncio.sleep(10)
    if auto_sessions.get(chat_id):
      await open_new_session(update, context)

async def open_new_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
  chat_id = update.effective_chat.id
  betting_sessions[chat_id] = {
      "is_recording": True,
      "user_bets": {}
  }
  await update.message.reply_text(
      '<b>Phiên đã được mở và bắt đầu nhận cược trong 60s</b>\n\n'
      '<b>[+] Cú pháp</b>: T [số tiền] hoặc X [số tiền]\n'
      'Ví dụ: T 9999 hoặc X 12345\n'
      '<b>[+] Cược tối thiểu là 5,000 VNĐ, không cược 2 cửa trong cùng 1 phiên</b>',
      parse_mode='HTML'
  )

  context.application.create_task(schedule_summarize(update, context))

def main():
  app = ApplicationBuilder().token(YOUR_TOKEN).build()

  app.add_handler(CommandHandler("help", help_command))
  app.add_handler(CommandHandler('bxh', leaderboard))
  app.add_handler(CommandHandler("taixiu", taixiu))
  app.add_handler(CommandHandler("register", register))
  app.add_handler(CommandHandler("profile", profile))
  app.add_handler(CommandHandler("giftcode", giftcode))
  app.add_handler(CommandHandler("congtien", congtien))
  app.add_handler(CommandHandler("taocode", taocode))
  app.add_handler(CommandHandler("listcode", listcode))
  app.add_handler(CommandHandler("chuyentien", chuyentien))
  app.add_handler(CommandHandler("deleteaccount", deleteaccount))
  app.add_handler(CommandHandler("trutien", trutien))
  app.add_handler(CommandHandler("chanle", chanle))
  app.add_handler(CommandHandler("doanso", doanso))
  app.add_handler(CommandHandler("money", money))
  app.add_handler(CommandHandler("mophien", mophien))
  app.add_handler(CommandHandler("S", slot))
  app.add_handler(CommandHandler("darts", darts))
  app.add_handler(CommandHandler("bowling", bowling))
  app.add_handler(CommandHandler("pot", pot))
  app.add_handler(CommandHandler("game", mini_games))
  app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bet))
  app.add_handler(CommandHandler("naptien", naptien))
  app.add_handler(CallbackQueryHandler(main_callback_handler))

  app.run_polling()

if __name__ == '__main__':
  print('KHÔNG BUG KHÔNG BUG KHÔNG BUG')
  main()

#                       _oo0oo_
#                      o8888888o
#                      88" . "88
#                      (| -_- |)
#                      0\  =  /0
#                    ___/`---'\___
#                  .' \\|     |// '.
#                 / \\|||  :  |||// \
#                / _||||| -:- |||||- \
#               |   | \\\  -  /// |   |
#               | \_|  ''\---/''  |_/ |
#               \  .-\__  '-'  ___/-. /
#             ___'. .'  /--.--\  `. .'___
#          ."" '<  `.___\_<|>_/___.' >' "".
#         | | :  `- \`.;`\ _ /`;.`/ - ` : | |
#         \  \ `_.   \_ __\ /__ _/   .-` /  /
#     =====`-.____`.___ \_____/___.-`___.-'=====
#                       `=---='
#
#     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#            Phật phù hộ, không bao giờ BUG
#     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
