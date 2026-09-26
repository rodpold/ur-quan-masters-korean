import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from steam_discovery import discover_games, parse_vdf, select_game, CONTENT


class SteamDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def game(self, library, appid='2645580', folder='Free Stars 테스트'):
        steamapps = library/'steamapps'
        steamapps.mkdir(parents=True, exist_ok=True)
        (steamapps/'appmanifest_2645580.acf').write_text(
            f'"AppState" {{ "appid" "{appid}" "installdir" "{folder}" }}', encoding='utf-8')
        game = steamapps/'common'/folder
        (game/CONTENT).parent.mkdir(parents=True, exist_ok=True)
        (game/CONTENT).touch()
        (game/'uqm.exe').touch()
        return game.resolve()

    def test_secondary_library_and_duplicate_roots(self):
        root = self.root/'Steam'; root.mkdir()
        extra = self.root/'Extra library'
        expected = self.game(extra)
        (root/'steamapps').mkdir()
        (root/'steamapps/libraryfolders.vdf').write_text(
            '"libraryfolders" { "1" { "path" '+json.dumps(str(extra))+' "apps" { "2645580" "1" } } }')
        self.assertEqual(discover_games([root, extra, root]), [expected])

    def test_old_library_format(self):
        root = self.root/'Steam'; (root/'steamapps').mkdir(parents=True)
        extra = self.root/'Other'
        expected = self.game(extra)
        (root/'steamapps/libraryfolders.vdf').write_text('"libraryfolders" { "1" '+json.dumps(str(extra))+' }')
        self.assertEqual(discover_games([root]), [expected])

    def test_missing_assets_wrong_app_and_traversal_are_rejected(self):
        root = self.root/'Steam'
        game = self.game(root)
        (game/'uqm.exe').unlink()
        self.assertEqual(discover_games([root]), [])
        self.game(root, appid='1')
        self.assertEqual(discover_games([root]), [])
        manifest = root/'steamapps/appmanifest_2645580.acf'
        for name in ('../escape', '..', 'C:/escape', r'..\\escape'):
            manifest.write_text('"AppState" { "appid" "2645580" "installdir" '+json.dumps(name)+' }')
            self.assertEqual(discover_games([root]), [])

    def test_bad_metadata_does_not_hide_valid_other_install(self):
        bad = self.root/'bad'; (bad/'steamapps').mkdir(parents=True)
        (bad/'steamapps/libraryfolders.vdf').write_text('"libraryfolders" {')
        expected = self.game(self.root/'good')
        self.assertEqual(discover_games([bad, self.root/'good']), [expected])

    def test_vdf_escape_comments_and_rejection(self):
        self.assertEqual(parse_vdf('// comment\n"path" "C:\\\\Steam"'), {'path': r'C:\Steam'})
        for text in ('"a" {', '"a" "x" "a" "y"', '}', '"a"', 'unquoted'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_vdf(text)

    def test_selection_never_guesses_and_explicit_wins(self):
        for games in ([], [Path('one'), Path('two')]):
            with patch('steam_discovery.discover_games', return_value=games):
                with self.assertRaises(ValueError): select_game()
                self.assertEqual(select_game('chosen'), Path('chosen'))
        with patch('steam_discovery.discover_games', return_value=[Path('one')]):
            self.assertEqual(select_game(), Path('one'))


if __name__ == '__main__':
    unittest.main()
