"""
Targul Cartii - Cart Manager v2
================================
1. Parseaza cosul salvat HTML → extrage URL-urile cartilor
2. Viziteaza fiecare pagina de carte (server-side) → extrage product_id
3. Genereaza hosting/index.html + hosting/script.js cu product_id-urile gata extrase
4. Andreea: targulcartii.ro → F12 → Console → paste → Enter → gata

Utilizare:
    python cart_manager.py [cart_html_file]
"""

import re
import json
import sys
import os
import time
import requests


# ─── Parsare cos salvat ──────────────────────────────────────────────

def parse_cart_html(file_path):
    """Extrage cartile din HTML-ul cosului salvat."""
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    books = []
    row_pattern = r'<div\s+class="cart_row"\s+id="row(\d+)">'
    row_matches = list(re.finditer(row_pattern, html))

    for i, row_match in enumerate(row_matches):
        row_id = row_match.group(1)
        start = row_match.start()
        end = row_matches[i + 1].start() if i + 1 < len(row_matches) else start + 5000
        section = html[start:end]

        book = {"row_id": row_id}

        m = re.search(r'<a\s+href="([^"]+)"\s+class="cart_name_row">([^<]+)</a>', section)
        if m:
            book["url"] = m.group(1)
            book["name"] = m.group(2).strip()

        m = re.search(r'<div\s+class="cart_isbn">ISBN:\s*([^<]+)</div>', section)
        if m:
            book["isbn"] = m.group(1).strip()

        m = re.search(r'<div\s+class="cart_condition_val">\s*Stare:\s*(\w+)', section)
        if m:
            book["condition"] = m.group(1).strip()

        m = re.search(r'<div\s+class="cart_total_col"[^>]*>([^<]+)</div>', section)
        if m:
            book["price"] = m.group(1).strip()

        if "name" in book and "url" in book:
            books.append(book)

    return books


# ─── Extragere product_id-uri (server-side) ──────────────────────────

def extract_product_ids(books, delay=1.0):
    """Viziteaza fiecare pagina de carte si extrage product_id din addToCart2()."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })

    results = []
    failed = []

    for i, book in enumerate(books):
        url = book["url"]
        name = book["name"]
        print(f"  [{i+1}/{len(books)}] {name}...", end=" ", flush=True)

        try:
            resp = session.get(url, timeout=15)
            # Cautam: addToCart2('product_id','condition','condition_key')
            m = re.search(r"addToCart2\('(\d+)','(\d+)','([^']+)'\)", resp.text)
            if m:
                pid = m.group(1)
                book["product_id"] = pid
                results.append(book)
                print(f"OK (pid={pid})")
            else:
                print("SKIP - nu s-a gasit addToCart2")
                failed.append(book)
        except Exception as e:
            print(f"EROARE - {e}")
            failed.append(book)

        if i < len(books) - 1:
            time.sleep(delay)

    return results, failed


# ─── Generare script.js (ultra-rapid, product_id gata extrase) ───────

def generate_script_js(books):
    """Script JS cu product_id-urile gata extrase. Doar POST-uri directe."""

    products = json.dumps(
        [{"pid": b["product_id"], "name": b["name"]} for b in books],
        ensure_ascii=False
    )

    return f"""(async function(){{
  var P={products};
  var D=500,ok=0,fail=0,errs=[];
  if(!window.location.hostname.includes('targulcartii.ro')){{
    alert('Acest script trebuie rulat pe targulcartii.ro!\\nDeschide targulcartii.ro, apoi F12 > Console > paste.');
    return;
  }}
  var sd=document.createElement('div');
  sd.style.cssText='position:fixed;bottom:0;left:0;right:0;z-index:99999;background:#1a1a2e;color:#e0e0e0;padding:12px 20px;font-family:monospace;font-size:14px;box-shadow:0 -2px 10px rgba(0,0,0,0.5)';
  sd.innerHTML='<div id="tcp">Pornire... 0/'+P.length+'</div><div style="background:#333;height:6px;margin-top:8px;border-radius:3px"><div id="tcf" style="background:#e94560;height:100%;width:0%;border-radius:3px;transition:width 0.3s"></div></div><div id="tcc" style="margin-top:5px;font-size:11px;color:#888"></div>';
  document.body.appendChild(sd);
  function up(m,c){{document.getElementById('tcp').textContent=m;document.getElementById('tcf').style.width=((ok+fail)/P.length*100).toFixed(1)+'%';if(c)document.getElementById('tcc').textContent=c}}
  function sl(ms){{return new Promise(function(r){{setTimeout(r,ms)}})}}
  for(var i=0;i<P.length;i++){{
    var p=P[i];
    up('Adaugare: '+(i+1)+'/'+P.length+' (OK:'+ok+' Erori:'+fail+')',p.name);
    try{{
      var r=await fetch('/index.php?route=checkout/cart/update',{{
        method:'POST',headers:{{'Content-Type':'application/x-www-form-urlencoded'}},
        body:'product_id='+p.pid+'&quantity=1'
      }});
      var j=await r.json();
      if(j&&!j.error){{ok++}}else{{fail++;errs.push(p.name)}}
    }}catch(e){{fail++;errs.push(p.name)}}
    await sl(D);
  }}
  document.getElementById('tcf').style.background=fail>0?'#e67e22':'#2ecc71';
  document.getElementById('tcf').style.width='100%';
  if(errs.length)console.log('Erori:',errs);
  up('GATA! '+ok+'/'+P.length+' adaugate. Redirectionare la cos in 3s...',' ');
  await sl(3000);
  window.location.href='/index.php?route=checkout/cart';
}})();
"""


# ─── Generare index.html ─────────────────────────────────────────────

def generate_index_html(books, js_script):
    """Pagina HTML cu lista de carti + scriptul de copiat."""

    total_price = 0
    for b in books:
        try:
            total_price += float(b.get("price", "0").replace("LEI", "").replace(",", ".").strip())
        except ValueError:
            pass

    book_rows = "\n".join(
        f'<tr><td>{i}</td>'
        f'<td><a href="{b["url"]}" target="_blank">{b["name"]}</a></td>'
        f'<td>{b.get("isbn","")}</td>'
        f'<td>{b.get("condition","")}</td>'
        f'<td>{b.get("price","")}</td></tr>'
        for i, b in enumerate(books, 1)
    )

    # Escape for safe HTML embedding
    js_for_html = js_script.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    est_minutes = max(1, len(books) * 1 // 60 + 1)

    return f"""<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cos Targul Cartii - {len(books)} carti</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',Tahoma,sans-serif;background:#f5f5f5;color:#333;padding:20px}}
.c{{max-width:1000px;margin:0 auto}}
h1{{text-align:center;color:#1a1a2e;margin-bottom:5px;font-size:24px}}
.sub{{text-align:center;color:#666;margin-bottom:20px}}
.sum{{display:flex;gap:15px;justify-content:center;margin-bottom:25px;flex-wrap:wrap}}
.cd{{background:#fff;padding:15px 25px;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,.1);text-align:center}}
.cd .n{{font-size:28px;font-weight:bold;color:#e94560}}
.cd .l{{font-size:12px;color:#888}}
.box{{background:#fff;border-radius:12px;padding:25px;margin-bottom:25px;box-shadow:0 2px 8px rgba(0,0,0,.08)}}
.box h2{{margin-bottom:15px;font-size:20px;color:#1a1a2e}}
.steps{{counter-reset:step}}
.steps li{{list-style:none;position:relative;padding:12px 0 12px 50px;border-left:3px solid #e0e0e0;margin-left:15px;font-size:15px;line-height:1.6}}
.steps li:last-child{{border-left-color:transparent}}
.steps li::before{{counter-increment:step;content:counter(step);position:absolute;left:-17px;top:10px;width:32px;height:32px;border-radius:50%;background:#e94560;color:#fff;font-weight:bold;font-size:14px;display:flex;align-items:center;justify-content:center}}
.steps li.active{{border-left-color:#e94560}}
.steps code{{background:#f0f0f0;padding:3px 8px;border-radius:4px;font-size:13px;font-family:monospace}}
.steps a{{color:#e94560;font-weight:bold}}
.bigbtn{{display:block;width:100%;padding:18px;border:none;border-radius:10px;font-size:18px;font-weight:bold;cursor:pointer;margin-top:15px;transition:all .2s}}
.bigbtn-red{{background:#e94560;color:#fff}}
.bigbtn-red:hover{{background:#d63851;transform:scale(1.01)}}
.bigbtn-green{{background:#27ae60;color:#fff}}
.script-area{{width:100%;height:100px;background:#1a1a2e;color:#7fdbca;border:2px solid #333;border-radius:8px;padding:12px;font-family:monospace;font-size:11px;resize:vertical;margin-top:10px}}
.copied-msg{{display:none;text-align:center;padding:10px;background:#27ae60;color:#fff;border-radius:8px;margin-top:10px;font-weight:bold;font-size:16px}}
table{{width:100%;background:#fff;border-collapse:collapse;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.1);margin-top:10px}}
th{{background:#1a1a2e;color:#fff;padding:12px 15px;text-align:left;font-size:13px}}
td{{padding:10px 15px;border-bottom:1px solid #eee;font-size:13px}}
tr:hover{{background:#f8f9fa}}
td a{{color:#e94560;text-decoration:none}}
td a:hover{{text-decoration:underline}}
.ft{{text-align:center;margin-top:20px;color:#999;font-size:12px}}
.warn{{background:#fff3cd;border:1px solid #ffc107;border-radius:8px;padding:12px 15px;margin-top:15px;font-size:13px;color:#856404}}
</style>
</head>
<body>
<div class="c">
  <h1>Cos de cumparaturi - Targul Cartii</h1>
  <p class="sub">{len(books)} carti pregatite pentru comanda</p>

  <div class="sum">
    <div class="cd"><div class="n">{len(books)}</div><div class="l">Carti</div></div>
    <div class="cd"><div class="n">{total_price:.2f} LEI</div><div class="l">Total estimat</div></div>
    <div class="cd"><div class="n">~{est_minutes} min</div><div class="l">Timp adaugare</div></div>
  </div>

  <div class="box">
    <h2>Cum comanzi (3 pasi simpli)</h2>
    <ol class="steps">
      <li class="active">
        Deschide <a href="https://www.targulcartii.ro/" target="_blank">targulcartii.ro</a> si <strong>logheaza-te in cont</strong>
      </li>
      <li>
        Trage butonul <strong style="color:#e94560">Adauga cartile in cos</strong> in bara de bookmarks.
      </li>
      <li>
        Pe <strong>targulcartii.ro</strong> apasa bookmark-ul, asteapta bara de progres (~{est_minutes} min). Cand termina, te duce <strong>automat la cos</strong> &rarr; <strong>Plateste</strong>
      </li>
    </ol>

    <textarea class="script-area" id="scriptArea" readonly style="display:none">{js_for_html}</textarea>

    <div id="bmBox" style="margin-top:10px;font-size:13px;color:#555">
      <p style="margin-bottom:6px;"><strong>Buton pentru bookmarks:</strong> trage-l in bara de bookmarks, apoi apasa-l cand esti pe <strong>targulcartii.ro</strong>.</p>
      <a id="bmLink" href="#"
         style="display:inline-block;margin-top:8px;padding:10px 16px;border-radius:8px;background:#1a1a2e;color:#fff;font-weight:bold;text-decoration:none;">
         Adauga cartile in cos
      </a>
    </div>

    <div class="warn">
      Scriptul adauga cartile direct in cos fara sa incarce pagini. E rapid (~{est_minutes} min pentru {len(books)} carti).
      Dupa ce vezi <strong>GATA!</strong> in bara de sus, apasa F5 si finalizeaza comanda.
    </div>
  </div>

  <div class="box">
    <h2>Lista completa ({len(books)} carti)</h2>
    <table>
      <thead><tr><th>#</th><th>Titlu</th><th>ISBN</th><th>Stare</th><th>Pret</th></tr></thead>
      <tbody>{book_rows}</tbody>
    </table>
  </div>

  <p class="ft">Product ID-urile au fost pre-extrase. Scriptul face doar POST-uri directe = viteza maxima.</p>
</div>

<script>
function prepareBookmarklet(){{
  var ta=document.getElementById('scriptArea');
  var code=ta.value.replace(/\\s+/g,' ');
  var link=document.getElementById('bmLink');
  link.href='javascript:'+code;
}}
window.addEventListener('load', prepareBookmarklet);
</script>
</body>
</html>"""


# ─── Main ────────────────────────────────────────────────────────────

def main():
    # Find cart HTML
    if len(sys.argv) > 1:
        cart_file = sys.argv[1]
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # 1) Daca exista explicit "Cos cumparaturi.html", il folosim mereu
        preferred = os.path.join(script_dir, "Cos cumparaturi.html")
        if os.path.exists(preferred):
            cart_file = preferred
        else:
            # 2) Altfel, fallback pe vechiul comportament (checkout_cart*.html)
            candidates = [
                f for f in os.listdir(script_dir)
                if "checkout_cart" in f.lower() and f.endswith(".html")
            ]
            if candidates:
                cart_file = os.path.join(script_dir, candidates[0])
            else:
                print("EROARE: Nu s-a gasit fisierul HTML al cosului.")
                print("Utilizare: python cart_manager.py <fisier_cos.html>")
                sys.exit(1)

    print(f"=== Targul Cartii - Cart Manager v2 ===\n")
    print(f"[1/3] Parsare cos: {os.path.basename(cart_file)}")
    books = parse_cart_html(cart_file)

    if not books:
        print("EROARE: Nu s-au gasit carti in cos!")
        sys.exit(1)

    print(f"      Gasite {len(books)} carti.\n")

    # Phase 2: Extract product IDs
    print(f"[2/3] Extragere product_id-uri (vizitare pagini carti)...")
    books_with_pid, failed = extract_product_ids(books, delay=0.8)

    print(f"\n      Extrase: {len(books_with_pid)} OK, {len(failed)} erori\n")

    if not books_with_pid:
        print("EROARE: Nu s-a putut extrage niciun product_id!")
        sys.exit(1)

    # Phase 3: Generate files
    print(f"[3/3] Generare fisiere...")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    hosting_dir = os.path.join(script_dir, "hosting")
    os.makedirs(hosting_dir, exist_ok=True)

    # Total price
    total = 0
    for b in books_with_pid:
        try:
            total += float(b.get("price", "0").replace("LEI", "").replace(",", ".").strip())
        except ValueError:
            pass

    # Save books.json (full data)
    json_path = os.path.join(script_dir, "books.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(books_with_pid, f, indent=2, ensure_ascii=False)
    print(f"      books.json salvat ({len(books_with_pid)} carti)")

    # Generate script.js
    js_script = generate_script_js(books_with_pid)
    js_path = os.path.join(hosting_dir, "script.js")
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js_script)
    print(f"      hosting/script.js generat ({len(js_script)} bytes)")

    # Generate index.html
    html_content = generate_index_html(books_with_pid, js_script)
    html_path = os.path.join(hosting_dir, "index.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"      hosting/index.html generat")

    # Summary
    print(f"\n{'='*55}")
    print(f"  GATA! {len(books_with_pid)} carti | {total:.2f} LEI")
    print(f"{'='*55}")
    print(f"  Fisiere de urcat pe hosting:")
    print(f"    hosting/index.html  - pagina pentru Andreea")
    print(f"    hosting/script.js   - scriptul (backup)")
    print(f"")
    print(f"  Andreea face asa:")
    print(f"    1. Deschide link-ul tau (index.html de pe hosting)")
    print(f"    2. Click COPIAZA SCRIPTUL")
    print(f"    3. targulcartii.ro > F12 > Console > Ctrl+V > Enter")
    print(f"    4. Asteapta GATA > F5 > Plateste")
    print(f"{'='*55}")

    if failed:
        print(f"\n  ATENTIE: {len(failed)} carti nu au putut fi procesate:")
        for b in failed:
            print(f"    - {b['name']}: {b['url']}")


if __name__ == "__main__":
    main()
