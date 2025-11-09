const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d');
const info = document.getElementById('info');

let gridData = null;
let riskGrid = null;
let currentPath = null;
let enemiesLocal = [];
let animating = false;
let startPos = null;
let goalPos = null;
let dragging = null; // 'start' | 'goal' | null
let zoomLevel = parseInt(document.getElementById('zoom').value, 10) || 24;

function fetchMap(){
  return fetch('/api/map').then(r=>r.json()).then(j=>{ gridData = j; return j; });
}

function getCellSize(){
  return zoomLevel;
}

function drawGrid(){
  if(!gridData) return;
  const rows = gridData.rows, cols = gridData.cols;
  const cell = getCellSize();
  const desiredW = cols * cell;
  const desiredH = rows * cell;
  canvas.width = desiredW * (window.devicePixelRatio || 1);
  canvas.height = desiredH * (window.devicePixelRatio || 1);
  canvas.style.width = desiredW + 'px';
  canvas.style.height = desiredH + 'px';
  ctx.setTransform(window.devicePixelRatio || 1, 0, 0, window.devicePixelRatio || 1, 0, 0);

  ctx.clearRect(0,0,desiredW,desiredH);
  for(let r=0;r<rows;r++){
    for(let c=0;c<cols;c++){
      const t = gridData.cells[r][c];
      let color = '#e6e6dc';
      if(t==='FOREST') color = '#78aa78';
      if(t==='WATER') color = '#78a0c8';
      if(t==='URBAN') color = '#bdbdbd';
      if(t==='MOUNTAIN') color = '#b4966b';
      if(t==='BLOCKED') color = '#282828';
      ctx.fillStyle = color;
      ctx.fillRect(c*cell, r*cell, cell-1, cell-1);
    }
  }

  if(document.getElementById('showRisk').checked && riskGrid){
    const maxRisk = Math.max(...riskGrid.flat());
    for(let r=0;r<rows;r++){
      for(let c=0;c<cols;c++){
        const v = riskGrid[r][c];
        if(!isFinite(v) || v<=0) continue;
        const a = Math.min(0.9, v / (maxRisk || 1));
        ctx.fillStyle = `rgba(255,0,0,${a*0.6})`;
        ctx.fillRect(c*cell, r*cell, cell-1, cell-1);
      }
    }
  }

  enemiesLocal.forEach(e=>{
    const [r,c,rg] = e;
    ctx.fillStyle = 'rgba(150,0,0,0.9)';
    ctx.beginPath(); ctx.arc(c*cell+cell/2, r*cell+cell/2, Math.max(4, cell/3), 0, Math.PI*2); ctx.fill();
    ctx.strokeStyle = 'rgba(150,0,0,0.5)'; ctx.lineWidth=1; ctx.beginPath(); ctx.arc(c*cell+cell/2, r*cell+cell/2, Math.max(6, rg*cell/2), 0, Math.PI*2); ctx.stroke();
  });

  if(startPos) drawMarker(startPos, 'start');
  if(goalPos) drawMarker(goalPos, 'goal');
}

function drawMarker(pos, type){
  const cell = getCellSize();
  const [r,c] = pos;
  if(type==='start'){
    ctx.fillStyle = 'rgba(50,120,255,0.95)';
    ctx.fillRect(c*cell+cell*0.12, r*cell+cell*0.12, cell*0.75, cell*0.75);
  } else {
    ctx.fillStyle = 'rgba(255,80,80,0.95)';
    ctx.beginPath(); ctx.arc(c*cell+cell/2, r*cell+cell/2, Math.max(6, cell*0.28), 0, Math.PI*2); ctx.fill();
  }
}

function drawPath(path){
  if(!path) return;
  const rows = gridData.rows, cols = gridData.cols;
  const cell = getCellSize();
  ctx.strokeStyle = '#000';
  ctx.lineWidth = Math.max(2, cell/6);
  ctx.beginPath();
  for(let i=0;i<path.length;i++){
    const [r,c] = path[i];
    const x = c*cell + cell/2, y = r*cell + cell/2;
    if(i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
  }
  ctx.stroke();
}

function tupleify(a){ return [parseInt(a[0],10), parseInt(a[1],10)]; }

document.getElementById('compute').addEventListener('click', ()=>{
  const mode = document.getElementById('mode').value;
  info.textContent = 'Computing...';
  const payload = { mode, enemies: enemiesLocal };
  if(startPos) payload.start = startPos;
  if(goalPos) payload.goal = goalPos;
  fetch('/api/path', {method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify(payload)})
    .then(r=>r.json())
    .then(j=>{
      currentPath = j.path;
      riskGrid = j.risk || null;
      startPos = j.start || startPos;
      goalPos = j.goal || goalPos;
      drawGrid();
      drawPath(j.path);
      updateRiskLegend();
      info.textContent = `cost=${j.total.toFixed(2)} len=${j.path?j.path.length:0}`;
      refreshEnemyList();
    }).catch(e=>{ info.textContent = 'Error: '+e.message });
});

fetchMap().then(()=>{ 
  startPos = gridData.meta && gridData.meta.start ? tupleify(gridData.meta.start) : [gridData.rows-1, 0];
  goalPos = gridData.meta && gridData.meta.goal ? tupleify(gridData.meta.goal) : [0, gridData.cols-1];
  drawGrid(); info.textContent='Map loaded. Click canvas to add enemies or click Compute.';
});

// pointer interactions: add/remove enemies or drag start/goal if enabled
canvas.addEventListener('pointerdown', (ev)=>{
  if(!gridData) return;
  const rect = canvas.getBoundingClientRect();
  const x = ev.clientX - rect.left, y = ev.clientY - rect.top;
  const rows = gridData.rows, cols = gridData.cols;
  const cell = getCellSize();
  const c = Math.floor(x / cell), r = Math.floor(y / cell);
  const dragEnabled = document.getElementById('dragStartGoal').checked;
  if(dragEnabled){
    if(startPos && startPos[0]===r && startPos[1]===c){ dragging = 'start'; return; }
    if(goalPos && goalPos[0]===r && goalPos[1]===c){ dragging = 'goal'; return; }
  }
  const foundIdx = enemiesLocal.findIndex(e=>e[0]===r && e[1]===c);
  if(foundIdx>=0) enemiesLocal.splice(foundIdx,1);
  else { const rg = Math.max(1, parseInt(document.getElementById('enemyRange').value||4,10)); enemiesLocal.push([r,c,rg]); }
  drawGrid(); if(currentPath) drawPath(currentPath);
  refreshEnemyList();
});

canvas.addEventListener('pointermove', (ev)=>{
  if(!dragging) return;
  const rect = canvas.getBoundingClientRect();
  const x = ev.clientX - rect.left, y = ev.clientY - rect.top;
  const cell = getCellSize(); const r = Math.floor(y / cell), c = Math.floor(x / cell);
  if(r<0||c<0||r>=gridData.rows||c>=gridData.cols) return;
  if(dragging==='start'){ startPos = [r,c]; }
  if(dragging==='goal'){ goalPos = [r,c]; }
  drawGrid(); if(currentPath) drawPath(currentPath);
});

canvas.addEventListener('pointerup', ()=>{ dragging = null; });

function refreshEnemyList(){
  const ul = document.getElementById('enemyList'); ul.innerHTML='';
  enemiesLocal.forEach((e,idx)=>{
    const li = document.createElement('li'); li.textContent = `r=${e[0]}, c=${e[1]}, range=${e[2]}`;
    ul.appendChild(li);
  });
}

document.getElementById('randomize').addEventListener('click', ()=>{
  fetch('/api/randomize').then(r=>r.json()).then(j=>{ enemiesLocal = j.enemies; refreshEnemyList(); drawGrid(); if(currentPath) drawPath(currentPath); });
});

// Clear enemies
document.getElementById('clearEnemies').addEventListener('click', ()=>{ enemiesLocal = []; refreshEnemyList(); drawGrid(); if(currentPath) drawPath(currentPath); });

// Fit-to-window: choose zoom to fit canvas-wrap
document.getElementById('fit').addEventListener('click', ()=>{
  if(!gridData) return;
  const wrap = document.getElementById('canvas-wrap');
  const availableW = wrap.clientWidth - 20; // padding
  const availableH = wrap.clientHeight - 20;
  const zoomW = Math.floor(availableW / gridData.cols);
  const zoomH = Math.floor(availableH / gridData.rows);
  const newZoom = Math.max(4, Math.min(60, Math.max(4, Math.min(zoomW, zoomH))))
  zoomLevel = newZoom;
  document.getElementById('zoom').value = zoomLevel;
  drawGrid(); if(currentPath) drawPath(currentPath);
});

// Export scenario
document.getElementById('exportScenario').addEventListener('click', ()=>{
  if(!gridData) return; const scenario = { meta: gridData.meta || {}, enemies: enemiesLocal, start: startPos, goal: goalPos, mode: document.getElementById('mode').value };
  const blob = new Blob([JSON.stringify(scenario, null, 2)], {type:'application/json'}); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href=url; a.download='scenario.json'; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
});

// Import scenario via file picker
document.getElementById('scenarioFile').addEventListener('change', (ev)=>{
  const f = ev.target.files[0]; if(!f) return; const reader = new FileReader(); reader.onload = (e)=>{
    try{ const s = JSON.parse(e.target.result);
      if(s.enemies) enemiesLocal = s.enemies.map(x=>[x[0], x[1], x[2]||4]);
      if(s.start) startPos = [s.start[0], s.start[1]];
      if(s.goal) goalPos = [s.goal[0], s.goal[1]];
      if(s.mode) document.getElementById('mode').value = s.mode;
      refreshEnemyList(); drawGrid(); if(currentPath) drawPath(currentPath);
      info.textContent = 'Scenario imported';
    } catch(x){ info.textContent = 'Invalid scenario file'; }
  };
  reader.readAsText(f);
});

// show risk min/max in legend when riskGrid updated
function updateRiskLegend(){
  if(!riskGrid){ document.getElementById('riskMin').textContent='0'; document.getElementById('riskMax').textContent='0'; return; }
  const vals = riskGrid.flat().filter(v=>isFinite(v));
  if(vals.length===0){ document.getElementById('riskMin').textContent='0'; document.getElementById('riskMax').textContent='0'; return; }
  const min = Math.min(...vals); const max = Math.max(...vals);
  document.getElementById('riskMin').textContent = min.toFixed(3);
  document.getElementById('riskMax').textContent = max.toFixed(3);
  drawRiskLegend(min, max);
}

function drawRiskLegend(min, max){
  const c = document.getElementById('legendCanvas');
  if(!c) return;
  const ctxL = c.getContext('2d');
  const w = c.width, h = c.height;
  // Clear
  ctxL.clearRect(0,0,w,h);
  // Draw gradient from green -> yellow -> red
  const g = ctxL.createLinearGradient(0,0,w,0);
  g.addColorStop(0, '#2ecc71');
  g.addColorStop(0.5, '#f1c40f');
  g.addColorStop(1, '#e74c3c');
  ctxL.fillStyle = g;
  ctxL.fillRect(0,0,w,h);
  // overlay subtle grid lines
  ctxL.strokeStyle = 'rgba(0,0,0,0.15)'; ctxL.lineWidth = 1;
  for(let x=0;x<w;x+=Math.max(4, Math.floor(w/8))){ ctxL.beginPath(); ctxL.moveTo(x,0); ctxL.lineTo(x,h); ctxL.stroke(); }
  // draw min/max ticks
  ctxL.fillStyle = 'rgba(255,255,255,0.95)'; ctxL.font = '10px Inter, sans-serif';
  const minS = (min===undefined? '0' : min.toFixed(3));
  const maxS = (max===undefined? '0' : max.toFixed(3));
  // write min left and max right (small, draw outside canvas by changing container text used already)
}

// initialize legend early
drawRiskLegend(0,0);

document.getElementById('download').addEventListener('click', ()=>{
  if(!currentPath) return; const data = {path: currentPath}; const blob = new Blob([JSON.stringify(data, null, 2)], {type:'application/json'});
  const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href=url; a.download='path.json'; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
});

document.getElementById('animate').addEventListener('click', ()=>{
  if(!currentPath || !gridData) return; if(animating) return; animating = true; const cell = getCellSize(); let i=0; const id = setInterval(()=>{
    drawGrid(); drawPath(currentPath.slice(0,i+1)); i++; if(i>=currentPath.length){ clearInterval(id); animating = false; }
  }, 60);
});

// zoom control
document.getElementById('zoom').addEventListener('input', (ev)=>{ zoomLevel = parseInt(ev.target.value,10); drawGrid(); if(currentPath) drawPath(currentPath); });

// save map (download a minimal meta)
document.getElementById('saveMap').addEventListener('click', ()=>{
  if(!gridData) return; const blob = new Blob([JSON.stringify(gridData.meta || {}, null, 2)], {type:'application/json'});
  const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href=url; a.download='map_meta.json'; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
});

// reset map to server default
document.getElementById('resetMap').addEventListener('click', ()=>{ fetchMap().then(()=>{ drawGrid(); if(currentPath) drawPath(currentPath); refreshEnemyList(); }); });

// load map from file input (preview only)
document.getElementById('mapFile').addEventListener('change', (ev)=>{
  const f = ev.target.files[0]; if(!f) return; const reader = new FileReader(); reader.onload = (e)=>{
    try{ const data = JSON.parse(e.target.result);
      if(data.rows && data.cols){
        gridData = { rows: data.rows, cols: data.cols, cells: [] , meta: data };
        for(let r=0;r<data.rows;r++){ const row=[]; for(let c=0;c<data.cols;c++){ row.push('OPEN'); } gridData.cells.push(row); }
        drawGrid(); info.textContent = 'Custom map loaded (preview only). Use Reset to restore server map.';
      } else { info.textContent = 'Map file does not look valid.' }
    } catch(x){ info.textContent = 'Failed to parse map file'; }
  };
  reader.readAsText(f);
});
