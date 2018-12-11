import os
import sys
import hashlib
import lhafile


class SlaveFile:
    def __init__(self, name, data, hasher):
        self.name = name
        self.data = data
        self.hasher = hasher
        self.hash_digest = None

    def get_hash(self):
        if self.data:
            self.hasher.update(self.data)
            self.hash_digest = self.hasher.hexdigest()
        else:
            raise ValueError('No slave data to hash')

    def __str__(self):
        return 'Slave File: {}\nSlave {} Hash: {}'.format(
            self.name, self.hasher.name.upper(), self.hash_digest)


class LhaSlaveArchive:
    def __init__(self, archive_path, hash_algorithm='SHA1'):
        self.original_path = archive_path
        self.hasher = self._get_hasher(hash_algorithm)
        self.absolute_path = os.path.abspath(self.original_path)
        try:
            self.lha_file = lhafile.lhafile.Lhafile(self.absolute_path)
            self.slaves = []
        except:
            print("Problem reading LHA")
            
    def read_lha(self):
        archive = lhafile.lhafile.Lhafile(self.absolute_path)
        for file in archive.filelist:
            if str(file.filename).lower().endswith('.slave'):
                self.slaves.append(
                    SlaveFile(
                        name=file.filename,
                        data=archive.read(file.filename),
                        hasher=self.hasher))

    def _get_hasher(self, hash_algorithm):
        if hash_algorithm is None or hash_algorithm.upper() == 'SHA1':
            return hashlib.sha1()

        return hashlib.md5()


# if __name__ == '__main__':
#     CWD = os.path.dirname(__file__)
#     FILE = os.path.join(CWD, 'test_data', 'Alcatraz.lha')
#     FILE = r"C:\Users\oaing\Downloads\Lemmings2.lha"
#     LHA_SLAVE = LhaSlaveArchive(archive_path=FILE)
#     LHA_SLAVE.read_lha()
#     for slave in LHA_SLAVE.slaves:
#         slave.get_hash()
#         print(slave)
