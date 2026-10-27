# Daily refresh procedure

Read-only on X. **Never post, reply, like, or write to X.** Never invent metrics: every view count comes from an X API `public_metrics.impression_count` read during the run.

## 0. Setup
```bash
cd /workspace
[ -d CatDowney.github.io ] || gh repo clone CatDowney/CatDowney.github.io
cd CatDowney.github.io && git pull --ff-only
TODAY=$(TZ=America/Vancouver date +%F)
START=$(date -u -d '7 days ago' +%Y-%m-%dT%H:00:00Z)
mkdir -p raw/$TODAY
```
Settings live in `config/watchlist.json`: timezone America/Vancouver, min_views 5000, star_views 10000, 8 accounts, operator @cat1cato.

## 1. Fetch watchlist posts (X public read tools, `x` namespace)
1. `get_users_by_usernames` with all handles from `config/watchlist.json` → numeric ids (cached ids below).
2. For each id: `get_users_posts` with `exclude=retweets,replies`, `start_time=$START`, `max_results=25`, `post.fields=public_metrics,created_at,author_id,referenced_tweets`. Follow `meta.next_token` via `pagination_token` until empty.
3. Optional cross-check: `search_posts_all` with `(from:a OR from:b ...) -is:retweet -is:reply -is:quote`, same start_time.
4. Save every raw response to `raw/$TODAY/<handle>.json`.
5. Keep **originals only**: drop posts whose `referenced_tweets` has type `quoted`, `retweeted` or `replied_to`.

Cached ids: skincarebyhyram 915643808649404416, DiscoverSelf 24968293, cerave 44693072, LabMuffin 428650517, GlowRecipe 2584952916, PaulasChoice 15842700, sokoglam 773058170, drdrayzday 805778873996771328.

## 2. Rebuild data.json
Keep brand fields unchanged (`brand_title`, `brand_handle`, `operator`, `ui`). Replace:
- `date`=$TODAY, `updated`=now (UTC ISO), `watch_window`.
- `watchlist_posts_7d`: all originals `{handle,name,views,url,posted_at,text}` sorted by views desc.
- `hits`: originals with views ≥ 5000; set `highlight: true` (★) when views ≥ 10000; `hook` = first ~140 chars of text. `hits_count` = len(hits).
- `no_hits`: one entry per account with no hit, `reason` stating post count and the highest observed views, `max_views`.
- `day_roster`: one row per account `{handle,name,views:best,total_views:sum,hit}`.
- `drafts_today` / `trend_radar.ideas`: today's operator drafts (only drafts supplied by Cat; no metrics).
- `trend_keywords.keywords`: `[{rank,keyword}]` from `config/watchlist.json` `keyword_domain_terms` (currently skin barrier, winter dryness, menopause skin, fewer products, three-step routine).
- Week/month boards: upsert today into `leaderboard_ledger.json`, then `python3 enrich_leaderboards.py` (env `XVS_DATA=data.json XVS_WATCHLIST=config/watchlist.json XVS_TIMEZONE=America/Vancouver XVS_MIN_VIEWS=5000 XVS_OPERATOR_HANDLE=@cat1cato`).
Validate: `python3 -m json.tool data.json >/dev/null`.

## 3. Preview (optional)
`python3 -m http.server 8765` → open http://127.0.0.1:8765/ and confirm the header meta shows $TODAY.

## 4. Push and verify
```bash
git add data.json raw/ leaderboard_ledger.json 2>/dev/null; git add -A
git commit -m "Daily refresh $TODAY" && git push origin main
# Pages rebuilds automatically; wait for it
until [ "$(gh api repos/CatDowney/CatDowney.github.io/pages --jq .status)" = built ]; do sleep 15; done
curl -s -o /dev/null -w '%{http_code}\n' https://catdowney.github.io/data.json   # expect 200
curl -s "https://catdowney.github.io/data.json?ts=$(date +%s)" | grep -q "\"date\": \"$TODAY\"" && echo fresh
```
If Pages was ever disabled: `gh api repos/CatDowney/CatDowney.github.io/pages -X POST -f 'source[branch]=main' -f 'source[path]=/'`.
