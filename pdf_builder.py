# pdf_builder.py
# Run from inside E:\PDF\PDFgallery\
# Generates ./index.html listing PDFs in the SAME folder.

from __future__ import annotations

import html
from pathlib import Path
from urllib.parse import quote
from datetime import datetime

BRAND_TITLE = "Mr Downes Maths"
BRAND_TAGLINE = "PDF Gallery"

DOTS = [
    ("dot1", "#2563eb"),  # blue
    ("dot2", "#ef4444"),  # red
    ("dot3", "#22c55e"),  # green
    ("dot4", "#111827"),  # near-black
]

OUTPUT_FILE = "index.html"

def human_size(n: int) -> str:
    # nice readable sizes
    units = ["B", "KB", "MB", "GB", "TB"]
    v = float(n)
    for u in units:
        if v < 1024 or u == "TB":
            if u == "B":
                return f"{int(v)} {u}"
            return f"{v:.1f} {u}"
        v /= 1024
    return f"{int(n)} B"

def fmt_dt(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")

def list_pdfs(root: Path) -> list[dict]:
    pdfs = sorted(
        [p for p in root.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"],
        key=lambda p: p.name.lower(),
    )
    rows = []
    for p in pdfs:
        href = quote(p.name)  # URL-encode spaces etc.
        st = p.stat()
        rows.append({
            "name": p.name,
            "name_safe": html.escape(p.name),
            "href": href,
            "size_h": html.escape(human_size(st.st_size)),
            "mtime_h": html.escape(fmt_dt(st.st_mtime)),
        })
    return rows

def render(rows: list[dict]) -> str:
    dots_html = "\n".join([f'<span class="dot {cls}" aria-hidden="true"></span>' for cls, _ in DOTS])
    dots_css = "\n".join([f".{cls}{{background:{col};}}" for cls, col in DOTS])

    trs = []
    for r in rows:
        trs.append(f"""
          <tr class="row" data-name="{html.escape(r['name'].lower())}">
            <td class="name">
              <span class="file">{r['name_safe']}</span>
              <div class="meta">
                <span class="pill">{r['size_h']}</span>
                <span class="pill">{r['mtime_h']}</span>
              </div>
            </td>
            <td class="actions">
              <a class="btn" href="{r['href']}" target="_blank" rel="noopener">View</a>
              <button class="btn" data-preview="{r['href']}">Preview</button>
              <a class="btn btn-ghost" href="{r['href']}" download>Download</a>
            </td>
          </tr>
        """.rstrip())

    total = len(rows)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(BRAND_TITLE)} — {html.escape(BRAND_TAGLINE)}</title>
  <style>
    :root{{
      --bg:#0b1220;
      --panel:#0f172a;
      --text:#e5e7eb;
      --muted:#9ca3af;
      --line:rgba(255,255,255,.08);
      --shadow: 0 10px 30px rgba(0,0,0,.35);
      --radius: 18px;
      --btn: rgba(255,255,255,.10);
      --btn2: rgba(255,255,255,.06);
      --focus: rgba(37,99,235,.35);
    }}

    *{{box-sizing:border-box}}
    body{{
      margin:0;
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
      color:var(--text);
      background: radial-gradient(1200px 800px at 20% 0%, #101b35, var(--bg));
    }}

    .wrap{{max-width: 980px; margin: 0 auto; padding: 22px 16px 40px;}}

    header{{
      display:flex; align-items:center; justify-content:space-between; gap:14px;
      padding: 18px 18px;
      background: linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.02));
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }}

    .brand{{display:flex; align-items:center; gap:12px; min-width: 220px;}}

    .dots{{
      display:flex; gap:7px; align-items:center;
      padding: 6px 8px;
      border-radius: 999px;
      background: rgba(255,255,255,.04);
      border: 1px solid var(--line);
    }}

    .dot{{width:10px; height:10px; border-radius:999px; box-shadow:0 2px 8px rgba(0,0,0,.35); transition: transform .15s ease;}}
    .dots:hover .dot:nth-child(1){{transform: translateY(-3px)}}
    .dots:hover .dot:nth-child(2){{transform: translateY(2px)}}
    .dots:hover .dot:nth-child(3){{transform: translateY(-2px)}}
    .dots:hover .dot:nth-child(4){{transform: translateY(1px)}}

    {dots_css}

    .title{{display:flex; flex-direction:column; line-height: 1.05;}}
    .title h1{{margin:0; font-size: 20px; letter-spacing: .2px;}}
    .title .sub{{margin-top: 6px; font-size: 13px; color: var(--muted);}}

    .controls{{display:flex; flex-direction:column; gap:8px; align-items:flex-end; width: min(420px, 100%);}}
    .search{{
      width: 100%;
      display:flex; gap:10px; align-items:center;
      padding: 10px 12px;
      border-radius: 14px;
      border: 1px solid var(--line);
      background: rgba(0,0,0,.18);
    }}
    .search input{{width:100%; border:0; outline:0; background: transparent; color: var(--text); font-size: 14px;}}
    .hint{{font-size: 12px; color: var(--muted);}}

    .panel{{
      margin-top: 16px;
      border-radius: var(--radius);
      border: 1px solid var(--line);
      background: rgba(255,255,255,.02);
      box-shadow: var(--shadow);
      overflow:hidden;
    }}

    .summary{{
      display:flex; justify-content:space-between; align-items:center;
      padding: 12px 16px;
      border-bottom: 1px solid var(--line);
      background: rgba(0,0,0,.12);
      color: var(--muted);
      font-size: 13px;
    }}

    table{{width:100%; border-collapse: collapse;}}
    tr.row{{border-bottom:1px solid var(--line)}}
    tr.row:last-child{{border-bottom:0}}
    td{{padding: 14px 16px; vertical-align: top;}}

    td.name .file{{display:block; font-weight: 600; font-size: 15px; word-break: break-word;}}
    .meta{{margin-top: 8px; display:flex; flex-wrap: wrap; gap: 8px;}}
    .pill{{font-size: 12px; color: var(--muted); border: 1px solid var(--line); background: rgba(255,255,255,.03); padding: 4px 8px; border-radius: 999px;}}

    td.actions{{width: 240px; padding-top: 12px;}}
    .btn{{
      display:inline-flex; align-items:center; justify-content:center;
      padding: 9px 11px;
      border-radius: 12px;
      border: 1px solid var(--line);
      background: var(--btn);
      color: var(--text);
      text-decoration:none;
      font-size: 13px;
      margin-right: 8px;
      margin-bottom: 8px;
      cursor:pointer;
      user-select:none;
      transition: transform .08s ease, background .15s ease;
    }}
    .btn:hover{{background: rgba(255,255,255,.14)}}
    .btn:active{{transform: translateY(1px)}}
    .btn:focus{{outline: 0; box-shadow: 0 0 0 4px var(--focus)}}
    .btn-ghost{{background: var(--btn2);}}

    @media (max-width: 720px){{
      header{{flex-direction: column; align-items:stretch}}
      .controls{{align-items:stretch; width:100%}}
      td.actions{{width:auto}}
    }}

    /* Modal */
    .modal{{position: fixed; inset: 0; background: rgba(0,0,0,.65); display:none; align-items:center; justify-content:center; padding: 18px;}}
    .modal.open{{display:flex}}
    .modal-card{{width: min(1100px, 100%); height: min(82vh, 820px); background: rgba(10, 14, 25, .98); border: 1px solid var(--line); border-radius: var(--radius); box-shadow: var(--shadow); overflow:hidden; display:flex; flex-direction:column;}}
    .modal-top{{display:flex; justify-content:space-between; align-items:center; padding: 12px 14px; border-bottom: 1px solid var(--line); background: rgba(255,255,255,.03);}}
    .modal-title{{font-size: 13px; color: var(--muted); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; padding-right: 10px;}}
    .modal-close{{padding: 8px 10px; border-radius: 12px; border: 1px solid var(--line); background: var(--btn2); color: var(--text); cursor:pointer; font-size: 13px;}}
    .modal-body{{flex:1}}
    .modal-body iframe{{width:100%; height:100%; border:0; background: #0b1220;}}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <div class="brand">
        <div class="dots" title="Mr Downes Maths">
          {dots_html}
        </div>
        <div class="title">
          <h1>{html.escape(BRAND_TITLE)}</h1>
          <div class="sub">{html.escape(BRAND_TAGLINE)}</div>
        </div>
      </div>

      <div class="controls">
        <div class="search">
          <input id="q" type="text" placeholder="Search PDFs (type to filter)..." autocomplete="off" />
        </div>
        <div class="hint">View opens in-browser. Download saves a copy. Preview shows page 1 quickly.</div>
      </div>
    </header>

    <div class="panel">
      <div class="summary">
        <div><span id="count">{total}</span> PDF(s)</div>
        <div>Folder: <code>PDFgallery</code></div>
      </div>

      <table>
        <tbody id="tbody">
          {"".join(trs) if trs else '<tr><td style="padding:16px;color:var(--muted)">No PDFs found in this folder.</td></tr>'}
        </tbody>
      </table>
    </div>
  </div>

  <div class="modal" id="modal" role="dialog" aria-modal="true" aria-label="PDF Preview">
    <div class="modal-card">
      <div class="modal-top">
        <div class="modal-title" id="modalTitle">Preview</div>
        <button class="modal-close" id="modalClose">Close</button>
      </div>
      <div class="modal-body">
        <iframe id="frame" title="PDF preview"></iframe>
      </div>
    </div>
  </div>

  <script>
    const q = document.getElementById('q');
    const rows = Array.from(document.querySelectorAll('tr.row'));
    const countEl = document.getElementById('count');

    function applyFilter() {{
      const term = (q.value || '').trim().toLowerCase();
      let shown = 0;
      for (const r of rows) {{
        const name = r.dataset.name || '';
        const ok = !term || name.includes(term);
        r.style.display = ok ? '' : 'none';
        if (ok) shown++;
      }}
      countEl.textContent = shown;
    }}
    q.addEventListener('input', applyFilter);

    const modal = document.getElementById('modal');
    const frame = document.getElementById('frame');
    const modalTitle = document.getElementById('modalTitle');
    const modalClose = document.getElementById('modalClose');

    function openModal(href) {{
      frame.src = href + "#page=1&view=FitH";
      modalTitle.textContent = "Preview: " + decodeURIComponent(href.split('/').pop());
      modal.classList.add('open');
    }}
    function closeModal() {{
      modal.classList.remove('open');
      frame.src = "";
    }}

    document.addEventListener('click', (e) => {{
      const btn = e.target.closest('button[data-preview]');
      if (btn) openModal(btn.dataset.preview);
    }});
    modalClose.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {{ if (e.target === modal) closeModal(); }});
    document.addEventListener('keydown', (e) => {{ if (e.key === 'Escape') closeModal(); }});
  </script>
</body>
</html>
"""

def main() -> None:
    root = Path(__file__).resolve().parent
    rows = list_pdfs(root)
    out = root / OUTPUT_FILE
    out.write_text(render(rows), encoding="utf-8")
    print(f"Wrote: {out}")
    print(f"PDFs found: {len(rows)}")

if __name__ == "__main__":
    main()
