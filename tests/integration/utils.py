import io

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage

def extract_text_from_pdf(pdf_content):
    """
    Extracts text from raw PDF content.
    """
    input_buffer = io.BytesIO(pdf_content)
    output_buffer = io.BytesIO()

    resource_manager = PDFResourceManager()
    laparams = LAParams()
    device = TextConverter(resource_manager, output_buffer, codec='utf-8', laparams=laparams)
    interpreter = PDFPageInterpreter(resource_manager, device)

    for page in PDFPage.get_pages(input_buffer):
        interpreter.process_page(page)

    text = output_buffer.getvalue()

    device.close()
    input_buffer.close()
    output_buffer.close()

    return text
