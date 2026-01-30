# pdf_builder.py
# Location: E:/pdfhub/pdf/
# Run: python pdf_builder.py
#
# Builds a compact white/grey index.html for PDFs in THIS folder.
# Sorting: default = most recent (modified time desc). Click headers to sort.

from __future__ import annotations

import html
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "index.html"

BRAND = "Mr Downes Maths"
TITLE = "PDF"
SUBTITLE = "Gallery"

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

    tr = []
    for r in rows:
        # data-* values used for sorting (numeric for size/mtime)
        tr.append(
            f"""
            <tr class="row"
                data-name="{html.escape(r['name_l'])}"
                data-size="{r['size']}"
                data-mtime="{r['mtime']}">
              <td class="name">
                <a class="file" href="{r['href']}" target="_blank" rel="noopener">{r['name']}</a>
                <span class="meta">{r['size_h']} · {r['date_h']}</span>
              </td>
              <td class="num">{r['size_h']}</td>
              <td class="num">{r['date_h']}</td>
              <td class="actions">
                <a class="btn" href="{r['href']}" target="_blank" rel="noopener">View</a>
                <a class="btn ghost" href="{r['href']}" download>Download</a>
              </td>
            </tr>
            """.rstrip()
        )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{html.escape(BRAND)} — {html.escape(TITLE)} {html.escape(SUBTITLE)}</title>
<style>
  :root {{
    --bg:#ffffff;
    --text:#111827;
    --muted:#6b7280;
    --line:#e5e7eb;
    --soft:#f3f4f6;
    --btn:#111827;
    --btnText:#ffffff;
  }}
  *{{box-sizing:border-box}}
  body{{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;background:var(--bg);color:var(--text)}}
  .wrap{{max-width:1050px;margin:0 auto;padding:16px 14px 28px}}
  header{{display:flex;align-items:center;justify-content:space-between;gap:12px;border:1px solid var(--line);background:#fff;border-radius:12px;padding:10px 12px}}
  .brand{{display:flex;align-items:center;gap:10px;min-width:220px}}
  .dots{{display:flex;gap:6px;align-items:center;padding:6px 8px;border:1px solid var(--line);border-radius:999px;background:var(--soft)}}
  .dot{{width:9px;height:9px;border-radius:999px}}
  .titles{{line-height:1.1}}
  .titles .h1{{font-weight:700;font-size:15px;margin:0}}
  .titles .h2{{font-size:12px;color:var(--muted);margin-top:3px}}
  .controls{{display:flex;flex-direction:column;gap:6px;align-items:flex-end;width:min(520px,100%)}}
  .search{{width:100%;display:flex;align-items:center;border:1px solid var(--line);border-radius:10px;padding:8px 10px;background:#fff}}
  .search input{{width:100%;border:0;outline:0;font-size:13px}}
  .hint{{font-size:12px;color:var(--muted)}}
  .panel{{margin-top:10px;border:1px solid var(--line);border-radius:12px;overflow:hidden}}
  .topbar{{display:flex;justify-content:space-between;align-items:center;padding:8px 10px;background:var(--soft);border-bottom:1px solid var(--line);font-size:12px;color:var(--muted)}}
  table{{width:100%;border-collapse:collapse}}
  th,td{{padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}}
  th{{font-size:12px;color:#374151;background:#fff;text-align:left;user-select:none;cursor:pointer;white-space:nowrap}}
  tr:last-child td{{border-bottom:0}}
  .name .file{{display:inline-block;font-weight:650;font-size:13px;color:var(--text);text-decoration:none}}
  .name .file:hover{{text-decoration:underline}}
  .meta{{display:block;margin-top:3px;font-size:12px;color:var(--muted)}}
  .num{{font-size:12px;color:#374151;white-space:nowrap}}
  .actions{{white-space:nowrap}}
  .btn{{display:inline-flex;align-items:center;justify-content:center;padding:6px 10px;border-radius:10px;border:1px solid var(--btn);background:var(--btn);color:var(--btnText);text-decoration:none;font-size:12px;margin-right:6px}}
  .btn.ghost{{background:#fff;color:var(--btn)}}
  .sortTag{{font-size:11px;color:var(--muted);margin-left:6px}}
  @media (max-width:820px){{
    th:nth-child(2), td:nth-child(2), th:nth-child(3), td:nth-child(3){{display:none}}
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
          <div class="h2">{html.escape(TITLE)} · {html.escape(SUBTITLE)}</div>
        </div>
      </div>
      <div class="controls">
        <div class="search"><input id="q" type="text" placeholder="Search…" autocomplete="off"></div>
        <div class="hint">Click headers to sort: Most recent · A–Z · Size</div>
      </div>
    </header>

    <div class="panel">
      <div class="topbar">
        <div><span id="count">{len(rows)}</span> PDF(s)</div>
        <div>Folder: <code>{html.escape(ROOT.name)}</code></div>
      </div>

      <table>
        <thead>
          <tr>
            <th data-key="name" data-type="text">Name <span class="sortTag" id="tagName"></span></th>
            <th data-key="size" data-type="num">Size <span class="sortTag" id="tagSize"></span></th>
            <th data-key="mtime" data-type="num">Modified <span class="sortTag" id="tagTime"></span></th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody id="tbody">
          {"" if tr else '<tr><td colspan="4" style="color:var(--muted);font-size:13px">No PDFs found.</td></tr>'}
          {"".join(tr)}
        </tbody>
      </table>
    </div>
  </div>

<script>
  const q = document.getElementById("q");
  const tbody = document.getElementById("tbody");
  const countEl = document.getElementById("count");
  const tags = {{
    name: document.getElementById("tagName"),
    size: document.getElementById("tagSize"),
    mtime: document.getElementById("tagTime"),
  }};

  let sortKey = "mtime";
  let sortDir = "desc"; // default: most recent

  function clearTags() {{
    for (const k of Object.keys(tags)) tags[k].textContent = "";
  }}
  function setTag() {{
    clearTags();
    const arrow = sortDir === "asc" ? "↑" : "↓";
    if (tags[sortKey]) tags[sortKey].textContent = arrow;
  }}

  function rowsArray() {{
    return Array.from(tbody.querySelectorAll("tr.row"));
  }}

  function sortRows() {{
    const rows = rowsArray();
    rows.sort((a,b) => {{
      const ta = a.dataset[sortKey];
      const tb = b.dataset[sortKey];

      if (sortKey === "name") {{
        const cmp = (ta || "").localeCompare(tb || "");
        return sortDir === "asc" ? cmp : -cmp;
      }} else {{
        const na = Number(ta || 0), nb = Number(tb || 0);
        return sortDir === "asc" ? (na - nb) : (nb - na);
      }}
    }});
    for (const r of rows) tbody.appendChild(r);
    setTag();
  }}

  function applyFilter() {{
    const term = (q.value || "").trim().toLowerCase();
    let shown = 0;
    for (const r of rowsArray()) {{
      const name = (r.dataset.name || "");
      const ok = !term || name.includes(term);
      r.style.display = ok ? "" : "none";
      if (ok) shown++;
    }}
    countEl.textContent = shown;
  }}

  document.querySelectorAll("th[data-key]").forEach(th => {{
    th.addEventListener("click", () => {{
      const key = th.dataset.key;
      if (sortKey === key) {{
        sortDir = (sortDir === "asc") ? "desc" : "asc";
      }} else {{
        sortKey = key;
        sortDir = (key === "mtime") ? "desc" : "asc"; // sensible defaults
      }}
      sortRows();
    }});
  }});

  q.addEventListener("input", applyFilter);

  // initial state
  setTag();
  sortRows();
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
            "date_h": html.escape(Path(p).stat().st_mtime_ns and __import__("datetime").datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d")),
        })

    OUT.write_text(build_html(rows), encoding="utf-8")
    print(f"Wrote: {OUT}")
    print(f"PDFs found: {len(rows)}")

if __name__ == "__main__":
    main()
