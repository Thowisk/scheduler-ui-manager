import mysql.connector

class TaskDao:

  db = None
  cursor = None
  config = {'user':'root', 'password': '', 'host':'127.0.0.1', 'database': 'taskproject'}

  @staticmethod
  def connect():
    TaskDao.db = mysql.connector.connect(**TaskDao.config)
    TaskDao.cursor = TaskDao.db.cursor()

  @staticmethod
  def get_task(id):
    if TaskDao.cursor is None:
      TaskDao.connect()
    TaskDao.cursor.execute('SELECT * FROM schemer_task WHERE id=' + str(id) + ';')
    return dict(zip(TaskDao.cursor.column_names, TaskDao.cursor.fetchone()))

  @staticmethod
  def update_task_state(id, new_state):
    if TaskDao.cursor is None:
      TaskDao.connect()
    TaskDao.cursor.execute('UPDATE schemer_task SET state=' + new_state + ' WHERE id=' + str(id) + ';')

  @staticmethod
  def delete_task(id):
    if TaskDao.cursor is None:
      TaskDao.connect()
    TaskDao.cursor.execute('DELETE FROM schemer_task WHERE id=' + str(id) + ';')
