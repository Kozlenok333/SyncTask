import socket
import threading
import time
from datetime import datetime
from mmap import error
from tkinter import *
from tkinter import ttk
import json
import re
import datetime

class SyncTask:
    def __init__(self):
        self.root = Tk()
        self.root.title("Авторизация")
        self.root.geometry("300x200")
        self.authorization_flag = False
        self.create_widgets()
        self.tasks_table = []
        self.user = ""
        self.data =""
        self.date_for_user = datetime.date.today()

    def create_widgets(self):
        self.login_label = Label(self.root, text='Login')
        self.login_entry = Entry(self.root)
        self.password_label = Label(self.root, text='Password')
        self.password_entry = Entry(self.root, show='*')

        self.authorization_button = Button(
            self.root,
            text='Войти',
            command=self.authorization
        )

        self.error_authorization = Label(self.root, text="", fg='red')

        self.login_label.pack(pady=5)
        self.login_entry.pack(pady=5)
        self.password_label.pack(pady=5)
        self.password_entry.pack(pady=5)
        self.authorization_button.pack(pady=10)
        self.error_authorization.pack(pady=5)

    def authorization(self):
        login = str(self.login_entry.get())
        password = str(self.password_entry.get())
        self.user = login
        try:
            self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_client.connect(("localhost",12345))
            self.socket_client.send(f"{login},{password}".encode('utf-8'))
            response = self.socket_client.recv(1024).decode('utf-8')
            if response == "YES":
                self.authorization_yes()
            else:
                self.authorization_no()
        except error:
            self.error_authorization.config(text="Сервер не отвечает")

    def authorization_yes(self):
        self.authorization_flag = True
        print("Удачно")
        self.error_authorization.config(text="")
        self.start()

    def authorization_no(self):
        self.authorization_flag = False
        print("Не получилось")
        self.error_authorization.config(text="Неверный логин или пароль")

    def select_item(self):
        try:
            self.item_id = self.tasks.selection()[0]
            self.selected_item = self.item_id
            print(self.item_id)
        except error as err:
            print(err)

    def update_selected_row(self):
        try:
            self.select_item()
            if self.selected_item:
                self.new_value = self.work.get()
                if self.new_value == 1:
                    self.new = "Не начато"
                elif self.new_value == 2:
                    self.new = "Выполнено"
                elif self.new_value == 3:
                    self.new = "В работе"
                self.tasks.set(self.selected_item, 5, value=self.new)
                self.change_uuid = self.tasks.set(self.selected_item,"id")
                self.change_status = self.tasks.set(self.selected_item,5)
                self.socket_client.send(f"change:{self.change_uuid}:{self.change_status}".encode('utf-8'))
        except error as err:
            print(err)
    def delete_selection_row(self):
        self.select_item()
        if self.selected_item:
            self.delete_uuid = self.tasks.set(self.selected_item, "id")
            self.socket_client.send(f"delete:{self.delete_uuid}".encode('utf-8'))
            self.tasks.delete(self.selected_item)

    def update_task(self):
        self.tasks.delete(*self.tasks.get_children())
        self.socket_client.send('tasks'.encode('utf-8'))
        self.data = self.socket_client.recv(100000).decode('utf-8')
        self.tasks_table = json.loads(self.data)
        for task_table in self.tasks_table:
            values = (
                task_table.get("uuid", ""),
                task_table.get("date", ""),
                task_table.get("responsible", ""),
                task_table.get("deadline", ""),
                task_table.get("task", ""),
                task_table.get("status", "")
            )
            self.tasks.insert("", END, values=values)
        self.synctask.after(5000, self.update_task)

    def append_task_for_user(self):
        self.responside_for_user = self.append_listbox_responside.get()
        self.deadline_for_user = self.append_entry_deadline.get()
        self.append_task_for_user = self.append_entry_task.get()
        self.status_for_user = "Не начато"
        pattern_append = r'([0-9][0-9][0-9][0-9])-([0-1][0-2])-([0-3][0-9]$)'
        match_append_2 = re.match(pattern_append, self.deadline_for_user)

        flag_deadline = False
        if match_append_2:
            no_m = ['01', '03', '05', '07', '09', '11']
            yes_m = ['04', '06', '08', '10', '12']
            if match_append_2.group(2) in no_m:
                if int(match_append_2.group(3)) <= 30:
                    #print("Yes")
                    flag_deadline = True
                    self.append_entry_deadline.config(bg="white", fg="black")
                    self.append_error.config(text='')

                else:
                    #print("No")
                    self.append_entry_deadline.config(bg = "red", fg="white")
                    self.append_error.config(text='Ошибка в написании даты!')

            elif match_append_2.group(2) == '02':
                if int(match_append_2.group(1)) % 4 != 0:
                    if int(match_append_2.group(3)) <= 28:
                        #print('Yes')
                        flag_deadline = True
                        self.append_entry_deadline.config(bg="white", fg="black")
                        self.append_error.config(text='')


                    else:
                        #print('No')
                        self.append_entry_deadline.config(bg="red", fg="white")
                        self.append_error.config(text='Ошибка в написании даты!')
                else:
                    if int(match_append_2.group(3)) <= 29:
                        #print('Yes')
                        flag_deadline = True
                        self.append_entry_deadline.config(bg="white", fg="black")
                        self.append_error.config(text='')

                    else:
                        #print('No')
                        self.append_entry_deadline.config(bg="red", fg="white")
                        self.append_error.config(text='Ошибка в написании даты!')
            elif match_append_2.group(2) in yes_m:
                if int(match_append_2.group(3)) <= 31:
                    #print("Yes")
                    flag_deadline = True
                    self.append_entry_deadline.config(bg="white", fg="black")
                    self.append_error.config(text='')


                else:
                    #print("No")
                    self.append_entry_deadline.config(bg="red", fg="white")
                    self.append_error.config(text='Ошибка в написании даты!')
        else:
            #print('No')
            self.append_entry_deadline.config(bg="red", fg="white")
            self.append_error.config(text='Ошибка в написании даты!')
        if flag_deadline:
            d = datetime.date(int(match_append_2.group(1)), int(match_append_2.group(2)), int(match_append_2.group(3)))
            if self.date_for_user <= d:
                self.task_for_user = f'append,{str(self.date_for_user)},{self.responside_for_user},{self.deadline_for_user},{self.append_task_for_user},{self.status_for_user}'
                print(self.task_for_user)
                self.socket_client.send(self.task_for_user.encode('utf-8'))
                self.append_entry_deadline.config(bg='white', fg="black")
                self.append_error.config(text='')
                self.update_task()

            else:
                self.append_entry_deadline.config(bg='red', fg="white")
                self.append_error.config(text='Дата не должна быть раньше чем сегодняшняя дата!')



    def start(self):
        if self.socket_client and self.authorization_flag == True:
            self.root.destroy()
            self.synctask = Tk()
            self.synctask.title("SyncTask")
            self.synctask.geometry("1001x600")

            self.user_label = Label(self.synctask, text=self.user)
            self.date_label = Label(self.synctask, text=str(self.date_for_user))
            self.tasks = ttk.Treeview(self.synctask)
            #self.tasks['columns'] = ("Дата поставленной задачи", "Ответственное лицо", "Выполнить до", "Задача", "Статус")
            self.tasks['columns'] = ("id","1", "2", "3", "4", "5")
            self.tasks.column("#0", width=0, stretch=NO)
            self.tasks.column("id", width=0, stretch=NO)
            self.tasks.heading("1", text="Дата поставленной задачи")
            self.tasks.heading("2", text="Ответственное лицо")
            self.tasks.heading("3", text="Выполнить до")
            self.tasks.heading("4", text="Задача")
            self.tasks.heading("5", text="Статус")

            self.user_label.grid(row=0, column = 3, sticky='e')
            self.date_label.grid(row=0, column = 4, sticky='e')
            self.tasks.grid(row=1, column=0, sticky='w', columnspan=5)
            self.update_task()

            if self.user == "admin":
                self.socket_client.send("list_users_admin".encode('utf-8'))
                self.list_users = self.socket_client.recv(1024).decode('utf-8')
                print(self.list_users)
                self.list_users = self.list_users.split(',')
                print(self.list_users)
                self.append_label = Label(self.synctask, text="Добавить задачу")
                self.append_label_responsible = Label(self.synctask, text="Ответственное лицо")
                self.append_listbox_responside = ttk.Combobox(self.synctask, values = self.list_users)
                #self.append_entry_responsible = Entry(self.synctask)
                self.append_label_deadline = Label(self.synctask, text="Выполнить до")
                self.append_entry_deadline = Entry(self.synctask)
                self.append_label_task = Label(self.synctask, text="Задача")
                self.append_entry_task = Entry(self.synctask, width=100)
                self.append_button_task = Button(self.synctask, text='Добавить задачу', command=self.append_task_for_user, width=45, height=3)
                self.append_error = Label(self.synctask, text='', fg='red')
                self.delete_label = Label(self.synctask, text='Удалить задачу')
                self.delete_button = Button(self.synctask, text='Удалить', command=self.delete_selection_row, width=45, height=3)

                self.append_label.grid(row=2, column=0, columnspan=5)
                self.append_label_responsible.grid(row=3, column=0)
                self.append_listbox_responside.grid(row=4, column=0)
                self.append_label_deadline.grid(row=3, column=1)
                self.append_entry_deadline.grid(row=4, column=1)
                self.append_label_task.grid(row=3, column=2)
                self.append_entry_task.grid(row=4, column=2)
                self.append_button_task.grid(row=5, column=0, columnspan=5, pady=5)
                self.append_error.grid(row=6, column=0, columnspan=5)
                self.delete_label.grid(row=7, column=0, columnspan=5)
                self.delete_button.grid(row=8, column=0, columnspan=5, pady=5)
            else:
                self.work = IntVar(value=0)
                #self.select_item = None
                self.rad_no = Radiobutton(self.synctask, text="Не начато", variable=self.work, value=1)
                self.rad_yes = Radiobutton(self.synctask, text="Выполнено", variable=self.work, value=2)
                self.rad_run = Radiobutton(self.synctask, text="В работе", variable=self.work, value=3)
                self.update_button = Button(self.synctask, text="Обновить", command=self.update_selected_row)
                self.status_label = Label(self.synctask, text="Изменить статус задачи")

                self.status_label.grid(row=2, column=0)
                self.rad_no.grid(row=3, column=0, sticky='w')
                self.rad_yes.grid(row=4, column=0, sticky='w')
                self.rad_run.grid(row=5, column=0, sticky='w')
                self.update_button.grid(row=6, column=0)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    client = SyncTask()
    client.run()