# pdf_builder.py
# Location: E:/pdfhub/pdf/
# Run:      python E:/pdfhub/pdf/pdf_builder.py
#
# Builds a compact white/grey GRID index.html with PDF thumbnails (page 1)
# rendered client-side using PDF.js (CDN) with lazy loading.
#
# PDFs are assumed to be in the SAME folder as this script (repo root).

from __future__ import annotations

import html
from pathlib import Path
from urllib.parse import quote
from datetime import datetime

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "index.html"

BRAND = "Mr Downes Maths"
TITLE = "PDF Gallery"

DOTS = ["#2563eb", "#ef4444", "#22c55e", "#111827"]  # blue, red, green, near-black

def human_size(n: int) -> str:
    v = float(n)
    for u in ["B", "KB", "MB", "GB", "TB"]:
        if v < 1024 or u == "TB":
            return f"{int(v)} {u}" if u == "B" else f"{v:.1f} {u}"
        v /= 1024
    return f"{n} B"

def gather_pdfs() -> list[Path]:
    return sorted(
        [p for p in ROOT.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"],
        key=lambda p: p.name.lower(),
    )

def build_html(rows: list[dict]) -> str:
    dot_html = "".join([f'<span class="dot" style="background:{c}"></span>' for c in DOTS])

    cards = []
    for r in rows:
        cards.append(f"""
        <article class="card"
          data-name="{html.escape(r['name_l'])}"
          data-size="{r['size']}"
          data-mtime="{r['mtime']}">
          <div class="thumb" title="Preview">
            <canvas class="cv" width="240" height="320" data-pdf="{r['href']}"></canvas>
            <div class="thumb-fallback" aria-hidden="true">PDF</div>
          </div>

          <div class="card-body">
            <a class="fname" href="{r['href']}" target="_blank" rel="noopener">{r['name']}</a>
            <div class="meta">{r['size_h']} · {r['date_h']}</div>

            <div class="actions">
              <a class="btn" href="{r['href']}" target="_blank" rel="noopener">View</a>
              <a class="btn ghost" href="{r['href']}" download>Download</a>
            </div>
          </div>
        </article>
        """.rstrip())

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{html.escape(BRAND)} — {html.escape(TITLE)}</title>

<style>
  :root {{
    --bg:#ffffff;
    --text:#111827;
    --muted:#6b7280;
    --line:#e5e7eb;
    --soft:#f3f4f6;
    --chip:#eef2ff;
    --btn:#111827;
    --btnText:#ffffff;
    --shadow: 0 8px 24px rgba(17,24,39,.08);
  }}

  *{{box-sizing:border-box}}
  body{{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;background:var(--bg);color:var(--text)}}
  .wrap{{max-width:1160px;margin:0 auto;padding:14px 12px 26px}}

  header{{
    display:flex;align-items:center;justify-content:space-between;gap:10px;
    border:1px solid var(--line);background:#fff;border-radius:12px;padding:10px 12px;
  }}
  .brand{{display:flex;align-items:center;gap:10px;min-width:230px}}
  .dots{{display:flex;gap:6px;align-items:center;padding:6px 8px;border:1px solid var(--line);border-radius:999px;background:var(--soft)}}
  .dot{{width:9px;height:9px;border-radius:999px}}
  .titles{{line-height:1.1}}
  .titles .h1{{font-weight:750;font-size:15px;margin:0}}
  .titles .h2{{font-size:12px;color:var(--muted);margin-top:3px}}

  .controls{{display:flex;flex-wrap:wrap;gap:8px;justify-content:flex-end;align-items:center;width:min(640px,100%)}}
  .search{{display:flex;align-items:center;border:1px solid var(--line);border-radius:10px;padding:8px 10px;background:#fff;min-width:min(360px,100%)}}
  .search input{{width:100%;border:0;outline:0;font-size:13px}}
  select{{
    border:1px solid var(--line);border-radius:10px;padding:8px 10px;
    background:#fff;font-size:13px;color:var(--text);
  }}
  .toggle{{
    border:1px solid var(--line);border-radius:10px;padding:8px 10px;background:#fff;
    font-size:13px;color:var(--text); cursor:pointer;
  }}

  .bar{{
    margin-top:10px;border:1px solid var(--line);border-radius:12px;overflow:hidden;background:#fff;
  }}
  .bar-top{{
    display:flex;justify-content:space-between;align-items:center;
    padding:8px 10px;background:var(--soft);border-bottom:1px solid var(--line);
    font-size:12px;color:var(--muted);
  }}

  .grid{{
    display:grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 10px;
    padding: 10px;
  }}

  .card{{
    border:1px solid var(--line);
    border-radius:12px;
    overflow:hidden;
    background:#fff;
    box-shadow: var(--shadow);
    display:flex;
    flex-direction:column;
    min-height: 350px;
  }}

  .thumb{{
    position:relative;
    background: linear-gradient(180deg, #fff, #f8fafc);
    border-bottom:1px solid var(--line);
    height: 240px;
    display:flex;
    align-items:center;
    justify-content:center;
  }}

  .cv{{
    width: 100%;
    height: 100%;
    object-fit: contain;
    display:block;
  }}

  .thumb-fallback{{
    position:absolute;
    inset: 10px;
    border:1px dashed var(--line);
    border-radius:10px;
    display:flex;
    align-items:center;
    justify-content:center;
    color: var(--muted);
    font-weight: 700;
    letter-spacing: .8px;
    background: rgba(255,255,255,.6);
  }}

  .card-body{{padding:10px 10px 12px; display:flex; flex-direction:column; gap:6px; flex:1;}}
  .fname{{font-weight:700;font-size:13px;color:var(--text);text-decoration:none; line-height:1.2;}}
  .fname:hover{{text-decoration:underline}}
  .meta{{font-size:12px;color:var(--muted)}}

  .actions{{margin-top:auto; display:flex; gap:8px; padding-top:6px;}}
  .btn{{
    display:inline-flex;align-items:center;justify-content:center;
    padding:7px 10px;border-radius:10px;border:1px solid var(--btn);
    background:var(--btn);color:var(--btnText);text-decoration:none;font-size:12px;
  }}
  .btn.ghost{{background:#fff;color:var(--btn)}}

  .hidden{{display:none !important}}

  @media (max-width: 520px){{
    .search{{min-width: 100%}}
    .controls{{justify-content:stretch}}
    select,.toggle{{flex:1}}
  }}
</style>
</head>

<body>
  <div class="wrap">
    <header>
      <div class="brand">
        <div class="dots" title="{html.escape(BRAND)}">{dot_html}</div>
        <div class="titles">
          <div class="h1">{html.escape(BRAND)}</div>
          <div class="h2">{html.escape(TITLE)}</div>
        </div>
      </div>

      <div class="controls">
        <div class="search"><input id="q" type="text" placeholder="Search PDFs…" autocomplete="off"></div>

        <select id="sort">
          <option value="mtime_desc" selected>Most recent</option>
          <option value="name_asc">A–Z</option>
          <option value="size_desc">Largest</option>
          <option value="size_asc">Smallest</option>
        </select>

        <button class="toggle" id="thumbToggle" type="button">Thumbnails: On</button>
      </div>
    </header>

    <div class="bar">
      <div class="bar-top">
        <div><span id="count">{len(rows)}</span> PDF(s)</div>
        <div>Folder: <code>{html.escape(ROOT.name)}</code></div>
      </div>

      <section class="grid" id="grid">
        {"".join(cards) if cards else '<div style="padding:10px;color:var(--muted)">No PDFs found.</div>'}
      </section>
    </div>
  </div>

  <!-- PDF.js (CDN) -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.10.38/pdf.min.js"></script>
  <script>
    const q = document.getElementById('q');
    const sortSel = document.getElementById('sort');
    const grid = document.getElementById('grid');
    const countEl = document.getElementById('count');
    const thumbToggle = document.getElementById('thumbToggle');

    let thumbsOn = true;

    function cards() {{
      return Array.from(grid.querySelectorAll('.card'));
    }}

    function applyFilter() {{
      const term = (q.value || '').trim().toLowerCase();
      let shown = 0;
      for (const c of cards()) {{
        const name = c.dataset.name || '';
        const ok = !term || name.includes(term);
        c.classList.toggle('hidden', !ok);
        if (ok) shown++;
      }}
      countEl.textContent = shown;
    }}

    function sortCards() {{
      const mode = sortSel.value;
      const list = cards();

      const cmpText = (a,b) => (a||'').localeCompare(b||'');
      const cmpNum  = (a,b) => (Number(a||0) - Number(b||0));

      list.sort((A,B) => {{
        if (mode === 'mtime_desc') return -cmpNum(A.dataset.mtime, B.dataset.mtime);
        if (mode === 'name_asc')   return  cmpText(A.dataset.name, B.dataset.name);
        if (mode === 'size_desc')  return -cmpNum(A.dataset.size, B.dataset.size);
        if (mode === 'size_asc')   return  cmpNum(A.dataset.size, B.dataset.size);
        return 0;
      }});

      for (const c of list) grid.appendChild(c);
      // after sorting, thumbnails will be handled by observer anyway
    }}

    q.addEventListener('input', applyFilter);
    sortSel.addEventListener('change', () => {{
      sortCards();
      applyFilter();
    }});

    thumbToggle.addEventListener('click', () => {{
      thumbsOn = !thumbsOn;
      thumbToggle.textContent = 'Thumbnails: ' + (thumbsOn ? 'On' : 'Off');
      document.documentElement.style.setProperty('--shadow', thumbsOn ? '0 8px 24px rgba(17,24,39,.08)' : 'none');

      // If turned off: stop rendering and hide canvases
      for (const cv of document.querySelectorAll('canvas.cv')) {{
        cv.style.display = thumbsOn ? 'block' : 'none';
        cv.nextElementSibling.style.display = thumbsOn ? 'none' : 'flex';
      }}
    }});

    // --- PDF.js thumbnail rendering (lazy) ---
    // Worker setup:
    pdfjsLib.GlobalWorkerOptions.workerSrc =
      "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.10.38/pdf.worker.min.js";

    const rendered = new Set();

    async function renderThumb(canvas) {{
      if (!thumbsOn) return;
      const url = canvas.dataset.pdf;
      if (!url || rendered.has(url)) return;
      rendered.add(url);

      const fallback = canvas.nextElementSibling; // .thumb-fallback

      try {{
        const loadingTask = pdfjsLib.getDocument(url);
        const pdf = await loadingTask.promise;
        const page = await pdf.getPage(1);

        // Fit to card thumb area
        const desiredWidth = canvas.getBoundingClientRect().width || 240;
        const viewport1 = page.getViewport({{ scale: 1 }});
        const scale = desiredWidth / viewport1.width;
        const viewport = page.getViewport({{ scale }});

        canvas.width = Math.floor(viewport.width);
        canvas.height = Math.floor(viewport.height);

        const ctx = canvas.getContext('2d', {{ alpha: false }});
        await page.render({{ canvasContext: ctx, viewport }}).promise;

        // Hide fallback once rendered
        if (fallback) fallback.style.display = 'none';
      }} catch (e) {{
        // keep fallback visible if render fails
        if (fallback) fallback.style.display = 'flex';
      }}
    }}

    const io = new IntersectionObserver((entries) => {{
      for (const e of entries) {{
        if (e.isIntersecting) {{
          const cv = e.target;
          renderThumb(cv);
          io.unobserve(cv);
        }}
      }}
    }}, {{ rootMargin: "300px 0px" }});

    function observeThumbs() {{
      for (const cv of document.querySelectorAll('canvas.cv')) {{
        // initial state based on toggle
        cv.style.display = thumbsOn ? 'block' : 'none';
        const fb = cv.nextElementSibling;
        if (fb) fb.style.display = thumbsOn ? 'none' : 'flex';

        if (thumbsOn) io.observe(cv);
      }}
    }}

    // Initial:
    sortCards();
    applyFilter();
    observeThumbs();
  </script>
</body>
</html>
"""

def main() -> None:
    rows = []
    for p in gather_pdfs():
        st = p.stat()
        rows.append({
            "name": html.escape(p.name),
            "name_l": p.name.lower(),
            "href": quote(p.name),
            "size": st.st_size,
            "size_h": html.escape(human_size(st.st_size)),
            "mtime": int(st.st_mtime),
            "date_h": html.escape(datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d")),
        })

    OUT.write_text(build_html(rows), encoding="utf-8")
    print(f"Wrote: {OUT}")
    print(f"PDFs found: {len(rows)}")

if __name__ == "__main__":
    main()
