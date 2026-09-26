"""Find runtime palette-remapping risks in a generated Korean addon."""
import argparse
import io
import json
from pathlib import Path, PurePosixPath
from zipfile import ZipFile
from PIL import Image


def audit(source, package):
    source_names=set(source.namelist()); package_names=set(package.namelist())
    rows={}
    checked=0
    for ani in sorted(package_names):
        if not ani.endswith('.ani'):continue
        for frame,line in enumerate(package.read(ani).decode().splitlines()):
            fields=line.split()
            if len(fields)!=5 or int(fields[2])<0:continue
            target=str(PurePosixPath(ani).parent/fields[0])
            original=target.replace('ko/','base/',1)
            if original not in source_names or target not in package_names:continue
            before=Image.open(io.BytesIO(source.read(original)))
            if before.mode!='P':continue
            checked+=1
            after=Image.open(io.BytesIO(package.read(target)))
            reason=None
            if after.mode!='P':reason='indexed_source_became_truecolor'
            elif after.getpalette()!=before.getpalette():reason='palette_index_colors_changed'
            if reason:
                row=rows.setdefault(target,{'image':target,'source':original,'reason':reason,'references':[]})
                row['references'].append({'ani':ani,'frame':frame,'colormap':int(fields[2])})
    return {'status':'runtime_risks_identified' if rows else 'palette_structure_preserved_runtime_pending',
            'indexed_frame_references_checked':checked,'risk_images':len(rows),
            'limitations':['An ANI colormap reference plus a truecolor conversion is a review target, not proof that every affected screen has incorrect colors.','Matching PNG colors do not prove matching runtime remapping, fades or highlights.','Only images referenced by addon ANI files and with matching base paths are checked.'],
            'rows':list(rows.values())}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('package',type=Path);p.add_argument('--output',type=Path)
    a=p.parse_args()
    with ZipFile(a.source) as source,ZipFile(a.package) as package: result=audit(source,package)
    text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if a.output:a.output.write_text(text,encoding='utf8')
    else:print(text)
