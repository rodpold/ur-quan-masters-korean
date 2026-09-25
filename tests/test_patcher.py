import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import patcher

class PatcherTests(unittest.TestCase):
    def test_records_keep_headers_order_and_duplicates(self):
        text = '#(game) -- BASE\r\ngame\r\n\r\n#()\r\n\r\n#(game)\r\ngame\r\n'
        result, counts = patcher.translate_table(text, {'game':'게임'})
        self.assertEqual(result, text.replace('\r\ngame\r\n','\r\n게임\r\n'))
        self.assertEqual(counts,{'game':2})
    def test_missing_translation_fails_closed(self):
        with self.assertRaises(ValueError):
            patcher.translate_table('#(a)\na\n',{'missing':'없음'})
    def test_install_idempotency_and_modified_uninstall_refusal(self):
        with tempfile.TemporaryDirectory() as tmp:
            game=Path(tmp)
            with patch.object(patcher,'validate_game',return_value=game), patch.object(patcher,'build',return_value=(b'fixture',{})):
                first=patcher.install(game)
                self.assertEqual(patcher.install(game),first)
                package=patcher.addon_dir(game)/'ko-ui.uqm'
                package.write_bytes(b'changed by user')
                with self.assertRaises(ValueError): patcher.uninstall(game)
                self.assertEqual(package.read_bytes(),b'changed by user')
                package.write_bytes(b'fixture')
                keep=game/'uqm.exe'; keep.write_bytes(b'original')
                patcher.uninstall(game)
                self.assertEqual(keep.read_bytes(),b'original')
                self.assertEqual(patcher.status(game)['state'],'not_installed')
    def test_foreign_directory_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            game=Path(tmp); target=patcher.addon_dir(game);target.mkdir(parents=True)
            foreign=target/'notes.txt';foreign.write_text('user notes')
            with self.assertRaises(ValueError): patcher.uninstall(game)
            self.assertEqual(foreign.read_text(),'user notes')


class RegressionTests(unittest.TestCase):
    def test_setup_preserves_headers_and_empty_menu_item(self):
        source='#(SUBTITLES)\n\nGraphics\nAudio\n\n#(TITLE)\nSetup\n'
        result=patcher.translate_setup(source,{'SUBTITLES':'\n화면\n소리','TITLE':'설정'})
        self.assertEqual(result,'#(SUBTITLES)\n\n화면\n소리\n\n#(TITLE)\n설정\n')
        with self.assertRaises(ValueError):
            patcher.translate_setup(source,{'SUBTITLES':'화면\n소리','TITLE':'설정'})
    def test_update_rolls_back_on_manifest_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            game=Path(tmp)
            with patch.object(patcher,'validate_game',return_value=game), patch.object(patcher,'build',return_value=(b'old',{})):
                first=patcher.install(game)
            original_write=patcher.atomic_write
            count=0
            def fail_second(path,data):
                nonlocal count
                count+=1
                if count==2: raise OSError('simulated disk error')
                return original_write(path,data)
            with patch.object(patcher,'validate_game',return_value=game), patch.object(patcher,'build',return_value=(b'new',{})), patch.object(patcher,'atomic_write',side_effect=fail_second):
                with self.assertRaises(OSError):patcher.install(game)
            self.assertEqual(patcher.status(game),first)
            self.assertEqual((patcher.addon_dir(game)/'ko-ui.uqm').read_bytes(),b'old')
    def test_upgrade_replaces_only_owned_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            game=Path(tmp)
            cfg=game/'uqm.cfg';cfg.write_bytes(b'musicvol = INT32:74')
            save=game/'save.00';save.write_bytes(b'user save')
            for content in [b'old',b'new']:
                with patch.object(patcher,'validate_game',return_value=game),patch.object(patcher,'build',return_value=(content,{})):
                    patcher.install(game)
            self.assertEqual((patcher.addon_dir(game)/'ko-ui.uqm').read_bytes(),b'new')
            patcher.uninstall(game)
            self.assertEqual(cfg.read_bytes(),b'musicvol = INT32:74')
            self.assertEqual(save.read_bytes(),b'user save')
    def test_launch_preserves_audio_and_existing_test_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            game=Path(tmp);profile=game/'test';profile.mkdir()
            cfg=profile/'uqm.cfg';original=b'musicvol = INT32:72\nsfxvol = INT32:83\n';cfg.write_bytes(original)
            with patch.object(patcher,'validate_game',return_value=game),patch.object(patcher,'status',return_value={'state':'installed'}),patch.object(patcher.subprocess,'Popen') as popen:
                patcher.launch(game,profile)
                self.assertEqual(cfg.read_bytes(),original)
                argv=popen.call_args.args[0]
                self.assertIn('--configdir',argv)
                self.assertFalse(any('vol' in arg for arg in argv))

if __name__ == '__main__': unittest.main()
