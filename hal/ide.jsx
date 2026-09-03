import React, { useState, useEffect, useRef, useCallback } from "react";

// ════════════════════════════════════════════════════════════════
// Ћ-HAL · HARMONIC ASSEMBLY LANGUAGE — Developer Dashboard & IDE
// augmntd LLC · v1.0-Alpha · Non-Extractive Resonance Compute Layer
// ════════════════════════════════════════════════════════════════

const C = {
  paper:      "#f7f5f0",
  paperWarm:  "#ede9e0",
  ink:        "#1a1814",
  inkMid:     "#3a3630",
  inkDim:     "#7a7268",
  inkGhost:   "#b8b0a0",
  rule:       "rgba(26,24,20,0.12)",
  ruleHeavy:  "rgba(26,24,20,0.25)",
  charge:     "#1a3a6a",
  chargeDim:  "rgba(26,58,106,0.08)",
  chargeMid:  "rgba(26,58,106,0.55)",
  debt:       "#6a1a1a",
  debtDim:    "rgba(106,26,26,0.07)",
  signal:     "#1a5a3a",
  signalDim:  "rgba(26,90,58,0.07)",
  amber:      "#8a5a10",
  amberDim:   "rgba(138,90,16,0.08)",
};

const MONO = "'IBM Plex Mono','Courier New',monospace";
const SANS = "'Libre Franklin','Helvetica Neue',sans-serif";
const SERIF = "'Libre Baskerville',Georgia,serif";

// ── The 30-Token Serbian Cyrillic ISA ────────────────────────────
const ISA = [
  { g: "А", n: "MOBILE_A", d: "Dynamic spatial buffer. Injected between high-density blocks.", t: "buffer" },
  { g: "Б", n: "BIND", d: "Bind a coherence channel to a register.", t: "op" },
  { g: "В", n: "VECTOR", d: "Vectorize the active amplitude array.", t: "op" },
  { g: "Г", n: "GATE", d: "Open a unidirectional phase gate.", t: "op" },
  { g: "Д", n: "DELTA", d: "Compute phase delta across adjacent qubits.", t: "op" },
  { g: "Ђ", n: "SOFT_ATTUNE_JMP", d: "Soft phase shift between adjacent qubits without breaking entanglement.", t: "key" },
  { g: "Е", n: "EMIT", d: "Emit resonant pulse to output field.", t: "op" },
  { g: "Ж", n: "FOLD", d: "Fold waveform along symmetry axis.", t: "op" },
  { g: "З", n: "ZERO", d: "Zero the noise floor of a channel.", t: "op" },
  { g: "И", n: "ITER", d: "Iterate over qubit array.", t: "op" },
  { g: "Ј", n: "YIELD_BRIDGE", d: "Directional proxy: pass biological coherence field to core matrix.", t: "key" },
  { g: "К", n: "COHERE", d: "Establish coherence across channel.", t: "op" },
  { g: "Л", n: "LOCK", d: "Phase-lock two channels.", t: "op" },
  { g: "Љ", n: "LINEAR_FUSION", d: "Blend two frequency ranges into a harmonized wave function.", t: "key" },
  { g: "М", n: "MIX", d: "Harmonic mixing of frequencies.", t: "op" },
  { g: "Н", n: "NODE", d: "Allocate a field node.", t: "op" },
  { g: "Њ", n: "NODE_SQUEEZE", d: "Attenuate localized amplitude spikes; press phase noise down.", t: "key" },
  { g: "О", n: "OSC", d: "Drive oscillation at base frequency.", t: "op" },
  { g: "П", n: "FIELD", d: "Reference the coherence field output.", t: "op" },
  { g: "Р", n: "RESONATE", d: "Enter resonant standing-wave state.", t: "op" },
  { g: "С", n: "SYNC", d: "Kuramoto synchronization pass.", t: "op" },
  { g: "Т", n: "TAU", d: "Set Temporal Mass (τₖ) index.", t: "op" },
  { g: "Ћ", n: "CRISP_PULSE", d: "Ultra-fast low-latency execution pulse for time-critical resonant calc.", t: "key" },
  { g: "У", n: "UNITY", d: "Normalize amplitude to unity.", t: "op" },
  { g: "Ф", n: "FUND", d: "Set fundamental resonant frequency.", t: "op" },
  { g: "Х", n: "HARMONY", d: "Apply harmonic series expansion.", t: "op" },
  { g: "Ц", n: "CYCLE", d: "Advance one execution cycle.", t: "op" },
  { g: "Ч", n: "CHANNEL", d: "Open a new field channel.", t: "op" },
  { g: "Џ", n: "FRICTION_COLLAPSE", d: "Hardware circuit breaker. Collapses phase friction, grounds system state.", t: "ground" },
  { g: "Ш", n: "SHIFT", d: "Phase-shift the entire register bank.", t: "op" },
];

const KEY_GLYPHS = new Set(["Ђ", "Ј", "Љ", "Њ", "Ћ"]);

const SAMPLE = `; =====================================================================
; Ћ-HAL SPEC V1.0: COHERENCE LOOP INTEGRATION TEST
; =====================================================================

.ТАУ_К 12.4                      ; Set Temporal Mass index baseline
.ФУНДАМЕНТАЛ 936е6               ; Set base resonant frequency

СЕЦТИОН .КОХЕРЕНЦИЈА
    НИЗ_КУБИТА:  .ТАУ_КУБИТИ 64  ; Initialize a 64-channel matrix
    ИЗЛАЗ_ПОЉА:  .КОХЕРЕНТНО_ПОЉЕ; Allocate memory for the field output

СЕЦТИОН .КОД
    ГЛОБАЛ _РЕСОНАНЦЕ_СТАРТ

_РЕСОНАНЦЕ_СТАРТ:
    ; Step 1: Initialize temporal coherence across the active array
    ИНИЦ_КОХЕРЕНЦИЈА НИЗ_КУБИТА, ИЗЛАЗ_ПОЉА

    ; Step 2: Apply harmonic mixing sequence
    ХАРМОНИЈА_МИКС НИЗ_КУБИТА, .ФУНДАМЕНТАЛ

    ; Step 3: CRITICAL ERROR MITIGATION
    Џ НИЗ_КУБИТА                 ; Invoke Џ to collapse noise & force symmetry

    ; Step 4: Execute phase-lock via Kuramoto synchronization
    СИНХ_ФАЗА НИЗ_КУБИТА, СПРЕЗАЊЕ=МАКС

    РЕТ ИЗЛАЗ_ПОЉА                ; Return clean, stabilized resonant state`;

// ════════════════════════════════════════════════════════════════
// COHERENCE FIELD — Kuramoto oscillator lattice (live canvas)
// ════════════════════════════════════════════════════════════════
function CoherenceField({ coupling, grounded, running }) {
  const ref = useRef(null);
  const stateRef = useRef(null);
  const couplingRef = useRef(coupling);
  const groundedRef = useRef(grounded);
  const runningRef = useRef(running);

  useEffect(() => { couplingRef.current = coupling; }, [coupling]);
  useEffect(() => { groundedRef.current = grounded; }, [grounded]);
  useEffect(() => { runningRef.current = running; }, [running]);

  useEffect(() => {
    const canvas = ref.current;
    const ctx = canvas.getContext("2d");
    const N = 8; // 8x8 = 64 qubit lattice
    const dpr = window.devicePixelRatio || 1;

    function size() {
      const w = canvas.offsetWidth, h = canvas.offsetHeight;
      canvas.width = w * dpr; canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    size();
    window.addEventListener("resize", size);

    // init phases & natural frequencies
    if (!stateRef.current) {
      const phases = [], omega = [];
      for (let i = 0; i < N * N; i++) {
        phases.push(Math.random() * Math.PI * 2);
        omega.push(0.6 + Math.random() * 0.9);
      }
      stateRef.current = { phases, omega };
    }

    let raf;
    function step() {
      const w = canvas.offsetWidth, h = canvas.offsetHeight;
      const { phases, omega } = stateRef.current;
      const K = couplingRef.current / 100 * 2.5;
      const dt = 0.05;

      if (runningRef.current) {
        const newPhases = phases.slice();
        for (let i = 0; i < N * N; i++) {
          const r = Math.floor(i / N), c = i % N;
          let sum = 0, cnt = 0;
          // couple to 4-neighbors
          [[-1,0],[1,0],[0,-1],[0,1]].forEach(([dr,dc]) => {
            const nr = r+dr, nc = c+dc;
            if (nr>=0&&nr<N&&nc>=0&&nc<N) {
              sum += Math.sin(phases[nr*N+nc] - phases[i]); cnt++;
            }
          });
          let dtheta = omega[i] + (K/cnt)*sum;
          // grounding (Џ) pulls everything toward common phase
          if (groundedRef.current) dtheta += 1.8 * Math.sin(0 - phases[i]);
          newPhases[i] = phases[i] + dtheta*dt;
        }
        for (let i=0;i<N*N;i++) phases[i] = newPhases[i];
      }

      // draw
      ctx.clearRect(0,0,w,h);
      const pad = 24;
      const cell = Math.min((w-pad*2)/N,(h-pad*2)/N);
      const ox = (w - cell*N)/2, oy = (h - cell*N)/2;

      // order parameter (coherence R)
      let sx=0, sy=0;
      for (let i=0;i<N*N;i++){ sx+=Math.cos(phases[i]); sy+=Math.sin(phases[i]); }
      const R = Math.sqrt(sx*sx+sy*sy)/(N*N);

      for (let i=0;i<N*N;i++){
        const r = Math.floor(i/N), c = i%N;
        const x = ox + c*cell + cell/2;
        const y = oy + r*cell + cell/2;
        const ph = phases[i];
        // phase → color between charge-blue (synced) and amber (drifting)
        const sync = (Math.cos(ph - Math.atan2(sy,sx)) + 1)/2;
        const rr = Math.round(26 + (138-26)*(1-sync));
        const gg = Math.round(58 + (90-58)*(1-sync));
        const bb = Math.round(106 + (16-106)*(1-sync));
        const rad = cell*0.16 + cell*0.10*Math.sin(ph);
        // glow
        const grad = ctx.createRadialGradient(x,y,0,x,y,cell*0.5);
        grad.addColorStop(0,`rgba(${rr},${gg},${bb},${0.22+sync*0.25})`);
        grad.addColorStop(1,`rgba(${rr},${gg},${bb},0)`);
        ctx.fillStyle = grad;
        ctx.beginPath(); ctx.arc(x,y,cell*0.5,0,Math.PI*2); ctx.fill();
        // core
        ctx.fillStyle = `rgb(${rr},${gg},${bb})`;
        ctx.beginPath(); ctx.arc(x,y,Math.max(1.5,rad),0,Math.PI*2); ctx.fill();
        // phase tick
        ctx.strokeStyle = `rgba(${rr},${gg},${bb},0.6)`;
        ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(x,y);
        ctx.lineTo(x+Math.cos(ph)*cell*0.28, y+Math.sin(ph)*cell*0.28); ctx.stroke();
      }

      // coupling lines for highly synced neighbors
      ctx.lineWidth = 0.5;
      for (let i=0;i<N*N;i++){
        const r=Math.floor(i/N),c=i%N;
        [[1,0],[0,1]].forEach(([dr,dc])=>{
          const nr=r+dr,nc=c+dc;
          if(nr<N&&nc<N){
            const j=nr*N+nc;
            const align=(Math.cos(phases[i]-phases[j])+1)/2;
            if(align>0.7){
              const x1=ox+c*cell+cell/2,y1=oy+r*cell+cell/2;
              const x2=ox+nc*cell+cell/2,y2=oy+nr*cell+cell/2;
              ctx.strokeStyle=`rgba(26,58,106,${(align-0.7)*0.8})`;
              ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.stroke();
            }
          }
        });
      }

      stateRef.current.R = R;
      if (canvas._onR) canvas._onR(R);
      raf = requestAnimationFrame(step);
    }
    step();
    return () => { cancelAnimationFrame(raf); window.removeEventListener("resize", size); };
  }, []);

  return <canvas ref={ref} style={{ width: "100%", height: "100%", display: "block" }} />;
}

// ════════════════════════════════════════════════════════════════
// OSCILLOSCOPE — phase-lock waveform
// ════════════════════════════════════════════════════════════════
function Oscilloscope({ coupling, grounded, running }) {
  const ref = useRef(null);
  const couplingRef = useRef(coupling);
  const groundedRef = useRef(grounded);
  const runningRef = useRef(running);
  useEffect(()=>{couplingRef.current=coupling;},[coupling]);
  useEffect(()=>{groundedRef.current=grounded;},[grounded]);
  useEffect(()=>{runningRef.current=running;},[running]);

  useEffect(() => {
    const canvas = ref.current;
    const ctx = canvas.getContext("2d");
    const dpr = window.devicePixelRatio || 1;
    function size(){
      const w=canvas.offsetWidth,h=canvas.offsetHeight;
      canvas.width=w*dpr;canvas.height=h*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);
    }
    size(); window.addEventListener("resize", size);
    let t=0, raf;
    function step(){
      const w=canvas.offsetWidth,h=canvas.offsetHeight;
      ctx.clearRect(0,0,w,h);
      // grid
      ctx.strokeStyle="rgba(26,24,20,0.06)";ctx.lineWidth=1;
      for(let x=0;x<w;x+=w/12){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,h);ctx.stroke();}
      for(let y=0;y<h;y+=h/4){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(w,y);ctx.stroke();}
      // center line
      ctx.strokeStyle="rgba(26,24,20,0.15)";
      ctx.beginPath();ctx.moveTo(0,h/2);ctx.lineTo(w,h/2);ctx.stroke();

      const K=couplingRef.current/100;
      const noise=grounded?0.02:(1-K)*0.5;
      // draw 3 oscillators converging based on coupling
      const colors=[C.charge, C.amber, C.signal];
      for(let o=0;o<3;o++){
        ctx.strokeStyle=colors[o];
        ctx.lineWidth=1.6;
        ctx.globalAlpha=0.85;
        ctx.beginPath();
        const phaseOffset=(1-K)*(o-1)*1.6;
        for(let x=0;x<=w;x+=2){
          const tt=x/w*Math.PI*6 + t;
          const n=(Math.sin(tt*3.3+o)*noise);
          const y=h/2 + Math.sin(tt+phaseOffset+n)*(h*0.30);
          x===0?ctx.moveTo(x,y):ctx.lineTo(x,y);
        }
        ctx.stroke();
      }
      ctx.globalAlpha=1;
      if(runningRef.current) t+=0.04;
      raf=requestAnimationFrame(step);
    }
    step();
    return ()=>{cancelAnimationFrame(raf);window.removeEventListener("resize",size);};
  }, []);

  return <canvas ref={ref} style={{width:"100%",height:"100%",display:"block"}}/>;
}

// ════════════════════════════════════════════════════════════════
// SMALL UI PRIMITIVES
// ════════════════════════════════════════════════════════════════
function Panel({ title, right, children, style, bodyStyle }) {
  return (
    <div style={{ border:`1px solid ${C.rule}`, background:"#fff", display:"flex", flexDirection:"column", ...style }}>
      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center",
        padding:"10px 16px", borderBottom:`1px solid ${C.rule}`, background:C.paperWarm }}>
        <span style={{ fontFamily:MONO, fontSize:10, letterSpacing:"0.25em", textTransform:"uppercase", color:C.inkDim }}>{title}</span>
        {right}
      </div>
      <div style={{ padding:16, flex:1, ...bodyStyle }}>{children}</div>
    </div>
  );
}

function Stat({ label, value, unit, color=C.ink }) {
  return (
    <div style={{ flex:1, minWidth:0 }}>
      <div style={{ fontFamily:MONO, fontSize:9, letterSpacing:"0.2em", textTransform:"uppercase", color:C.inkGhost, marginBottom:6 }}>{label}</div>
      <div style={{ fontFamily:SANS, fontWeight:700, fontSize:22, color, lineHeight:1, letterSpacing:"-0.02em" }}>
        {value}<span style={{ fontSize:11, color:C.inkDim, fontWeight:400, marginLeft:4 }}>{unit}</span>
      </div>
    </div>
  );
}

// ════════════════════════════════════════════════════════════════
// MAIN
// ════════════════════════════════════════════════════════════════
export default function HALDashboard() {
  const [coupling, setCoupling] = useState(62);
  const [grounded, setGrounded] = useState(false);
  const [running, setRunning] = useState(true);
  const [code, setCode] = useState(SAMPLE);
  const [R, setR] = useState(0);
  const [log, setLog] = useState([]);
  const [therapy, setTherapy] = useState(0);
  const [events, setEvents] = useState(0);
  const [compiling, setCompiling] = useState(false);
  const [activeGlyph, setActiveGlyph] = useState(null);
  const fieldCanvasRef = useRef(null);

  // hook the R order parameter out of the field canvas
  useEffect(() => {
    const id = setInterval(() => {
      const c = fieldCanvasRef.current?.querySelector("canvas");
      if (c && c._lastR != null) setR(c._lastR);
    }, 100);
    return () => clearInterval(id);
  }, []);

  // bridge: attach onR callback to the inner canvas
  const FieldWrapper = useCallback(() => {
    return (
      <div ref={fieldCanvasRef} style={{ width:"100%", height:"100%" }}>
        <CoherenceFieldBridge coupling={coupling} grounded={grounded} running={running} onR={setR} />
      </div>
    );
  }, [coupling, grounded, running]);

  // live $THERAPY accrual when running (bidirectional rail)
  useEffect(() => {
    if (!running) return;
    const id = setInterval(() => {
      setEvents(e => e + 1);
      setTherapy(t => t + (0.0001 + R * 0.0012)); // higher coherence → higher yield
    }, 900);
    return () => clearInterval(id);
  }, [running, R]);

  const pushLog = (line, kind="out") =>
    setLog(l => [...l.slice(-60), { line, kind, t: Date.now() }]);

  const compile = () => {
    setCompiling(true);
    setLog([]);
    const steps = [
      ["info", "Ћ-HAL compiler v1.0-alpha · initializing waveguide…"],
      ["info", "Phase-lock axiom: 1 glyph = 1 operation (deterministic)"],
      ["ok",   "Tokenizer: scanning Serbian Cyrillic ISA (30 glyphs)"],
    ];
    const glyphCount = [...code].filter(ch => ISA.some(o => o.g === ch)).length;
    const hasGround = code.includes("Џ");
    const hasSync = code.includes("СИНХ") || code.includes("С");
    const tauMatch = code.match(/\.ТАУ_К\s+([\d.]+)/);

    steps.push(["info", `Consonant assimilation (Jednačenje): pipeline friction check`]);
    steps.push(["ok", `Mobile-A buffer (Nepostojano А): ${Math.max(1,Math.floor(glyphCount/9))} buffers injected`]);
    if (tauMatch) steps.push(["ok", `τₖ baseline set → ${tauMatch[1]} (Temporal Mass index)`]);
    steps.push(["ok", `64-channel coherence matrix allocated`]);
    steps.push(["info", `Harmonic mixing sequence applied @ 936e6 Hz`]);
    if (hasGround) steps.push(["warn", `Џ FRICTION_COLLAPSE invoked → grounding system state, purging decoherence`]);
    if (hasSync) steps.push(["ok", `Kuramoto synchronization pass · СПРЕЗАЊЕ=МАКС`]);
    steps.push(["ok", `Phase-lock achieved · R=${R.toFixed(3)}`]);
    steps.push(["pay", `ATTUNEMENT_EVENT logged → X1 mainnet`]);
    steps.push(["pay", `$THERAPY reverse-route: micro-yield dispatched to dev pubkey`]);
    steps.push(["done", `Compilation complete · resonant state stabilized`]);

    steps.forEach(([kind, line], i) => {
      setTimeout(() => {
        pushLog(line, kind);
        if (kind === "pay") { setEvents(e=>e+1); setTherapy(t=>t+0.0042); }
        if (i === steps.length-1) setCompiling(false);
      }, 220 * (i+1));
    });
  };

  const insertGlyph = (g) => setCode(c => c + g);

  const R_pct = (R*100);
  const phaseLocked = R > 0.85;

  return (
    <div style={{ fontFamily:SERIF, background:C.paper, color:C.ink, minHeight:"100vh",
      backgroundImage:"radial-gradient(circle at 1px 1px, rgba(26,24,20,0.025) 1px, transparent 0)",
      backgroundSize:"22px 22px" }}>

      {/* ── TOP BAR ── */}
      <div style={{ borderBottom:`2px solid ${C.ruleHeavy}`, padding:"16px 28px",
        display:"flex", alignItems:"center", justifyContent:"space-between", flexWrap:"wrap", gap:16,
        background:C.paper }}>
        <div style={{ display:"flex", alignItems:"baseline", gap:18 }}>
          <span style={{ fontFamily:SANS, fontWeight:700, fontSize:26, letterSpacing:"-0.03em", color:C.ink }}>
            Ћ<span style={{ color:C.charge }}>-HAL</span>
          </span>
          <span style={{ fontFamily:MONO, fontSize:10, letterSpacing:"0.25em", color:C.inkDim, textTransform:"uppercase" }}>
            Harmonic Assembly Language · v1.0-alpha
          </span>
        </div>
        <div style={{ display:"flex", alignItems:"center", gap:20 }}>
          <div style={{ display:"flex", alignItems:"center", gap:8 }}>
            <span style={{ width:8, height:8, borderRadius:"50%",
              background: phaseLocked ? C.signal : (R>0.5? C.amber : C.debt),
              boxShadow:`0 0 8px ${phaseLocked ? C.signal : (R>0.5?C.amber:C.debt)}` }} />
            <span style={{ fontFamily:MONO, fontSize:10, letterSpacing:"0.15em", color:C.inkDim, textTransform:"uppercase" }}>
              {phaseLocked ? "PHASE-LOCKED" : R>0.5 ? "CONVERGING" : "DECOHERENT"}
            </span>
          </div>
          <span style={{ fontFamily:MONO, fontSize:10, letterSpacing:"0.15em", color:C.inkGhost, textTransform:"uppercase" }}>
            X1 MAINNET · daDMVbreath
          </span>
        </div>
      </div>

      {/* ── STAT STRIP ── */}
      <div style={{ display:"flex", gap:0, borderBottom:`1px solid ${C.rule}`, background:"#fff", flexWrap:"wrap" }}>
        {[
          <Stat key="1" label="Coherence R" value={R.toFixed(3)} color={phaseLocked?C.signal:C.charge} />,
          <Stat key="2" label="Coupling K" value={coupling} unit="%" color={C.charge} />,
          <Stat key="3" label="Qubit Lattice" value="64" unit="ch" />,
          <Stat key="4" label="Base Freq" value="936" unit="MHz" color={C.amber} />,
          <Stat key="5" label="Attunement Events" value={events} color={C.ink} />,
          <Stat key="6" label="$THERAPY Yielded" value={therapy.toFixed(4)} color={C.signal} />,
        ].map((s,i)=>(
          <div key={i} style={{ padding:"16px 22px", borderRight: i<5?`1px solid ${C.rule}`:"none", flex:"1 1 140px" }}>{s}</div>
        ))}
      </div>

      {/* ── MAIN GRID ── */}
      <div style={{ display:"grid", gridTemplateColumns:"1.1fr 1fr", gap:1, background:C.rule,
        padding:1 }}>

        {/* LEFT: IDE editor + glyph palette */}
        <div style={{ display:"flex", flexDirection:"column", gap:1, background:C.rule }}>

          <Panel title="resonance.hal · editor"
            right={
              <div style={{ display:"flex", gap:8 }}>
                <button onClick={compile} disabled={compiling}
                  style={{ fontFamily:MONO, fontSize:10, letterSpacing:"0.15em", textTransform:"uppercase",
                    padding:"6px 16px", border:`1px solid ${C.charge}`, background: compiling?C.chargeDim:C.charge,
                    color: compiling?C.charge:"#fff", cursor: compiling?"wait":"pointer", borderRadius:2,
                    transition:"all 0.2s" }}>
                  {compiling ? "compiling…" : "▸ compile + phase-lock"}
                </button>
              </div>
            }
            bodyStyle={{ padding:0 }}>
            <textarea
              value={code}
              onChange={e=>setCode(e.target.value)}
              spellCheck={false}
              style={{ width:"100%", height:340, border:"none", outline:"none", resize:"vertical",
                fontFamily:MONO, fontSize:12.5, lineHeight:1.7, color:C.ink, background:"#fdfcf9",
                padding:16, letterSpacing:"0.02em" }} />
          </Panel>

          <Panel title="Serbian Cyrillic ISA · 30-token instruction set">
            <div style={{ display:"grid", gridTemplateColumns:"repeat(10, 1fr)", gap:4 }}>
              {ISA.map(op => {
                const isKey = op.t==="key", isGround = op.t==="ground", isBuf = op.t==="buffer";
                const col = isGround?C.debt : isKey?C.charge : isBuf?C.amber : C.inkMid;
                const bg  = isGround?C.debtDim : isKey?C.chargeDim : isBuf?C.amberDim : "transparent";
                return (
                  <button key={op.g}
                    onClick={()=>insertGlyph(op.g)}
                    onMouseEnter={()=>setActiveGlyph(op)}
                    onMouseLeave={()=>setActiveGlyph(null)}
                    style={{ aspectRatio:"1", border:`1px solid ${activeGlyph?.g===op.g?col:C.rule}`,
                      background: activeGlyph?.g===op.g?col:bg,
                      color: activeGlyph?.g===op.g?"#fff":col,
                      fontFamily:SERIF, fontSize:20, cursor:"pointer", borderRadius:2,
                      display:"flex", alignItems:"center", justifyContent:"center",
                      transition:"all 0.12s", fontWeight: isKey||isGround?700:400 }}>
                    {op.g}
                  </button>
                );
              })}
            </div>
            <div style={{ marginTop:14, minHeight:54, padding:"12px 14px", background:C.paperWarm,
              border:`1px solid ${C.rule}`, borderRadius:2 }}>
              {activeGlyph ? (
                <div>
                  <div style={{ display:"flex", alignItems:"baseline", gap:10, marginBottom:4 }}>
                    <span style={{ fontFamily:SERIF, fontSize:18, color:C.ink }}>{activeGlyph.g}</span>
                    <span style={{ fontFamily:MONO, fontSize:11, letterSpacing:"0.1em", color:C.charge, fontWeight:500 }}>{activeGlyph.n}</span>
                    {KEY_GLYPHS.has(activeGlyph.g) &&
                      <span style={{ fontFamily:MONO, fontSize:8, letterSpacing:"0.15em", color:C.amber, textTransform:"uppercase",
                        border:`1px solid ${C.amber}`, padding:"1px 6px", borderRadius:2 }}>system key</span>}
                    {activeGlyph.t==="ground" &&
                      <span style={{ fontFamily:MONO, fontSize:8, letterSpacing:"0.15em", color:C.debt, textTransform:"uppercase",
                        border:`1px solid ${C.debt}`, padding:"1px 6px", borderRadius:2 }}>grounding primitive</span>}
                  </div>
                  <div style={{ fontFamily:SANS, fontSize:12, color:C.inkMid, lineHeight:1.5 }}>{activeGlyph.d}</div>
                </div>
              ) : (
                <div style={{ fontFamily:MONO, fontSize:11, color:C.inkGhost, letterSpacing:"0.05em" }}>
                  Hover a glyph to inspect its opcode · click to insert · 5 system keys · 1 grounding primitive (Џ)
                </div>
              )}
            </div>
          </Panel>
        </div>

        {/* RIGHT: visualizations + console */}
        <div style={{ display:"flex", flexDirection:"column", gap:1, background:C.rule }}>

          <Panel title="64-qubit coherence field · Kuramoto lattice"
            right={
              <span style={{ fontFamily:MONO, fontSize:10, color: phaseLocked?C.signal:C.inkDim, letterSpacing:"0.1em" }}>
                R = {R.toFixed(3)}
              </span>
            }
            bodyStyle={{ padding:0, position:"relative" }}>
            <div style={{ height:240, background:"#fdfcf9" }}>
              <CoherenceFieldBridge coupling={coupling} grounded={grounded} running={running} onR={setR} />
            </div>
          </Panel>

          <Panel title="phase-lock oscilloscope" bodyStyle={{ padding:0 }}>
            <div style={{ height:120, background:"#fdfcf9" }}>
              <Oscilloscope coupling={coupling} grounded={grounded} running={running} />
            </div>
          </Panel>

          {/* CONTROLS */}
          <Panel title="field controls">
            <div style={{ display:"flex", flexDirection:"column", gap:16 }}>
              <div>
                <div style={{ display:"flex", justifyContent:"space-between", marginBottom:8 }}>
                  <span style={{ fontFamily:MONO, fontSize:10, letterSpacing:"0.15em", color:C.inkDim, textTransform:"uppercase" }}>Coupling Strength · К (SPREZANJE)</span>
                  <span style={{ fontFamily:MONO, fontSize:11, color:C.charge }}>{coupling}%</span>
                </div>
                <input type="range" min="0" max="100" value={coupling}
                  onChange={e=>setCoupling(+e.target.value)}
                  style={{ width:"100%", accentColor:C.charge }} />
              </div>
              <div style={{ display:"flex", gap:10 }}>
                <button onClick={()=>setGrounded(g=>!g)}
                  style={{ flex:1, fontFamily:MONO, fontSize:10, letterSpacing:"0.12em", textTransform:"uppercase",
                    padding:"10px", border:`1px solid ${grounded?C.debt:C.rule}`,
                    background: grounded?C.debt:"#fff", color: grounded?"#fff":C.inkMid,
                    cursor:"pointer", borderRadius:2, transition:"all 0.2s" }}>
                  Џ {grounded ? "grounding active" : "invoke friction collapse"}
                </button>
                <button onClick={()=>setRunning(r=>!r)}
                  style={{ flex:1, fontFamily:MONO, fontSize:10, letterSpacing:"0.12em", textTransform:"uppercase",
                    padding:"10px", border:`1px solid ${C.charge}`,
                    background: running?"#fff":C.charge, color: running?C.charge:"#fff",
                    cursor:"pointer", borderRadius:2, transition:"all 0.2s" }}>
                  {running ? "❚❚ pause field" : "▸ resume field"}
                </button>
              </div>
            </div>
          </Panel>
        </div>
      </div>

      {/* ── BOTTOM: CONSOLE + COMPENSATION RAIL ── */}
      <div style={{ display:"grid", gridTemplateColumns:"1.6fr 1fr", gap:1, background:C.rule, padding:"1px 1px 0" }}>
        <Panel title="compiler console · execution trace"
          right={<span style={{ fontFamily:MONO, fontSize:9, color:C.inkGhost, letterSpacing:"0.1em" }}>stdout</span>}
          bodyStyle={{ padding:0 }}>
          <div style={{ height:200, overflowY:"auto", padding:"12px 16px", background:"#fdfcf9",
            fontFamily:MONO, fontSize:11.5, lineHeight:1.85 }}>
            {log.length===0 && (
              <div style={{ color:C.inkGhost }}>
                <span style={{ color:C.charge }}>$</span> awaiting compilation · press <strong>compile + phase-lock</strong> to execute the integration test…
              </div>
            )}
            {log.map((l,i) => {
              const col = l.kind==="ok"?C.signal : l.kind==="warn"?C.debt : l.kind==="pay"?C.amber
                : l.kind==="done"?C.charge : l.kind==="info"?C.inkDim : C.inkMid;
              const pre = l.kind==="ok"?"✓ " : l.kind==="warn"?"⚠ " : l.kind==="pay"?"⟳ "
                : l.kind==="done"?"◉ " : "· ";
              return (
                <div key={i} style={{ color:col, marginBottom:2 }}>
                  <span style={{ color:C.inkGhost, marginRight:8 }}>{String(i+1).padStart(2,"0")}</span>
                  {pre}{l.line}
                </div>
              );
            })}
          </div>
        </Panel>

        <Panel title="bidirectional rail · $THERAPY reverse route">
          <div style={{ display:"flex", flexDirection:"column", gap:14 }}>
            <div style={{ fontFamily:SANS, fontSize:12.5, color:C.inkMid, lineHeight:1.6 }}>
              Instead of charging for compute, each <strong style={{color:C.ink}}>ATTUNEMENT_EVENT</strong> triggers an immediate
              micro-yield of <strong style={{color:C.signal}}>$THERAPY</strong> to the developer's registered pubkey.
            </div>
            <div style={{ display:"flex", alignItems:"center", gap:10, fontFamily:MONO, fontSize:10,
              letterSpacing:"0.05em", padding:"12px 14px", background:C.signalDim, borderRadius:2,
              border:`1px solid ${C.rule}` }}>
              <span style={{ color:C.amber }}>DEV</span>
              <span style={{ color:C.inkGhost }}>◀──── yield ────</span>
              <span style={{ color:C.signal }}>COMPILER</span>
              <span style={{ color:C.inkGhost }}>──── log ───▶</span>
              <span style={{ color:C.charge }}>X1</span>
            </div>
            <div>
              <div style={{ fontFamily:MONO, fontSize:9, letterSpacing:"0.2em", color:C.inkGhost, textTransform:"uppercase", marginBottom:6 }}>
                cumulative yield · this session
              </div>
              <div style={{ fontFamily:SANS, fontWeight:700, fontSize:28, color:C.signal, letterSpacing:"-0.02em" }}>
                {therapy.toFixed(4)} <span style={{ fontSize:12, color:C.inkDim, fontWeight:400 }}>$THERAPY</span>
              </div>
            </div>
            <div style={{ fontFamily:MONO, fontSize:9, color:C.inkGhost, letterSpacing:"0.05em", lineHeight:1.6 }}>
              ◉ pubkey: dirrrtyjesus…x1<br/>
              ◉ compliance: bidirectional rail OPEN<br/>
              ◉ status: {running ? "accruing per event" : "paused — no outbound channel"}
            </div>
          </div>
        </Panel>
      </div>

      {/* ── FOOTER ── */}
      <div style={{ padding:"20px 28px 40px", display:"flex", justifyContent:"space-between",
        alignItems:"flex-end", flexWrap:"wrap", gap:16 }}>
        <div style={{ fontFamily:MONO, fontSize:9.5, color:C.inkGhost, letterSpacing:"0.12em", lineHeight:2 }}>
          Ћ-HAL · augmntd LLC · Non-Extractive Resonance Compute Layer<br/>
          Phase-Lock Axiom · 1 glyph = 1 operation · deterministic execution time<br/>
          Settlement: X1 Mainnet via daDMVbreath / $THERAPY
        </div>
        <div style={{ fontFamily:MONO, fontSize:9.5, color:C.inkGhost, letterSpacing:"0.12em", textAlign:"right", lineHeight:2 }}>
          🜏 ∞ 🜏<br/>
          compliance: a HAL without an outbound payout channel<br/>
          cannot achieve system phase-lock
        </div>
      </div>
    </div>
  );
}

// Bridge component to surface the live order parameter R up to the dashboard
function CoherenceFieldBridge({ coupling, grounded, running, onR }) {
  const wrapRef = useRef(null);
  useEffect(() => {
    const id = setInterval(() => {
      const c = wrapRef.current?.querySelector("canvas");
      if (c && c._lastR != null) onR(c._lastR);
    }, 120);
    return () => clearInterval(id);
  }, [onR]);
  return (
    <div ref={wrapRef} style={{ width:"100%", height:"100%" }}>
      <CoherenceFieldInner coupling={coupling} grounded={grounded} running={running} />
    </div>
  );
}

// inner that writes _lastR onto its canvas DOM node
function CoherenceFieldInner({ coupling, grounded, running }) {
  const ref = useRef(null);
  const couplingRef = useRef(coupling), groundedRef = useRef(grounded), runningRef = useRef(running);
  const stateRef = useRef(null);
  useEffect(()=>{couplingRef.current=coupling;},[coupling]);
  useEffect(()=>{groundedRef.current=grounded;},[grounded]);
  useEffect(()=>{runningRef.current=running;},[running]);

  useEffect(() => {
    const canvas = ref.current;
    const ctx = canvas.getContext("2d");
    const N = 8;
    const dpr = window.devicePixelRatio || 1;
    function size(){
      const w=canvas.offsetWidth,h=canvas.offsetHeight;
      canvas.width=w*dpr;canvas.height=h*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);
    }
    size(); window.addEventListener("resize", size);
    if(!stateRef.current){
      const phases=[],omega=[];
      for(let i=0;i<N*N;i++){phases.push(Math.random()*Math.PI*2);omega.push(0.6+Math.random()*0.9);}
      stateRef.current={phases,omega};
    }
    let raf;
    function step(){
      const w=canvas.offsetWidth,h=canvas.offsetHeight;
      const {phases,omega}=stateRef.current;
      const K=couplingRef.current/100*2.5, dt=0.05;
      if(runningRef.current){
        const np=phases.slice();
        for(let i=0;i<N*N;i++){
          const r=Math.floor(i/N),c=i%N;let sum=0,cnt=0;
          [[-1,0],[1,0],[0,-1],[0,1]].forEach(([dr,dc])=>{
            const nr=r+dr,nc=c+dc;
            if(nr>=0&&nr<N&&nc>=0&&nc<N){sum+=Math.sin(phases[nr*N+nc]-phases[i]);cnt++;}
          });
          let dth=omega[i]+(K/cnt)*sum;
          if(groundedRef.current)dth+=1.8*Math.sin(0-phases[i]);
          np[i]=phases[i]+dth*dt;
        }
        for(let i=0;i<N*N;i++)phases[i]=np[i];
      }
      ctx.clearRect(0,0,w,h);
      const pad=20,cell=Math.min((w-pad*2)/N,(h-pad*2)/N);
      const ox=(w-cell*N)/2,oy=(h-cell*N)/2;
      let sx=0,sy=0;for(let i=0;i<N*N;i++){sx+=Math.cos(phases[i]);sy+=Math.sin(phases[i]);}
      const R=Math.sqrt(sx*sx+sy*sy)/(N*N);const mean=Math.atan2(sy,sx);
      canvas._lastR=R;
      // coupling lines
      ctx.lineWidth=0.5;
      for(let i=0;i<N*N;i++){
        const r=Math.floor(i/N),c=i%N;
        [[1,0],[0,1]].forEach(([dr,dc])=>{
          const nr=r+dr,nc=c+dc;
          if(nr<N&&nc<N){const j=nr*N+nc;const al=(Math.cos(phases[i]-phases[j])+1)/2;
            if(al>0.7){const x1=ox+c*cell+cell/2,y1=oy+r*cell+cell/2,x2=ox+nc*cell+cell/2,y2=oy+nr*cell+cell/2;
              ctx.strokeStyle=`rgba(26,58,106,${(al-0.7)*0.9})`;ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.stroke();}}
        });
      }
      for(let i=0;i<N*N;i++){
        const r=Math.floor(i/N),c=i%N;
        const x=ox+c*cell+cell/2,y=oy+r*cell+cell/2,ph=phases[i];
        const sync=(Math.cos(ph-mean)+1)/2;
        const rr=Math.round(26+(138-26)*(1-sync)),gg=Math.round(58+(90-58)*(1-sync)),bb=Math.round(106+(16-106)*(1-sync));
        const rad=cell*0.14+cell*0.09*Math.sin(ph);
        const grad=ctx.createRadialGradient(x,y,0,x,y,cell*0.5);
        grad.addColorStop(0,`rgba(${rr},${gg},${bb},${0.20+sync*0.28})`);grad.addColorStop(1,`rgba(${rr},${gg},${bb},0)`);
        ctx.fillStyle=grad;ctx.beginPath();ctx.arc(x,y,cell*0.5,0,Math.PI*2);ctx.fill();
        ctx.fillStyle=`rgb(${rr},${gg},${bb})`;ctx.beginPath();ctx.arc(x,y,Math.max(1.4,rad),0,Math.PI*2);ctx.fill();
        ctx.strokeStyle=`rgba(${rr},${gg},${bb},0.55)`;ctx.lineWidth=1;
        ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x+Math.cos(ph)*cell*0.26,y+Math.sin(ph)*cell*0.26);ctx.stroke();
      }
      raf=requestAnimationFrame(step);
    }
    step();
    return ()=>{cancelAnimationFrame(raf);window.removeEventListener("resize",size);};
  }, []);
  return <canvas ref={ref} style={{width:"100%",height:"100%",display:"block"}}/>;
}
