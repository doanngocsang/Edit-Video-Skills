#!/usr/bin/env python3
"""Dung video 'Explainer chia doi' tu video talking-head + plan.json + transcript.

  python explainer_render.py --video work/cut.mp4 --plan work/plan.json \
      --words work/words.json --out output/ten-video-explainer.mp4

plan.json   : xem SKILL.md (segments: full/split, header, items).
words.json  : [{"word": "...", "start": 1.23, "end": 1.50}, ...] (lay tu transcript SAU cat).

Moi doan 'split' duoc render (Playwright) thanh chuoi PNG 1080x1920: nen + tieu de +
do hoa o nua tren; khung mat nguoi bo goc o nua duoi; caption tung tu o giua.
Doan 'full' giu nguyen video goc. Ghep 1 lan bang ffmpeg, audio goc giu nguyen.
"""
import argparse, json, math, shutil, subprocess, sys
from pathlib import Path

FPS = 30
W, H = 1080, 1920
BOX = dict(x=36, y=1250, w=1008, h=720, r=40)   # khung mat (tran xuong mep duoi)
CAP_SPLIT_Y = 1150                               # caption trong doan split
CAP_FULL_Y = 1430                                # caption trong doan full


def ffprobe_duration(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def snap(t):
    return round(t * FPS) / FPS


def normalize_segments(plan, dur):
    segs = sorted(plan["segments"], key=lambda s: s["start"])
    out, cur = [], 0.0
    for s in segs:
        st, en = snap(max(s["start"], cur)), snap(min(s["end"], dur))
        if en - st < 1 / FPS:
            continue
        if st - cur >= 1 / FPS:
            out.append({"start": cur, "end": st, "layout": "full"})
        s = dict(s, start=st, end=en)
        out.append(s)
        cur = en
    if dur - cur >= 1 / FPS:
        out.append({"start": cur, "end": snap(dur), "layout": "full"})
    return out


# ----------------------------------------------------------------------------- HTML
HTML = r"""<!doctype html><html><head><meta charset="utf-8"><style>
__FONTFACE__
:root{--bg:#F3F2EF;--fg:#111;--acc:__ACC__;--card:#fff;--muted:#6b6b6b}
.dark{--bg:#000;--fg:#fff;--card:#1b1b1b;--muted:#9a9a9a}
html,body{margin:0;width:1080px;height:1920px;overflow:hidden;background:var(--bg);color:var(--fg);
  font-family:'XSans','Be Vietnam Pro','Inter',sans-serif}
.abs{position:absolute}
#hdr{left:40px;right:40px;top:150px;text-align:center}
#hdr .l1{font-size:64px;font-weight:800;letter-spacing:-.5px;line-height:1.25}
#hdr .box{display:inline-block;background:var(--acc);color:#fff;padding:2px 16px 6px;border-radius:10px;
  transform-origin:left center}
#hdr .sub{font-family:'XSerif','Lora','DejaVu Serif',serif;font-style:italic;font-size:50px;
  font-weight:400;margin-top:4px;line-height:1.3}
.tile{width:190px;height:190px;border-radius:44px;background:#fff;display:flex;align-items:center;
  justify-content:center;box-shadow:0 14px 40px rgba(0,0,0,.18)}
.tile img{width:62%;height:62%;object-fit:contain}
.lbl{font-size:44px;font-weight:800;text-align:center;margin-top:16px}
.shot{border:6px solid var(--acc);border-radius:26px;overflow:hidden;background:#fff;
  box-shadow:0 20px 50px rgba(0,0,0,.35)}
.shot img{width:100%;display:block}
.cbadge{width:96px;height:96px;border-radius:50%;background:#111;display:flex;align-items:center;
  justify-content:center;box-shadow:0 6px 18px rgba(0,0,0,.35)}
.cbadge img{width:56%;height:56%;object-fit:contain}
.typ{left:40px;right:40px;border-radius:30px;background:#2f2f2f;color:#fff;font-size:36px;
  padding:34px 36px 70px;line-height:1.4;font-family:'Inter',sans-serif;word-break:break-all}
.typ .plus{position:absolute;left:36px;bottom:20px;font-size:40px;color:#aaa}
.caret{display:inline-block;width:3px;height:40px;background:#fff;vertical-align:-6px;margin-left:2px}
.stat{background:var(--acc);color:#fff;border-radius:16px;padding:10px 22px 12px;text-align:center;
  box-shadow:0 10px 30px rgba(0,0,0,.35)}
.stat .v{font-size:54px;font-weight:800;line-height:1.05}
.stat .k{font-size:20px;font-weight:700;letter-spacing:2px;text-transform:uppercase;opacity:.95}
.grid{left:40px;right:40px;display:grid;gap:10px}
.gcell{position:relative;aspect-ratio:9/12;border-radius:10px;overflow:hidden;background:#333}
.gcell img{width:100%;height:100%;object-fit:cover}
.gcell .hl{position:absolute;inset:0;border:5px solid var(--acc);border-radius:10px}
.gcell .vb{position:absolute;left:6px;bottom:6px;background:var(--acc);color:#fff;font-size:20px;
  font-weight:800;padding:3px 8px;border-radius:6px}
.cmp{width:440px;border-radius:26px;background:var(--card);border:3px solid #444;padding:30px 20px 26px;
  text-align:center}
.cmp.red{border-color:var(--acc)}
.cmp .av{width:120px;height:120px;border-radius:50%;margin:0 auto 14px;overflow:hidden;background:#555}
.cmp .av img{width:100%;height:100%;object-fit:cover}
.cmp .t{font-size:38px;font-weight:800}
.cmp .tag{display:inline-block;margin-top:10px;padding:4px 14px;border-radius:8px;font-size:22px;
  font-weight:800;letter-spacing:1px;background:#3a3a3a;color:#ddd}
.cmp.red .tag{background:var(--acc);color:#fff}
.cmp .ok{margin-top:16px;font-size:24px;color:#2fbf71;font-weight:700}
.res{background:#fff;color:#111;border:4px solid var(--acc);border-radius:14px;padding:14px 26px;
  font-size:30px;font-weight:800;text-align:center}
.big{left:40px;right:40px;text-align:center;font-size:110px;font-weight:900;line-height:1.05}
</style></head><body class="__THEME__">
<div id="hdr" class="abs"></div><div id="items"></div>
<script>
const S=__SEG__;
const clamp=x=>Math.max(0,Math.min(1,x));
const eOut=x=>1-Math.pow(1-clamp(x),3);
const eInOut=x=>{x=clamp(x);return x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2};
const back=x=>{x=clamp(x);const c=1.7;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)};
const esc=s=>String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const items=document.getElementById('items');
const hdr=document.getElementById('hdr');
// ---- header(s): co the doi trong 1 doan: S.headers=[{at,text,accent,sub}]
const H=(S.headers||[]).map(h=>{const d=document.createElement('div');d.style.position='absolute';
 d.style.left=0;d.style.right=0;
 let l1=esc(h.text||'');
 if(h.accent){l1+=(h.text?' ':'')+`<span class="box">${esc(h.accent)}</span>`;}
 d.innerHTML=`<div class="l1">${l1}</div>`+(h.sub?`<div class="sub">${esc(h.sub)}</div>`:'');
 hdr.appendChild(d);return {h,d};});
// ---- items
const I=(S.items||[]).map(it=>{const d=document.createElement('div');d.className='abs';
 d.style.left='0';d.style.top='0';d.style.width='1080px';items.appendChild(d);
 const y=it.y??340; const k=it.type;
 if(k==='icon'){d.innerHTML=`<div style="position:absolute;top:${y}px;left:0;right:0;display:flex;flex-direction:column;align-items:center">
   <div class="tile"><img src="${it.src}"></div>${it.label?`<div class="lbl">${esc(it.label)}</div>`:''}</div>`;}
 else if(k==='screenshot'){const w=it.w??620,vh=it.h??620;const x=(1080-w)/2;
  let corners='';(it.corners||[]).forEach((c,i)=>{const cx=i===0?x-34:x+w-62;corners+=`<div class="cbadge cb" style="position:absolute;left:${cx}px;top:${y-34}px"><img src="${c}"></div>`});
  d.innerHTML=`<div class="shot sh" style="position:absolute;left:${x}px;top:${y}px;width:${w}px;height:${vh}px"><img class="si" src="${it.src}"></div>${corners}`;}
 else if(k==='typing'){d.innerHTML=`<div class="typ" style="position:absolute;top:${y}px"><span class="tx"></span><span class="caret"></span><span class="plus">+</span></div>`;}
 else if(k==='stats'){let h='';(it.stats||[]).forEach((s,i)=>{const side=s.side||(i%2?'right':'left');
   const pos=side==='left'?`left:${s.x??24}px`:`right:${s.x??24}px`;
   h+=`<div class="stat st" data-side="${side}" style="position:absolute;top:${s.y??(y+i*170)}px;${pos}"><div class="v">${esc(s.value)}</div><div class="k">${esc(s.label||'')}</div></div>`});d.innerHTML=h;}
 else if(k==='grid'){const cols=it.cols??6;let h='';(it.images||[]).forEach((src,i)=>{const hl=(it.highlights||[]).find(q=>q.i===i);
   h+=`<div class="gcell gc" data-i="${i}"><img src="${src}">${hl?`<div class="hl"></div>${hl.label?`<div class="vb">▶ ${esc(hl.label)}</div>`:''}`:''}</div>`});
   d.innerHTML=`<div class="grid" style="position:absolute;top:${y}px;grid-template-columns:repeat(${cols},1fr)">${h}</div>`;}
 else if(k==='compare'){let h='';(it.cards||[]).forEach((c,i)=>{const x=i===0?60:580;
   h+=`<div class="cmp cc ${c.rival?'red':''}" style="position:absolute;top:${y}px;left:${x}px"><div class="av">${c.img?`<img src="${c.img}">`:''}</div><div class="t">${esc(c.title)}</div>${c.tag?`<div class="tag">${esc(c.tag)}</div>`:''}${c.ok?`<div class="ok">✓ ${esc(c.ok)}</div>`:''}</div>`});d.innerHTML=h;}
 else if(k==='flow'){const xs=[220,540,860],ty=y,cy=y+330;let ic='',p='';
   (it.sources||[]).slice(0,3).forEach((src,i)=>{ic+=`<div class="cbadge fs" style="position:absolute;left:${xs[i]-60}px;top:${ty}px;width:120px;height:120px;background:${it.sourceBg||'#fff'}"><img src="${src}"></div>`;
     p+=`<path class="fp" d="M ${xs[i]} ${ty+130} C ${xs[i]} ${ty+240}, 540 ${cy-120}, 540 ${cy-70}" fill="none" stroke="${getComputedStyle(document.documentElement).getPropertyValue('--acc')}" stroke-width="5" stroke-linecap="round"/>`});
   d.innerHTML=`<svg width="1080" height="1920" style="position:absolute;left:0;top:0">${p}</svg>${ic}
   <div class="tile fc" style="position:absolute;left:${540-80}px;top:${cy-60}px;width:160px;height:160px;border-radius:38px"><img src="${it.center}"></div>
   ${it.result?`<div class="res fr" style="position:absolute;left:250px;right:250px;top:${cy+130}px">${esc(it.result)}</div>`:''}`;
   d.querySelectorAll('.fp').forEach(pa=>{const L=pa.getTotalLength();pa.style.strokeDasharray=L;pa.dataset.len=L;});}
 else if(k==='text'){d.innerHTML=`<div class="big" style="position:absolute;top:${y}px">${esc(it.text)}</div>`;}
 return {it,d};});

function render(t){ // t = giay tuyet doi tren timeline
 // header: header co 'at' lon nhat <= t
 let cur=null;H.forEach(o=>{if(t>=o.h.at-1e-6)cur=o;});
 H.forEach(o=>{if(o!==cur){o.d.style.opacity=0;return;}
  const p=eOut((t-o.h.at)/0.3);o.d.style.opacity=p;o.d.style.transform=`translateY(${(1-p)*30}px)`;
  const b=o.d.querySelector('.box');if(b){const q=eOut((t-o.h.at-0.12)/0.25);b.style.transform=`scaleX(${q})`;}
 });
 I.forEach(({it,d})=>{const a=it.at??S.start,u=it.until??S.end,k=it.type;
  const on=t>=a&&t<u; if(!on){d.style.display='none';return;} d.style.display='block';
  const lt=t-a, out=(u<S.end-1e-3)?clamp((u-t)/0.2):1;
  d.style.opacity=out;
  if(k==='icon'){const s=back(lt/0.35);d.firstElementChild.style.transform=`scale(${s})`;}
  else if(k==='screenshot'){const p=eOut(lt/0.3);const sh=d.querySelector('.sh');
   sh.style.transform=`scale(${0.85+0.15*p})`;sh.style.opacity=p;
   const im=d.querySelector('.si');const vh=sh.clientHeight;const ih=im.clientHeight;
   const sc=it.scroll??0, sd=it.scrollDelay??0.8;
   if(sc>0&&ih>vh){const q=eInOut((lt-sd)/Math.max(0.5,(u-a)-sd-0.3));im.style.transform=`translateY(${-q*sc*(ih-vh)}px)`;}
   d.querySelectorAll('.cb').forEach((c,i)=>{c.style.transform=`scale(${back((lt-0.25-i*0.12)/0.3)})`;});}
  else if(k==='typing'){const p=eOut(lt/0.25);const box=d.querySelector('.typ');box.style.opacity=p;
   const n=Math.floor(Math.max(0,lt-(it.delay??0.3))*(it.cps??18));
   d.querySelector('.tx').textContent=(it.text||'').slice(0,n);
   d.querySelector('.caret').style.opacity=(Math.floor(lt*2.5)%2===0||n<(it.text||'').length)?1:0;}
  else if(k==='stats'){d.querySelectorAll('.st').forEach((s,i)=>{const p=eOut((lt-(it.stagger??0.3)*i)/0.35);
   const dir=s.dataset.side==='left'?-1:1;s.style.opacity=p;s.style.transform=`translateX(${dir*(1-p)*160}px)`;});}
  else if(k==='grid'){const p=eOut(lt/0.3);d.firstElementChild.style.opacity=p;
   const hls=it.highlights||[];hls.forEach((h,j)=>{const c=d.querySelector(`.gc[data-i="${h.i}"]`);if(!c)return;
    const q=back((lt-(it.hlDelay??0.6)-j*0.3)/0.3);c.querySelectorAll('.hl,.vb').forEach(e=>{e.style.opacity=clamp(q);e.style.transform=`scale(${0.7+0.3*q})`});});}
  else if(k==='compare'){d.querySelectorAll('.cc').forEach((c,i)=>{const at=(it.cardAt&&it.cardAt[i]!=null)?it.cardAt[i]-a:i*0.8;
   const p=eOut((lt-at)/0.35);c.style.opacity=p;c.style.transform=`translateX(${(i?1:-1)*(1-p)*140}px)`;});}
  else if(k==='flow'){d.querySelectorAll('.fs').forEach((e,i)=>{e.style.transform=`scale(${back((lt-i*0.15)/0.3)})`;});
   d.querySelectorAll('.fp').forEach((pa,i)=>{const q=eInOut((lt-0.5-i*0.1)/0.7);pa.style.strokeDashoffset=pa.dataset.len*(1-q);});
   const fc=d.querySelector('.fc');fc.style.transform=`scale(${back((lt-1.2)/0.35)})`;
   const fr=d.querySelector('.fr');if(fr){const q=eOut((lt-1.6)/0.3);fr.style.opacity=q;fr.style.transform=`translateY(${(1-q)*20}px)`;}}
  else if(k==='text'){const p=back(lt/0.3);d.firstElementChild.style.transform=`scale(${p})`;}
 });
 return Promise.all([...document.images].filter(im=>!im.complete).map(im=>new Promise(r=>{im.onload=im.onerror=r})));
}
</script></body></html>"""


def font_face(fonts_dir):
    css = []
    if not fonts_dir:
        return ""
    fd = Path(fonts_dir)
    sans = next((p for n in ["BeVietnamPro-ExtraBold.ttf", "BeVietnamPro-Bold.ttf"] for p in [fd / n] if p.exists()), None)
    serif = next((p for n in ["Lora-Italic.ttf", "Lora-Italic[wght].ttf", "PlayfairDisplay-Italic.ttf"]
                  for p in [fd / n] if p.exists()), None)
    if sans:
        css.append(f"@font-face{{font-family:'XSans';src:url('{sans.resolve().as_uri()}');font-weight:100 900}}")
    if serif:
        css.append(f"@font-face{{font-family:'XSerif';src:url('{serif.resolve().as_uri()}');font-style:italic}}")
    return "\n".join(css)


def resolve_srcs(seg, base: Path):
    def fix(v):
        if isinstance(v, str) and not v.startswith(("http", "data:", "file:")):
            p = (base / v).resolve()
            if not p.exists():
                sys.exit(f"Khong tim thay file: {v}")
            return p.as_uri()
        return v
    for it in seg.get("items", []):
        for key in ("src", "center"):
            if key in it:
                it[key] = fix(it[key])
        for key in ("corners", "images", "sources"):
            if key in it:
                it[key] = [fix(x) for x in it[key]]
        for c in it.get("cards", []):
            if c.get("img"):
                c["img"] = fix(c["img"])


def render_split(seg, idx, work: Path, acc, fonts_dir, base, page):
    d = work / f"seg{idx:02d}"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    seg = json.loads(json.dumps(seg))
    resolve_srcs(seg, base)
    if "header" in seg and "headers" not in seg:
        seg["headers"] = [dict(seg["header"], at=seg["start"])]
    for h in seg.get("headers", []):
        h.setdefault("at", seg["start"])
    theme = "dark" if seg.get("theme", "light") == "dark" else ""
    html = (HTML.replace("__SEG__", json.dumps(seg, ensure_ascii=False)).replace("__ACC__", acc)
            .replace("__THEME__", theme).replace("__FONTFACE__", font_face(fonts_dir)))
    hp = d / "page.html"
    hp.write_text(html, encoding="utf-8")
    page.goto(hp.as_uri())
    page.wait_for_timeout(300)
    n = round((seg["end"] - seg["start"]) * FPS)
    for f in range(n):
        page.evaluate(f"render({seg['start'] + f / FPS})")
        page.screenshot(path=str(d / f"{f + 1:04d}.png"))
    return d, n


def make_mask(path: Path):
    from PIL import Image, ImageDraw
    m = Image.new("L", (BOX["w"], BOX["h"]), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, BOX["w"] - 1, BOX["h"] - 1 + BOX["r"] * 2),
                                        radius=BOX["r"], fill=255)
    m.save(path)


def ass_time(t):
    t = max(0, t)
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def write_ass(words, segs, path: Path, font, acc_hex):
    def layout_at(t):
        for s in segs:
            if s["start"] <= t < s["end"]:
                return s
        return segs[-1]
    lines = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 2", "",
             "[V4+ Styles]",
             "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
             f"Style: Full,{font},76,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,5,2,5,40,40,0,1",
             f"Style: SplitLight,{font},64,&H00111111,&H00111111,&H00FFFFFF,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,40,40,0,1",
             f"Style: SplitDark,{font},64,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,40,40,0,1",
             "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for i, w in enumerate(words):
        txt = str(w["word"]).strip()
        if not txt:
            continue
        st = w["start"]
        en = words[i + 1]["start"] if i + 1 < len(words) and words[i + 1]["start"] - w["end"] < 0.6 else w["end"] + 0.15
        en = max(en, st + 0.12)
        s = layout_at(st)
        if s.get("layout") == "split" and not s.get("noCaption"):
            style = "SplitDark" if s.get("theme") == "dark" else "SplitLight"
            y = CAP_SPLIT_Y
        else:
            style, y = "Full", CAP_FULL_Y
        txt = txt.replace("{", "").replace("}", "")
        lines.append(f"Dialogue: 0,{ass_time(st)},{ass_time(en)},{style},,0,0,0,,"
                     f"{{\\pos(540,{y})\\fscx112\\fscy112\\t(0,90,\\fscx100\\fscy100)}}{txt}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--words", help="words.json (bo trong = khong caption)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--work", default="work/explainer")
    ap.add_argument("--fonts", default="assets/fonts")
    ap.add_argument("--caption-font", default="Be Vietnam Pro ExtraBold")
    ap.add_argument("--face-y", type=float, default=None, help="tam khung mat theo chieu doc (0-1) trong video goc")
    ap.add_argument("--only-frames", action="store_true", help="chi render PNG, khong ghep (de xem thu)")
    a = ap.parse_args()

    plan_path = Path(a.plan).resolve()
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    base = Path(plan.get("baseDir", Path.cwd()))
    acc = plan.get("accent", "#E5322D")
    face_y = a.face_y if a.face_y is not None else plan.get("faceY", 0.36)
    dur = ffprobe_duration(a.video)
    segs = normalize_segments(plan, dur)
    work = Path(a.work).resolve(); work.mkdir(parents=True, exist_ok=True)
    fonts_dir = a.fonts if Path(a.fonts).exists() else None

    from playwright.sync_api import sync_playwright
    rendered = {}
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--allow-file-access-from-files"])
        page = b.new_page(viewport={"width": W, "height": H})
        for i, s in enumerate(segs):
            if s.get("layout") == "split":
                rendered[i] = render_split(s, i, work, acc, fonts_dir, base, page)
                print(f"render doan {i}: {s['start']:.2f}-{s['end']:.2f}s ({rendered[i][1]} khung)")
        b.close()
    if a.only_frames:
        return

    mask = work / "mask.png"; make_mask(mask)
    # crop khung mat: ti le BOX tu video 1080x1920
    ch = round(W * BOX["h"] / BOX["w"] / 2) * 2
    cy = int(min(max(face_y * H - ch / 2, 0), H - ch))

    inputs = ["-i", a.video, "-loop", "1", "-i", str(mask)]
    fg, chains, labels, k = [], [], [], 2
    n = len(segs)
    fg.append(f"[0:v]fps={FPS},scale={W}:{H},setsar=1,split={n}" + "".join(f"[v{i}]" for i in range(n)))
    if rendered:
        fg.append(f"[1:v]format=gray,split={len(rendered)}" + "".join(f"[mk{i}]" for i in rendered))
    for i, s in enumerate(segs):
        trim = f"[v{i}]trim=start={s['start']}:end={s['end']},setpts=PTS-STARTPTS"
        if i in rendered:
            d, nf = rendered[i]
            inputs += ["-framerate", str(FPS), "-i", str(d / "%04d.png")]
            fg.append(f"{trim},crop={W}:{ch}:0:{cy},scale={BOX['w']}:{BOX['h']},format=rgba[f{i}]")
            fg.append(f"[mk{i}]trim=end_frame={nf},setpts=PTS-STARTPTS[m{i}]")
            fg.append(f"[f{i}][m{i}]alphamerge[fa{i}]")
            fg.append(f"[{k}:v]format=rgba,setpts=PTS-STARTPTS[bg{i}]")
            fg.append(f"[bg{i}][fa{i}]overlay={BOX['x']}:{BOX['y']}:shortest=1,format=yuv420p[s{i}]")
            k += 1
        else:
            fg.append(f"{trim},format=yuv420p[s{i}]")
        labels.append(f"[s{i}]")
    fg.append("".join(labels) + f"concat=n={n}:v=1:a=0[cv]")
    last = "[cv]"
    if a.words and Path(a.words).exists():
        words = json.loads(Path(a.words).read_text(encoding="utf-8"))
        ass = work / "captions.ass"
        write_ass(words, segs, ass, a.caption_font, acc)
        sub = ass.relative_to(Path.cwd()).as_posix() if ass.is_relative_to(Path.cwd()) else ass.as_posix().replace(":", "\\:")
        fd = f":fontsdir={Path(a.fonts).as_posix()}" if fonts_dir else ""
        fg.append(f"{last}subtitles='{sub}'{fd}[vout]"); last = "[vout]"
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fg),
           "-map", last, "-map", "0:a?", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
           "-r", str(FPS), "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
           "-af", "loudnorm=I=-14:TP=-1:LRA=11", "-movflags", "+faststart", a.out]
    (work / "ffmpeg_cmd.txt").write_text(" ".join(cmd), encoding="utf-8")
    subprocess.run(cmd, check=True)
    print(f"OK -> {a.out}")


if __name__ == "__main__":
    main()
