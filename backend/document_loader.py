# ============================================================
# DOCUMENT LOADER & TEXT PROCESSING
# ============================================================

from pathlib import Path
from pypdf import PdfReader
from docx import Document


# ------------------------------------------------------------
# 1. Read PDF files using pypdf
# ------------------------------------------------------------
def read_pdf(file_path):
    """Extract text from a PDF file."""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


# ------------------------------------------------------------
# 2. Read DOCX files using python-docx
# ------------------------------------------------------------
def read_docx(file_path):
    """Extract text from a Word (.docx) file."""
    document = Document(file_path)
    text = ""
    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            text += paragraph.text + "\n"

    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip():
                    text += cell.text + "\n"
    return text


# ------------------------------------------------------------
# 3. Read Plain TXT files
# ------------------------------------------------------------
def read_txt(file_path):
    """Read content from a text file."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


# ------------------------------------------------------------
# 4. Clean text
# ------------------------------------------------------------
def clean_text(text):
    """Remove redundant spaces and fix empty lines."""
    lines = [line.strip() for line in text.split("\n")]
    # Keep non-empty lines or single spacing between paragraphs
    cleaned_lines = []
    for line in lines:
        if line:
            cleaned_lines.append(line)
        elif cleaned_lines and cleaned_lines[-1] != "":
            cleaned_lines.append("")
    return "\n".join(cleaned_lines).strip()


# ------------------------------------------------------------
# 5. Split text into chunks
# ------------------------------------------------------------
def split_into_chunks(text, chunk_size=600, overlap=100):
    """
    Split text into simple overlapping chunks so context is preserved.
    """
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        if len(current_chunk) + len(paragraph) + 2 <= chunk_size:
            current_chunk = f"{current_chunk}\n\n{paragraph}".strip()
        else:
            if current_chunk:
                chunks.append(current_chunk)

            # If a single paragraph is very long, split it by lines
            if len(paragraph) > chunk_size:
                lines = paragraph.split("\n")
                sub_chunk = ""
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    if len(sub_chunk) + len(line) + 1 <= chunk_size:
                        sub_chunk = f"{sub_chunk}\n{line}".strip()
                    else:
                        if sub_chunk:
                            chunks.append(sub_chunk)
                        sub_chunk = line
                current_chunk = sub_chunk
            else:
                # Add overlap from end of previous chunk if available
                if chunks and overlap > 0:
                    prev_words = chunks[-1].split()
                    overlap_prefix = " ".join(prev_words[-15:])
                    current_chunk = f"{overlap_prefix}\n\n{paragraph}".strip()
                else:
                    current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


# ------------------------------------------------------------
# 6. Load all personal documents from folder
# ------------------------------------------------------------
def load_all_documents(folder_path):
    """
    Read all documents (.pdf, .txt, .docx) from data directory,
    chunk them, and attach filename metadata.
    """
    all_chunks = []
    folder = Path(folder_path)
    chunk_id = 1

    for file_path in sorted(folder.iterdir()):
        if not file_path.is_file():
            continue

        filename = file_path.name
        ext = file_path.suffix.lower()

        # Read based on file extension
        if ext == ".pdf":
            raw_text = read_pdf(str(file_path))
        elif ext == ".docx":
            raw_text = read_docx(str(file_path))
        elif ext == ".txt":
            raw_text = read_txt(str(file_path))
        else:
            continue

        # Clean text
        text = clean_text(raw_text)
        if not text:
            continue

        # Chunk text
        chunks = split_into_chunks(text, chunk_size=600, overlap=100)

        # Build chunk list with metadata
        for chunk in chunks:
            all_chunks.append({
                "id": chunk_id,
                "text": chunk,
                "source": filename
            })
            chunk_id += 1

    return all_chunks
