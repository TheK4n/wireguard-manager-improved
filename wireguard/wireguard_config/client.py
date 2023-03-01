import subprocess
from wireguard.wireguard_config.models import Client


class ClientCreator:
    def __init__(self, username: str):
        self.__username = username

    def create(self) -> Client:

        username = self.__username
        privkey = self.__generate_privkey()
        pubkey = self.__generate_pubkey(privkey)
        psk = self.__generate_psk()

        client = Client(
            name=username,
            privatekey=privkey,
            publickey=pubkey,
            presharedkey=psk,
        )

        return client

    def __generate_privkey(self) -> str:
        return self._execute_shell_command("wg genkey")

    def __generate_pubkey(self, privkey: str) -> str:
        return self._execute_shell_command("wg pubkey", stdin=privkey)

    def __generate_psk(self) -> str:
        return self._execute_shell_command("wg genpsk")

    @staticmethod
    def _execute_shell_command(command: str,
                               stdin: str | None = None) -> str:
        PIPE = subprocess.PIPE
        p = subprocess.Popen(["bash", "-c", command], stdout=PIPE, stdin=PIPE)
        stdout, _ =  p.communicate(input=stdin.encode() if stdin else None)
        return stdout.decode().strip()


if __name__ == '__main__':
    client_creator = ClientCreator("kan")
    print(client_creator.create())
