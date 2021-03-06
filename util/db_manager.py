import os , sys, sqlite3
from util.path_manager import path_manager
import datetime

from util.Folder import Folder
from util.File import File

class db_injector:
    def __init__(self, path = "db/main.db", save_config = True):
        self.path = path
        self.save_config = save_config

    def __enter__(self):
        # create the connection to the database file
        self.con = sqlite3.connect(self.path)
        # ge the connection query slot

        return self.con.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.save_config:
            self.con.commit()
        # close the connection
        self.con.close()
        del self # delete the object


class db_manager:
    def __init__(self, path = "db/main.db"):
        self.path = path
        # initialize the db folder if it does not exist
        if not os.path.exists("db"):
            os.mkdir("db")
            self.initialize_db()


    def initialize_db(self):
        # create the database tables if tables does not exist
        with db_injector(self.path, True) as cursor:
            # create the main folder table
            cursor.execute(
                """CREATE TABLE folders(id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL ,
                                        name VARCHAR(150) NOT NULL,
                                        path TEXT NOT NULL UNIQUE ,
                                        time TIMESTAMP NOT NULL ,
                                        fav BOOLEAN NOT NULL,
                                        type TEXT NOT NULL DEFAULT 'N',
                                        pw TEXT)"""
            )

            cursor.execute("""
                    CREATE TABLE files(id INTEGER PRIMARY KEY AUTOINCREMENT  UNIQUE NOT NULL,
                                        file TEXT NOT NULL,
                                        path TEXT NOT NULL,
                                        time TIMESTAMP NOT NULL,
                                        fav BOOLEAN NOT NULL)""")

            cursor.execute(
                """CREATE TABLE recycle_folders(id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL ,
                                        name VARCHAR(150) NOT NULL,
                                        path TEXT NOT NULL UNIQUE ,
                                        time TIMESTAMP NOT NULL ,
                                        fav BOOLEAN NOT NULL)"""
            )

            cursor.execute("""
                                CREATE TABLE recycle_files(id INTEGER PRIMARY KEY AUTOINCREMENT  UNIQUE NOT NULL,
                                                    file TEXT NOT NULL,
                                                    path TEXT NOT NULL,
                                                    time TIMESTAMP NOT NULL,
                                                    fav BOOLEAN NOT NULL)""")
            print("[INFO] database create successfull.")

    def add_folder(self, name : str , parent_path : str, type  : str):

        folder_path = path_manager.get_path_for_folder(parent_path, self.get_paths(parent_path))

        now = datetime.datetime.now()
        with db_injector(self.path) as cursor:
            cursor.execute("INSERT INTO folders(name, path, time, fav, type) VALUES(?, ?, ?, ?, ?)", (name, folder_path,
                                                                                               now, False, type))
        return folder_path

    def add_instance(self, children : list[Folder, File]):

        with db_injector(self.path) as cursor:
            for child in children:
                if isinstance(child, Folder):
                    self.add_folder_instance(child, cursor)
                else:
                    self.add_file_instance(child, cursor)

    def add_folder_instance(self, folder : Folder, cursor):

        cursor.execute("INSERT INTO folders(name, path, time, fav, type) VALUES(?, ?, ?, ?, ?) ",
                       (folder.name, folder.path, folder.time, folder.fav, folder.type))

    def add_file_instance(self, file : File, cursor):

        cursor.execute("INSERT INTO files(file, path, time, fav) VALUES (?, ?, ?, ?)",
                       (file.file, file.path, file.time, file.fav))


    def add_file(self, file : str , path : str):

        now = datetime.datetime.now()
        with db_injector(self.path) as cursor:
            cursor.execute("""INSERT INTO files(file , path, time ,fav) VALUES (?, ?, ?, ?)""" ,(file, path, now, False))

    def add_files(self, file_list : list[str], path):

        now = datetime.datetime.now()
        with db_injector(self.path) as cursor:
            for file in file_list:
                cursor.execute(f"""INSERT INTO files(file , path, time ,fav) VALUES (?, ?, ?, ?)""", (file, path, now, False))

        return now


    def get_paths(self, parent_path : str):

        paths = []
        with db_injector(self.path, False) as cursor:
            cursor.execute("SELECT path FROM folders WHERE path LIKE ? ORDER BY path", (f"{parent_path}_%",))
            paths = [x[0] for  x in cursor.fetchall()]

        # filter paths
        paths_ = []
        for item in paths:
            if parent_path == ".":
                if len(item.split(".")) == 2:
                    paths_.append(item)
            else:
                if len(parent_path.split(".")) + 1 == len(item.split(".")):
                    paths_.append(item)

        return paths_

    def open_folder(self, path : str) -> list[list]:

        with db_injector(self.path, False) as cursor:
            cursor.execute(f"SELECT name, path, time, fav, type ,pw FROM folders WHERE path LIKE ? ORDER BY time " ,
                           (f"{path}_%", ))
            paths = cursor.fetchall()

            paths_ = []
            for item in paths:
                if path == ".":
                    if len(item[1].split(".")) == 2:
                        paths_.append(item)
                else:
                    if len(path.split(".")) + 1 == len(item[1].split(".")):
                        paths_.append(item)

            return paths_

        return []

    def open_folder_as_instance(self, path : str) -> list[Folder]:

        paths = self.open_folder(path)
        folders = []
        for folder in paths:
            folders.append(
                Folder(folder[0], folder[1], folder[2], folder[3], folder[4])
            )

        return folders

    def folder_count(self, path  :str):
        return len(self.open_folder(path))

    def file_count(self, path : str):

        with db_injector(self.path, False) as cursor:
            cursor.execute("SELECT COUNT(file) FROM files WHERE path = ?", (path, ))
            return cursor.fetchall()[0][0]

        return 0

    def open_files(self, path  : str):

        with db_injector(self.path, False) as cursor:
            cursor.execute(
                f"SELECT file, path, time, fav FROM files WHERE path = ? ORDER BY time ", (path, ))
            return cursor.fetchall()

        return []

    def open_files_as_instance(self, path : str) -> list[File]:
        files_ = self.open_files(path)
        return [File(*x) for x in self.open_files(path)]

    def get_folder_name(self, path : str):

        with db_injector(self.path, False) as cursor:
            cursor.execute(f"SELECT name FROM folders WHERE path = ? ", (path, ))
            data = cursor.fetchall()
            if data != []:
                name = data[0][0]
            else:
                name = None

        return name

    def get_files(self, path : str):

        file_list = []
        with db_injector(self.path, False) as cursor:
            cursor.execute(f"SELECT file FROM files WHERE path = '{path}' ORDER BY name ")
            data = cursor.fetchall()
            if data:
                file_list = [x[0] for x in data]

        return file_list

    def folder(self, path):

        with db_injector(self.path, False) as cursor:
            cursor.execute(
                "SELECT name, path ,time, fav, type, pw FROM folders WHERE path LIKE ? LIMIT 1", (path ,))
            return cursor.fetchall()[0]

        return []

    def rename_folder(self, path : str , new_name : str):

        with db_injector(self.path) as cursor:
            cursor.execute("UPDATE folders SET name = ? WHERE path = ?", (new_name, path))

    def change_favorite_folder(self, path : str, state : bool):

        with db_injector(self.path) as cursor:
            cursor.execute("UPDATE folders SET fav = ? WHERE path = ?", (state, path))

    def change_favorite_file(self, path : str, file : str ,state : bool):

        with db_injector(self.path) as cursor:
            cursor.execute("UPDATE files SET fav = ? WHERE path = ? AND file = ? ", (state, path, file))

    def numberOfFolders(self, path : str):

        with db_injector(self.path, False) as cursor:
            cursor.execute(f"SELECT path FROM folders WHERE path LIKE ? ",
                           (f"{path}_%",))
            paths = cursor.fetchall()

            paths_ = []
            for item in paths:
                if path == ".":
                    if len(item.split(".")) == 2:
                        paths_.append(item)
                else:
                    if len(path.split(".")) + 1 == len(item.split(".")):
                        paths_.append(item)

            return len(paths_)

    def numberOfFiles(self, path : str):

        with db_injector(self.path, False) as cursor:
            cursor.execute(f"SELECT file FROM files WHERE path = ? ", (path, ))
            return len(cursor.fetchall())

        return 0

    def deleteFolder(self, path : str) -> bool:

        # get the info about the folder
        with db_injector(self.path) as cursor:
            cursor.execute("SELECT * FROM folders WHERE path =  ? LIMIT 1", (path, ))
            data = cursor.fetchall()

            if data:
                cursor.execute("DELETE FROM folders WHERE path = ?", (path, ))
                # add to the recycle bin table
                cursor.execute("INSERT INTO recycle_folders(id, name, path, time, fav) VALUES(?, ?, ? ,?, ?)", data[0])
                return True
        return False

    def deleteFile(self, path: str , file : str) -> bool:

        with db_injector(self.path) as cursor:
            cursor.execute("SELECT * FROM files WHERE path = ? AND file = ? LIMIT 1", (path, file))
            data = cursor.fetchall()

            if data:
                cursor.execute("DELETE FROM files WHERE path = ? AND file = ?", (path, file))
                # add to the recycle bin table
                cursor.execute("INSERT INTO recycle_files(id, file, path, time, fav) VALUES(?, ?, ? ,?, ?)", data[0])
                return True
            return False

    def delete_from_instance(self, children : list[Folder, File]):

        with db_injector(self.path) as cursor:
            for child in children:
                if isinstance(child, Folder):
                    self.delete_folder_instance(child, cursor)
                else:
                    self.delete_file_instance(child, cursor)

    def delete_folder_instance(self, folder : Folder , cursor):

        cursor.execute("DELETE FROM folders WHERE path = ? AND name = ?", (folder.path, folder.name))

    def delete_file_instance(self, file : File, cursor):

        cursor.execute("DELETE FROM files WHERE file = ? AND path = ?", (file.file, file.path))

    def removeFolder(self, path : str) -> bool:

        # get the info about the folder
        with db_injector(self.path) as cursor:
            cursor.execute("SELECT * FROM folders WHERE path =  ?", (path, ))
            data = cursor.fetchall()

            if data:
                cursor.execute("DELETE FROM folders WHERE path = ? ", (path, ))
                return True
        return False

    def removeFile(self, path: str , file : str) -> bool:

        with db_injector(self.path) as cursor:
            cursor.execute("SELECT * FROM files WHERE path = ? AND file = ?", (path, file))
            data = cursor.fetchall()

            if data:
                cursor.execute("DELETE FROM files WHERE path = ? AND file = ?", (path, file))
                return True
            return False

    def open_favorites_folders(self):

        with db_injector(self.path, False) as cursor:
            cursor.execute(f"SELECT name, path, time, fav ,type ,pw FROM folders WHERE fav = ? " ,
                           (1, ))
            return cursor.fetchall()


        return []

    def open_favorites_files(self):

        with db_injector(self.path, False) as cursor:
            cursor.execute(f"SELECT file, path, time, fav FROM files WHERE fav = ? ",
                           (1,))
            return cursor.fetchall()

        return []

    def change_folder_color(self, path : str,type : str):

        with db_injector(self.path) as cursor:
            cursor.execute("UPDATE folders SET type = ? WHERE path = ?", (type, path))

