import abc
import dbm

from Crypto.PublicKey import RSA


class KeyBase(abc.ABC):
    def __init__(self, pass_phrase):
        if isinstance(pass_phrase, str):
            pass_phrase = pass_phrase.encode('utf-8')
        self._pass_phrase = pass_phrase

    @property
    @abc.abstractmethod
    def private_key(self):
        pass

    @property
    @abc.abstractmethod
    def public_key(self):
        pass


class KeyGenerator(KeyBase):
    def __init__(self, pass_phrase, path='./private_key.bin'):
        super().__init__(pass_phrase)
        self.__path = path
        self.__private_key = RSA.generate(2048)
        self.__public_key = self.__private_key.publickey()
        self.__write_public_key()
        self.__write_private_key()

    def __write_public_key(self):
        with dbm.open('./sys_file/db', 'c') as db:
            db[b'public_key'] = self.__public_key.export_key()

    def __write_private_key(self):
        private_key_enc = self.__private_key.export_key(passphrase=self._pass_phrase, pkcs=8,
                                                        protection="scryptAndAES128-CBC")
        with open(self.__path, 'wb') as f:
            f.write(private_key_enc)

    @property
    def private_key(self):
        return self.__private_key

    @property
    def public_key(self):
        return self.__public_key


class KeyGetter(KeyBase):
    def __init__(self, pass_phrase, path='./private_key.bin'):
        super().__init__(pass_phrase)
        self.__path = path
        self.__public_key = self.__get_public_key()
        self.__private_key = self.__get_private_key()

    def __get_public_key(self):
        with dbm.open('./sys_file/db', 'c') as db:
            public_key = db[b'public_key']
        return RSA.import_key(public_key)

    def __get_private_key(self):
        with open(self.__path) as f:
            private_key_enc = f.read()
        # TODO: add handler to deal with incorrect password
        return RSA.import_key(private_key_enc, passphrase=self._pass_phrase)

    @property
    def private_key(self):
        return self.__private_key

    @property
    def public_key(self):
        return self.__public_key


# test
if __name__ == '__main__':
    s = KeyGenerator('123123')
    h = KeyGetter('123123')
    assert s.public_key == h.public_key
    assert s.private_key == h.private_key
