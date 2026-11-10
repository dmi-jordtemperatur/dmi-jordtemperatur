import csv
import json
import math
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = 'https://opendataapi.dmi.dk/v2/metObs/collections/observation/items'
OUT = Path('jordtemperatur.csv')
FIELDS = ['stationId', 'temperatur', 'lat', 'lon', 'målt_utc', 'målt_dansk_tid']
MAX_AGE_HOURS = 2


def get_json(url):
    request = Request(url, headers={'User-Agent': 'dmi-soil-temperature-map/1.0', 'Accept': 'application/geo+json'})
    with urlopen(request, timeout=60) as response:
        return json.load(response)


def main():
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=24)
    params = {
        'parameterId': 'temp_soil',
        'bbox': '7,54,16,58',
        'datetime': f'{start.isoformat().replace("+00:00", "Z")}/{now.isoformat().replace("+00:00", "Z")}',
        'limit': 10000,
    }
    url = BASE + '?' + urlencode(params)
    latest = {}
    seen_urls = set()
    while url:
        if url in seen_urls:
            raise RuntimeError('DMI pagination loop detected')
        seen_urls.add(url)
        payload = get_json(url)
        for feature in payload.get('features', []):
            props = feature.get('properties') or {}
            geometry = feature.get('geometry') or {}
            coords = geometry.get('coordinates') or []
            if props.get('parameterId') != 'temp_soil' or len(coords) < 2:
                continue
            station = props.get('stationId')
            value = props.get('value')
            observed = props.get('observed')
            if not station or not observed or not isinstance(value, (float, int)) or not math.isfinite(value):
                continue
            lon, lat = coords[:2]
            if not all(isinstance(x, (float, int)) and math.isfinite(x) for x in (lon, lat)):
                continue
            if not (7 <= lon <= 16 and 54 <= lat <= 58):
                continue
            try:
                timestamp = datetime.fromisoformat(observed.replace('Z', '+00:00'))
            except ValueError:
                continue
            if timestamp.tzinfo is None:
                continue
            if timestamp > now or now - timestamp > timedelta(hours=MAX_AGE_HOURS):
                continue
            old = latest.get(station)
            if old is None or timestamp > old['timestamp']:
                latest[station] = {'timestamp': timestamp, 'temperature': value, 'lat': lat, 'lon': lon}
        next_link = next((link.get('href') for link in payload.get('links', []) if link.get('rel') == 'next'), None)
        url = next_link

    if not latest:
        raise RuntimeError('No recent DMI soil observations found. Existing CSV is left unchanged.')

    from zoneinfo import ZoneInfo
    dk = ZoneInfo('Europe/Copenhagen')
    with OUT.open('w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        for station, item in sorted(latest.items()):
            writer.writerow({
                'stationId': station,
                'temperatur': item['temperature'],
                'lat': item['lat'],
                'lon': item['lon'],
                'målt_utc': item['timestamp'].isoformat(timespec='minutes'),
                'målt_dansk_tid': item['timestamp'].astimezone(dk).strftime('%Y-%m-%d %H:%M %Z'),
            })
    print(f'Wrote {len(latest)} stations to {OUT}')


if __name__ == '__main__':
    main()
