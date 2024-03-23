from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import random
import string
import json
from datetime import datetime
from unidecode import unidecode
import pytz

vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
from function import format_currency

def clean_name(name):
  name_lower = name.lower()
  name_without_accents = unidecode(name_lower)
  name_cleaned = name_without_accents.replace(" ", "")
  return name_cleaned

def remove_banking_request(user_id):
  try:
      with open("banking.json", "r") as file:
          data = json.load(file)
      if str(user_id) in data:
          del data[str(user_id)]  
          with open("banking.json", "w") as file:
              json.dump(data, file, indent=4)  
  except FileNotFoundError:
      pass
  except json.JSONDecodeError:
      print("Lỗi rồi")

def update_balance(user_id, amount):
  try:
      with open('data.json', 'r') as file:
          users = json.load(file)
  except FileNotFoundError:
      print("File không tồn tại.")
      return False
  user_found = False
  for user in users:
      if user["user_id"] == user_id:
          user["balance"] += amount
          user_found = True
          break

  if not user_found:
      print("Không tìm thấy người dùng.")
      return False
  try:
      with open('data.json', 'w', encoding='utf-8') as file:
          json.dump(users, file, ensure_ascii=False, indent=4)
  except Exception as e:
      print(f"Không thể cập nhật dữ liệu. Lỗi: {e}")
      return False

  return True

def save_banking_data(user_id, username, so_tien, status="pending"):
  try:
      with open("banking.json", "r") as file:
          data = json.load(file)
  except FileNotFoundError:
      data = {}

  data[str(user_id)] = {
      "username": username,
      "so_tien": so_tien,
      "time": datetime.now().isoformat(),
      "status": status
  }

  with open("banking.json", "w", encoding='utf-8') as file:
      json.dump(data, file, ensure_ascii=False, indent=4)

def check_banking_status(user_id):
  try:
      with open("banking.json", "r") as file:
          data = json.load(file)
      if str(user_id) in data and data[str(user_id)]["status"] == "pending":
          return True
  except FileNotFoundError:
      pass
  return False

def update_banking_status(user_id, status):
  try:
      with open("banking.json", "r") as file:
          data = json.load(file)
      if str(user_id) in data:
          data[str(user_id)]["status"] = status
          with open("banking.json", "w") as file:
              json.dump(data, file, indent=4)
  except FileNotFoundError:
      pass

async def naptien(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  if update.effective_chat.type == "private":
    user = update.effective_user
    if check_banking_status(user.id):
      await update.message.reply_text("Bạn đang có yêu cầu nạp tiền đang chờ duyệt. Vui lòng chờ xử lí.")
      return
    try:
      so_tien = context.args[0]

      if not so_tien.isdigit():
        await update.message.reply_text("Số tiền không hợp lệ ❌")
        return
      if int(so_tien) < 10000:
        await update.message.reply_text(f"Số tiền nạp tối thiểu là {format_currency(10000)}",parse_mode="HTML")
        return

      if user.full_name:
        full_name = clean_name(user.full_name)
      else:
         full_name = "user"
      letters = ''.join(random.choices(string.ascii_uppercase, k=5))
      digits = ''.join(random.choices(string.digits, k=7))
      random_str = letters + digits
      noidung = f"{full_name} {random_str}"
      username = user.username

      message_text = (f"STK: <code>99999999999999</code>\n"
                      f"Ngân hàng: <b>MBBANK</b>\n"
                      f"Chủ tài khoản: <b>TRẦN VĂN A</b>\n\n"
                      f"Vui lòng nạp tiền theo đúng nội dung\n"
                      f"<code>{noidung}</code>\n"
                     f"Sau khi nạp hãy nhấn Xác Nhận\n")

      keyboard = [[InlineKeyboardButton("Xác Nhận ✅", callback_data=f"bank:confirm_{so_tien}_{noidung}_{user.id}"),
               InlineKeyboardButton("Huỷ Bỏ ❌", callback_data=f"bank:cancel_{user.id}")]]
      reply_markup = InlineKeyboardMarkup(keyboard)

      await update.message.reply_text(message_text, reply_markup=reply_markup,parse_mode="HTML")
      save_banking_data(user.id, username, so_tien)

    except IndexError:
      await update.message.reply_text("Vui lòng nhập số tiền cần nạp. Ví dụ: /naptien 100000")
  else:
      await update.message.reply_text("Lệnh này chỉ hoạt động trong tin nhắn riêng với bot.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
      query = update.callback_query
      await query.answer()
      data = query.data
      args = data.split("_")

      if args[0] == "bank:confirm":
          so_tien, noidung, user_id = args[1:]
          admin_message = (f"Người nạp: {query.from_user.full_name} (ID: {user_id})\n"
                           f"Số tiền: {format_currency(int(so_tien))}\n"
                           f"Nội dung: {noidung}\n"
                           f"Thời gian nạp: {datetime.now(vietnam_tz).strftime('%H:%M:%S %d-%m-%Y')}")
          keyboard = [
              [InlineKeyboardButton("Duyệt ✅", callback_data=f"bank:approve_{user_id}_{so_tien}"),
               InlineKeyboardButton("Từ Chối ❌", callback_data=f"bank:deny_{user_id}_{so_tien}")]
          ]
          reply_markup = InlineKeyboardMarkup(keyboard)
          await context.bot.send_message(chat_id=5145402317, text=admin_message, reply_markup=reply_markup,parse_mode="HTML")
          await query.edit_message_text(text=f"Yêu cầu nạp tiền đã được gửi đến quản trị viên 📤\nSố tiền: {format_currency(int(so_tien))} \nNội dung: <code>{noidung}</code>\nNgày tạo đơn: {datetime.now(vietnam_tz).strftime('%H:%M:%S %d-%m-%Y')}",parse_mode="HTML")

      elif args[0] == "bank:cancel":
          user_id = args[1]
          remove_banking_request(user_id)
          await query.edit_message_text(text="Bạn đã huỷ bỏ yêu cầu nạp tiền.")

      elif args[0] == "bank:approve":
          user_id, so_tien = args[1:]
          so_tien = int(so_tien)
          if update_balance(int(user_id), so_tien):
            user = await context.bot.get_chat(user_id)
            user_name = user.full_name  
            success_message = f"Nạp thành công {format_currency(so_tien)} vào tài khoản của bạn."
            await context.bot.send_message(chat_id=user_id, text=success_message,parse_mode="HTML")
            await query.edit_message_text(text=f"Đã duyệt yêu cầu nạp {format_currency(so_tien)} của {user_name}",parse_mode="HTML")
            update_banking_status(user_id, "completed")
          else:
            await query.edit_message_text(text=f"Có lỗi xảy ra khi nạp.")

      elif args[0] == "bank:deny":
          user_id, so_tien = args[1:]
          user = await context.bot.get_chat(user_id)
          user_name = user.full_name 
          fail_message = f"Yêu cầu nạp {format_currency(int(so_tien))} của bạn đã bị từ chối"
          await context.bot.send_message(chat_id=user_id, text=fail_message,parse_mode="HTML")
          await query.edit_message_text(text=f"Đã từ chối yêu cầu nạp {format_currency(int(so_tien))} của {user_name}",parse_mode="HTML")
          update_banking_status(user_id, "completed")