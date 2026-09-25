"""Compare installed UQM glyphs with candidates; game-derived output stays ignored."""
import argparse, io, json, zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
SAMPLE='우리는 너희의 응답을 기다린다.'
ENGLISH='We await your reply.'
BG='#0e1725'; FG='#f4eddb'; BLUE='#80cdf1'
def font(file,size): return ImageFont.truetype(str(file),size)
def korean(info,size,binary=True):
 f=font(ROOT/info['file'],size); box=f.getbbox(SAMPLE)
 im=Image.new('L',(box[2]-box[0],box[3]-box[1])); ImageDraw.Draw(im).text((-box[0],-box[1]),SAMPLE,font=f,fill=255)
 return im.point(lambda a:255 if a>=128 else 0) if binary else im

def paste_mask(canvas,mask,xy,scale=3,color=FG):
 mask=mask.resize((mask.width*scale,mask.height*scale),Image.Resampling.NEAREST)
 canvas.paste(color,xy,mask)

def original(archive,path):
 prefix=path.removeprefix('FONTRES:')+'/'
 glyphs=[]
 for c in ENGLISH:
  try:
   im=Image.open(io.BytesIO(archive.read(prefix+f'{ord(c):05x}.png'))).convert('RGBA')
  except KeyError:
   glyphs.append((None,4,0)); continue
  alpha=im.getchannel('A')
  if alpha.getextrema()==(255,255): alpha=im.convert('L')
  h=im.height; hotspot=7 if h in (8,9) else h-3
  glyphs.append((alpha,im.width+1,hotspot))
 top=max((h for m,w,h in glyphs if m),default=0)
 bottom=max((m.height-h for m,w,h in glyphs if m),default=0)
 out=Image.new('L',(sum(w for m,w,h in glyphs),max(1,top+bottom)))
 x=0
 for m,w,h in glyphs:
  if m: out.paste(m,(x,top-h))
  x+=w
 return out

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--game',type=Path,required=True); args=ap.parse_args()
 reg=json.loads((ROOT/'translations/fonts.ko.json').read_text(encoding='utf-8'))
 labels=font(ROOT/'vendor/galmuri/Galmuri11.ttf',24)
 small=font(ROOT/'vendor/galmuri/Galmuri11.ttf',12)
 out=ROOT/'artifacts/font-review'; out.mkdir(parents=True,exist_ok=True)
 order=reg['expressive_specimen_order']
 overview=Image.new('RGB',(1600,100+len(order)*232),BG); d=ImageDraw.Draw(overview)
 d.text((24,18),'개성 있는 한글 8종 / 실제 폰트 렌더링',font=labels,fill=FG)
 d.text((24,55),'왼쪽: 24px 안티앨리어싱 2배 / 오른쪽: 12px/16px 이진화, 16px AA 3배 (게임 화면 아님)',font=small,fill=BLUE)
 for i,name in enumerate(order):
  y=100+i*232; info=reg['fonts'][name]
  d.line((24,y-8,1570,y-8),fill='#2c3d50'); d.text((24,y),name,font=labels,fill=BLUE)
  paste_mask(overview,korean(info,24,False),(24,y+55),2)
  for size,dy in [(12,40),(16,104)]:
   d.text((760,y+dy-18),f'{size}px binary / 3x',font=small,fill=BLUE)
   paste_mask(overview,korean(info,size),(760,y+dy),3)
  d.text((760,y+150),'16px AA / 3x (가장자리 유지)',font=small,fill=BLUE)
  paste_mask(overview,korean(info,16,False),(760,y+170),3)
 overview.save(ROOT/'docs/expressive-fonts.png')
 archive=zipfile.ZipFile(args.game/'content/packages/uqm-0.8.0-content.uqm')
 cards=[]
 for row in reg['dialogue_fonts']:
  name=row['candidate_font']; info=reg['fonts'][name]
  card=Image.new('RGB',(1320,270),BG); d=ImageDraw.Draw(card)
  d.text((24,10),row['id']+'  /  '+name+' (후보)',font=labels,fill=BLUE)
  d.text((24,52),'원본 영문 PNG / 3배',font=small,fill=FG)
  if row['original_font']:
   paste_mask(card,original(archive,row['original_font']),(24,82))
  else:
   d.text((24,85),'독립 리소스 없음: 공유 관계 확인 필요',font=small,fill=FG)
  d.text((24,170),'같은 영문 표본 / 한글 표본으로 형태 비교',font=small,fill=BLUE)
  outline=info.get('raster_kind')=='outline'
  sizes=[12,16] if outline else [info['raster_px']]
  for j,size in enumerate(sizes):
   y=60+j*62; d.text((655,y-16),f'{size}px binary / 3x'+('' if outline else ' / native pixel'),font=small,fill=BLUE)
   paste_mask(card,korean(info,size),(655,y),3)
  if outline:
   d.text((655,178),'16px AA / 3x (가장자리 유지)',font=small,fill=BLUE)
   paste_mask(card,korean(info,16,False),(655,195),3)
  d.line((24,266,1290,266),fill='#2c3d50')
  cards.append(card)
 for page in range(3):
  sheet=Image.new('RGB',(1320,70+9*270),BG); d=ImageDraw.Draw(sheet)
  d.text((24,15),f'원본 영문 / 한글 후보 비교 {page+1}/3 — 미확정, 게임 미적용',font=labels,fill=FG)
  for j,c in enumerate(cards[page*9:(page+1)*9]):sheet.paste(c,(0,70+j*270))
  sheet.save(out/f'comparison-{page+1}.png')
 picks=['chmmr','pkunk','mycon','shofixti','syreen','spathi']
 featured=Image.new('RGB',(1320,len(picks)*270),BG)
 for i,id in enumerate(picks):featured.paste(cards[next(j for j,r in enumerate(reg['dialogue_fonts']) if r['id']==id)],(0,i*270))
 featured.save(out/'featured.png')
 body=''.join(f'<h2>종족별 비교 {i}</h2><img src="comparison-{i}.png">' for i in range(1,4))
 (out/'index.html').write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><title>UQM 폰트 비교</title><style>body{background:#0e1725;color:#f4eddb;font:18px sans-serif;margin:24px}img{max-width:100%;height:auto}a{color:#80cdf1}</style><h1>원본 영문과 한글 후보</h1><p>게임에서 추출한 원본 글리프와 별도 한글 글꼴을 같은 3배 확대율로 비교합니다. 12/16px는 시험 크기이며 행간/레이아웃 적용 완료를 뜻하지 않습니다. 24px는 디자인 참고입니다. 축소된 브라우저 화면보다 원본 크기로 확대해 확인하세요.</p><a href="../../docs/expressive-fonts.png">새 글꼴 8종 비교</a>'+body+'</html>',encoding='utf-8')
 print(out/'index.html')
if __name__=='__main__':main()

