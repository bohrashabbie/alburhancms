"""Fetch key public endpoints from the live CMS and report where asset URLs point."""
import json
import re
import urllib.request

import sys as _sys
BASE = _sys.argv[1] if len(_sys.argv) > 1 else "http://13.60.4.75:8002"
ENDPOINTS = [
    "/api/public/site-content",
    "/api/public/products",
    "/api/public/brands",
    "/api/public/carousel",
    "/api/public/banners",
    "/api/public/services",
    "/api/public/team",
    "/api/public/project-categories",
]

total_s3 = total_local = total_ip = 0
for ep in ENDPOINTS:
    try:
        with urllib.request.urlopen(BASE + ep, timeout=30) as r:
            raw = r.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"{ep}: ERROR {e}")
        continue
    s3 = len(re.findall(r"alburhan-asset\.s3", raw))
    local = re.findall(r"\"/uploads/[^\"]*", raw)
    ip = re.findall(r"http://13\.60\.4\.75[^\"]*", raw)
    total_s3 += s3
    total_local += len(local)
    total_ip += len(ip)
    print(f"{ep}: {len(raw)} bytes | s3={s3} local={len(local)} ip={len(ip)}")
    for m in local[:5]:
        print(f"   LOCAL: {m}")
    for m in ip[:5]:
        print(f"   IP:    {m}")

print(f"\nTOTALS: s3={total_s3} local={total_local} ip={total_ip}")
