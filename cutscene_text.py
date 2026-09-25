"""Hash-bound subtitle replacement, preserving non-text script records."""
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent
HEADER=re.compile(r'^#\([^\r\n]*\)[^\r\n]*\r?\n',re.M)

def load_intro():
    return json.loads((ROOT/'translations/intro.ko.json').read_text(encoding='utf-8'))

def compile_script(raw,spec,font_paths=None):
    if hashlib.sha256(raw).hexdigest()!=spec['source_sha256']:
        raise ValueError('Cutscene source hash mismatch')
    text=raw.decode('utf-8-sig');matches=list(HEADER.finditer(text));edits=[];seen=set()
    for i,m in enumerate(matches):
        end=matches[i+1].start() if i+1<len(matches) else len(text)
        body=text[m.end():end];clean=body.rstrip('\r\n');key=f'{i:04d}'
        if clean.startswith('TFI '):
            seen.add(key)
            if key not in spec['records']:raise ValueError('Untranslated subtitle '+key)
            translated=spec['records'][key]
            if not translated.strip() or '\r' in translated or re.search(r'^#\(',translated,re.M):
                raise ValueError('Invalid subtitle '+key)
            if len(translated.splitlines())!=len(clean[4:].splitlines()):raise ValueError('Subtitle line count '+key)
            newline='\r\n' if '\r\n' in body else '\n'
            edits.append((m.end(),m.end()+len(clean),'TFI '+translated.replace('\n',newline)))
        elif font_paths and clean in font_paths:
            edits.append((m.end(),m.end()+len(clean),font_paths[clean]))
    if seen!=set(spec['records']):raise ValueError('Unknown subtitle IDs')
    for start,end,value in reversed(edits):text=text[:start]+value+text[end:]
    return text.encode('utf-8')

def add_intro(entries,rmp,archive,spec,addon):
    paths={'FONT 0 base/fonts/starcon.fon':f'FONT 0 addons/{addon}/ko/fonts/starcon.fon',
           'FONT 1 base/fonts/slides.fon':f'FONT 1 addons/{addon}/ko/fonts/slides.fon'}
    entries['ko/cutscene/intro/intro.txt']=compile_script(archive.read(spec['source_path']),spec,paths)
    prefix='base/fonts/slides.fon/'
    for name in archive.namelist():
        if name.startswith(prefix) and name.endswith('.png'):entries[name.replace('base/','ko/',1)]=archive.read(name)
    # Same native Galmuri9 glyphs already verified for the player font.
    for name,data in list(entries.items()):
        if name.startswith('ko/fonts/player.fon/') and name.endswith('.png') and int(Path(name).stem,16)>127:
            entries[name.replace('/player.fon/','/slides.fon/')]=data
    rmp.append('slides.intro = STRTAB:ko/cutscene/intro/intro.txt')


def load_ending():
    return json.loads((ROOT/'translations/ending.ko.json').read_text(encoding='utf-8'))


def compile_ending_wrapper(raw,spec,addon):
    if hashlib.sha256(raw).hexdigest()!=spec['wrapper_sha256']:
        raise ValueError('Ending wrapper hash mismatch')
    old=b'CALL base/cutscene/ending/final.txt'
    if raw.count(old)!=1:raise ValueError('Ending final CALL mismatch')
    return raw.replace(old,f'CALL addons/{addon}/ko/cutscene/ending/final.txt'.encode())


def add_ending(entries,rmp,archive,spec,addon):
    # The shared slides glyphs are prepared by add_intro before this call.
    from ending_card import add_card
    image_paths=add_card(entries,archive,addon)
    entries['ko/cutscene/ending/final.txt']=compile_script(archive.read(spec['source_path']),spec,
        {'FONT 0 base/fonts/slides.fon':f'FONT 0 addons/{addon}/ko/fonts/slides.fon',**image_paths})
    entries['ko/cutscene/ending/ending.txt']=compile_ending_wrapper(archive.read(spec['wrapper_path']),spec,addon)
    rmp.append('slides.ending = STRTAB:ko/cutscene/ending/ending.txt')
