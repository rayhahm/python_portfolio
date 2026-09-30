# ServiceTitan Helper — Century Mechanical

A small Streamlit chatbot so the team can ask ServiceTitan how-to questions
from their phone. Answers come from Claude (`claude-haiku-4-5`), grounded
only in the articles under `knowledge/` — it won't make up menu paths that
aren't in there.

## How it works

- `knowledge/*.md` — the reference articles the bot is allowed to answer from.
- `rag.py` — loads those articles and hands them all to Claude as context on
  every question. (A keyword-search retrieval step was tried first, but it
  silently found nothing for Korean questions against the English articles
  — no literal term overlap — so it was dropped in favor of just sending
  everything, which the current knowledge base size easily allows.)
- `app.py` — the Streamlit chat UI; sends the knowledge base + conversation
  history + question to Claude and streams back the answer.

## 1. Run it locally

```bash
cd servicetitan_chatbot
python -m venv .venv && source .venv/bin/activate   # optional but recommended
pip install -r requirements.txt

cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# then edit .streamlit/secrets.toml and paste your real Anthropic API key
# (get one at https://console.anthropic.com)

streamlit run app.py
```

Open the local URL it prints — on your phone, only works if the phone is on
the same network and you use your computer's LAN IP instead of `localhost`.
For real phone access by the whole team, deploy it (step 2).

## 2. Deploy so teammates can open it on their phone

Easiest free option — **Streamlit Community Cloud**:

1. Push this repo to GitHub (already done if you're reading this from there).
2. Go to https://share.streamlit.io, sign in, click **New app**.
3. Point it at this repo, branch, and set the main file path to
   `servicetitan_chatbot/app.py`.
4. In the app's **Settings → Secrets**, paste:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
5. Deploy. You get a public URL like `https://your-app.streamlit.app` —
   send that link to the team; it works fine in a mobile browser.

If you'd rather keep it private/internal, deploy the same app to any host
that runs Python (a small VM, Render, Railway, etc.) instead — `app.py` and
`requirements.txt` don't change.

## 3. Add real ServiceTitan content (important)

The articles currently in `knowledge/` are a **starter template** written
from general knowledge of how ServiceTitan works, not pulled from
ServiceTitan's actual Help Center — this sandbox's network policy blocks
`help.servicetitan.com`, so it couldn't be scraped from here. Treat every
file's exact button names/menu paths as "probably close, verify before
trusting."

To replace them with the real thing, pick one:

**A. Scrape the public Help Center (run on your own machine, not this
sandbox):**

```bash
cd servicetitan_chatbot
pip install -r scripts/requirements.txt
python scripts/scrape_servicetitan_help.py \
  https://help.servicetitan.com/docs/getting-started-with-servicetitan \
  https://help.servicetitan.com/docs/... \
  -o knowledge
```

Grab article URLs by browsing help.servicetitan.com and copying links for
the topics your team actually asks about most. Some articles require being
logged into your ServiceTitan account — for those, save the page as HTML
from your browser and pass the local file path instead of a URL.

**B. Use your own internal SOPs instead (often more useful — these can
describe *your* company's exact workflow, not just ServiceTitan's generic
one):** just drop `.md` files into `knowledge/`, one `# Title` at the top
and `## Section` headings for each sub-topic, same format as the existing
files.

Either way, after adding files, redeploy (Streamlit Cloud redeploys
automatically on git push) — no code changes needed.

## Notes

- ServiceTitan also has its own built-in AI assistant, **Atlas**, inside the
  platform itself — worth telling the team about that too, since it has
  access to your live account data (job status, customer records, etc.)
  that this bot deliberately does not.
- This bot only answers from `knowledge/`; it does not call the ServiceTitan
  API and cannot look up live jobs/customers. If the team later wants that
  (e.g. "how many jobs are scheduled today"), that's a separate integration
  requiring ServiceTitan API credentials — ask if you want that added.
- Cost: Claude Haiku 4.5 is inexpensive per message; for a small internal
  team's usage this should be a few dollars a month at most. Check current
  pricing at https://www.anthropic.com/pricing if you want to estimate.
