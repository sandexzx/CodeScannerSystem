import logging
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Tuple, Sequence, Optional

PLACEHOLDER_PATTERN = re.compile(r"{{\s*([A-Za-z0-9_]+)\s*}}")


class RawTSPL(str):
    """Marker class used to inject raw TSPL blocks without sanitising quotes."""


ITEM_START_Y = 185
ITEM_STEP = 45
FOOTER_LINE_GAP = 20
FOOTER_LINE_HEIGHT = 25


def _sanitize_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, RawTSPL):
        return str(value)
    text = str(value)
    # TSPL strings use double quotes, so swap them to single quotes to avoid breaking the template
    return text.replace('"', "'")


def _escape_text(value: object, *, max_length: Optional[int] = None) -> str:
    """Convert arbitrary value to TSPL-safe text."""
    text = "" if value is None else str(value)
    if max_length is not None and max_length > 0 and len(text) > max_length:
        truncate_at = max(0, max_length - 3)
        text = text[:truncate_at] + "..."
    return text.replace('"', "'")


def _build_item_blocks(codes: Sequence[str]) -> RawTSPL:
    """Produce TSPL commands for the list of codes with checkboxes."""
    if not codes:
        placeholder = _escape_text("Box is empty. No data")
        y = ITEM_START_Y
        lines = [
            f'TEXT 30,{y},"0",0,2,2,"{placeholder}"',
            f"BAR 30,{y + 30},380,2"
        ]
        return RawTSPL("\n".join(lines))

    lines = []
    for idx, raw_code in enumerate(codes):
        y = ITEM_START_Y + idx * ITEM_STEP
        code = _escape_text(raw_code, max_length=28)
        prefix = f"{idx + 1:02d}. "
        lines.append(f"BOX 30,{y},60,{y + 30},2")
        lines.append(f'TEXT 90,{y + 5},"0",0,2,2,"{prefix}{code}"')
        lines.append(f"BAR 90,{y + 35},320,2")

    return RawTSPL("\n".join(lines))


def _build_footer_block(count: object, notes: Sequence[str], items_count: int) -> RawTSPL:
    """Create TSPL commands for footer section with summarising lines."""
    safe_notes = [_escape_text(note, max_length=46) for note in notes if str(note).strip()]

    items_height = max(items_count, 1) * ITEM_STEP
    bar_y = ITEM_START_Y + items_height
    text_start = bar_y + FOOTER_LINE_GAP

    lines = [f"BAR 30,{bar_y},380,2"]

    if not safe_notes:
        safe_notes = [_escape_text(f"Total items: {count}"), _escape_text("Signature: ___________")]

    for idx, note in enumerate(safe_notes):
        y = text_start + idx * FOOTER_LINE_HEIGHT
        lines.append(f'TEXT 30,{y},"0",0,1,1,"{note}"')

    return RawTSPL("\n".join(lines))


def prepare_label_data(
    *,
    title: str,
    date: str,
    time: str,
    batch: str,
    plu: str,
    box_number: object,
    count: object,
    session: str,
    codes: Optional[Sequence[str]] = None,
    notes: Optional[Sequence[str]] = None,
    extra_fields: Optional[Dict[str, object]] = None,
) -> Dict[str, object]:
    """Build a label data dictionary ready for template rendering."""

    codes_list = list(codes or [])
    count_text = _escape_text(count)
    default_notes = [
        f"Total items: {count_text or '0'}",
        f"Printed: {date} {time}".strip()
    ]
    final_notes = notes if notes is not None and list(notes) else default_notes

    data: Dict[str, object] = {
        'TITLE': _escape_text(title or "GROUP LABEL"),
        'DATE': _escape_text(date),
        'TIME': _escape_text(time),
        'BATCH': _escape_text(batch),
        'PLU': _escape_text(plu),
        'BOX_NUMBER': _escape_text(box_number),
        'COUNT': count_text,
        'SESSION': _escape_text(session),
        'ITEM_LINES': _build_item_blocks(codes_list),
        'FOOTER_LINES': _build_footer_block(count_text, final_notes, len(codes_list)),
    }

    if extra_fields:
        for key, value in extra_fields.items():
            data[key] = value

    return data


def render_template(template_content: str, variables: Dict[str, object]) -> str:
    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        return _sanitize_value(variables.get(key, ""))

    return PLACEHOLDER_PATTERN.sub(repl, template_content)


def load_template(template_path: Path) -> str:
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")
    return template_path.read_text(encoding="utf-8")


def build_label(template_path: Path, variables: Dict[str, object]) -> str:
    template_content = load_template(template_path)
    return render_template(template_content, variables)


def send_to_printer(printer_name: str, tspl_content: str) -> Tuple[bool, str]:
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".tspl", encoding="utf-8") as tmp_file:
            tmp_file.write(tspl_content)
            tmp_path = Path(tmp_file.name)

        command = ["lpr", "-P", printer_name, "-o", "raw", str(tmp_path)]
        subprocess.run(command, check=True)
        return True, f"Задание отправлено на принтер {printer_name}"
    except FileNotFoundError:
        logging.error("Команда lpr не найдена. Проверьте установку CUPS")
        return False, "Команда lpr не найдена"
    except subprocess.CalledProcessError as exc:
        logging.error("Ошибка отправки задания на печать: %s", exc)
        return False, f"Ошибка отправки в lpr: {exc}"
    finally:
        if tmp_path and tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                logging.warning("Не удалось удалить временный файл %s", tmp_path)


def print_label(printer_name: str, template_path: Path, variables: Dict[str, object]) -> Tuple[bool, str, str]:
    tspl_content = build_label(template_path, variables)
    success, message = send_to_printer(printer_name, tspl_content)
    return success, message, tspl_content
