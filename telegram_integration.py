import telegram
import pymongo_implementation as pyimp
import config
import time
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import threading


logging.basicConfig(format='\n%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

updater = Updater(token=config.TELEGRAM_BOT_TOKEN, use_context=True) 

# 'AUX' FUNCTIONS
def logMessage(message):	
	print("\n{} - [{} - {}] {} - ( [{}] - {} {} - '{}' ).".format(message.date, message.chat.id, message.message_id, message.text, message.from_user.id, message.from_user.first_name, message.from_user.last_name, message.from_user.username))

def logUserMessage(update, context):
	logMessage(update.message)

def shutdown():
	updater.stop()
	updater.is_idle = False

def getTasksFromDatabase(user_id):
	tasks = []
	for task in pyimp.getTasks(user_id):
		tasks.append(task)
	return tasks

# 'HANDLER' FUNCTIONS
def start(update, context):
	logUserMessage(update, context)
	message	= context.bot.send_message(chat_id=update.effective_chat.id, text='Im a bot, please talk to me!')
	logMessage(message)

def stop(update, context):
	logUserMessage(update, context)
	if update.effective_user.id == config.ADMIN_USER_ID:
		message = context.bot.send_message(chat_id=update.effective_chat.id, text='Killing process...')
		logMessage(message)
		threading.Thread(target=shutdown).start()
	else:
		message =context.bot.send_message(chat_id=update.effective_chat.id, text='You dont have permission to do this. Stop!')
		logMessage(message)


def showTasks(update, context):
	# is bot or user validation todo i think thats not really needed
	logUserMessage(update, context)
	tasks = getTasksFromDatabase(update.effective_user.id)
	
	if tasks:	
		message = context.bot.send_message(text='TASKS', chat_id=update.effective_chat.id)
		logMessage(message)

		for task in tasks:

			message_text = ' - ' + task["task"] + '\n---> {}'.format('completed' if task['is_completed'] else 'not completed')
			message = context.bot.send_message(text=message_text, chat_id=update.effective_chat.id)
			logMessage(message)
			time.sleep(0.05)
	else:
		message = context.bot.send_message(chat_id=update.effective_chat.id, text='You dont have any tasks. Try adding one')
		logMessage(message)

def addTask(update, context):
	logUserMessage(update, context)
	task = ' '.join(context.args)
	if task:
		task_text = pyimp.addTask(update.effective_user.id, task)
		message = context.bot.send_message(chat_id=update.effective_chat.id, text=task_text)
		logMessage(message)
		showTasks(update, context)
	else:
		message = context.bot.send_message(chat_id=update.effective_chat.id, text="You din't say what do you to add. Try /add YOUR TASK .")
		logMessage(message)

def deleteTask(update, context):
	logUserMessage(update, context)
	task = ' '.join(context.args)
	if task:
		task_text = pyimp.deleteTask(update.effective_user.id, task)
		message = context.bot.send_message(chat_id=update.effective_chat.id, text=task_text)
		logMessage(message)
		showTasks(update, context)
	else:
		message = context.bot.send_message(chat_id=update.effective_chat.id, text="You din't say which task do you to delete. Try /delete YOUR TASK .")
		logMessage(message)

def completeTask(update, context):
	logUserMessage(update, context)
	task = ' '.join(context.args)
	if task:
		task_text, already_completed = pyimp.completeTask(update.effective_user.id, task)
		message = context.bot.send_message(chat_id=update.effective_chat.id, text=task_text)
		logMessage(message)
		if not already_completed:
			showTasks(update, context)
	else:
		message = context.bot.send_message(chat_id=update.effective_chat.id, text="You din't say which task do you to complete. Try /complete YOUR TASK .")
		logMessage(message)

def uncompleteTask(update, context):
	logUserMessage(update, context)
	task = ' '.join(context.args)
	if task:
		task_text = pyimp.uncompleteTask(update.effective_user.id, task)
		message = context.bot.send_message(chat_id=update.effective_chat.id, text=task_text)
		logMessage(message)
		showTasks(update, context)
	else:
		message = context.bot.send_message(chat_id=update.effective_chat.id, text="You din't say which task do you to complete. Try /complete YOUR TASK .")
		logMessage(message)

def sendMessage(update, context):
	logUserMessage(update, context)
	if update.effective_user.id == config.ADMIN_USER_ID:
		args = context.args
		if args:
			if len(args) > 1:
				try:
					chat_id = int(args[0])
					chat_id = args[0]
					text = args[1:]
					text = ' '.join(text)
					context.bot.send_message(chat_id=chat_id, text=text)
					message = context.bot.send_message(chat_id=update.effective_chat.id, text="Sending '{}' to {}".format(text, chat_id))
					logMessage(message)
				except:
					message = context.bot.send_message(chat_id=update.effective_chat.id, text='Invalid chat id.')
					logMessage(message)
		else:
			message = context.bot.send_message(chat_id=update.effective_chat.id, text='Make sure you are typing the arguments')
			logMessage(message)
	else:
		message = context.bot.send_message(chat_id=update.effective_chat.id, text='You dont have permission to do this. Stop!')
		logMessage(message)

def unknownCommand(update, context):
	logUserMessage(update, context)
	message = context.bot.send_message(chat_id=update.effective_chat.id, text='This command does not exist, try a different one.')
	logMessage(message)

def main():
	dispatcher = updater.dispatcher
	bot = telegram.Bot(token=TOKEN)

	# handlers
	user_message_handler = MessageHandler(Filters.text & (~Filters.command), logUserMessage)
	start_handler = CommandHandler('start', start)
	stop_handler = CommandHandler('stop', stop)
	show_tasks_handler = CommandHandler('show', showTasks)
	add_task_handler = CommandHandler('add', addTask)
	delete_task_handler = CommandHandler('delete', deleteTask)
	complete_task_handler = CommandHandler('complete', completeTask)
	uncomplete_task_handler = CommandHandler('uncomplete', uncompleteTask)
	send_message_handler = CommandHandler('send', sendMessage)
	unknown_handler = MessageHandler(Filters.regex('/.*'), unknownCommand)

	# add handlers
	dispatcher.add_handler(user_message_handler)
	dispatcher.add_handler(start_handler)
	dispatcher.add_handler(stop_handler)
	dispatcher.add_handler(show_tasks_handler)
	dispatcher.add_handler(add_task_handler)
	dispatcher.add_handler(delete_task_handler)
	dispatcher.add_handler(complete_task_handler)
	dispatcher.add_handler(uncomplete_task_handler)
	dispatcher.add_handler(send_message_handler)
	dispatcher.add_handler(unknown_handler)

	updater.start_polling()


if __name__ == '__main__':

	main()