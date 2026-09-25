"""Exercise real builds/install/update/uninstall in an isolated temporary fixture.

Does not launch UQM or access the user's configuration/save directory.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import patcher

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def snapshot(root):
    return {p.relative_to(root).as_posix():digest(p) for p in sorted(root.rglob('*')) if p.is_file()}

def verify(game):
    game=patcher.validate_game(game)
    real_addon_before=patcher.status(game)
    source_files=[game/'uqm.exe',game/patcher.SOURCE]
    for name in ('uqm-0.8.0-voice.uqm','uqm-0.8.0-3domusic.uqm'):
        p=game/'content/addons'/name
        if p.is_file():source_files.append(p)
    original_hashes={p.relative_to(game).as_posix():digest(p) for p in source_files}
    stages=[]
    with tempfile.TemporaryDirectory(prefix='uqm-ko-install-audit-') as tmp:
        fixture=Path(tmp)
        for p in source_files:
            dest=fixture/p.relative_to(game);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
        profile=fixture/'audit-user-profile';profile.mkdir()
        (profile/'uqm.cfg').write_bytes(b'musicvol = INT32:72\nsfxvol = INT32:83\n')
        (profile/'uqmsave.00').write_bytes(b'INERT AUDIT SAVE FIXTURE\x00\xff')
        other=fixture/'content/addons/audit-other-addon';other.mkdir(parents=True)
        (other/'keep.txt').write_bytes(b'Unrelated addon must survive all lifecycle operations.\n')
        baseline=snapshot(fixture)
        def check_owned_only():
            now=snapshot(fixture)
            for name,expected in baseline.items():
                if now.get(name)!=expected:raise AssertionError('Baseline file changed: '+name)
            expected_extra={f'content/addons/{patcher.ADDON}/ko-ui.uqm',f'content/addons/{patcher.ADDON}/manifest.json'}
            if set(now)-set(baseline)!=expected_extra:raise AssertionError('Unexpected installation file set')
        print('Fresh compact installation',flush=True)
        first=patcher.install(fixture,'compact');check_owned_only()
        if patcher.status(fixture)!=first:raise AssertionError('Installation status mismatch')
        stages.append({'stage':'fresh_install','sha256':first['sha256'],'result':'passed'})
        owned=patcher.addon_dir(fixture);times={p.name:p.stat().st_mtime_ns for p in owned.iterdir()}
        print('Identical reinstall',flush=True)
        again=patcher.install(fixture,'compact');check_owned_only()
        if again!=first or {p.name:p.stat().st_mtime_ns for p in owned.iterdir()}!=times:raise AssertionError('Identical reinstall rewrote files')
        stages.append({'stage':'idempotent_reinstall','result':'passed_no_owned_files_rewritten'})
        print('Real alternate-font package update',flush=True)
        updated=patcher.install(fixture,'larger');check_owned_only()
        if updated['sha256']==first['sha256'] or patcher.status(fixture)!=updated:raise AssertionError('Update did not replace package')
        stages.append({'stage':'update_larger_fixture_only','sha256':updated['sha256'],'result':'passed'})
        print('Removal and repeated removal',flush=True)
        if patcher.uninstall(fixture)!= {'state':'not_installed'}:raise AssertionError('Uninstall failed')
        if snapshot(fixture)!=baseline or owned.exists():raise AssertionError('Uninstall did not restore baseline file set')
        if patcher.uninstall(fixture)!= {'state':'not_installed'} or snapshot(fixture)!=baseline:raise AssertionError('Repeated uninstall changed baseline')
        stages.append({'stage':'uninstall_and_repeat','result':'passed_baseline_files_identical'})
    if {p.relative_to(game).as_posix():digest(p) for p in source_files}!=original_hashes:raise AssertionError('Real source changed')
    if patcher.status(game)!=real_addon_before:raise AssertionError('Real installed addon changed')
    return {'status':'isolated_real_build_lifecycle_passed','stages':stages,'baseline_file_hashes':baseline,
            'real_game_source_hashes':original_hashes,'real_installed_addon_unchanged':True,
            'limitations':['No game executable was launched.','Save/config preservation uses inert fixture files, not real user saves.','Does not certify cross-version migration, process-crash/power-loss recovery, or linguistic/runtime quality.','Larger UI is an existing experimental option used only to exercise a differing update package; it was not installed in the real game.']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--game',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    report=verify(a.game)
    a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'report':str(a.report)},ensure_ascii=False))
