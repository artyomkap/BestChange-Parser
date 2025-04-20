import aiosqlite


def get_connection():
    return aiosqlite.connect("db.sqlite3")  # укажите полный путь до вашей базы в проекте
