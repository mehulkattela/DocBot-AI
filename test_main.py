import unittest
import subprocess
from unittest.mock import MagicMock, patch
from main import extract_text_from_pdf, extract_text_from_doc

class TestDocumentProcessing(unittest.TestCase):

    @patch("pymupdf.open")  # Mocking the fitz (pymupdf) library for PDF extraction
    def test_extract_text_from_pdf(self, mock_fitz_open):
        # Creates a mock PDF object. Here, we set page_count to simulate a PDF with one page.
        mock_pdf = MagicMock()
        mock_pdf.page_count = 1
        
        # Creates a mock page object with a method get_text that returns a predefined string when called.
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Sample text from PDF."
        
        # Configures the mock PDF to return the mock page when load_page is called.
        mock_pdf.load_page.return_value = mock_page
        
        # This simulates the context manager behavior of fitz.open, ensuring that when it is called in your main code, it returns the mock PDF object.
        mock_fitz_open.return_value.__enter__.return_value = mock_pdf

        # This simulates a file-like object that your function would read from, returning a byte string.
        mock_file = MagicMock()
        mock_file.read.return_value = b"fake_pdf_content"

        # Calls the extract_text_from_pdf function and asserts that its output matches the expected string.
        result = extract_text_from_pdf(mock_file)
        self.assertEqual(result, "Sample text from PDF.")

    @patch("pymupdf.open")
    def test_extract_text_from_pdf_empty(self, mock_fitz_open):
        # Simulate an empty PDF
        mock_pdf = MagicMock()
        mock_pdf.page_count = 0
        mock_fitz_open.return_value.__enter__.return_value = mock_pdf
        
        mock_file = MagicMock()
        mock_file.read.return_value = b"fake_pdf_content"

        result = extract_text_from_pdf(mock_file)
        self.assertEqual(result, "")  # Expecting an empty string

    @patch("pymupdf.open")
    def test_extract_text_from_pdf_multiple_pages(self, mock_fitz_open):
        mock_pdf = MagicMock()
        mock_pdf.page_count = 2
        
        mock_page_1 = MagicMock()
        mock_page_1.get_text.return_value = "Page 1 text."
        mock_pdf.load_page.side_effect = [mock_page_1, MagicMock(get_text=lambda: "Page 2 text.")]
        
        mock_fitz_open.return_value.__enter__.return_value = mock_pdf
        
        mock_file = MagicMock()
        mock_file.read.return_value = b"fake_pdf_content"

        result = extract_text_from_pdf(mock_file)
        self.assertEqual(result, "Page 1 text.Page 2 text.")  # Expecting concatenated text
        
    @patch("subprocess.run")  # Mocking subprocess call for DOC extraction
    def test_extract_text_from_doc(self, mock_subprocess_run):
        # Simulate file input as a byte stream
        mock_file = MagicMock()
        mock_file.read.return_value = b"fake_doc_content"

        # Setup mock subprocess response
        mock_subprocess_run.return_value = MagicMock(stdout="Sample text from DOC.")
        
        # Call the function and assert
        result = extract_text_from_doc(mock_file)
        self.assertEqual(result, "Sample text from DOC.")

    @patch("subprocess.run")
    def test_extract_text_from_doc_empty(self, mock_subprocess_run):
        mock_file = MagicMock()
        mock_file.read.return_value = b""
        mock_subprocess_run.return_value = MagicMock(stdout="")

        result = extract_text_from_doc(mock_file)
        self.assertEqual(result, "")  # Expecting an empty string

    @patch("subprocess.run")
    def test_extract_text_from_doc_invalid(self, mock_subprocess_run):
        mock_file = MagicMock()
        mock_file.read.return_value = b"fake_doc_content"

        # Simulate a subprocess error
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(1, 'antiword')

        result = extract_text_from_doc(mock_file)
        self.assertEqual(result, "")  # Expecting an empty string or handling error appropriately

if __name__ == "__main__":
    unittest.main()