#import libraries

import telegram
from telegram.ext import *
from datetime import *
import csv
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import requests
import json
import pandas as pd
import os, sys
from datetime import *
import gspread_dataframe

#Set your parh
path = './Documents/4D&K'

#BOT API
BOT_KEY = '1823840395:AAEP5ciz50f3mpN8HZniufVpyi6IZwy1L3M'

#Set scope when autheticating
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive.file',
         'https://www.googleapis.com/auth/drive']

# Authenticate using your credentials
creds = ServiceAccountCredentials.from_json_keyfile_name("Python Sheets API Key.json",scope)

# Initialize the client
client = gspread.authorize(creds)

#Open the sheet by name
expenses_sheet = client.open("4D&K").worksheet("Expenses")
sales_sheet = client.open("4D&K").worksheet("Sales")

# start command
def start_command(update,context):
    update.message.reply_text("""Is this /expenses or a /sales?""")

# user chooses /expenses or /sales
def input_expense(update, context):
    entry = update.message.text.split(',')
    try:
        entry[1] = float(entry[1])
    except:
        # If this fails, the input text was not separated by a comma
        update.message.reply_text("""Input the description, amount. Don't forget the comma.

Sales categories are Dressed Chicken and Live Weight. Please note that by-product is under the Dressed Chicken category.
""")
    # Now we will build the buttons that will be displayed to the user. For this example, I chose 9 pre-set Types:
    buttons = [[]]
    buttons.append([])
    buttons.append([])
    buttons[0].append(telegram.InlineKeyboardButton(text='Transportation', callback_data=str(update.message.message_id) + '=' + str(update.message.date) + '=' + 'Transportation' + '=' + str(entry[0]) + '=' + str(entry[1])))
    buttons[0].append(telegram.InlineKeyboardButton(text='Dressing Fee', callback_data=str(update.message.message_id) + '=' + str(update.message.date) + '=' + 'Dressing Fee' + '=' + str(entry[0]) + '=' + str(entry[1])))
    buttons[0].append(telegram.InlineKeyboardButton(text='Plastic', callback_data=str(update.message.message_id) + '=' + str(update.message.date) + '=' + 'Plastic' + '=' + str(entry[0]) + '=' + str(entry[1])))
    buttons[1].append(telegram.InlineKeyboardButton(text='Ice', callback_data=str(update.message.message_id) + '=' + str(update.message.date) + '=' + 'Ice' + '=' + str(entry[0]) + '=' + str(entry[1])))
    buttons[1].append(telegram.InlineKeyboardButton(text='Labor', callback_data=str(update.message.message_id) + '=' + str(update.message.date) + '=' + 'Labor' + '=' + str(entry[0]) + '=' + str(entry[1])))
    buttons[1].append(telegram.InlineKeyboardButton(text='Other Expenses', callback_data=str(update.message.message_id) + '=' + str(update.message.date) + '=' + 'Other Expenses' + '=' + str(entry[0]) + '=' + str(entry[1])))
    buttons[2].append(telegram.InlineKeyboardButton(text='Dressed Chicken', callback_data=str(update.message.message_id) + '=' + str(update.message.date) + '=' + 'Dressed Chicken' + '=' + str(entry[0]) + '=' + str(entry[1])))
    buttons[2].append(telegram.InlineKeyboardButton(text='Live Weight', callback_data=str(update.message.message_id) + '=' + str(update.message.date) + '=' + 'Live Weight' + '=' + str(entry[0]) + '=' + str(entry[1])))
    #buttons[2].append(telegram.InlineKeyboardButton(text='Travel', callback_data=str(update.message.message_id) + '=' + str(update.message.date) + '=' + 'Travel' + '=' + str(entry[0]) + '=' + str(entry[1])))
    #buttons[2].append(telegram.InlineKeyboardButton(text='Services', callback_data=str(update.message.message_id) + '=' + str(update.message.date) + '=' + 'Services' + '=' + str(entry[0]) + '=' + str(entry[1])))
    #buttons[2].append(telegram.InlineKeyboardButton(text='Sport', callback_data=str(update.message.message_id) + '=' + str(update.message.date) + '=' + 'Sport' + '=' + str(entry[0]) + '=' + str(entry[1])))

    # With the buttons, we create a keyboard:
    keyboard = telegram.InlineKeyboardMarkup(buttons)

    # And we send the reply to the channel:
    bot.send_message(update.message.chat_id, update.message.text, reply_markup=keyboard)

#input the data to the spreadsheet
def callback_query_handler(update, context):
    try:
        # Once the user chooses a Type, we can go ahead and delete the message to reduce clutter in the channel:
        bot.delete_message(update.callback_query.message.chat_id, str(update.callback_query.message.message_id))

        #keep updated with the gsheet
        client = gspread.authorize(creds)
        expenses_sheet = client.open("4D&K").worksheet("Expenses")
        sales_sheet = client.open("4D&K").worksheet("Sales")
        expenses_data = expenses_sheet.get_all_records()
        sales_data = sales_sheet.get_all_records()


        #insert data to GSheets
        date_today = date.today().isoformat()
        input_type = update.callback_query.data.split('=')[2]
        description = update.callback_query.data.split('=')[3]
        price = update.callback_query.data.split('=')[4]
        row_to_insert = [date_today, input_type, description, price]

        if input_type == "Transportation" or input_type == "Dressing Fee" or input_type == "Plastic" or input_type == "Ice" or input_type == "Labor" or input_type == "Other Expenses":
            expenses_sheet.insert_row(row_to_insert, len(expenses_data) + 2)

        if input_type == "Dressed Chicken" or input_type == "Live Weight":
            sales_sheet.insert_row(row_to_insert, len(sales_data) + 2)

        bot.send_message(update.callback_query.message.chat_id, 'Saved: ' + input_type + ' - ' + description)
        bot.send_message(update.callback_query.message.chat_id,"""To input another entry, just following the same format. To restart, type or click /start. To end the session, type or click /end.""")

    except:
        return

#end command
def end_command(update,context):
    update.message.reply_text("You have chosen to end the session. Thank you, and have a great day!")

#build the main funtion
bot = telegram.Bot(token=BOT_KEY)

def main():
    updater = Updater(BOT_KEY, use_context = True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("end", end_command))
    dp.add_handler(MessageHandler(Filters.all, input_expense))
    dp.add_handler(CallbackQueryHandler(callback_query_handler))

    updater.start_polling()
    updater.idle()

main()
