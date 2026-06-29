import os
import sys
import json
import urllib.request
import datetime
import argparse

BASE = "https://s3-us-west-2.amazonaws.com/elasticbeanstalk-us-west-2-200256718728/historical_data"
HEADERS = {"User-Agent": "Java/26", "Accept": "*/*", "Connection": "keep-alive"}

def fetch_index(provider, symbol):
    url = f"{BASE}/{provider}/{symbol}/index.json"
    req = urllib.request.Request(url, headers=HEADERS)
    print(f"Fetching index: {url}")
    resp = urllib.request.urlopen(req, timeout=15)
    return json.loads(resp.read().decode("utf-8"))

def ts_to_date(ts_str):
    ts = int(ts_str) / 1000
    return datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")

def download_file(provider, symbol, filename, out_dir):
    url = f"{BASE}/{provider}/{symbol}/{filename}"
    req = urllib.request.Request(url, headers=HEADERS)
    resp = urllib.request.urlopen(req, timeout=30)
    path = os.path.join(out_dir, filename)
    with open(path, "wb") as f:
        f.write(resp.read())
    size_kb = os.path.getsize(path) / 1024
    return size_kb

def main():
    parser = argparse.ArgumentParser(description="Download MotiveWave historical market data from S3")
    parser.add_argument("symbol", help="Instrument symbol (e.g. ENQU6.CME, ESU6.CME, NQZ5.CME)")
    parser.add_argument("--provider", default="CQG", help="Data provider (default: CQG)")
    parser.add_argument("--type", choices=["all", "bar", "tick"], default="all", help="Data type filter")
    parser.add_argument("--out", default="./historical_data", help="Output directory")
    parser.add_argument("--list", action="store_true", help="List available files without downloading")
    args = parser.parse_args()

    try:
        index = fetch_index(args.provider, args.symbol)
    except Exception as e:
        print(f"Failed to fetch index: {e}")
        sys.exit(1)

    # filter out index.json from the list
    files = [f for f in index if f != "index.json"]

    # apply type filter
    if args.type == "bar":
        files = [f for f in files if "bar_data" in f]
    elif args.type == "tick":
        files = [f for f in files if "tick_data" in f]

    if args.list:
        print(f"\nAvailable files for {args.provider}/{args.symbol}: {len(files)}")
        print("-" * 60)
        for f in files:
            ts = f.split(".")[0]
            dtype = "BAR" if "bar_data" in f else "TICK"
            print(f"  {ts_to_date(ts)}  {dtype:4s}  {f}")
        return

    out_dir = os.path.join(args.out, args.provider, args.symbol)
    os.makedirs(out_dir, exist_ok=True)

    print(f"\nDownloading {len(files)} files to {out_dir}")
    print("-" * 60)

    total_kb = 0
    for i, filename in enumerate(files, 1):
        ts = filename.split(".")[0]
        dtype = "BAR" if "bar_data" in filename else "TICK"
        try:
            kb = download_file(args.provider, args.symbol, filename, out_dir)
            total_kb += kb
            print(f"  [{i}/{len(files)}] {ts_to_date(ts)} {dtype:4s} {kb:.1f} KB")
        except Exception as e:
            print(f"  [{i}/{len(files)}] FAILED: {filename} ({e})")

    print(f"\nDone. Total: {total_kb/1024:.1f} MB across {len(files)} files.")
    print(f"Saved to: {os.path.abspath(out_dir)}")

if __name__ == "__main__":
    main()
