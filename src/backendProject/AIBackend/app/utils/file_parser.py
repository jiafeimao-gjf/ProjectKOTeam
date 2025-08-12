import PyPDF2
import docx


def parse_file(filename):
    ext = filename.split('.')[-1]
    if ext == 'pdf':
        with open(filename, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ''.join(page.extract_text() for page in reader.pages)
    elif ext == 'docx':
        doc = docx.Document(filename)
        text = '\n'.join(para.text for para in doc.paragraphs)
    elif ext == 'txt':
        with open(filename, 'r') as f:
            text = f.read()
    else:
        text = ''
    return text
