"""Fetch MS-Lighting pages and report whether media references point to S3 or local /public paths."""
import re
import sys
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5001"
PAGES = ["/", "/products", "/manufacturing", "/projects", "/commercial", "/downloads"]

LOCAL_RE = re.compile(r'(?:src|href)="(/(?:renders|scenes|banners|markets|video)/[^"]+)"')
S3_RE = re.compile(r"alburhan-asset\.s3[^\"\\&]*")

total_local = total_s3 = 0
for page in PAGES:
    try:
        req = urllib.request.Request(BASE + page, headers={"User-Agent": "check"})
        with urllib.request.urlopen(req, timeout=60) as r:
            html = r.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"{page}: ERROR {e}")
        continue
    local = LOCAL_RE.findall(html)
    s3 = S3_RE.findall(html)
    total_local += len(local)
    total_s3 += len(s3)
    print(f"{page}: s3-refs={len(s3)} local-media-refs={len(local)}")
    for m in local[:10]:
        print(f"   LOCAL: {m}")

print(f"\nTOTALS: s3={total_s3} local={total_local}")
