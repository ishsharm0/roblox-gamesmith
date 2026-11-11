import importlib.machinery
import importlib.util
import pathlib
import unittest
from unittest.mock import patch
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]

def load(name):
    loader = importlib.machinery.SourceFileLoader(name, str(ROOT / 'tools' / name))
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module

class StudioSelectionTests(unittest.TestCase):
    def test_open_reuses_existing_window_without_killing_studio(self):
        driver = load('rbxgame')
        with patch.object(driver, 'project', return_value={'name':'Test'}), \
             patch.object(driver, 'studio_window_open', return_value=[123]), \
             patch.object(driver, 'cmd_save'), patch.object(driver, 'cmd_build'), \
             patch.object(driver, 'cmd_push') as push, \
             patch.object(driver, 'sh'), patch.object(driver.time, 'sleep'), \
             patch.object(driver.os, 'kill') as kill:
            driver.cmd_open([])
            kill.assert_not_called()
            push.assert_called_once()
    def test_updated_launcher_window_is_found_through_mcp(self):
        driver = load('rbxgame')
        results = [subprocess.CompletedProcess([], 1, '', ''),
                   subprocess.CompletedProcess([], 0, '{"studios":[{"id":"safe-window","name":"QualityValidation.rbxlx"}]}', '')]
        with patch.dict(driver.os.environ, {'STUDIO_REMOTE': ''}), \
             patch.object(driver.subprocess, 'run', side_effect=results):
            self.assertEqual(driver.studio_window_open('/tmp/QualityValidation.rbxlx'), ['safe-window'])

    def test_remote_studio_skips_the_local_process_check(self):
        driver = load('rbxgame')
        listing = subprocess.CompletedProcess([], 0, '{"studios":[{"id":"pc-window","name":"Game.rbxlx"}]}', '')
        with patch.dict(driver.os.environ, {'STUDIO_REMOTE': 'user@pc'}), \
             patch.object(driver.subprocess, 'run', side_effect=[listing]) as run:
            self.assertEqual(driver.studio_window_open('/tmp/Game.rbxlx'), ['pc-window'])
            self.assertEqual(run.call_count, 1)

    def test_explicit_unknown_window_never_falls_back(self):
        studio = load('studio')
        with patch.object(studio, 'studios', return_value='{"studios":[{"id":"other","name":"Other Game"}]}'):
            with self.assertRaises(SystemExit):
                studio.pick_studio(None, 'Lily-Pad-Leap.rbxlx')

    def test_failed_scenario_exits_nonzero_and_always_stops(self):
        driver = load('rbxgame')
        with patch.object(driver, 'project', return_value={'name':'Test'}), \
             patch('builtins.open', unittest.mock.mock_open(read_data='error("failure")')), \
             patch.object(driver.time, 'sleep'), \
             patch.object(driver, 'studio', return_value=subprocess.CompletedProcess([],0,'','')) as studio, \
             patch.object(driver.subprocess, 'run', return_value=subprocess.CompletedProcess([],1,'scenario failed','')):
            with self.assertRaises(SystemExit):
                driver.cmd_test(['scenario.luau'])
            self.assertIn(unittest.mock.call('stop', check=False), studio.call_args_list)

if __name__ == '__main__':
    unittest.main()
