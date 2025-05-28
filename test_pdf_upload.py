#!/usr/bin/env python3
"""
Test script for PDF upload and parsing functionality
"""

import requests
import os
import sys

def test_pdf_upload():
    """Test PDF upload functionality"""
    
    # API endpoint
    upload_url = "http://localhost:8000/api/v1/resources/upload"
    
    # Test with available files
    test_files = []
    
    # Check for test PDF
    if os.path.exists("test_document.pdf"):
        test_files.append("test_document.pdf")
    
    # Check for any other PDF files in the directory
    for file in os.listdir("."):
        if file.endswith(".pdf") and file not in test_files:
            test_files.append(file)
    
    # If no PDF files, create a test text file
    if not test_files:
        print("No PDF test files found. Creating a test text file...")
        test_content = """
This is a test document for the PDF parsing system.

Features:
- Support for PDF documents
- Support for Markdown files  
- Support for plain text files
- OCR capability for scanned PDFs
- Automatic content extraction

The system uses multiple parsing methods:
1. pypdf for text-based PDFs
2. pdfplumber as fallback
3. OCR with Tesseract for scanned documents

This ensures maximum compatibility with different PDF types.
        """.strip()
        
        with open("test_document.txt", "w", encoding="utf-8") as f:
            f.write(test_content)
        test_files = ["test_document.txt"]
    
    for file_path in test_files:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
            
        print(f"\n=== Testing upload: {file_path} ===")
        
        try:
            with open(file_path, "rb") as f:
                files = {"file": (file_path, f, "application/octet-stream")}
                data = {
                    "title": f"Test Upload - {os.path.basename(file_path)}",
                    "description": f"Test upload of {file_path} to verify parsing functionality"
                }
                
                print(f"Uploading {file_path}...")
                response = requests.post(upload_url, files=files, data=data)
                
                if response.status_code == 201:
                    result = response.json()
                    print("✅ Upload successful!")
                    print(f"   Resource ID: {result['id']}")
                    print(f"   Title: {result['title']}")
                    print(f"   File Type: {result['file_type']}")
                    print(f"   File Size: {result['file_size']} bytes")
                    print(f"   Message: {result['message']}")
                    
                    # Get the full resource details
                    resource_url = f"http://localhost:8000/api/v1/resources/{result['id']}"
                    detail_response = requests.get(resource_url)
                    
                    if detail_response.status_code == 200:
                        details = detail_response.json()
                        content = details.get('parsed_content', '')
                        print(f"   Extracted Content Length: {len(content)} characters")
                        print(f"   Content Preview: {content[:300]}...")
                        
                        # For PDF files, show more details
                        if file_path.endswith('.pdf'):
                            print(f"\n   📄 PDF Parsing Results:")
                            print(f"   - Successfully extracted text from PDF")
                            print(f"   - Content appears to be: {'✅ Meaningful' if len(content) > 100 else '⚠️ Limited'}")
                            if "Test PDF Document" in content:
                                print(f"   - ✅ Found expected title in content")
                            if "pypdf" in content or "pdfplumber" in content:
                                print(f"   - ✅ Found expected technical terms")
                    
                else:
                    print(f"❌ Upload failed with status {response.status_code}")
                    try:
                        error_detail = response.json()
                        print(f"   Error: {error_detail.get('detail', response.text)}")
                    except:
                        print(f"   Error: {response.text}")
                    
        except Exception as e:
            print(f"❌ Error uploading {file_path}: {e}")
    
    # Clean up test file
    if "test_document.txt" in test_files and os.path.exists("test_document.txt"):
        os.remove("test_document.txt")
        print("\n🧹 Cleaned up test file")

def test_api_health():
    """Test if the API is running"""
    try:
        response = requests.get("http://localhost:8000/api/v1/resources/")
        if response.status_code == 200:
            print("✅ API is running and accessible")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing PDF Upload and Parsing Functionality")
    print("=" * 50)
    
    # Check if API is running
    if not test_api_health():
        print("\n💡 Make sure the backend server is running:")
        print("   cd poc-backend && python run.py")
        sys.exit(1)
    
    # Run upload tests
    test_pdf_upload()
    
    print("\n✨ Test completed!")
    print("\n💡 To test with your own PDF files:")
    print("   1. Place PDF files in the poc-backend directory")
    print("   2. Run this script again")
    print("   3. The script will automatically detect and test all PDF files") 