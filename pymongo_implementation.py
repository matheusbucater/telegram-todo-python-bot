import pymongo
import config
import datetime


client = pymongo.MongoClient(config.CONNECTION_STRING)
db = client.todo_database
todo = db.todo

now = datetime.datetime.now()
now = now.strftime("%d-%m-%Y %H:%M:%S")
now = now+"-03:00"

def logDatabase(text):
	print('\n{} - {}'.format(now, text))

def taskExists(user_id, task):
	document_filter = { "user_id": user_id, "task": task }
	return list(todo.find(document_filter))

def isTaskCompleted(user_id, task):
	document_filter = { "user_id": user_id, "task": task }
	return list(todo.find(document_filter))[0]['is_completed']

def addTask(user_id, task):
	task_exists = taskExists(user_id, task)
	if not task_exists:
		task_document = { "user_id": user_id, "task": task, "is_completed": False, "is_chore": False }
		todo.insert_one(task_document)
		logDatabase('Task added to user {}.'.format(user_id))
		return 'Adding new task... ( {} )'.format(task)
	else:
		logDatabase('Task not added to user {} -> Task already exists'.format(user_id))
		return "The task ( {} ) already exists, please add a different one.".format(task)

def deleteTask(user_id, task):
	task_exists = taskExists(user_id, task)
	if task_exists:
		document_filter = { "user_id": user_id, "task": task }
		todo.delete_one(document_filter)
		logDatabase('Task deleted from user {}.'.format(user_id))
		return 'Deleting task... ( {} )'.format(task)
	else:
		logDatabase("Task not deleted from user {} -> Task does not exists".format(user_id))
		return '\nThe task ( {} ) does not exists, please try again.'.format(task)

def completeTask(user_id, task):
	task_exists = taskExists(user_id, task)
	if task_exists:
		if not isTaskCompleted(user_id, task):
			document_filter = { "user_id": user_id, "task": task }
			document_action = { "$set": { "is_completed": True } }
			todo.update_one(document_filter, document_action)
			logDatabase('Task updated to completed on user {}'.format(user_id))
			return 'Completing task... ( {} )'.format(task), False
		else:
			return 'Task already completed. If you want to uncomplete use /uncomplete command.', True
	else:
		logDatabase('\nTask not completed on user {} -> Task does not exists.'.format(user_id))
		return '\nThe task ( {} ) does not exists, please try again.'.format(task)

def uncompleteTask(user_id, task):
	document_filter = { "user_id": user_id, "task": task }
	document_action = { "$set": { "is_completed": False } }
	todo.update_one(document_filter, document_action)
	logDatabase('Task updated to not completed on user {}'.format(user_id))
	return 'Uncompliting task... ( {} )'.format((task))

def getTasks(user_id):
	document_filter = { "user_id": user_id }
	cursor = todo.find(document_filter)
	documents_list = [document for document in cursor]
	return documents_list
