
import json,datetime
d=json.load(open('data.json'))
xd=json.load(open('raw/2026-11-23/x_drafts.json'))
d['drafts_today']=xd
d.setdefault('trend_radar',{})['ideas']=xd
d['updated']=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
d['watch_window']='2026-11-16T18Z to '+datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ')
json.dump(d,open('data.json','w'),indent=2,ensure_ascii=False)
