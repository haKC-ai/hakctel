import tempfile
import unittest
from pathlib import Path

from tools import theme_tool


class ThemeToolTest(unittest.TestCase):
    def test_contrast(self):
        self.assertGreater(theme_tool.contrast("#000000", "#FFFFFF"), 20)

    def test_rejects_traversal_id(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad" / "theme.ini"
            path.parent.mkdir()
            values = {key: "x" for key in theme_tool.REQUIRED}
            values.update(
                {
                    "schema": "1",
                    "id": "../bad",
                    "full_frame_invert": "false",
                    "colors.body_bg": "#000000",
                    "colors.body_fg": "#FFFFFF",
                }
            )
            with self.assertRaises(ValueError):
                theme_tool.validate_theme(path, values)


if __name__ == "__main__":
    unittest.main()
