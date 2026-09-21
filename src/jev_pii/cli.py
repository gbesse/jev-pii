# Purpose: Scan JSON column maps, preview payloads, diff and render reports.
import argparse,json,sys
from pathlib import Path
from .core import *
def main(argv=None):
 p=argparse.ArgumentParser(prog='jev-pii');p.add_argument('command',choices=['scan','estimate','report','diff']);p.add_argument('input');p.add_argument('other',nargs='?');p.add_argument('--out');p.add_argument('--local-only',action='store_true');p.add_argument('--dry-run',action='store_true');p.add_argument('--mask',action='store_true');a=p.parse_args(argv)
 try:
  first=json.loads(Path(a.input).read_text())
  if a.command=='diff':result=diff(first,json.loads(Path(a.other).read_text()))
  elif a.command=='report':Path(a.out).write_text(html_report(first));return
  else:result=scan_columns(first,local_only=a.local_only or not a.dry_run,dry_run=a.dry_run,mask=a.mask,transport=FakeJev());result['payloads']=[x.decode() for x in result['payloads']]
  text=json.dumps(result,indent=2);Path(a.out).write_text(text) if a.out else print(text)
 except Exception as e:print(f'jev-pii: {e}',file=sys.stderr);raise SystemExit(1)
