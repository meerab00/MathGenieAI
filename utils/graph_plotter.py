
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import re
from langchain_core.messages import HumanMessage,SystemMessage

matplotlib.use("Agg")


def plot_graph(question: str, llm=None):
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor("#0e0e1e")
    ax.set_facecolor("#0e0e1e")
    ax.tick_params(colors="#aaaacc")
    for spine in ax.spines.values():
        spine.set_color("#333355")
    ax.xaxis.label.set_color("#aaaacc")
    ax.yaxis.label.set_color("#aaaacc")
    ax.title.set_color("#e4e4f0")

    equation = extract_equation(question, llm)

    if not equation:
        ax.text(0.5, 0.5, "Could not parse equation.\nTry: y = x^2 + 3x - 2",
                ha="center", va="center", color="#f87171", fontsize=13,
                transform=ax.transAxes)
        return fig

    try:
        x = np.linspace(-10, 10, 800)
        safe_dict = {
            "x": x, "np": np,
            "sin": np.sin, "cos": np.cos, "tan": np.tan,
            "exp": np.exp, "log": np.log, "sqrt": np.sqrt,
            "abs": np.abs, "pi": np.pi, "e": np.e,
        }
        eq = equation.replace("^", "**").replace("ln", "log")
        y = eval(eq, {"__builtins__": {}}, safe_dict)

        ax.plot(x, y, color="#7c6af7", linewidth=2.5, label=f"y = {equation}")
        ax.axhline(y=0, color="#444466", linewidth=0.8)
        ax.axvline(x=0, color="#444466", linewidth=0.8)
        ax.grid(True, color="#1e1e38", linewidth=0.7)
        ax.set_xlabel("x", fontsize=12)
        ax.set_ylabel("y", fontsize=12)
        ax.set_title(f"Graph: y = {equation}", fontsize=13, pad=12)
        ax.legend(facecolor="#111122", edgecolor="#333355", labelcolor="#e4e4f0")
        ax.set_ylim(-50, 50)
        fig.tight_layout()
        return fig

    except Exception as e:
        ax.text(0.5, 0.5, f"Plot error: {str(e)}",
                ha="center", va="center", color="#f87171", fontsize=11,
                transform=ax.transAxes)
        return fig


def extract_equation(question: str, llm=None) -> str:
    patterns = [
        r"y\s*=\s*([^\n,;]+)",
        r"f\(x\)\s*=\s*([^\n,;]+)",
        r"plot\s+([^\n,;]+)",
        r"graph\s+(?:of\s+)?([^\n,;]+)",
        r"GRAPH:\s*([^\n]+)",
    ]
    for pat in patterns:
        m = re.search(pat, question, re.IGNORECASE)
        if m:
            return m.group(1).strip()

    if llm:
        try:
            prompt = f"""Extract ONLY the right-hand side of y = f(x) from this question.
Use Python/numpy syntax. Return NONE if not plottable.
Question: {question}"""
            resp = llm.invoke([HumanMessage(content=prompt)])
            result = resp.content.strip()
            if result and result != "NONE" and len(result) < 200:
                return result
        except Exception:
            pass

    return ""
