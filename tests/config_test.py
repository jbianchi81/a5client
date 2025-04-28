from unittest import TestCase, main
from a5client import read_config
from a5client import write_config
import os

class TestConfig(TestCase):
    def test_config_file_not_found(self):
        config = read_config("/inexistent/file65408046806548.txt")
        self.assertEqual(config.get("log","filename"), "/var/log/a5client.log")

    def test_write_config_file(self):
        write_config("/tmp/config65408046806548.txt", True)
        config = read_config("/tmp/config65408046806548.txt")
        self.assertEqual(config.get("log","filename"), "/var/log/a5client.log")
        self.assertEqual(config.get("log","filename"), "/var/log/a5client.log")
        os.remove("/tmp/config65408046806548.txt")

    def test_write_config_file_defaults(self):
        write_config()
        self.assertTrue(os.path.exists(os.path.join(os.environ["HOME"],".a5client.ini")))
        config = read_config()
        self.assertTrue(config.has_section("log"))

if __name__ == '__main__':
    main()