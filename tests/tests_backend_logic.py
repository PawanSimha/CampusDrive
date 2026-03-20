import unittest
import re
from utils.helpers import allowed_file, generate_group_code

class TestBackendLogic(unittest.TestCase):
    def test_allowed_file(self):
        self.assertTrue(allowed_file("test.pdf"))
        self.assertTrue(allowed_file("image.png"))
        self.assertTrue(allowed_file("doc.docx"))
        self.assertFalse(allowed_file("script.sh"))
        self.assertFalse(allowed_file("malicious.exe"))

    def test_group_code_format(self):
        code = generate_group_code()
        # Format should be AAAA-0000
        self.assertTrue(re.match(r'^[A-Z]{4}-\d{4}$', code))

    def test_unique_codes(self):
        codes = [generate_group_code() for _ in range(100)]
        self.assertEqual(len(codes), len(set(codes)), "Group codes should be reasonably unique")

if __name__ == '__main__':
    unittest.main()
