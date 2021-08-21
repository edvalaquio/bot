# import libraries
import logging
from datetime import *

import gspread
import telegram
from oauth2client.service_account import ServiceAccountCredentials
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
)

import config
import constants


# Initializing logger
logging.basicConfig(
    format="%(asctime)s %(levelname)-5.5s [%(name)s:%(lineno)s][%(threadName)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# build the main funtion
chatbot_client = telegram.Bot(token=config.BOT_KEY)


def get_service_account_credentials():
    return ServiceAccountCredentials.from_json_keyfile_name(
        filename=config.GSPREAD_CREDENTIALS_LOCATION,
        scopes=constants.GSPREAD_SERVICE_ACCOUNT_SCOPES,
    )


# start command
def start_command(update, context):
    logger.info("Received /start command from user - ")
    update.message.reply_text("Is this /expenses or a /sales?")


# user chooses /expenses or /sales
def input_expense(update, context):
    try:
        # Unpack message sent by user after `split`
        # `ValueError` will be raised if the length of the split message
        # is less than two
        description, amount = update.message.text.split(",")
        # Verifies whether if amount provided by user is a number
        assert int(amount) or float(amount)
    except (AssertionError, ValueError):
        # If this fails, the input text was not separated by a comma
        message = (
            "Input the description, amount. Don't forget the comma.\n\n"
            "Sales categories are Dressed Chicken and Live Weight. "
            "Please note that by-product is under the Dressed Chicken category."
        )
        update.message.reply_text(message)
        return

    # Now we will build the buttons that will be displayed to the user. For this example, I chose 9 pre-set Types:
    buttons = [[]]
    buttons.append([])
    buttons.append([])
    buttons[0].append(
        telegram.InlineKeyboardButton(
            text="Transportation",
            callback_data=str(update.message.message_id)
            + "="
            + str(update.message.date)
            + "="
            + "Transportation"
            + "="
            + str(description)
            + "="
            + str(amount),
        )
    )
    buttons[0].append(
        telegram.InlineKeyboardButton(
            text="Dressing Fee",
            callback_data=str(update.message.message_id)
            + "="
            + str(update.message.date)
            + "="
            + "Dressing Fee"
            + "="
            + str(description)
            + "="
            + str(amount),
        )
    )
    buttons[0].append(
        telegram.InlineKeyboardButton(
            text="Plastic",
            callback_data=str(update.message.message_id)
            + "="
            + str(update.message.date)
            + "="
            + "Plastic"
            + "="
            + str(description)
            + "="
            + str(amount),
        )
    )
    buttons[1].append(
        telegram.InlineKeyboardButton(
            text="Ice",
            callback_data=str(update.message.message_id)
            + "="
            + str(update.message.date)
            + "="
            + "Ice"
            + "="
            + str(description)
            + "="
            + str(amount),
        )
    )
    buttons[1].append(
        telegram.InlineKeyboardButton(
            text="Labor",
            callback_data=str(update.message.message_id)
            + "="
            + str(update.message.date)
            + "="
            + "Labor"
            + "="
            + str(description)
            + "="
            + str(amount),
        )
    )
    buttons[1].append(
        telegram.InlineKeyboardButton(
            text="Other Expenses",
            callback_data=str(update.message.message_id)
            + "="
            + str(update.message.date)
            + "="
            + "Other Expenses"
            + "="
            + str(description)
            + "="
            + str(amount),
        )
    )
    buttons[2].append(
        telegram.InlineKeyboardButton(
            text="Dressed Chicken",
            callback_data=str(update.message.message_id)
            + "="
            + str(update.message.date)
            + "="
            + "Dressed Chicken"
            + "="
            + str(description)
            + "="
            + str(amount),
        )
    )
    buttons[2].append(
        telegram.InlineKeyboardButton(
            text="Live Weight",
            callback_data=str(update.message.message_id)
            + "="
            + str(update.message.date)
            + "="
            + "Live Weight"
            + "="
            + str(description)
            + "="
            + str(amount),
        )
    )
    # buttons[2].append(telegram.InlineKeyboardButton(text='Travel', callback_data=str(update.message.message_id) + '=' + str(update.message.date) + '=' + 'Travel' + '=' + str(description) + '=' + str(amount)))
    # buttons[2].append(telegram.InlineKeyboardButton(text='Services', callback_data=str(update.message.message_id) + '=' + str(update.message.date) + '=' + 'Services' + '=' + str(description) + '=' + str(amount)))
    # buttons[2].append(telegram.InlineKeyboardButton(text='Sport', callback_data=str(update.message.message_id) + '=' + str(update.message.date) + '=' + 'Sport' + '=' + str(description) + '=' + str(amount)))

    # With the buttons, we create a keyboard:
    keyboard = telegram.InlineKeyboardMarkup(buttons)

    # And we send the reply to the channel:
    chatbot_client.send_message(
        update.message.chat_id, update.message.text, reply_markup=keyboard
    )


# input the data to the spreadsheet
def callback_query_handler(update, context):
    try:
        # Once the user chooses a Type, we can go ahead and delete the message to reduce clutter in the channel:
        chatbot_client.delete_message(
            update.callback_query.message.chat_id,
            str(update.callback_query.message.message_id),
        )

        # keep updated with the gsheet
        credentials = get_service_account_credentials()
        client = gspread.authorize(credentials)
        expenses_sheet = client.open("4D&K").worksheet("Expenses")
        sales_sheet = client.open("4D&K").worksheet("Sales")
        expenses_data = expenses_sheet.get_all_records()
        sales_data = sales_sheet.get_all_records()

        # insert data to GSheets
        date_today = date.today().isoformat()
        input_type = update.callback_query.data.split("=")[2]
        description = update.callback_query.data.split("=")[3]
        price = update.callback_query.data.split("=")[4]
        row_to_insert = [date_today, input_type, description, price]

        if (
            input_type == "Transportation"
            or input_type == "Dressing Fee"
            or input_type == "Plastic"
            or input_type == "Ice"
            or input_type == "Labor"
            or input_type == "Other Expenses"
        ):
            expenses_sheet.insert_row(row_to_insert, len(expenses_data) + 2)

        if input_type == "Dressed Chicken" or input_type == "Live Weight":
            sales_sheet.insert_row(row_to_insert, len(sales_data) + 2)

        chatbot_client.send_message(
            update.callback_query.message.chat_id,
            "Saved: " + input_type + " - " + description,
        )
        chatbot_client.send_message(
            update.callback_query.message.chat_id,
            """To input another entry, just following the same format. To restart, type or click /start. To end the session, type or click /end.""",
        )

    except:
        return


# end command
def end_command(update, context):
    update.message.reply_text(
        "You have chosen to end the session. Thank you, and have a great day!"
    )


def main():
    logger.info("Process started")
    updater = Updater(config.BOT_KEY, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("end", end_command))
    dp.add_handler(MessageHandler(Filters.all, input_expense))
    dp.add_handler(CallbackQueryHandler(callback_query_handler))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
