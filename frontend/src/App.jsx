import { useState, useRef, useEffect } from "react";
import axios from "axios";
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
} from "recharts";

const API = "http://localhost:8000";

const css = `
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&family=JetBrains+Mono:wght@400;500&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: #0c0a06;
    color: #f5f0e8;
    font-family: 'DM Sans', sans-serif;
    min-height: 100vh;
    font-size: 15px;
  }

  /* NAV */
  .nav {
    position: sticky; top: 0; z-index: 100;
    background: rgba(12,10,6,0.85);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(255,255,255,0.07);
    padding: 0 40px;
    height: 60px;
    display: flex; align-items: center; justify-content: space-between;
  }
  .nav-logo { display: flex; align-items: center; gap: 10px; font-family: 'Syne', sans-serif; font-weight: 800; font-size: 18px; color: #f5f0e8; }
  .nav-logo-dot { width: 28px; height: 28px; background: #16a34a; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 14px; }
  .nav-links { display: flex; gap: 4px; }
  .nav-btn {
    background: none; border: none; cursor: pointer;
    font-family: 'Syne', sans-serif; font-size: 12px; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: rgba(245,240,232,0.45);
    padding: 8px 16px; border-radius: 999px;
    transition: all 0.2s;
  }
  .nav-btn:hover { color: #f5f0e8; background: rgba(255,255,255,0.06); }
  .nav-btn.active { background: #16a34a; color: #f5f0e8; }

  /* PAGE */
  .page { max-width: 1100px; margin: 0 auto; padding: 50px 40px; }

  /* PAGE HEADER */
  .page-label { font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.15em; color: #16a34a; margin-bottom: 10px; }
  .page-title { font-family: 'Syne', sans-serif; font-size: 48px; font-weight: 800; line-height: 1.05; color: #f5f0e8; margin-bottom: 14px; }
  .page-title span { color: #16a34a; }
  .page-sub { color: rgba(245,240,232,0.4); font-size: 14px; max-width: 420px; line-height: 1.6; }

  /* SCANNER LAYOUT */
  .scanner-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; margin-top: 40px; }
  @media (max-width: 768px) { .scanner-grid { grid-template-columns: 1fr; } }

  /* DROPZONE */
  .dropzone {
    border: 2px dashed rgba(255,255,255,0.15);
    border-radius: 18px;
    min-height: 300px;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer; transition: all 0.2s; overflow: hidden; position: relative;
  }
  .dropzone:hover { border-color: rgba(22,163,74,0.5); background: rgba(22,163,74,0.04); }
  .dropzone.dragging { border-color: #16a34a; background: rgba(22,163,74,0.08); transform: scale(1.01); }
  .dropzone-inner { text-align: center; padding: 40px; }
  .dropzone-icon { width: 64px; height: 64px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 28px; margin: 0 auto 16px; }
  .dropzone-title { font-family: 'Syne', sans-serif; font-weight: 600; color: rgba(245,240,232,0.6); margin-bottom: 6px; }
  .dropzone-sub { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: rgba(245,240,232,0.3); }
  .dropzone img { width: 100%; height: 100%; object-fit: cover; min-height: 300px; }

  /* BUTTON */
  .btn {
    width: 100%; padding: 16px; border-radius: 14px; border: none; cursor: pointer;
    font-family: 'Syne', sans-serif; font-weight: 700; font-size: 16px;
    letter-spacing: 0.03em; transition: all 0.2s; margin-top: 12px;
  }
  .btn-primary { background: #16a34a; color: #f5f0e8; }
  .btn-primary:hover { background: #15803d; transform: translateY(-1px); }
  .btn-primary:active { transform: scale(0.98); }
  .btn-disabled { background: rgba(255,255,255,0.06); color: rgba(245,240,232,0.25); cursor: not-allowed; }
  .btn-sm {
    width: auto; padding: 8px 16px; font-size: 13px; margin-top: 0;
    background: rgba(255,255,255,0.06); color: rgba(245,240,232,0.5); border-radius: 8px;
  }
  .btn-sm:hover { background: rgba(255,255,255,0.1); color: #f5f0e8; }

  /* LOADING SPINNER */
  .spinner { width: 18px; height: 18px; border: 2px solid rgba(245,240,232,0.2); border-top-color: #f5f0e8; border-radius: 50%; animation: spin 0.9s linear infinite; display: inline-block; vertical-align: middle; margin-right: 8px; }
  @keyframes spin { to { transform: rotate(360deg); } }

  /* ERROR */
  .error-box { background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); border-radius: 12px; padding: 14px 18px; color: #f87171; font-family: 'JetBrains Mono', monospace; font-size: 13px; margin-top: 12px; }

  /* CARD */
  .card { background: rgba(255,255,255,0.03); border-radius: 18px; padding: 24px; }
  .card-fresh { border: 1px solid rgba(34,197,94,0.25); background: rgba(20,83,45,0.15); }
  .card-rotten { border: 1px solid rgba(239,68,68,0.25); background: rgba(127,29,29,0.15); }
  .card-neutral { border: 1px solid rgba(255,255,255,0.08); }
  .card-placeholder { border: 1px dashed rgba(255,255,255,0.08); min-height: 200px; display: flex; align-items: center; justify-content: center; }

  /* RESULT CARD */
  .result-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 20px; }
  .result-label { font-family: 'JetBrains Mono', monospace; font-size: 10px; text-transform: uppercase; letter-spacing: 0.15em; color: rgba(245,240,232,0.4); margin-bottom: 6px; }
  .result-food { font-family: 'Syne', sans-serif; font-size: 32px; font-weight: 800; color: #f5f0e8; }
  .result-circle { width: 58px; height: 58px; border-radius: 50%; border: 2px solid; display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: 700; flex-shrink: 0; }
  .result-circle-fresh { border-color: #22c55e; color: #22c55e; animation: pulse-fresh 2s ease infinite; }
  .result-circle-rotten { border-color: #ef4444; color: #ef4444; animation: pulse-rotten 2s ease infinite; }
  @keyframes pulse-fresh { 0%,100%{box-shadow:0 0 0 0 rgba(34,197,94,0.4)} 50%{box-shadow:0 0 0 10px rgba(34,197,94,0)} }
  @keyframes pulse-rotten { 0%,100%{box-shadow:0 0 0 0 rgba(239,68,68,0.4)} 50%{box-shadow:0 0 0 10px rgba(239,68,68,0)} }

  .badges { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 20px; }
  .badge { padding: 4px 12px; border-radius: 999px; font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.08em; }
  .badge-fresh { background: rgba(34,197,94,0.12); color: #22c55e; border: 1px solid rgba(34,197,94,0.25); }
  .badge-rotten { background: rgba(239,68,68,0.12); color: #ef4444; border: 1px solid rgba(239,68,68,0.25); }
  .badge-conf { color: rgba(245,240,232,0.4); font-family: 'JetBrains Mono', monospace; font-size: 12px; }
  .badge-warn { color: rgba(250,204,21,0.7); font-size: 12px; font-family: 'JetBrains Mono', monospace; }

  .metrics { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px; }
  .metric { background: rgba(255,255,255,0.04); border-radius: 12px; padding: 14px 16px; }
  .metric-label { font-family: 'JetBrains Mono', monospace; font-size: 10px; text-transform: uppercase; letter-spacing: 0.12em; color: rgba(245,240,232,0.35); margin-bottom: 6px; }
  .metric-value { font-family: 'Syne', sans-serif; font-size: 24px; font-weight: 800; color: #f5f0e8; }
  .metric-unit { font-size: 13px; font-weight: 400; color: rgba(245,240,232,0.35); margin-left: 4px; font-family: 'DM Sans', sans-serif; }

  .freshness-bar-row { display: flex; justify-content: space-between; font-family: 'JetBrains Mono', monospace; font-size: 11px; color: rgba(245,240,232,0.4); margin-bottom: 8px; }
  .freshness-bar-bg { height: 6px; background: rgba(255,255,255,0.08); border-radius: 999px; overflow: hidden; margin-bottom: 20px; }
  .freshness-bar-fill { height: 100%; border-radius: 999px; transition: width 1s ease; }

  .tips-box { border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 16px; }
  .tips-label { font-family: 'JetBrains Mono', monospace; font-size: 10px; text-transform: uppercase; letter-spacing: 0.15em; color: rgba(245,240,232,0.4); margin-bottom: 10px; }
  .tips-main { color: #f5f0e8; font-size: 14px; line-height: 1.6; margin-bottom: 8px; }
  .tips-row { color: rgba(245,240,232,0.5); font-size: 12px; line-height: 1.6; }

  /* GRADCAM */
  .gradcam-box { border: 1px solid rgba(255,255,255,0.08); border-radius: 18px; padding: 20px; margin-top: 16px; }
  .gradcam-box img { width: 100%; border-radius: 10px; }

  /* RECIPES */
  .recipes-box { border: 1px solid rgba(255,255,255,0.08); border-radius: 18px; padding: 24px; margin-top: 24px; background: rgba(255,255,255,0.02); }
  .recipe-item { border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; overflow: hidden; margin-bottom: 10px; }
  .recipe-header { display: flex; align-items: center; justify-content: space-between; padding: 14px 18px; cursor: pointer; transition: background 0.15s; }
  .recipe-header:hover { background: rgba(255,255,255,0.04); }
  .recipe-name { font-family: 'Syne', sans-serif; font-weight: 600; color: #f5f0e8; font-size: 15px; }
  .recipe-meta { display: flex; gap: 12px; margin-top: 4px; }
  .recipe-meta span { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: rgba(245,240,232,0.35); }
  .recipe-arrow { color: rgba(245,240,232,0.3); font-size: 16px; transition: transform 0.2s; }
  .recipe-body { padding: 0 18px 16px; border-top: 1px solid rgba(255,255,255,0.06); }
  .recipe-section-label { font-family: 'JetBrains Mono', monospace; font-size: 10px; text-transform: uppercase; letter-spacing: 0.12em; color: rgba(245,240,232,0.35); margin: 14px 0 8px; }
  .ingredients { display: flex; flex-wrap: wrap; gap: 6px; }
  .ingredient { padding: 4px 10px; background: rgba(22,163,74,0.12); color: #86efac; font-size: 12px; border-radius: 999px; border: 1px solid rgba(22,163,74,0.2); }
  .steps { list-style: none; }
  .steps li { display: flex; gap: 12px; font-size: 13px; color: rgba(245,240,232,0.75); line-height: 1.6; margin-bottom: 8px; }
  .step-num { font-family: 'JetBrains Mono', monospace; color: #16a34a; font-weight: 500; flex-shrink: 0; }
  .recipe-why { color: rgba(245,240,232,0.35); font-size: 12px; font-style: italic; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 10px; margin-top: 10px; }

  /* HISTORY */
  .filters { display: flex; gap: 10px; margin: 30px 0 20px; flex-wrap: wrap; }
  .input { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 9px 16px; color: #f5f0e8; font-family: 'JetBrains Mono', monospace; font-size: 13px; outline: none; transition: border-color 0.2s; }
  .input:focus { border-color: rgba(22,163,74,0.5); }
  .input::placeholder { color: rgba(245,240,232,0.25); }
  select.input { cursor: pointer; }

  .table-wrap { border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; overflow: hidden; }
  table { width: 100%; border-collapse: collapse; }
  thead tr { background: rgba(255,255,255,0.04); border-bottom: 1px solid rgba(255,255,255,0.08); }
  th { padding: 12px 16px; text-align: left; font-family: 'JetBrains Mono', monospace; font-size: 10px; text-transform: uppercase; letter-spacing: 0.12em; color: rgba(245,240,232,0.35); font-weight: 400; }
  td { padding: 14px 16px; border-bottom: 1px solid rgba(255,255,255,0.04); }
  tbody tr:hover { background: rgba(255,255,255,0.03); }
  tbody tr:last-child td { border-bottom: none; }
  .td-food { font-family: 'Syne', sans-serif; font-weight: 600; color: #f5f0e8; font-size: 15px; }
  .td-mono { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: rgba(245,240,232,0.5); }
  .td-del { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: rgba(245,240,232,0.2); cursor: pointer; background: none; border: none; transition: color 0.2s; }
  .td-del:hover { color: #ef4444; }

  .mini-bar-bg { width: 60px; height: 4px; background: rgba(255,255,255,0.08); border-radius: 999px; overflow: hidden; display: inline-block; vertical-align: middle; margin-right: 6px; }
  .mini-bar-fill { height: 100%; border-radius: 999px; }

  .pagination { display: flex; align-items: center; justify-content: center; gap: 10px; margin-top: 24px; }
  .page-btn { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 8px 18px; color: rgba(245,240,232,0.5); font-family: 'JetBrains Mono', monospace; font-size: 13px; cursor: pointer; transition: all 0.15s; }
  .page-btn:hover:not(:disabled) { color: #f5f0e8; background: rgba(255,255,255,0.08); }
  .page-btn:disabled { opacity: 0.3; cursor: not-allowed; }
  .page-info { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: rgba(245,240,232,0.35); }

  /* ANALYTICS */
  .stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 36px; }
  @media (max-width: 768px) { .stat-grid { grid-template-columns: repeat(2,1fr); } }
  .stat-box { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 22px; }
  .stat-label { font-family: 'JetBrains Mono', monospace; font-size: 10px; text-transform: uppercase; letter-spacing: 0.12em; color: rgba(245,240,232,0.35); margin-bottom: 10px; }
  .stat-value { font-family: 'Syne', sans-serif; font-size: 38px; font-weight: 800; color: #f5f0e8; line-height: 1; }
  .stat-sub { font-size: 12px; color: rgba(245,240,232,0.35); margin-top: 6px; font-family: 'JetBrains Mono', monospace; }

  .charts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
  @media (max-width: 768px) { .charts-grid { grid-template-columns: 1fr; } }
  .chart-box { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 24px; }
  .chart-label { font-family: 'JetBrains Mono', monospace; font-size: 10px; text-transform: uppercase; letter-spacing: 0.15em; color: rgba(245,240,232,0.4); margin-bottom: 20px; }
  .chart-legend { display: flex; justify-content: center; gap: 20px; margin-top: 12px; }
  .legend-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 6px; }
  .legend-text { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: rgba(245,240,232,0.4); }

  .expiring-box { background: rgba(120,53,15,0.2); border: 1px solid rgba(251,191,36,0.2); border-radius: 16px; padding: 24px; margin-top: 20px; }
  .expiring-label { font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.12em; color: rgba(250,204,21,0.6); margin-bottom: 16px; }
  .expiring-item { display: flex; align-items: center; justify-content: space-between; border: 1px solid rgba(255,255,255,0.07); border-radius: 10px; padding: 12px 16px; margin-bottom: 8px; background: rgba(0,0,0,0.2); }
  .expiring-food { font-family: 'Syne', sans-serif; font-weight: 600; color: #f5f0e8; }
  .expiring-rec { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: rgba(245,240,232,0.35); margin-top: 2px; }
  .expiring-days-urgent { font-family: 'JetBrains Mono', monospace; font-size: 14px; font-weight: 500; color: #ef4444; }
  .expiring-days-warn { font-family: 'JetBrains Mono', monospace; font-size: 14px; font-weight: 500; color: #facc15; }

  /* EMPTY / LOADING */
  .centered { display: flex; align-items: center; justify-content: center; min-height: 300px; }
  .empty-text { font-family: 'JetBrains Mono', monospace; font-size: 13px; color: rgba(245,240,232,0.2); }
  .big-spinner { width: 40px; height: 40px; border: 2px solid rgba(255,255,255,0.08); border-top-color: #16a34a; border-radius: 50%; animation: spin 0.9s linear infinite; }
`;

// ─── COMPONENTS ─────────────────────────────────────────────

function ResultCard({ result }) {
  const fresh = result.status === "Fresh";
  const hex   = fresh ? "#22c55e" : "#ef4444";
  return (
    <div className={`card ${fresh ? "card-fresh" : "card-rotten"}`}>
      <div className="result-header">
        <div>
          <div className="result-label">Detected</div>
          <div className="result-food">{result.food}</div>
        </div>
        <div className={`result-circle ${fresh ? "result-circle-fresh" : "result-circle-rotten"}`}>
          {fresh ? "✓" : "✕"}
        </div>
      </div>

      <div className="badges">
        <span className={`badge ${fresh ? "badge-fresh" : "badge-rotten"}`}>{result.status}</span>
        <span className="badge-conf">{result.confidence_percent}% confidence</span>
        {result.note && <span className="badge-warn">⚠ {result.note}</span>}
      </div>

      <div className="metrics">
        {[
          { label: "Freshness",  value: result.freshness_score,  unit: "/ 100" },
          { label: "Days Left",  value: result.days_to_spoil,    unit: "days" },
          { label: "Scan ID",    value: result.scan_id.slice(0,8), unit: "..." },
        ].map(({ label, value, unit }) => (
          <div className="metric" key={label}>
            <div className="metric-label">{label}</div>
            <div className="metric-value">{value}<span className="metric-unit">{unit}</span></div>
          </div>
        ))}
      </div>

      <div className="freshness-bar-row">
        <span>Freshness Score</span><span>{result.freshness_score} / 100</span>
      </div>
      <div className="freshness-bar-bg">
        <div className="freshness-bar-fill" style={{ width: `${result.freshness_score}%`, background: hex }} />
      </div>

      {result.storage_tips && (
        <div className="tips-box">
          <div className="tips-label">Storage Tips</div>
          <div className="tips-main">{result.storage_tips.short}</div>
          {result.storage_tips.temperature && <div className="tips-row">🌡 {result.storage_tips.temperature}</div>}
          {result.storage_tips.avoid       && <div className="tips-row">⚠ {result.storage_tips.avoid}</div>}
          {result.storage_tips.tip         && <div className="tips-row">💡 {result.storage_tips.tip}</div>}
        </div>
      )}
    </div>
  );
}

function RecipeCard({ recipes, food }) {
  const [open, setOpen] = useState(null);
  if (!recipes?.length) return null;
  return (
    <div className="recipes-box">
      <div className="tips-label" style={{ marginBottom: 16 }}>Recipes for {food}</div>
      {recipes.map((r, i) => (
        <div className="recipe-item" key={i}>
          <div className="recipe-header" onClick={() => setOpen(open === i ? null : i)}>
            <div>
              <div className="recipe-name">{r.name}</div>
              <div className="recipe-meta">
                <span>⏱ {r.time}</span>
                <span>📊 {r.difficulty}</span>
              </div>
            </div>
            <span className="recipe-arrow" style={{ transform: open === i ? "rotate(180deg)" : "none" }}>↓</span>
          </div>
          {open === i && (
            <div className="recipe-body">
              <div className="recipe-section-label">Ingredients</div>
              <div className="ingredients">
                {r.ingredients.map((ing, j) => <span className="ingredient" key={j}>{ing}</span>)}
              </div>
              <div className="recipe-section-label">Steps</div>
              <ol className="steps">
                {r.steps.map((s, j) => (
                  <li key={j}><span className="step-num">{j + 1}.</span><span>{s}</span></li>
                ))}
              </ol>
              {r.why && <div className="recipe-why">💡 {r.why}</div>}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// ─── PAGES ──────────────────────────────────────────────────

function Scanner() {
  const [file, setFile]         = useState(null);
  const [preview, setPreview]   = useState(null);
  const [result, setResult]     = useState(null);
  const [recipes, setRecipes]   = useState(null);
  const [gradcam, setGradcam]   = useState(null);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState(null);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef();

  function handleFile(f) {
    if (!f) return;
    setFile(f); setPreview(URL.createObjectURL(f));
    setResult(null); setRecipes(null); setGradcam(null); setError(null);
  }

  async function analyze() {
    if (!file) return;
    setLoading(true); setError(null);
    try {
      const form = new FormData();
      form.append("file", file);
      const { data } = await axios.post(`${API}/predict`, form);
      setResult(data);
      setGradcam(`${API}/uploads/${data.scan_id}.png`);
      try {
        const { data: rec } = await axios.get(`${API}/recipes/${data.food.toLowerCase()}`);
        setRecipes(rec.recipes);
      } catch (_) {}
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong. Is the API running on port 8000?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <div className="page-label">Food Analysis</div>
      <h1 className="page-title">Scan your<br /><span>produce.</span></h1>
      <p className="page-sub">Upload an image of any fruit or vegetable to get freshness status, shelf life estimate, and recipe ideas.</p>

      <div className="scanner-grid">
        <div>
          <div
            className={`dropzone${dragging ? " dragging" : ""}`}
            onClick={() => inputRef.current.click()}
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={(e) => { e.preventDefault(); setDragging(false); handleFile(e.dataTransfer.files[0]); }}
          >
            <input ref={inputRef} type="file" accept="image/*" style={{ display: "none" }} onChange={(e) => handleFile(e.target.files[0])} />
            {preview
              ? <img src={preview} alt="preview" />
              : <div className="dropzone-inner">
                  <div className="dropzone-icon">📷</div>
                  <div className="dropzone-title">Drop image here</div>
                  <div className="dropzone-sub">or click to browse · JPG, PNG, WEBP</div>
                </div>
            }
          </div>
          <button
            className={`btn ${file && !loading ? "btn-primary" : "btn-disabled"}`}
            onClick={analyze}
            disabled={!file || loading}
          >
            {loading ? <><span className="spinner" />Analyzing...</> : "Analyze"}
          </button>
          {error && <div className="error-box">✕ {error}</div>}
        </div>

        <div>
          {result
            ? <ResultCard result={result} />
            : <div className="card card-neutral card-placeholder">
                <span className="empty-text">Results will appear here</span>
              </div>
          }
          {gradcam && result && (
            <div className="gradcam-box" style={{ marginTop: 16 }}>
              <div className="tips-label" style={{ marginBottom: 12 }}>Model Attention (Grad-CAM)</div>
              <img src={gradcam} alt="Grad-CAM" onError={() => setGradcam(null)} />
            </div>
          )}
        </div>
      </div>

      {recipes && result && <RecipeCard recipes={recipes} food={result.food} />}
    </div>
  );
}

function History() {
  const [scans, setScans]   = useState([]);
  const [total, setTotal]   = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState(null);
  const [food, setFood]     = useState("");
  const [status, setStatus] = useState("");
  const [page, setPage]     = useState(0);
  const limit = 10;

  useEffect(() => { fetch(); }, [food, status, page]);

  async function fetch() {
    setLoading(true);
    try {
      const params = { limit, offset: page * limit };
      if (food)   params.food   = food;
      if (status) params.status = status;
      const { data } = await axios.get(`${API}/history`, { params });
      setScans(data.scans); setTotal(data.total);
    } catch { setError("Could not load history."); }
    finally { setLoading(false); }
  }

  async function del(id) {
    await axios.delete(`${API}/history/${id}`);
    fetch();
  }

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="page">
      <div className="page-label">Scan Records</div>
      <h1 className="page-title">History</h1>
      <p className="page-sub" style={{ color: "rgba(245,240,232,0.35)" }}>{total} total scans</p>

      <div className="filters">
        <input className="input" placeholder="Filter by food..." value={food}
          onChange={(e) => { setFood(e.target.value); setPage(0); }} />
        <select className="input" value={status} onChange={(e) => { setStatus(e.target.value); setPage(0); }}>
          <option value="">All Status</option>
          <option value="Fresh">Fresh</option>
          <option value="Rotten">Rotten</option>
        </select>
        {(food || status) && (
          <button className="btn btn-sm" onClick={() => { setFood(""); setStatus(""); setPage(0); }}>Clear</button>
        )}
      </div>

      {error ? <div className="error-box">{error}</div>
      : loading ? <div className="centered"><div className="big-spinner" /></div>
      : scans.length === 0 ? <div className="centered"><span className="empty-text">No scans found.</span></div>
      : <>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                {["Food","Status","Confidence","Freshness","Days Left","Date",""].map(h => <th key={h}>{h}</th>)}
              </tr>
            </thead>
            <tbody>
              {scans.map(s => {
                const fresh = s.status === "Fresh";
                const hex   = fresh ? "#22c55e" : "#ef4444";
                return (
                  <tr key={s.id}>
                    <td className="td-food">{s.food}</td>
                    <td><span className={`badge ${fresh ? "badge-fresh" : "badge-rotten"}`}>{s.status}</span></td>
                    <td className="td-mono">{s.confidence_percent}%</td>
                    <td>
                      <div style={{ display: "flex", alignItems: "center" }}>
                        <div className="mini-bar-bg"><div className="mini-bar-fill" style={{ width: `${s.freshness_score}%`, background: hex }} /></div>
                        <span className="td-mono">{s.freshness_score}</span>
                      </div>
                    </td>
                    <td className="td-mono">{s.days_to_spoil}d</td>
                    <td className="td-mono">{new Date(s.created_at).toLocaleDateString()}</td>
                    <td><button className="td-del" onClick={() => del(s.id)}>Delete</button></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        {totalPages > 1 && (
          <div className="pagination">
            <button className="page-btn" disabled={page === 0} onClick={() => setPage(p => p - 1)}>← Prev</button>
            <span className="page-info">{page + 1} / {totalPages}</span>
            <button className="page-btn" disabled={page >= totalPages - 1} onClick={() => setPage(p => p + 1)}>Next →</button>
          </div>
        )}
      </>}
    </div>
  );
}

function Analytics() {
  const [stats, setStats]     = useState(null);
  const [history, setHistory] = useState([]);
  const [expiring, setExpiring] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      axios.get(`${API}/stats`),
      axios.get(`${API}/history`, { params: { limit: 200 } }),
      axios.get(`${API}/recipes/expiring`),
    ]).then(([s, h, e]) => {
      setStats(s.data); setHistory(h.data.scans); setExpiring(e.data.suggestions);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="centered" style={{ minHeight: "60vh" }}><div className="big-spinner" /></div>;
  if (!stats)  return <div className="centered"><span className="empty-text">Could not load analytics.</span></div>;

  const pieData = [
    { name: "Fresh",  value: stats.fresh_count },
    { name: "Rotten", value: stats.rotten_count },
  ];

  const foodFreq = {};
  history.forEach(s => s.food && (foodFreq[s.food] = (foodFreq[s.food] || 0) + 1));
  const barData = Object.entries(foodFreq).map(([food, count]) => ({ food, count }))
    .sort((a, b) => b.count - a.count).slice(0, 8);

  const pct = (n) => stats.total_scans ? Math.round(n / stats.total_scans * 100) : 0;

  return (
    <div className="page">
      <div className="page-label">Insights</div>
      <h1 className="page-title">Analytics</h1>

      <div className="stat-grid">
        {[
          { label: "Total Scans",   value: stats.total_scans,   sub: null },
          { label: "Fresh",         value: stats.fresh_count,   sub: `${pct(stats.fresh_count)}% of scans` },
          { label: "Rotten",        value: stats.rotten_count,  sub: `${pct(stats.rotten_count)}% of scans` },
          { label: "Avg Days Left", value: stats.avg_days_left, sub: "for fresh items" },
        ].map(({ label, value, sub }) => (
          <div className="stat-box" key={label}>
            <div className="stat-label">{label}</div>
            <div className="stat-value">{value}</div>
            {sub && <div className="stat-sub">{sub}</div>}
          </div>
        ))}
      </div>

      <div className="charts-grid">
        <div className="chart-box">
          <div className="chart-label">Fresh vs Rotten</div>
          {stats.total_scans === 0
            ? <div className="centered"><span className="empty-text">No data yet</span></div>
            : <>
              <ResponsiveContainer width="100%" height={180}>
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={4} dataKey="value">
                    <Cell fill="#22c55e" />
                    <Cell fill="#ef4444" />
                  </Pie>
                  <Tooltip contentStyle={{ background: "#1a1208", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, color: "#f5f0e8", fontFamily: "JetBrains Mono" }} />
                </PieChart>
              </ResponsiveContainer>
              <div className="chart-legend">
                {pieData.map((d, i) => (
                  <span className="legend-text" key={d.name}>
                    <span className="legend-dot" style={{ background: i === 0 ? "#22c55e" : "#ef4444" }} />
                    {d.name}: {d.value}
                  </span>
                ))}
              </div>
            </>
          }
        </div>

        <div className="chart-box">
          <div className="chart-label">Most Scanned Foods</div>
          {barData.length === 0
            ? <div className="centered"><span className="empty-text">No data yet</span></div>
            : <ResponsiveContainer width="100%" height={200}>
                <BarChart data={barData} margin={{ top: 0, right: 0, bottom: 0, left: -20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="food" tick={{ fill: "rgba(245,240,232,0.35)", fontSize: 10, fontFamily: "JetBrains Mono" }} />
                  <YAxis tick={{ fill: "rgba(245,240,232,0.35)", fontSize: 10, fontFamily: "JetBrains Mono" }} />
                  <Tooltip contentStyle={{ background: "#1a1208", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, color: "#f5f0e8", fontFamily: "JetBrains Mono" }} />
                  <Bar dataKey="count" fill="#22c55e" radius={[4, 4, 0, 0]} opacity={0.85} />
                </BarChart>
              </ResponsiveContainer>
          }
        </div>
      </div>

      {expiring.length > 0 && (
        <div className="expiring-box">
          <div className="expiring-label">⚠ Use These Soon — {expiring.length} item{expiring.length > 1 ? "s" : ""} expiring within 3 days</div>
          {expiring.map((item, i) => (
            <div className="expiring-item" key={i}>
              <div>
                <div className="expiring-food">{item.food}</div>
                <div className="expiring-rec">{item.recipes.length} recipe{item.recipes.length > 1 ? "s" : ""} available</div>
              </div>
              <span className={item.days_to_spoil <= 1 ? "expiring-days-urgent" : "expiring-days-warn"}>
                {item.days_to_spoil === 0 ? "Today!" : `${item.days_to_spoil}d left`}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── APP ────────────────────────────────────────────────────

export default function App() {
  const [page, setPage] = useState("scanner");

  return (
    <>
      <style>{css}</style>
      <nav className="nav">
        <div className="nav-logo">
          <div className="nav-logo-dot">🥬</div>
          FreshScan
        </div>
        <div className="nav-links">
          {["scanner", "history", "analytics"].map(p => (
            <button key={p} className={`nav-btn${page === p ? " active" : ""}`} onClick={() => setPage(p)}>
              {p.charAt(0).toUpperCase() + p.slice(1)}
            </button>
          ))}
        </div>
      </nav>
      {page === "scanner"   && <Scanner />}
      {page === "history"   && <History />}
      {page === "analytics" && <Analytics />}
    </>
  );
}
