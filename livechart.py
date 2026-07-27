"""
livechart.py
-------------
A CLIENT-SIDE live candlestick chart (Plotly.js in the browser) that fetches
data straight from Binance and updates itself in place every few seconds —
WITHOUT any Streamlit rerun. This means:
  - no full-page/graph reload on refresh
  - your zoom / pan is preserved (uirevision)
  - smooth, real-time candles like a pro trading app

It only works for Binance-sourced symbols (crypto, and Gold via PAXGUSDT).
The fetch runs in the user's own browser, so Binance geo-blocks on the cloud
server don't apply.
"""

import json
import streamlit.components.v1 as components

_PLOTLY_CDN = "https://cdn.plot.ly/plotly-2.35.2.min.js"


def render_live_chart(binance_symbol: str, interval: str, height: int = 560,
                      pred_text: str = "", pred_color: str = "#888") -> None:
    """Render the self-updating client-side chart via an HTML component."""
    cfg = {
        "symbol": binance_symbol.upper(),
        "interval": interval,
        "predText": pred_text,
        "predColor": pred_color,
    }
    html = _TEMPLATE.replace("__CFG__", json.dumps(cfg)).replace("__CDN__", _PLOTLY_CDN)
    components.html(html, height=height + 56)


_TEMPLATE = """
<div id="err" style="color:#e74c3c;font-family:sans-serif;font-size:13px;padding:6px;"></div>
<div id="readout" style="font-family:sans-serif;font-size:13px;padding:2px 6px;color:#cfd3d8;"></div>
<div id="chart" style="width:100%;height:__HEIGHTPX__;"></div>
<script src="__CDN__"></script>
<script>
const CFG = __CFG__;
const HEIGHT = __HEIGHTNUM__;
const HOSTS = ["https://api.binance.com","https://data-api.binance.vision","https://api1.binance.com"];

function sma(a,p){const o=Array(a.length).fill(null);let s=0;for(let i=0;i<a.length;i++){s+=a[i];if(i>=p)s-=a[i-p];if(i>=p-1)o[i]=s/p;}return o;}
function ema(a,p){const o=Array(a.length).fill(null);const k=2/(p+1);let e=null;for(let i=0;i<a.length;i++){e=(e===null)?a[i]:a[i]*k+e*(1-k);o[i]=e;}return o;}
function rsi(a,p){const o=Array(a.length).fill(null);let g=0,l=0;for(let i=1;i<a.length;i++){const d=a[i]-a[i-1];const up=Math.max(d,0),dn=Math.max(-d,0);if(i<=p){g+=up;l+=dn;if(i===p){g/=p;l/=p;o[i]=100-100/(1+(l===0?100:g/l));}}else{g=(g*(p-1)+up)/p;l=(l*(p-1)+dn)/p;o[i]=100-100/(1+(l===0?100:g/l));}}return o;}
function bands(a,p,m){const mid=sma(a,p);const up=Array(a.length).fill(null),lo=Array(a.length).fill(null);for(let i=p-1;i<a.length;i++){let s=0;for(let j=i-p+1;j<=i;j++)s+=(a[j]-mid[i])**2;const sd=Math.sqrt(s/p);up[i]=mid[i]+m*sd;lo[i]=mid[i]-m*sd;}return {up,lo};}

async function getKlines(){
  const url = `/api/v3/klines?symbol=${CFG.symbol}&interval=${CFG.interval}&limit=200`;
  for(const h of HOSTS){
    try{const r=await fetch(h+url);if(r.ok)return await r.json();}catch(e){}
  }
  return null;
}

let started=false;
async function update(){
  const k=await getKlines();
  const err=document.getElementById('err');
  if(!k){err.textContent="Live feed unavailable right now — retrying...";return;}
  err.textContent="";
  const t=[],o=[],hi=[],lo=[],c=[],v=[],vc=[];
  for(const row of k){t.push(new Date(row[0]));o.push(+row[1]);hi.push(+row[2]);lo.push(+row[3]);c.push(+row[4]);v.push(+row[5]);vc.push((+row[4]>=+row[1])?'#2ecc71':'#e74c3c');}
  const last=c[c.length-1];
  const s20=sma(c,20), s50=sma(c,50), rs=rsi(c,14), bb=bands(c,20,2);

  // --- Live indicator readout (values + simple signal) ---
  const rNow = rs[rs.length-1];
  const prev = c[c.length-2] || last;
  const chg = ((last-prev)/prev*100);
  const trend = (s20[s20.length-1]>s50[s50.length-1]) ? "🟢 Uptrend" : "🔴 Downtrend";
  let rTag = "neutral"; if(rNow!=null){ if(rNow>70) rTag="overbought"; else if(rNow<30) rTag="oversold"; }
  const fmt = (x)=> x==null? "—" : x.toLocaleString(undefined,{maximumFractionDigits:2});
  document.getElementById('readout').innerHTML =
     `<b>${last.toLocaleString(undefined,{maximumFractionDigits:4})}</b> `
    +`<span style="color:${chg>=0?'#2ecc71':'#e74c3c'}">(${chg>=0?'+':''}${chg.toFixed(2)}%)</span>`
    +` &nbsp;·&nbsp; RSI ${fmt(rNow)} (${rTag}) &nbsp;·&nbsp; SMA20 ${fmt(s20[s20.length-1])}`
    +` &nbsp;·&nbsp; SMA50 ${fmt(s50[s50.length-1])} &nbsp;·&nbsp; ${trend}`;

  const traces=[
    {x:t,open:o,high:hi,low:lo,close:c,type:'candlestick',name:'Price',xaxis:'x',yaxis:'y',
      increasing:{line:{color:'#2ecc71'}},decreasing:{line:{color:'#e74c3c'}}},
    {x:t,y:bb.up,type:'scatter',mode:'lines',line:{color:'#888',width:1},name:'BB',xaxis:'x',yaxis:'y',hoverinfo:'skip'},
    {x:t,y:bb.lo,type:'scatter',mode:'lines',line:{color:'#888',width:1},name:'BB',xaxis:'x',yaxis:'y',hoverinfo:'skip',showlegend:false},
    {x:t,y:s20,type:'scatter',mode:'lines',line:{color:'#f5a623',width:1.2},name:'SMA20',xaxis:'x',yaxis:'y'},
    {x:t,y:s50,type:'scatter',mode:'lines',line:{color:'#4a90e2',width:1.2},name:'SMA50',xaxis:'x',yaxis:'y'},
    {x:t,y:v,type:'bar',marker:{color:vc},name:'Vol',xaxis:'x',yaxis:'y2'},
    {x:t,y:rs,type:'scatter',mode:'lines',line:{color:'#9b59b6'},name:'RSI',xaxis:'x',yaxis:'y3'}
  ];

  const pcol = last>=o[o.length-1] ? '#2ecc71' : '#e74c3c';
  const shapes=[
    {type:'line',xref:'paper',x0:0,x1:1,yref:'y',y0:last,y1:last,line:{color:pcol,dash:'dot',width:1}},
    {type:'line',xref:'paper',x0:0,x1:1,yref:'y3',y0:70,y1:70,line:{color:'#e74c3c',dash:'dot',width:1}},
    {type:'line',xref:'paper',x0:0,x1:1,yref:'y3',y0:30,y1:30,line:{color:'#2ecc71',dash:'dot',width:1}}
  ];
  const annotations=[
    {xref:'paper',x:1,y:last,yref:'y',xanchor:'left',text:' '+last.toLocaleString(undefined,{maximumFractionDigits:4})+' ',showarrow:false,font:{color:'#fff',size:11},bgcolor:pcol}
  ];
  if(CFG.predText){
    // Small arrow that sits just ABOVE the latest candle and follows it up/down
    // (re-anchored to the newest candle on every update, so it tracks the price).
    const gap=(Math.max.apply(null,hi)-Math.min.apply(null,lo))*0.02 || 0;
    annotations.push({x:t[t.length-1],y:hi[hi.length-1]+gap,xref:'x',yref:'y',
      text:CFG.predText,showarrow:true,arrowhead:2,arrowsize:0.9,arrowwidth:1.4,
      arrowcolor:CFG.predColor,ax:0,ay:-22,font:{color:'#fff',size:11},
      bgcolor:CFG.predColor,borderpad:2});
  }

  const layout={
    height:HEIGHT, margin:{l:6,r:66,t:6,b:20},
    paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)', font:{color:'#9aa0a6',size:11},
    dragmode:'pan', showlegend:true, legend:{orientation:'h',y:1.03,font:{size:10}},
    uirevision:'keep-'+CFG.symbol+'-'+CFG.interval,
    xaxis:{rangeslider:{visible:false},gridcolor:'rgba(128,128,128,0.12)',anchor:'y3'},
    yaxis:{domain:[0.42,1.0],side:'right',gridcolor:'rgba(128,128,128,0.12)'},
    yaxis2:{domain:[0.26,0.40],side:'right',gridcolor:'rgba(128,128,128,0.12)',title:{text:'Vol',font:{size:9}}},
    yaxis3:{domain:[0.0,0.24],side:'right',range:[0,100],gridcolor:'rgba(128,128,128,0.12)',title:{text:'RSI',font:{size:9}}},
    shapes:shapes, annotations:annotations
  };
  Plotly.react('chart',traces,layout,{scrollZoom:true,displaylogo:false,responsive:true,
    modeBarButtonsToRemove:['select2d','lasso2d']});
  started=true;
}
update();
setInterval(update, 4000);
</script>
""".replace("__HEIGHTPX__", "560px").replace("__HEIGHTNUM__", "560")
