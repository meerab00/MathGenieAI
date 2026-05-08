import re
import numpy as np
import plotly.graph_objects as go

_GRAPH_KEYWORDS = re.compile(
    r"graph|plot|draw|sketch|f\(x\)|y\s*=|curve|parabola|function|visuali[sz]e",
    re.IGNORECASE,
)

def should_plot_graph(text: str) -> bool:
    return bool(_GRAPH_KEYWORDS.search(text or ""))

def extract_graph_expr(response: str):
    match = re.search(r"GRAPH_EXPR:\s*(.+)", response)
    return match.group(1).strip() if match else None

def plot_graph(expr: str):
    try:
        x = np.linspace(-10, 10, 600)
        safe_globals = {
            "__builtins__": {},
            "x": x, "np": np,
            "sin": np.sin, "cos": np.cos, "tan": np.tan,
            "exp": np.exp, "log": np.log, "log10": np.log10,
            "sqrt": np.sqrt, "abs": np.abs,
            "pi": np.pi, "e": np.e,
            "sinh": np.sinh, "cosh": np.cosh, "tanh": np.tanh,
            "arcsin": np.arcsin, "arccos": np.arccos, "arctan": np.arctan,
        }
        y = eval(expr, safe_globals)
        y = np.where(np.isfinite(y) & (np.abs(y) < 1e6), y, np.nan)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x, y=y, mode="lines",
            name=f"f(x) = {expr}",
            line=dict(color="#ff6584", width=2.5),
        ))
        fig.update_layout(
            title=dict(text=f"📊 Graph: f(x) = {expr}", font=dict(size=14)),
            xaxis=dict(title="x", zeroline=True, zerolinecolor="#6c63ff", gridcolor="#2a2a3a"),
            yaxis=dict(title="f(x)", zeroline=True, zerolinecolor="#6c63ff", gridcolor="#2a2a3a"),
            paper_bgcolor="#13131e", plot_bgcolor="#13131e",
            font=dict(color="#e8e8f0", family="monospace"),
            height=350, margin=dict(l=40, r=20, t=50, b=40),
        )
        return fig
    except Exception:
        return None
