from fpdf import FPDF
from datetime import datetime
import re

def _strip_markdown(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"^#{1,3}\s", "", text, flags=re.MULTILINE)
    return text

class MathGeniePDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(108, 99, 255)
        self.cell(0, 10, "MathGenie AI — Solution", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(150, 150, 170)
        self.cell(0, 6, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                  align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(3)
        self.set_draw_color(108, 99, 255)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 170)
        self.cell(0, 10, f"Page {self.page_no()} | MathGenie AI", align="C")

def export_chat_to_pdf(messages: list) -> bytes:
    pdf = MathGeniePDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if not isinstance(content, str):
            continue

        if role == "user":
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(255, 101, 132)
            pdf.cell(0, 7, "You:", new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(108, 99, 255)
            pdf.cell(0, 7, "MathGenie AI:", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(30, 30, 50)
        clean = _strip_markdown(content)
        try:
            pdf.multi_cell(0, 6, clean)
        except Exception:
            pdf.multi_cell(0, 6, clean.encode("latin-1", "replace").decode("latin-1"))

        pdf.ln(3)
        pdf.set_draw_color(220, 220, 235)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)

    return bytes(pdf.output())
