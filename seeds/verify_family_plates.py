"""Verify categoryRender covers all 15 family slugs."""
import sys
sys.path.insert(0, r"c:\dumbstack\ab1\web")
# Can't import TS — just check S3 + list expected
import urllib.request

BASE = "https://alburhan-asset.s3.eu-north-1.amazonaws.com/site"
FAMILIES = [
  "track-spot-light","magnet-light","linear-light","ceiling-light","high-bay",
  "module-series","wall-light","lawn-light","street-light","flood-light",
]
RENDERS = [
  "renders/MS-240R.png","renders/MS-252.png","renders/MS-220GR.png",
  "renders/MS-1140.png","renders/MS-341AR.png",
]

ok = fail = 0
for slug in FAMILIES:
    url = f"{BASE}/families/{slug}.webp"
    try:
        r = urllib.request.urlopen(url, timeout=20)
        print(f"OK  {slug} {r.status}")
        ok += 1
    except Exception as e:
        print(f"FAIL {slug} {e}")
        fail += 1
for path in RENDERS:
    url = f"{BASE}/{path}"
    try:
        r = urllib.request.urlopen(url, timeout=20)
        print(f"OK  {path} {r.status}")
        ok += 1
    except Exception as e:
        print(f"FAIL {path} {e}")
        fail += 1
print(f"ok={ok} fail={fail}")
sys.exit(0 if fail == 0 else 1)
