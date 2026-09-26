import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import patcher
import steam_launch as sl


def config(value=None):
    option = '' if value is None else '"LaunchOptions" "'+value.replace('\\', '\\\\').replace('"', '\\"')+'"'
    return ('// keep comment\r\n"UserLocalConfigStore" { "Software" { "Valve" { "Steam" { "apps" { '
            '"99" { "LaunchOptions" "other game" } "2645580" { "Playtime" "42" '+option+
            ' } } } } } "unrelated" "retained" }\r\n')


class SteamLaunchTests(unittest.TestCase):
    def setUp(self):
        self.registration = patch.object(sl, 'require_registered_game')
        self.registration.start()
        self.addCleanup(self.registration.stop)

    def test_game_copy_cannot_configure_real_steam_installation(self):
        self.registration.stop()
        with patch.object(sl, 'discover_games', return_value=[]):
            with self.assertRaises(ValueError): sl.require_registered_game(Path.cwd())

    def test_single_current_account_without_mostrecent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root/'userdata/1/config/localconfig.vdf'
            target.parent.mkdir(parents=True); target.write_text(config())
            with patch.object(sl,'steam_roots',return_value=[root,root]), patch.object(sl,'read_vdf',return_value={'users':{'76561197960265729':{'AutoLogin':'1'}}}):
                self.assertEqual(sl.account_config(),target)
            with patch.object(sl,'steam_roots',return_value=[root]), patch.object(sl,'read_vdf',return_value={'users':{'76561197960265729':{},'76561197960265730':{}}}):
                with self.assertRaises(ValueError): sl.account_config()

    def test_only_target_value_changes_and_quotes_roundtrip(self):
        original = '-w --logfile "C:\\my logs\\game.log"'
        source = config(original)
        updated = sl.replace_options(source, original+' '+sl.ARGUMENTS)
        self.assertEqual(sl.options(updated)[1][2], original+' '+sl.ARGUMENTS)
        self.assertEqual(sl.replace_options(updated, original), source)

    def test_missing_option_insert_remove_preserves_other_settings(self):
        source = config()
        result = sl.replace_options(source, sl.ARGUMENTS)
        restored = sl.replace_options(result, None)
        self.assertEqual(sl.parse_vdf(restored), sl.parse_vdf(source))
        self.assertIn('"99" { "LaunchOptions" "other game" }', result)
        self.assertTrue(result.startswith('// keep comment\r\n'))

    def test_missing_game_and_duplicate_keys_are_rejected(self):
        with self.assertRaises(ValueError):
            sl.replace_options(config().replace('2645580','123'), 'new')
        with self.assertRaises(ValueError):
            sl.replace_options(config().replace('"Playtime"', '"LaunchOptions" "a" "launchoptions" "b" "Playtime"'), 'new')

    def test_install_restore_preserves_later_unrelated_edits(self):
        with tempfile.TemporaryDirectory() as tmp:
            game = Path(tmp)/'game'; game.mkdir()
            account = Path(tmp)/'localconfig.vdf'; account.write_bytes(config('-w').encode())
            with patch.object(patcher,'validate_game',return_value=game), patch.object(patcher,'build',return_value=(b'fixture',{})):
                patcher.install(game)
            with patch.object(sl,'require_closed'), patch.object(sl,'account_config',return_value=account):
                sl.configure(game)
                backup = patcher.addon_dir(game)/sl.BACKUP
                before = backup.read_bytes()
                sl.configure(game)
                self.assertEqual(backup.read_bytes(),before)
                # An update keeps the original options backup.
                with patch.object(patcher,'validate_game',return_value=game), patch.object(patcher,'build',return_value=(b'new',{})):
                    patcher.install(game)
                account.write_bytes(account.read_bytes().replace(b'"42"',b'"88"'))
                patcher.uninstall(game)
                self.assertEqual(account.read_bytes(),config('-w').replace('"42"','"88"').encode())
                self.assertFalse(patcher.addon_dir(game).exists())

    def test_user_modified_options_and_wrong_account_are_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            game = Path(tmp)/'game'; game.mkdir()
            account = Path(tmp)/'localconfig.vdf'; account.write_bytes(config().encode())
            with patch.object(patcher,'validate_game',return_value=game), patch.object(patcher,'build',return_value=(b'fixture',{})):
                patcher.install(game)
            with patch.object(sl,'require_closed'), patch.object(sl,'account_config',return_value=account):
                sl.configure(game)
                account.write_bytes(sl.replace_options(account.read_text(),'-custom').encode())
                before = account.read_bytes()
                with self.assertRaises(ValueError): patcher.uninstall(game)
                self.assertEqual(account.read_bytes(),before)
                self.assertTrue((patcher.addon_dir(game)/sl.BACKUP).exists())
                with patch.object(sl,'account_config',return_value=Path(tmp)/'other'):
                    with self.assertRaises(ValueError): sl.restore(game)

    def test_running_steam_and_wrapper_leave_files_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            game = Path(tmp)/'game'; game.mkdir()
            account = Path(tmp)/'localconfig.vdf'; account.write_bytes(config('wrapper %command%').encode())
            with patch.object(patcher,'validate_game',return_value=game), patch.object(patcher,'build',return_value=(b'fixture',{})):
                patcher.install(game)
            before = account.read_bytes()
            with patch.object(sl,'require_closed',side_effect=ValueError('running')):
                with self.assertRaises(ValueError): sl.configure(game)
            with patch.object(sl,'require_closed'), patch.object(sl,'account_config',return_value=account):
                with self.assertRaises(ValueError): sl.configure(game)
            self.assertEqual(account.read_bytes(),before)
            self.assertFalse((patcher.addon_dir(game)/sl.BACKUP).exists())

    def test_failed_write_retains_original_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            game = Path(tmp)/'game'; game.mkdir()
            account = Path(tmp)/'localconfig.vdf'; account.write_bytes(config().encode())
            with patch.object(patcher,'validate_game',return_value=game), patch.object(patcher,'build',return_value=(b'fixture',{})):
                patcher.install(game)
            write = patcher.atomic_write
            def fail_config(path, data):
                if path == account: raise OSError('disk error')
                write(path,data)
            with patch.object(sl,'require_closed'), patch.object(sl,'account_config',return_value=account), patch.object(patcher,'atomic_write',side_effect=fail_config):
                with self.assertRaises(OSError): sl.configure(game)
            self.assertEqual(account.read_bytes(),config().encode())
            self.assertFalse((patcher.addon_dir(game)/sl.BACKUP).exists())


if __name__ == '__main__': unittest.main()
