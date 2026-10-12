from pathlib import Path
import shutil,zipfile
R=Path(__file__).resolve().parents[1];src=R/'cad/fullsize';dest=R/'site/fullsize';dest.mkdir(exist_ok=True)
for p in (src/'exports').iterdir():
 if p.is_file():shutil.copy2(p,dest/p.name)
for p in (R/'docs/manufacturing').glob('*.md'):shutil.copy2(p,dest/p.name)
with zipfile.ZipFile(dest/'review-package.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
 for p in sorted(src.rglob('*')):
  if p.is_file() and '__pycache__' not in p.parts:z.write(p,'cad/'+str(p.relative_to(src)))
 for p in sorted((R/'docs/manufacturing').glob('*.md')):z.write(p,'review/'+p.name)
print('Full-size review package:',(dest/'review-package.zip').stat().st_size,'bytes')
