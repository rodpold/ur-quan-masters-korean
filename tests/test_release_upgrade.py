import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import patcher


class ReleaseUpgradeTests(unittest.TestCase):
    def test_same_payload_updates_old_version_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            game = Path(tmp)
            with patch.object(patcher, 'validate_game', return_value=game), patch.object(patcher, 'build', return_value=(b'fixture', {})):
                with patch.object(patcher, 'VERSION', '0.1.0'):
                    patcher.install(game)
                result = patcher.install(game)
            self.assertEqual(result['version'], patcher.VERSION)
            self.assertEqual(json.loads((patcher.addon_dir(game)/'manifest.json').read_text())['version'], patcher.VERSION)
            self.assertEqual((patcher.addon_dir(game)/'ko-ui.uqm').read_bytes(), b'fixture')

    def test_version_upgrade_rolls_back_on_manifest_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            game = Path(tmp)
            with patch.object(patcher, 'validate_game', return_value=game), patch.object(patcher, 'build', return_value=(b'fixture', {})):
                with patch.object(patcher, 'VERSION', '0.1.0'):
                    before = patcher.install(game)
                real_write = patcher.atomic_write
                count = 0
                def fail_once(path, data):
                    nonlocal count
                    count += 1
                    if count == 2:
                        raise OSError('disk failure')
                    real_write(path, data)
                with patch.object(patcher, 'atomic_write', side_effect=fail_once):
                    with self.assertRaises(OSError):
                        patcher.install(game)
                self.assertEqual(patcher.status(game), before)
