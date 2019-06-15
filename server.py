from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor


class Client(Protocol):
    ip: str = None
    login: str = None
    factory: 'Chat'
    hist: str = 'hist.txt'

    def __init__(self, factory):
        """
        Инициализация фабрики клиента
        :param factory:
        """
        self.factory = factory

    def connectionMade(self):
        """
        Обработчик подключения нового клиента
        """
        f = open(self.hist, 'r')
        self.ip = self.transport.getHost().host
        self.factory.clients.append(self)
        print(f"New user connected: {self.ip}")
        self.transport.write("Welcome to chat\n".encode())
        serv_history = f.read()
        self.transport.write(serv_history.encode())

    def dataReceived(self, data: bytes):
        """
        Обработчик нового сообщения от клиента
        :param data:
        """

        message = data.decode().replace('\n', '')
        f = open(self.hist, 'a+')
        if self.login is not None:
            server_message = f"{self.login}: {message}"
            f.write(f"{self.login}: {message}\n")
            self.factory.notify_all_users(server_message)

            print(server_message)
        else:
            if message.startswith("login:"):
                tlogin = message.replace("login:", "")
                if self.factory.searchLogin(tlogin):
                    self.transport.write("Login already in use".encode())
                else:
                    self.login = tlogin
                    notification = f"New user connected: {self.login}\n"

                    self.factory.notify_all_users(notification)
                    print(notification)
            else:
                print("Error: Invalid client login")
        f.close()

    def connectionLost(self, reason=None):
        """
        Обработчик отключения клиента
        :param reason:
        """
        self.factory.clients.remove(self)
        print(f"Client disconnected: {self.ip}")


class Chat(Factory):
    clients: list

    def __init__(self):
        """
        Инициализация сервера
        """
        self.clients = []

    def searchLogin(self, tlogin: str):
        for cl in self.clients:
            if cl.login == tlogin:
                print("login in use")
                return True
        return None

    def startFactory(self):
        """
        Запуск процесса ожидания новых клиентов
        :return:
        """

        print("Server started [OK]")

    def buildProtocol(self, addr):
        """
        Инициализация нового клиента
        :param addr:
        :return:
        """
        return Client(self)

    def notify_all_users(self, data: str):
        """
        Отправка сообщений всем текущим пользователям
        :param data:
        :return:
        """

        for user in self.clients:
            user.transport.write(data.encode())


if __name__ == '__main__':
    reactor.listenTCP(7419, Chat())
    reactor.run()
