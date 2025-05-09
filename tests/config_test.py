from unittest import TestCase, main
from  a5client import read_config, write_config, defaults, config_path
import os

class TestConfig(TestCase):
    def test_config_file_not_found(self):
        self.assertRaises(FileNotFoundError, read_config, "/inexistent/file65408046806548.txt")

    def test_write_config_file(self):
        write_config("/tmp/config65408046806548.txt", True)
        config = read_config("/tmp/config65408046806548.txt")
        self.assertEqual(config.get("log","filename"), defaults["log"]["filename"])
        os.remove("/tmp/config65408046806548.txt")

    def test_write_config_file_defaults(self):
        write_config()
        self.assertTrue(os.path.exists(config_path))
        config = read_config()
        self.assertTrue(config.has_section("log"))

if __name__ == '__main__':
    main()