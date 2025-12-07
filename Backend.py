import json
import socket
import threading
import  uuid
import re



users = {
    "admin": "password123",
    "user1": "user1",
    "user2": "user2",
    "user3": "user3",
    "user4": "user4",
    "user5": "user5",
    "test": "test"
}

def handle_client(client_socket, client_address):
    print(f'Клиент подключен: {client_address}')

    try:
        auth_data = client_socket.recv(1024).decode('utf-8')
        print(f"Данные авторизации: {auth_data}")

        if ',' in auth_data:
            login, password = auth_data.split(',', 1)

            if login in users and users[login] == password:
                client_socket.send("YES".encode('utf-8'))
                print(f"Клиент {login} авторизован")

                while True:
                    data = client_socket.recv(1024).decode('utf-8')
                    if not data:
                        print(f"Клиент {login} отключился")
                        break
                    print(f"Сообщение от {login}: {data}")
                    if data == "tasks":
                        tasks = []
                        with open("tasks.txt", 'r', encoding='utf-8') as file_task:
                            lines = file_task.readlines()
                            for line in lines:
                                if (login == "admin" or login == "test") and data == "tasks":
                                    line2 = line.strip().split(',')
                                    if len(line2) == 6:
                                        task = {
                                        "uuid": line2[0],
                                        "date": line2[1],
                                        "responsible": line2[2],
                                        "deadline": line2[3],
                                        "task": line2[4],
                                        "status": line2[5]
                                        }
                                        tasks.append(task)
                                else:
                                    line2 = line.strip().split(',')
                                    if len(line2) == 6 and line2[2] == login:
                                        task = {
                                            "uuid": line2[0],
                                            "date": line2[1],
                                            "responsible": line2[2],
                                            "deadline": line2[3],
                                            "task": line2[4],
                                            "status": line2[5]
                                        }
                                        tasks.append(task)
                        tasks_json = json.dumps(tasks, ensure_ascii=False)
                        client_socket.send(tasks_json.encode('utf-8'))
                        print("Отправил")

                    elif data == "list_users_admin":
                        list_users = list(users.keys())
                        list_users.remove("admin")
                        list_users.remove("test")
                        list_users_csv = ""
                        for i in range(len(list_users)):
                            if i != len(list_users) - 1:
                                list_users_csv+=f'{list_users[i]},'
                            else:
                                list_users_csv+=list_users[i]
                        client_socket.send(list_users_csv.encode('utf-8'))


                    pattern_change = r'^change:.+$'
                    match_change = re.match(pattern_change, data)
                    if match_change:
                        print('change')
                        str_change = str(data).split(':')
                        change_id = str_change[1]
                        change_status = str_change[2]
                        file_task = open("tasks.txt", 'r', encoding='utf-8')
                        lines = file_task.readlines()
                        with open("tasks.txt", 'w', encoding='utf-8') as file_task:
                            for line in lines:
                                line2 = line.strip().split(',')
                                if line2[0] == change_id:
                                    line2[5] = change_status
                                    line3 = f'{line2[0]},{line2[1]},{line2[2]},{line2[3]},{line2[4]},{line2[5]}\n'
                                    file_task.write(line3)
                                else:
                                    file_task.write(line)

                    pattern_append = r'^append,.+$'
                    match_append = re.match(pattern_append, data)
                    if match_append:
                        print("append")
                        str_append = str(data).split(',')
                        append_date = str_append[1]
                        append_responside = str_append[2]
                        append_deadline = str_append[3]
                        append_task = str_append[4]
                        append_status = str_append[5]
                        append_uuid = uuid.uuid4()
                        new_append_for_user = f'{append_uuid},{append_date},{append_responside},{append_deadline},{append_task},{append_status}\n'
                        with open("tasks.txt", "a", encoding="utf-8") as file_task:
                            file_task.write(new_append_for_user)
                    pattern_delete = r'^delete:.+$'
                    match_delete = re.match(pattern_delete, data)
                    if match_delete:
                        print('delete')
                        str_delete = str(data).split(':')
                        delete_uuid = str_delete[1]
                        file_task_del = open("tasks.txt", 'r', encoding='utf-8')
                        lines_del = file_task_del.readlines()
                        with open("tasks.txt", 'w', encoding='utf-8') as file_task_del2:
                            for line_del in lines_del:
                                line2_del = line_del.strip().split(',')
                                if line2_del[0] == delete_uuid:
                                    print(line2_del)
                                else:
                                    file_task_del2.write(f'{line_del}')



            else:
                client_socket.send("NO".encode('utf-8'))
                print(f"Неудачная авторизация: {auth_data}")
        else:
            client_socket.send("NO".encode('utf-8'))

    except ConnectionResetError:
        print(f"Клиент {client_address} разорвал соединение")
    except Exception as e:
        print(f"Ошибка с клиентом {client_address}: {e}")
    finally:
        client_socket.close()
        print(f"Соединение с {client_address} закрыто")


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))
    server_socket.listen(5)
    print("Сервер запущен. Ожидаем подключения...")

    try:
        while True:
            client_socket, client_address = server_socket.accept()

            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address)
            )
            client_thread.daemon = True
            client_thread.start()

    except KeyboardInterrupt:
        print("\nОстановка сервера...")
    finally:
        server_socket.close()


if __name__ == "__main__":
    start_server()