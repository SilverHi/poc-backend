#!/usr/bin/env python3
"""
Create a test PDF file for testing PDF parsing functionality
"""

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.units import inch
    
    def create_test_pdf():
        """Create a simple test PDF file"""
        filename = "test_document.pdf"
        
        # Create a simple PDF with reportlab
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title = Paragraph("Test PDF Document", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Content
        content = """
        This is a test PDF document created to verify the PDF parsing functionality.
        
        The system supports multiple parsing methods:
        
        1. pypdf - Fast parsing for text-based PDFs
        2. pdfplumber - More robust parsing as fallback
        3. OCR with Tesseract - For scanned documents
        
        Features:
        • Automatic file type detection
        • Multiple encoding support
        • Comprehensive error handling
        • Detailed logging
        
        This PDF should be successfully parsed by any of the first two methods,
        as it contains standard text content.
        
        If you see this text in the parsed output, the PDF parsing is working correctly!
        """
        
        for line in content.strip().split('\n'):
            if line.strip():
                p = Paragraph(line.strip(), styles['Normal'])
                story.append(p)
                story.append(Spacer(1, 6))
        
        # Build PDF
        doc.build(story)
        print(f"✅ Created test PDF: {filename}")
        return filename
    
    if __name__ == "__main__":
        create_test_pdf()
        
except ImportError:
    print("❌ reportlab not installed. Installing...")
    import subprocess
    import sys
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
        print("✅ reportlab installed successfully")
        print("🔄 Please run this script again to create the test PDF")
    except Exception as e:
        print(f"❌ Failed to install reportlab: {e}")
        print("\n💡 Alternative: Create a simple text-based PDF manually or use an existing PDF file")
        
        # Create a simple text file as fallback
        with open("test_document_fallback.txt", "w", encoding="utf-8") as f:
            f.write("""Test Document for PDF Parsing

This is a fallback text document since reportlab is not available.

The PDF parsing system supports:
- Text-based PDFs (using pypdf)
- Complex PDFs (using pdfplumber) 
- Scanned PDFs (using OCR with Tesseract)

To test with a real PDF:
1. Place a PDF file in this directory
2. Update the test script with the filename
3. Run the test again
""")
        print("📄 Created fallback text file: test_document_fallback.txt") 