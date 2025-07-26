import fitz  # PyMuPDF

def extract_headings_and_text(path, filename):
    doc = fitz.open(path)
    sections = []
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        lines = []
        for block in blocks:
            for line in block.get("lines", []):
                text = " ".join(span["text"] for span in line["spans"] if span["text"].strip()).strip()
                if text:
                    lines.append((text, line["spans"][0]["size"], page_num))
        # Heuristic: headings are lines with large font size and short length
        if not lines:
            continue
        font_sizes = [size for _, size, _ in lines]
        if not font_sizes:
            continue
        max_font = max(font_sizes)
        heading_candidates = [i for i, (text, size, _) in enumerate(lines) if size >= max_font - 1 and len(text.split()) <= 12]
        heading_candidates.append(len(lines))  # sentinel for last section
        for idx in range(len(heading_candidates) - 1):
            i = heading_candidates[idx]
            j = heading_candidates[idx + 1]
            heading_text = lines[i][0]
            section_text = " ".join(lines[k][0] for k in range(i, j)).strip()
            sections.append({
                "title": heading_text,
                "text": section_text,
                "page": page_num,
                "document": filename
            })
    return sections
