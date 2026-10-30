#!/usr/bin/env python3
"""Render carousel 3D: cac the video bo goc xoay vong quanh nguoi noi.

Xuat 2 chuoi PNG trong suot (1080x1920):
  <out>/back/%04d.png   - the + nua vong sang o PHIA SAU nguoi
  <out>/front/%04d.png  - the + nua vong sang o PHIA TRUOC nguoi
Ghep: video goc -> back -> nguoi (da tach nen) -> front.

Vi du:
  python orbit_carousel.py --cards a.mp4 b.mp4 c.mp4 d.mp4 --duration 4 --out work/orbit
"""
import argparse, json, math, shutil, subprocess, sys
from pathlib import Path


def extract_frames(clip, start, duration, fps, w, h, dst):
    dst.mkdir(parents=True, exist_ok=True)
    vf = (f"scale={w*2}:{h*2}:force_original_aspect_ratio=increase,"
          f"crop={w*2}:{h*2},fps={fps}")
    # Neu clip ngan hon duration thi lap lai (stream_loop)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-ss", str(start),
                    "-i", str(clip), "-t", str(duration), "-vf", vf, "-q:v", "3",
                    str(dst / "%04d.jpg")], check=True)
    n = len(list(dst.glob("*.jpg")))
    if n == 0:
        sys.exit(f"Khong trich duoc khung tu {clip}")
    return n


HTML = r"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;width:1080px;height:1920px;background:transparent;overflow:hidden}
#stage{position:absolute;inset:0;perspective:__PERSP__px;perspective-origin:540px __CY__px}
#ring{position:absolute;left:540px;top:__CY__px;width:0;height:0;transform-style:preserve-3d}
.card{position:absolute;width:__W__px;height:__H__px;left:-__HW__px;top:-__HH__px;
  border-radius:__RAD__px;overflow:hidden;backface-visibility:visible;
  box-shadow:0 0 0 3px rgba(255,255,255,.85),0 18px 40px rgba(0,0,0,.45)}
.card img{width:100%;height:100%;object-fit:cover;display:block}
.card .gloss{position:absolute;inset:0;background:linear-gradient(135deg,rgba(255,255,255,.28),rgba(255,255,255,0) 45%)}
svg{position:absolute;left:0;top:0}
</style></head><body>
<svg width="1080" height="1920"><defs>
 <linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="__GLOW__" stop-opacity="0"/>
 <stop offset=".5" stop-color="__GLOW__"/><stop offset="1" stop-color="__GLOW__" stop-opacity="0"/></linearGradient>
 <filter id="b" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="6"/></filter></defs>
 <g id="arc"><path id="a1" fill="none" stroke="url(#g)" stroke-width="10" filter="url(#b)"/>
 <path id="a2" fill="none" stroke="#fff" stroke-opacity=".9" stroke-width="2.5"/></g></svg>
<div id="stage"><div id="ring"></div></div>
<script>
const C=__CFG__;
const ring=document.getElementById('ring');
const cards=[];
for(let i=0;i<C.n;i++){const d=document.createElement('div');d.className='card';
 d.innerHTML='<img><div class="gloss"></div>';ring.appendChild(d);cards.push(d);}
const ease=x=>1-Math.pow(1-Math.min(1,Math.max(0,x)),3);
function render(f,layer){
 const t=f/C.fps, D=C.duration;
 const kin=ease(t/C.enter), kout=ease((D-t)/C.exit), k=Math.min(kin,kout);
 const R=C.radius*(0.45+0.55*k);
 const base=C.startAngle + C.speed*t + (1-kin)*-90;
 ring.style.transform=`rotateX(${-C.tilt}deg)`;
 for(let i=0;i<C.n;i++){
  const th=base+i*360/C.n, r=th*Math.PI/180, z=Math.cos(r), s=Math.sin(r);
  const isFront=z>=0;
  let op=k;
  if(isFront){ // the di ngang mat nguoi thi mo dan de khong che mat
    const side=Math.abs(s); op*=Math.min(1,Math.max(0,(side-C.faceClear)/0.25)); }
  const show=(layer==='front')===isFront;
  const c=cards[i];
  c.style.display=show&&op>0.01?'block':'none';
  c.style.opacity=op;
  // the gan camera nhat: vien phat sang (giong mau)
  const hl=Math.max(0,(z-0.85)/0.15);
  c.style.boxShadow=`0 0 0 3px rgba(255,255,255,.85),0 0 ${30*hl}px ${8*hl}px ${C.glow}${Math.round(hl*230).toString(16).padStart(2,'0')},0 18px 40px rgba(0,0,0,.45)`;
  c.style.transform=`rotateY(${th}deg) translateZ(${R}px) rotateY(${-th*C.faceCam}deg) scale(${0.6+0.4*k})`;
  c.querySelector('img').src=C.frames[i][Math.min(f,C.frames[i].length-1)];
 }
 // vong sang: ellipse, nua tren o lop sau, nua duoi o lop truoc
 const rx=R*1.18, ry=R*Math.sin(C.tilt*Math.PI/180)*1.6+12, cy=C.cy+C.arcDy;
 const top=`M ${540-rx} ${cy} A ${rx} ${ry} 0 0 1 ${540+rx} ${cy}`;
 const bot=`M ${540-rx} ${cy} A ${rx} ${ry} 0 0 0 ${540+rx} ${cy}`;
 const d=layer==='front'?bot:top;
 document.getElementById('a1').setAttribute('d',d);
 document.getElementById('a2').setAttribute('d',d);
 document.getElementById('arc').style.opacity=C.arc?k:0;
 return Promise.all([...document.images].filter(im=>!im.complete).map(im=>new Promise(r=>{im.onload=im.onerror=r})));
}
</script></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cards", nargs="+", required=True, help="3-6 clip/anh cho cac the")
    ap.add_argument("--card-start", type=float, default=0.0, help="giay bat dau lay trong moi clip the")
    ap.add_argument("--duration", type=float, default=4.0)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--out", required=True)
    ap.add_argument("--card-w", type=int, default=300)
    ap.add_argument("--card-h", type=int, default=440)
    ap.add_argument("--radius", type=float, default=470)
    ap.add_argument("--center-y", type=int, default=1120, help="tam vong (ngang nguc nguoi noi)")
    ap.add_argument("--tilt", type=float, default=10, help="do nghieng vong (do)")
    ap.add_argument("--speed", type=float, default=40, help="toc do quay do/giay")
    ap.add_argument("--start-angle", type=float, default=50)
    ap.add_argument("--face-cam", type=float, default=0.55, help="0=the xoay theo vong, 1=luon nhin thang camera")
    ap.add_argument("--face-clear", type=float, default=0.0,
                    help="0=the truoc di ngang nguoi van hien (giong mau); 0.3-0.5=the chinh giua mo dan neu vong o ngang mat")
    ap.add_argument("--enter", type=float, default=0.6)
    ap.add_argument("--exit", type=float, default=0.45)
    ap.add_argument("--glow", default="#ffb347", help="mau vong sang")
    ap.add_argument("--no-arc", action="store_true")
    ap.add_argument("--arc-dy", type=int, default=250, help="ha vong sang xuong duoi tam the")
    a = ap.parse_args()

    if not 2 <= len(a.cards) <= 8:
        sys.exit("Can 2-8 the (khuyen nghi 4-6).")
    out = Path(a.out).resolve()
    if out.exists():
        shutil.rmtree(out)
    nframes = int(round(a.duration * a.fps))
    frames = []
    for i, c in enumerate(a.cards):
        d = out / f"card{i}"
        extract_frames(c, a.card_start, a.duration, a.fps, a.card_w, a.card_h, d)
        fl = sorted(d.glob("*.jpg"))
        frames.append([p.as_uri() for p in fl])

    cfg = dict(n=len(a.cards), fps=a.fps, duration=a.duration, radius=a.radius, cy=a.center_y,
               tilt=a.tilt, speed=a.speed, startAngle=a.start_angle, faceCam=a.face_cam,
               faceClear=a.face_clear, enter=a.enter, exit=a.exit, frames=frames,
               arc=not a.no_arc, arcDy=a.arc_dy, glow=a.glow)
    html = (HTML.replace("__CFG__", json.dumps(cfg)).replace("__PERSP__", "1600")
            .replace("__CY__", str(a.center_y)).replace("__W__", str(a.card_w))
            .replace("__H__", str(a.card_h)).replace("__HW__", str(a.card_w // 2))
            .replace("__HH__", str(a.card_h // 2)).replace("__RAD__", str(a.card_w // 9))
            .replace("__GLOW__", a.glow))
    page_file = out / "orbit.html"
    page_file.write_text(html, encoding="utf-8")

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--allow-file-access-from-files"])
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto(page_file.as_uri())
        for layer in ("back", "front"):
            ld = out / layer
            ld.mkdir(parents=True, exist_ok=True)
            for f in range(nframes):
                pg.evaluate(f"render({f}, '{layer}')")
                pg.screenshot(path=str(ld / f"{f+1:04d}.png"), omit_background=True)
        b.close()
    print(json.dumps({"frames": nframes, "back": str(out / 'back'), "front": str(out / 'front')}))


if __name__ == "__main__":
    main()
