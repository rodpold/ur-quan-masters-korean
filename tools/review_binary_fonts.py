"""Render binary-only race proposals and verify unique font families/files."""
import argparse,io,json,math,zipfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from render_expressive_fonts import original
ROOT=Path(__file__).resolve().parents[1]
SAMPLE='교신을 계속하라.'
BG='#101928';FG='#f3efd9';BLUE='#83c7ed'

def load():return json.loads((ROOT/'translations/fonts.ko.json').read_text(encoding='utf-8'))
def corpus():
 texts=[SAMPLE,'함장, 응답하라.','우리는 너희의 응답을 기다린다.','함장, 교신을 계속할까요? 켬 / 끔']
 for p in [ROOT/'translations/ui.ko.json',ROOT/'translations/setup.ko.json',*(ROOT/'translations/dialogue').glob('*.json')]:texts.extend(json.loads(p.read_text(encoding='utf-8')).values())
 return sorted({c for t in texts for c in t if ord(c)>127})

def specimen(info,size,text=SAMPLE):
 face=ImageFont.truetype(str(ROOT/info['file']),size)
 chars=corpus();boxes=[face.getbbox(c) for c in chars];top=min(b[1] for b in boxes);bottom=max(b[3] for b in boxes)
 parts=[]
 for c in text:
  b=face.getbbox(c);left=min(0,b[0]);w=max(1,math.ceil(face.getlength(c)),b[2]-left)
  m=Image.new('L',(w,bottom-top));ImageDraw.Draw(m).text((-left,-top),c,font=face,fill=255)
  parts.append(m.point(lambda a:255 if a>=128 else 0))
 result=Image.new('L',(sum(m.width+1 for m in parts)-1,bottom-top));x=0
 for m in parts:result.paste(m,(x,0));x+=m.width+1
 assert set(result.tobytes())<={0,255}
 return result

def check(reg):
 groups={};results={};chars=corpus()
 for row in reg['dialogue_fonts']:
  group=row['font_group'];name=row['candidate_font'];info=reg['fonts'][name]
  if group in groups:assert groups[group]==name
  groups[group]=name
  face=ImageFont.truetype(str(ROOT/info['file']),row['candidate_raster_px']);notdef=bytes(face.getmask(chr(0x10ffff)))
  missing=[c for c in chars if bytes(face.getmask(c))==notdef or not any(face.getmask(c))]
  blank_binary=[]
  for c in chars:
   if not any(a>=128 for a in bytes(face.getmask(c))):blank_binary.append(c)
  assert not missing and not blank_binary,(name,missing,blank_binary)
  mask=specimen(info,row['candidate_raster_px'])
  results[row['id']]={'font':name,'group':group,'raster_px':row['candidate_raster_px'],'checked_characters':len(chars),'missing':missing,'blank_binary':blank_binary,'sample_ink_height':mask.getbbox()[3]-mask.getbbox()[1],'shared_baseline_box_height':mask.height,'alpha_levels':[0,255],'game_layout_verified':False}
 assert len(groups)==24 and len(set(groups.values()))==24
 assert len({reg['fonts'][n]['design_family'] for n in groups.values()})==24
 assert len({reg['fonts'][n]['file'] for n in groups.values()})==24
 assert len({reg['fonts'][n]['sha256'] for n in groups.values()})==24
 return {'groups':24,'dialogue_ids':len(results),'distinct_files':24,'results':results}

def paste(canvas,mask,xy):
 assert xy[0]+mask.width*3<=canvas.width-15
 assert xy[1]+mask.height*3<=canvas.height-10
 canvas.paste(FG,xy,mask.resize((mask.width*3,mask.height*3),Image.Resampling.NEAREST))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--game',required=True,type=Path);a=ap.parse_args();reg=load();report=check(reg)
 (ROOT/'docs/binary-font-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 rows=[r for r in reg['dialogue_fonts'] if r['id']==r['font_group']]
 label=ImageFont.truetype(str(ROOT/'vendor/galmuri/Galmuri11.ttf'),24);small=ImageFont.truetype(str(ROOT/'vendor/galmuri/Galmuri11.ttf'),12)
 for page in range(2):
  sheet=Image.new('RGB',(1600,70+6*180),BG);d=ImageDraw.Draw(sheet);d.text((20,15),f'종족별 흑백 폰트 24종 / {page+1} / 배정안, 게임 미적용',font=label,fill=FG)
  for i,row in enumerate(rows[page*12:(page+1)*12]):
   x=20+(i%2)*800;y=75+(i//2)*180;name=row['candidate_font'];size=row['candidate_raster_px']
   d.text((x,y),row['id']+' / '+name,font=label,fill=BLUE);d.text((x,y+32),f'{size}px 렌더링 / 3배 확대 / 알파 0 또는 255',font=small,fill=FG)
   paste(sheet,specimen(reg['fonts'][name],size),(x,y+62));d.line((x,y+168,x+755,y+168),fill='#304050')
  sheet.save(ROOT/f'docs/binary-race-fonts-{page+1}.png')
 out=ROOT/'artifacts/binary-font-review';out.mkdir(exist_ok=True,parents=True);cards=[]
 with zipfile.ZipFile(a.game/'content/packages/uqm-0.8.0-content.uqm') as z:
  for row in reg['dialogue_fonts']:
   card=Image.new('RGB',(1450,210),BG);d=ImageDraw.Draw(card);name=row['candidate_font'];size=row['candidate_raster_px']
   d.text((20,8),row['id']+' / '+name,font=label,fill=BLUE)
   d.text((20,44),'원본 영문 PNG / 3배',font=small,fill=FG)
   if row['original_font']:paste(card,original(z,row['original_font']),(20,73))
   else:d.text((20,73),'독립 리소스 없음; 그룹 공유 배정안',font=small,fill=FG)
   d.text((690,44),f'한글 {size}px / 흑백 / 3배 / 게임 적용 전',font=small,fill=FG)
   paste(card,specimen(reg['fonts'][name],size),(690,68))
   d.text((20,155),row['selection_reason'],font=small,fill=BLUE)
   d.text((20,180),row['review_caveat'],font=small,fill=FG);cards.append(card)
 for page in range(3):
  sheet=Image.new('RGB',(1450,9*210),BG)
  for i,c in enumerate(cards[page*9:(page+1)*9]):sheet.paste(c,(0,i*210))
  sheet.save(out/f'comparison-{page+1}.png')
 picks=['kohrah','pkunk','melnorme','talkingpet','umgah','vux'];featured=Image.new('RGB',(1450,6*210),BG)
 for i,id in enumerate(picks):featured.paste(cards[next(j for j,r in enumerate(reg['dialogue_fonts']) if r['id']==id)],(0,i*210))
 featured.save(out/'featured.png')
 body=''.join(f'<h2>원본 비교 {i}</h2><img src="comparison-{i}.png">' for i in range(1,4))
 (out/'index.html').write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><title>흑백 종족 폰트 비교</title><style>body{background:#101928;color:#f3efd9;font:18px sans-serif;margin:24px}img{max-width:100%}</style><h1>24개 그룹 / 24개 독립 폰트</h1><p>같은 종족의 별도 대화 3개만 공유합니다. 반투명 없음. 3배 최근접 확대이며 게임 화면은 아닙니다. 렌더링 크기는 설치 보장이 아니며 실제 자막 공간/긴 대사/색상별 가독성은 검증 전입니다. 미확정 배정안입니다.</p>'+body+'</html>',encoding='utf-8')
 print('PASS: 24 unique groups/files; binary glyph coverage and preview bounds checked.')
 print(out/'index.html')
if __name__=='__main__':main()
