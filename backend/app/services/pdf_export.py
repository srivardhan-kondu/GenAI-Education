import io
import logging
from typing import List

from fpdf import FPDF

logger = logging.getLogger(__name__)


class EduGenPDF(FPDF):
    """Custom PDF class for EduGen AI study notes."""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "EduGen AI  |  Study Notes", align="R")
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def add_title(self, title: str, difficulty: str = ""):
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(30, 30, 80)
        self.cell(0, 14, self._safe(title), new_x="LMARGIN", new_y="NEXT")
        if difficulty:
            self.set_font("Helvetica", "", 11)
            self.set_text_color(100, 100, 100)
            self.cell(0, 8, f"Difficulty: {difficulty.capitalize()}", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)
        # Divider line
        self.set_draw_color(79, 70, 229)  # indigo-600
        self.set_line_width(0.6)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)

    def add_section(self, heading: str, content: str = "", items: list = None):
        # Section heading
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(79, 70, 229)
        self.cell(0, 10, self._safe(heading), new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

        # Content paragraph
        if content:
            self.set_font("Helvetica", "", 10)
            self.set_text_color(40, 40, 40)
            self.multi_cell(0, 6, self._safe(content))
            self.ln(4)

        # Bullet items
        if items:
            self.set_font("Helvetica", "", 10)
            self.set_text_color(40, 40, 40)
            for i, item in enumerate(items, 1):
                self.cell(6)  # indent
                self.multi_cell(0, 6, self._safe(f"{i}. {item}"))
                self.ln(1)
            self.ln(4)

    def add_cornell_notes(self, cue_column: list, summary: str):
        """Render Cornell Notes format with cue/notes pairs."""
        # Table header
        self.set_font("Helvetica", "B", 10)
        self.set_fill_color(238, 242, 255)  # indigo-50
        self.set_text_color(30, 30, 80)
        self.cell(55, 8, "  Cue / Question", border=1, fill=True)
        self.cell(0, 8, "  Notes", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

        # Rows
        self.set_font("Helvetica", "", 9)
        self.set_text_color(40, 40, 40)
        for pair in cue_column:
            cue = self._safe(pair.get("cue", ""))
            notes = self._safe(pair.get("notes", ""))

            # Calculate row height based on content
            cue_lines = max(1, len(cue) // 25 + 1)
            notes_lines = max(1, len(notes) // 55 + 1)
            row_h = max(cue_lines, notes_lines) * 6

            x = self.get_x()
            y = self.get_y()

            # Check for page break
            if y + row_h > 270:
                self.add_page()
                y = self.get_y()

            self.set_font("Helvetica", "B", 9)
            self.set_xy(x, y)
            self.multi_cell(55, 6, cue, border="LR")
            cue_end_y = self.get_y()

            self.set_font("Helvetica", "", 9)
            self.set_xy(x + 55, y)
            self.multi_cell(0, 6, notes, border="R")
            notes_end_y = self.get_y()

            final_y = max(cue_end_y, notes_end_y)
            # Bottom border for row
            self.line(x, final_y, 200, final_y)
            self.set_y(final_y)

        self.ln(6)

        # Summary box
        if summary:
            self.set_font("Helvetica", "B", 11)
            self.set_text_color(79, 70, 229)
            self.cell(0, 8, "Summary", new_x="LMARGIN", new_y="NEXT")
            self.set_font("Helvetica", "", 10)
            self.set_text_color(40, 40, 40)
            self.set_fill_color(248, 250, 252)  # slate-50
            self.multi_cell(0, 6, self._safe(summary), fill=True)

    def add_flashcards(self, flashcards: list):
        """Render flashcards as numbered Q&A pairs."""
        for i, card in enumerate(flashcards, 1):
            q = self._safe(card.get("question", ""))
            a = self._safe(card.get("answer", ""))

            # Check for page break
            if self.get_y() > 255:
                self.add_page()

            # Question
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(79, 70, 229)
            self.multi_cell(0, 6, f"Q{i}: {q}")
            self.ln(1)

            # Answer
            self.set_font("Helvetica", "", 10)
            self.set_text_color(40, 40, 40)
            self.set_fill_color(248, 250, 252)
            self.multi_cell(0, 6, f"A: {a}", fill=True)
            self.ln(4)

    @staticmethod
    def _safe(text: str) -> str:
        """Ensure text is safe for latin-1 PDF encoding."""
        if not text:
            return ""
        return text.encode("latin-1", errors="replace").decode("latin-1")


class PDFExportService:
    """Generates downloadable PDF study notes."""

    def generate_structured_pdf(self, notes_data: dict) -> bytes:
        """Generate a structured study notes PDF."""
        pdf = EduGenPDF()
        pdf.alias_nb_pages()
        pdf.add_page()

        pdf.add_title(notes_data["topic"], notes_data.get("difficulty_level", ""))

        for section in notes_data.get("sections", []):
            pdf.add_section(
                heading=section.get("heading", ""),
                content=section.get("content", ""),
                items=section.get("items"),
            )

        return pdf.output()

    def generate_cornell_pdf(self, notes_data: dict) -> bytes:
        """Generate a Cornell Notes PDF."""
        pdf = EduGenPDF()
        pdf.alias_nb_pages()
        pdf.add_page()

        pdf.add_title(
            f"{notes_data['topic']} — Cornell Notes",
            notes_data.get("difficulty_level", ""),
        )

        pdf.add_cornell_notes(
            notes_data.get("cue_column", []),
            notes_data.get("summary", ""),
        )

        return pdf.output()

    def generate_flashcards_pdf(self, notes_data: dict) -> bytes:
        """Generate a flashcards PDF."""
        pdf = EduGenPDF()
        pdf.alias_nb_pages()
        pdf.add_page()

        pdf.add_title(f"{notes_data['topic']} — Flashcards")
        pdf.add_flashcards(notes_data.get("flashcards", []))

        return pdf.output()


pdf_export_service = PDFExportService()
