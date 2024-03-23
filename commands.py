from telegram import Update
from telegram.ext import ContextTypes
import json
from datetime import datetime
import pytz
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from function import load_config, format_currency, is_user_admin

vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
current_time = datetime.now(vietnam_tz).strftime("%H:%M:%S %d-%m-%Y")

auto_sessions = {}

YOUR_TOKEN = '6715931797:AAHd7Hg-0xYtdDJt9DsA2LEbCkj_TrEUOJg'
admin_ids = []

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

async def mini_games(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  keyboard = [
      [InlineKeyboardButton("Tài Xỉu", callback_data='desc_taixiu'),
       InlineKeyboardButton("Chẵn Lẻ", callback_data='desc_chanle')],
      [InlineKeyboardButton("Đoán Số", callback_data='desc_doanso'),
       InlineKeyboardButton("Slot Machine", callback_data='desc_slot_machine')],
      [InlineKeyboardButton("Ném Phi Tiêu", callback_data='desc_darts'),
       InlineKeyboardButton("Bowling", callback_data='desc_bowling')]
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  await update.message.reply_text("Hãy chọn Game bạn muốn tìm hiểu 👇👇👇", reply_markup=reply_markup)

async def description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  query = update.callback_query
  await query.answer()

  with open('nohu.json', 'r') as file:
    data = json.load(file)

  if query.data.startswith('desc_pot_'):
    if query.data == 'desc_pot_taixiu':
        amount = data.get('taixiu', {}).get('amount', 0)
        text = f"Số tiền trong hũ Tài Xỉu: <b>{format_currency(amount)}</b>"
    elif query.data == 'desc_pot_slot_machine':
        amount = data.get('slot_machine', {}).get('amount', 0)
        text = f"Số tiền trong hũ Slot Machine: <b>{format_currency(amount)}</b>"
    else:
        text = "Có lỗi xảy ra, vui lòng thử lại sau."
    await query.edit_message_text(text=text, parse_mode='HTML')
    return

  game_descriptions = {
      "desc_taixiu": (
          f"<b>➤ Tài Xỉu Chẵn Lẻ:</b> Game lắc 3 con xúc xắc, nếu tổng của cả 3 xúc xắc từ 3-10 thì là Xỉu, từ 11-18 thì là Tài. Người chơi ăn tiền dựa trên cược của mình\n"
          f"<b>📌 Tỉ lệ:</b> x{taixiu_multiplier} (tài/xỉu) | x{taixiu_chanle_multiplier} (tài/xỉu chẵn lẻ)\n"
          f"<b>➡️ Cược tối thiểu:</b> {format_currency(taixiu_min_bet)}\n"
          f"<b>🎮 Cú pháp:</b> <code>/taixiu [tài/xỉu] [tiền cược]</code>\n"
          f"VD: <code>/taixiu tài 10000</code>\n\n"
          f"Nội dung  |   Kết quả       | Tỉ lệ ăn\n"
          f"TC             |  12,14,16,18   |    x{taixiu_chanle_multiplier}\n"
          f"TL             |   11,13,15,17    |    x{taixiu_chanle_multiplier}\n"
          f"XC             |     4,6,8,10     |    x{taixiu_chanle_multiplier}\n"
          f"XL             |      3,5,7,9       |    x{taixiu_chanle_multiplier}\n"
          f"T               |      11 -> 18     |    x{taixiu_multiplier}\n"
          f"X               |      3  -> 10     |    x{taixiu_multiplier}"
      ),
      "desc_chanle": (
          f"<b>➤ Chẵn Lẻ:</b> Game lắc 1 con xúc xắc, người chơi sẽ cược số nút trên xúc xắc là chẵn hay lẻ. Người chơi ăn tiền dựa trên cược của mình\n"
          f"<b>📌 Tỉ lệ:</b> x{chanle_multiplier}\n"
          f"<b>➡️ Cược tối thiểu:</b> {format_currency(chanle_min_bet)}\n"
          f"<b>🎮 Cú pháp:</b> <code>/chanle [chẵn/lẻ] [tiền cược]</code>\n"
          f"VD: <code>/chanle le 10000</code>\n\n"
          f"Nội dung  |   Kết quả       | Tỉ lệ ăn\n"
          f"C               |     2,4,6          |    x{chanle_multiplier}\n"
          f"L               |      1,3,5          |    x{chanle_multiplier}"
      ),
      "desc_doanso": (
          f"<b>➤ Đoán Số:</b> Game lắc 1 con xúc xắc, người chơi sẽ cược số nút trên xúc xắc. Người chơi ăn tiền dựa trên cược của mình\n"
          f"<b>📌 Tỉ lệ:</b> x{doanso_multiplier}\n"
          f"<b>➡️ Cược tối thiểu:</b> {format_currency(doanso_min_bet)}\n"
          f"<b>🎮 Cú pháp:</b> <code>/doanso [số nút] [tiền cược]</code>\n"
          f"VD: <code>/doanso 6 10000</code>"
      ),
      "desc_slot_machine": (
          f"<b>➤ Slot Machine:</b> Game sử dụng máy đánh bài để quay kết quả, có 4 icon: số 7, chùm nho, quả chanh, bar\n"
          f"<b>📌 Three of a Kind:</b> Quay ra 3 icon giống nhau. Tiền thưởng sẽ x{three_of_a_kind_multiplier}\n"
          f"<b>📌 Double Seven:</b> Quay ra 2 icon số 7 nằm đầu tiên. Tiền thưởng sẽ x{double_seven_multiplier}\n"
          f"<b>📌 JackPot:</b> Quay ra 3 icon số 7. Giải thưởng đặc biệt: tiền thưởng sẽ x{jackpot_multiplier} và ăn toàn bộ tiền trong hũ\n"
          f"<b>🎁 Nổ Hũ:</b> mỗi 1 người chơi thua Slot Machine, trích 35% tiền cược thua vào trong hũ, cộng dồn đến khi có người nổ hũ sẽ ăn hết tiền trong hũ\n"
          f"<b>➡️ Cược tối thiểu:</b> {format_currency(slot_min_bet)}\n"
          f"<b>🎮 Cú pháp:</b> <code>/S [tiền cược]</code>\n"
          f"VD: <code>/S 10000</code>\n\n"
          f"Kết quả                       | Tỉ lệ ăn\n"
          f"7️⃣7️⃣7️⃣                     |    x{jackpot_multiplier}\n"
          f"7️⃣7️⃣[🍋,🍇,BAR]   |    x{double_seven_multiplier}\n"
          f"🍋🍋🍋                     |    x{three_of_a_kind_multiplier}\n"
          f"🍇🍇🍇                     |    x{three_of_a_kind_multiplier}\n"
          f"BAR BAR BAR            |    x{three_of_a_kind_multiplier}"
      ),
      "desc_darts": (
          f"<b>➤ Ném Phi Tiêu:</b> Ném ra 1 phi tiêu vào bia. Người chơi sẽ đoán ném vào vòng trắng hay đỏ. Nếu ném vào hồng tâm và đoán màu đỏ sẽ nhận x{darts_multiplier_aim} tiền thưởng, nếu ném trượt sẽ mất hết\n"
          f"<b>🎮 Cú pháp:</b> <code>/darts [T/D] [tiền cược]</code>\n"
          f"<b>➡️ Cược tối thiểu:</b> {format_currency(darts_min_bet)}\n"
          f"VD: <code>/darts t 50000</code>\n\n"
          f"Nội dung  |     Kết quả       | Tỉ lệ ăn\n"
          f"T               |  Vòng Trắng    |    x{darts_multiplier}\n"
          f"D               |    Vòng Đỏ       |    x{darts_multiplier}\n"
          f"D               |  Tâm Của Bia  |   x{darts_multiplier_aim}"
      ),
      "desc_bowling": (
          f"<b>➤ Bowling:</b> Ném 1 quả bóng Bowling vào 7 Ki gỗ. Người chơi đoán số Ki gỗ không bị ngã. Nếu ném trượt sẽ mất hết, nếu ném đổ toàn bộ và đoán số Ki gỗ còn lại là chẵn sẽ nhận x3 tiền thưởng\n"
          f"<b>🎮 Cú pháp:</b> <code>/bowling [bc/bl/bt/bx] [tiền cược]</code>\n"
          f"<b>➡️ Cược tối thiểu:</b> {format_currency(bowling_min_bet)}\n"
          f"VD: <code>/bowling [bc/bl/bt/bx] [tiền cược]</code>\n\n"
          f"Nội dung  |   Kết quả   | Tỉ lệ ăn\n"
          f"BC             |     2,4,6      |    x{bowling_tai_xiu_chan_le_multiplier}\n"
          f"BL             |      1,3,5       |    x{bowling_tai_xiu_chan_le_multiplier}\n"
          f"BT             |      4,5,6      |    x{bowling_tai_xiu_chan_le_multiplier}\n"
          f"BX             |      1,2,3      |    x{bowling_tai_xiu_chan_le_multiplier}\n"
          f"BC             |         0         |    x{bowling_strike_multiplier}"
      )
  }

  description = game_descriptions.get(query.data, "Mô tả không khả dụng.")
  await query.edit_message_text(text=description, parse_mode='HTML')

async def pot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  keyboard = [
      [InlineKeyboardButton("Tài Xỉu", callback_data='desc_pot_taixiu')],
      [InlineKeyboardButton("Slot Machine", callback_data='desc_pot_slot_machine')]
  ]

  reply_markup = InlineKeyboardMarkup(keyboard)
  await update.message.reply_text('Chọn Hũ Để Xem Số Tiền', reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

  help_text = """
<b>Các Lệnh Có Sẵn</b>
/bxh - Bảng Xếp Hạng Đại Gia
/game - Danh Sách Các Game
/pot - Xem Tiền Trong Hũ
/taixiu - Game Tài xỉu
/doanso - Game Đoán Số
/chanle - Game Chẵn Lẻ
/S - Game Slot Machine
/register - Đăng Kí Tài Khoản
/profile - Xem Thông Tin Tài Khoản
/giftcode - Nhập Giftcode
/chuyentien - Chuyển Tiền Cho Người Khác
/money - Xem Tiền Người Khác
/deleteaccount - Xoá Tài Khoản
"""

  if is_user_admin(update.effective_user.id):

      admin_help_text = """
<b>Lệnh Của Admin</b>
/congtien - Cộng Tiền Cho Người Dùng 
/trutien - Trừ Tiền Của Người Dùng 
/taocode - Tạo Giftcode Mới
/listcode - Liệt Kê Tất Cả Giftcodes
/mophien - Mở Phiên Tài Xỉu Trong 60s Để Đặt Cược
"""
      help_text += admin_help_text  

  await update.message.reply_text(help_text,parse_mode='HTML')

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

  with open('data.json', 'r', encoding='utf-8') as f:
      users = json.load(f)

  sorted_users = sorted(users, key=lambda x: x['balance'], reverse=True)

  message = "Bảng Xếp Hạng Đại Gia\n\n"
  for i, user in enumerate(sorted_users, start=1):
      balance_formatted = f"{user['balance']:,}"
      message += f"{i}. {user['full_name']} - {balance_formatted} VNĐ\n"

  await update.message.reply_text(message)

async def trutien(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  if not is_user_admin(update.effective_user.id):
      await update.message.reply_text('Bạn không có quyền sử dụng lệnh này.')
      return

  args = context.args
  if len(args) != 2 or not args[1].isdigit():
      await update.message.reply_text('Cú pháp không đúng. Sử dụng: /trutien @username số_tiền')
      return

  username = args[0].lstrip('@')
  amount = int(args[1])

  with open('data.json', 'r+', encoding='utf-8') as file:
      users = json.load(file)
      user = next((u for u in users if u['user_name'] == username), None)
      if user:
          if user['balance'] >= amount:
              user['balance'] -= amount
              file.seek(0)
              json.dump(users, file, indent=4, ensure_ascii=False)
              file.truncate()
              await update.message.reply_text(f"Đã trừ <b>{amount:,} VNĐ</b> vào tài khoản của {user['full_name']}\nSố dư còn lại: <b>{user['balance']:,} VNĐ</b>",parse_mode='HTML')
          else:
              await update.message.reply_text(f"Tài khoản của {user['full_name']} không đủ để trừ {amount:,} VNĐ.")
      else:
          await update.message.reply_text('Không tìm thấy người dùng.')

async def money(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  args = context.args
  if len(args) != 1:
      await update.message.reply_text('Sử dụng lệnh sai. Hãy nhập theo mẫu: /money @username')
      return

  username = args[0].lstrip('@')

  with open('data.json', 'r', encoding='utf-8') as file:
      users = json.load(file)
      user = next((u for u in users if u['user_name'] == username), None)

      if user:
          balance_formatted = f"{user['balance']:,}"
          await update.message.reply_text(f'Số dư của {user["full_name"]} là <b>{balance_formatted} VNĐ</b>',parse_mode='HTML')
      else:
          await update.message.reply_text('Không tìm thấy người dùng.')

async def deleteaccount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  user_id = update.effective_user.id

  try:
      with open('data.json', 'r+', encoding='utf-8') as file:
          users = json.load(file)

          if str(user_id) in users:
              del users[str(user_id)]  

              file.seek(0)
              json.dump(users, file, indent=4, ensure_ascii=False)
              file.truncate()  

              await update.message.reply_text("Tài khoản của bạn đã được xóa thành công.")
          else:
              await update.message.reply_text("Tài khoản không tồn tại.")
  except FileNotFoundError:
      await update.message.reply_text("Không tìm thấy dữ liệu.")

async def congtien(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  if not is_user_admin(update.effective_user.id):
      await update.message.reply_text('Bạn không có quyền sử dụng lệnh này.')
      return

  args = context.args
  if len(args) != 2 or not args[1].isdigit():
      await update.message.reply_text('Cú pháp không đúng. Sử dụng: /congtien @username số_tiền')
      return

  username = args[0].lstrip('@')
  amount = int(args[1])

  with open('data.json', 'r+', encoding='utf-8') as file:
      users = json.load(file)
      user = next((u for u in users if u['user_name'] == username), None)
      if user:
          user['balance'] += amount
          file.seek(0)
          json.dump(users, file, indent=4, ensure_ascii=False)
          file.truncate()
          await update.message.reply_text(f"Đã cộng <b>{amount:,} VNĐ</b> vào tài khoản của {user['full_name']}\nSố dư hiện tại: <b>{user['balance']:,} VNĐ</b>",parse_mode='HTML')
      else:
          await update.message.reply_text('Không tìm thấy người dùng.')

async def listcode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  if not is_user_admin(update.effective_user.id):
      await update.message.reply_text('Bạn không có quyền sử dụng lệnh này.')
      return

  try:
      with open('giftcode.json', 'r', encoding='utf-8') as file:
          codes = json.load(file)

      codes_to_remove = [code for code, details in codes.items() if details['uses'] <= 0]
      for code in codes_to_remove:
          del codes[code]

      if codes_to_remove:

          with open('giftcode.json', 'w', encoding='utf-8') as file:
              json.dump(codes, file, indent=4, ensure_ascii=False)

      if not codes:
          await update.message.reply_text("Hiện không có giftcode nào.")
          return

      message_text = "<b>Danh sách Giftcode</b>\n"
      for code, details in codes.items():
          amount_formatted = "{:,}".format(details['amount'])
          message_text += f"Code: <code>{code}</code>, Số tiền: {amount_formatted} VNĐ, Lượt dùng: {details['uses']}\n\n"
      await update.message.reply_text(message_text, parse_mode='HTML')
  except FileNotFoundError:
      await update.message.reply_text("Không tìm thấy dữ liệu giftcode.")

async def chuyentien(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    if len(args) != 2 or not args[1].isdigit():
        await update.message.reply_text('Cú pháp không hợp lệ. Sử dụng: /chuyentien @username số_tiền')
        return

    receiver_username = args[0].lstrip('@')  
    amount = int(args[1])
    sender_id = update.effective_user.id

    if amount <= 0:
        await update.message.reply_text('Số tiền chuyển phải lớn hơn 0.')
        return

    try:
        with open('data.json', 'r+', encoding='utf-8') as file:
            users = json.load(file)

            sender = None
            receiver = None
            for user in users:
                if user['user_id'] == sender_id:
                    sender = user
                if user['user_name'] == receiver_username:
                    receiver = user

            if not sender:
                await update.message.reply_text('Không tìm thấy thông tin của bạn trong hệ thống. Đảm bảo bạn đã đăng ký.')
                return

            if not receiver:
                await update.message.reply_text('Không tìm thấy người nhận.')
                return

            if sender['balance'] < amount:
                await update.message.reply_text('Bạn không có đủ tiền để thực hiện giao dịch này.')
                return

            sender['balance'] -= amount
            receiver['balance'] += amount

            file.seek(0)
            json.dump(users, file, indent=4, ensure_ascii=False)
            file.truncate()

            await update.message.reply_text(f"💵Chuyển thành công <b>{amount:,} VNĐ</b> tới {receiver['full_name']}✨\n💳 Số dư còn lại của bạn: <b>{sender['balance']:,} VNĐ</b>",parse_mode='HTML')

    except Exception as e:
        await update.message.reply_text(f'Có lỗi xảy ra: {e}')

async def taocode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  if not is_user_admin(update.effective_user.id):
      await update.message.reply_text('Bạn không có quyền sử dụng lệnh này.')
      return

  args = context.args
  if len(args) != 3 or not args[1].isdigit() or not args[2].isdigit():
      await update.message.reply_text('Cú pháp không đúng. Sử dụng: /taocode CODE [số_tiền] [số_lượt_dùng]')
      return

  code = args[0].upper()
  amount = int(args[1])
  uses = int(args[2])

  with open('giftcode.json', 'r+', encoding='utf-8') as file:
      giftcodes = json.load(file)
      if code in giftcodes:
          await update.message.reply_text('Giftcode này đã tồn tại.')
      else:
          giftcodes[code] = {'amount': amount, 'uses': uses}
          file.seek(0)
          json.dump(giftcodes, file, indent=4, ensure_ascii=False)
          file.truncate()
          await update.message.reply_text(f'Giftcode {code} đã được tạo với {amount:,} VNĐ và {uses} lượt sử dụng✨')

async def giftcode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  user_id = update.effective_user.id
  user_name = update.effective_user.first_name
  if not context.args:
      await update.message.reply_text('Vui lòng nhập giftcode. Ví dụ: /giftcode GIFT100')
      return

  gift_code = context.args[0].upper()

  with open('giftcode.json', 'r+', encoding='utf-8') as gift_file:
      giftcodes = json.load(gift_file)
      if gift_code in giftcodes and giftcodes[gift_code]['uses'] > 0:

          with open('data.json', 'r+', encoding='utf-8') as user_file:
              users = json.load(user_file)
              user = next((u for u in users if u['user_id'] == user_id), None)
              if user:
                  if gift_code in user.get('used_giftcodes', []):
                      await update.message.reply_text('Bạn đã sử dụng giftcode này rồi.')
                      return
                  else:
                      user.setdefault('used_giftcodes', []).append(gift_code)
                      user['balance'] += giftcodes[gift_code]['amount']
                      giftcodes[gift_code]['uses'] -= 1
                      await update.message.reply_text(f'Bạn đã nhận được <b>{giftcodes[gift_code]["amount"]:,} VNĐ</b> từ giftcode <b>{gift_code}</b>\nSố dư của bạn: <b>{user["balance"]:,} VNĐ</b>',parse_mode='HTML')
              else:
                  await update.message.reply_text('Thông tin của bạn chưa được đăng ký. Hãy sử dụng lệnh /register.')
                  return

              user_file.seek(0)
              json.dump(users, user_file, indent=4, ensure_ascii=False)
              user_file.truncate()

          gift_file.seek(0)
          json.dump(giftcodes, gift_file, indent=4, ensure_ascii=False)
          gift_file.truncate()
      else:
          await update.message.reply_text('Giftcode không hợp lệ hoặc đã hết lượt sử dụng.')

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  user_id = update.effective_user.id
  user_name = update.effective_user.username

  full_name = update.effective_user.full_name

  with open('data.json', 'r+', encoding='utf-8') as file:
      users = json.load(file)
      if any(user['user_id'] == user_id for user in users):
          await update.message.reply_text('Bạn đã đăng ký rồi.')
      else:

          new_user = {
              "user_id": user_id,
              "user_name": user_name,
              "full_name": full_name,  
              "balance": 50000
          }
          users.append(new_user)
          file.seek(0)
          json.dump(users, file, indent=4, ensure_ascii=False)
          file.truncate()
          await update.message.reply_text('Đăng ký thành công.')

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  user_id = update.effective_user.id

  with open("data.json", "r", encoding="utf-8") as file:
      users = json.load(file)
      user = next((user for user in users if user["user_id"] == user_id), None)
      if user:
          await update.message.reply_text(f'👤User ID: {user["user_id"]}\n🪪Tên: {user["full_name"]}\n💳Số dư: <b>{"{:,}".format(user["balance"])} VNĐ</b>',parse_mode='HTML')

      else:
          await update.message.reply_text('Thông tin của bạn chưa được đăng ký. Hãy sử dụng lệnh /register.')