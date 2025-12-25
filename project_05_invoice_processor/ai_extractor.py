"""AI Invoice Extractor using Gemini - TEXT EXTRACTION APPROACH"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Import libraries
import google.generativeai as genai
from PIL import Image
import pdfplumber
import pytesseract

# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables!")

genai.configure(api_key=api_key)


class InvoiceExtractor:
    """Extract invoice data using TEXT extraction + Gemini LLM"""
    
    def __init__(self, model_name="gemini-2.5-flash"):
        """Initialize with Gemini model"""
        self.model = genai.GenerativeModel(model_name)
        print(f"✅ Initialized InvoiceExtractor with {model_name}")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using pdfplumber"""
        try:
            text_content = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    # Extract text
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
                    
                    # Also try to extract tables
                    tables = page.extract_tables()
                    for table in tables:
                        # Convert table to text
                        for row in table:
                            text_content.append(" | ".join([str(cell) if cell else "" for cell in row]))
            
            full_text = "\n".join(text_content)
            print(f"   📄 Extracted {len(full_text)} characters from PDF")
            return full_text
            
        except Exception as e:
            print(f"   ❌ PDF extraction failed: {e}")
            return ""
    
    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image using Tesseract OCR"""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            print(f"   🖼️  Extracted {len(text)} characters from image via OCR")
            return text
            
        except Exception as e:
            print(f"   ❌ OCR failed: {e}")
            print("   ℹ️  Make sure Tesseract is installed: https://github.com/tesseract-ocr/tesseract")
            return ""
    
    def extract_purchase_invoice(self, file_path: str) -> Dict[str, Any]:
        """
        Extract data from PURCHASE invoice (you are buying from supplier).
        Uses TEXT extraction + Gemini for parsing.
        
        Args:
            file_path: Path to invoice file (PDF/Image)
            
        Returns:
            Dictionary with extracted invoice data
        """
        print(f"\n📄 Processing PURCHASE invoice: {Path(file_path).name}")
        
        # Step 1: Extract text from file
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            print("   📑 Extracting text from PDF...")
            invoice_text = self.extract_text_from_pdf(file_path)
        else:
            print("   🖼️  Extracting text from image via OCR...")
            invoice_text = self.extract_text_from_image(file_path)
        
        if not invoice_text or len(invoice_text) < 50:
            return {
                "success": False,
                "error": "Could not extract sufficient text from invoice"
            }
        
        # Step 2: Send text to Gemini for structured parsing
        try:
            response = self._parse_purchase_invoice_text(invoice_text)
            return response
            
        except Exception as e:
            print(f"❌ Parsing failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def extract_sales_invoice(self, file_path: str) -> Dict[str, Any]:
        """
        Extract data from SALES invoice (you are selling to customer).
        Uses TEXT extraction + Gemini for parsing.
        
        Args:
            file_path: Path to invoice file (PDF/Image)
            
        Returns:
            Dictionary with extracted invoice data
        """
        print(f"\n📄 Processing SALES invoice: {Path(file_path).name}")
        
        # Step 1: Extract text from file
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            print("   📑 Extracting text from PDF...")
            invoice_text = self.extract_text_from_pdf(file_path)
        else:
            print("   🖼️  Extracting text from image via OCR...")
            invoice_text = self.extract_text_from_image(file_path)
        
        if not invoice_text or len(invoice_text) < 50:
            return {
                "success": False,
                "error": "Could not extract sufficient text from invoice"
            }
        
        # Step 2: Send text to Gemini for structured parsing
        try:
            response = self._parse_sales_invoice_text(invoice_text)
            return response
            
        except Exception as e:
            print(f"❌ Parsing failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_purchase_invoice_text(self, invoice_text: str) -> Dict[str, Any]:
        """Parse extracted text into structured purchase invoice data using Gemini"""
        
        prompt = f"""You are an expert invoice parser. Extract data from this PURCHASE invoice text.
This is an invoice where a BUSINESS is BUYING from a SUPPLIER.

**CRITICAL: Return ONLY valid JSON, no markdown, no explanations.**

Invoice Text:
{invoice_text}

Extract the following in this EXACT JSON format:

{{
  "supplier_name": "Supplier/vendor name",
  "invoice_number": "Invoice/bill number",
  "invoice_date": "Date (YYYY-MM-DD format)",
  "due_date": "Payment due date (YYYY-MM-DD) or null",
  "supplier_gstin": "Supplier GST number if present",
  "supplier_address": "Supplier address",
  "supplier_contact": "Phone/email if present",
  
  "items": [
    {{
      "name": "Item/product name",
      "description": "Additional details if any",
      "hsn_code": "HSN/SAC code if present",
      "quantity": float (just number),
      "unit": "piece/box/kg/etc",
      "unit_price": float (unit price before GST),
      "gst_rate": float (GST % like 18, 12, 5),
      "gst_amount": float,
      "total": float (final amount for this item)
    }}
  ],
  
  "subtotal": float (total before GST),
  "total_gst": float (total GST amount),
  "total_amount": float (grand total),
  "payment_terms": "Net 30 days or similar",
  
  "raw_text": "Any other important information"
}}

RULES:
- Return ONLY JSON
- All amounts must be numbers (float), not strings
- If a field is not found, use null
- Extract ALL line items
- Be precise with numbers"""

        response = self.model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Clean response
        if result_text.startswith("```json"):
            result_text = result_text.replace("```json", "").replace("```", "").strip()
        elif result_text.startswith("```"):
            result_text = result_text.replace("```", "").strip()
        
        # Parse JSON
        data = json.loads(result_text)
        
        print(f"✅ Extracted PURCHASE: {data.get('supplier_name', 'Unknown')}")
        print(f"   Invoice: {data.get('invoice_number')}")
        print(f"   Items: {len(data.get('items', []))}")
        print(f"   Total: ₹{data.get('total_amount', 0):,.2f}")
        
        return {
            "success": True,
            "data": data
        }
    
    def _parse_sales_invoice_text(self, invoice_text: str) -> Dict[str, Any]:
        """Parse extracted text into structured sales invoice data using Gemini"""
        
        prompt = f"""You are an expert invoice parser. Extract data from this SALES invoice text.
This is an invoice where a BUSINESS is SELLING to a CUSTOMER.

**CRITICAL: Return ONLY valid JSON, no markdown, no explanations.**

Invoice Text:
{invoice_text}

Extract the following in this EXACT JSON format:

{{
  "customer_name": "Customer/buyer name",
  "invoice_number": "Invoice/bill number",
  "invoice_date": "Date (YYYY-MM-DD format)",
  "due_date": "Payment due date (YYYY-MM-DD) or null",
  "customer_gstin": "Customer GST number if present",
  "customer_address": "Customer address",
  "customer_contact": "Phone/email if present",
  
  "items": [
    {{
      "name": "Item/product name",
      "description": "Additional details if any",
      "hsn_code": "HSN/SAC code if present",
      "quantity": float (just number),
      "unit": "piece/box/kg/etc",
      "unit_price": float (selling price per unit before GST),
      "gst_rate": float (GST % like 18, 12, 5),
      "gst_amount": float,
      "total": float (final amount for this item)
    }}
  ],
  
  "subtotal": float (total before GST),
  "total_gst": float (total GST amount),
  "total_amount": float (grand total),
  "payment_terms": "Net 30 days or similar",
  
  "raw_text": "Any other important information"
}}

RULES:
- Return ONLY JSON
- All amounts must be numbers (float), not strings
- If a field is not found, use null
- Extract ALL line items
- Be precise with numbers
- This is a SALES invoice (you are selling TO the customer)"""

        response = self.model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Clean response
        if result_text.startswith("```json"):
            result_text = result_text.replace("```json", "").replace("```", "").strip()
        elif result_text.startswith("```"):
            result_text = result_text.replace("```", "").strip()
        
        # Parse JSON
        data = json.loads(result_text)
        
        print(f"✅ Extracted SALES: {data.get('customer_name', 'Unknown')}")
        print(f"   Invoice: {data.get('invoice_number')}")
        print(f"   Items: {len(data.get('items', []))}")
        print(f"   Total: ₹{data.get('total_amount', 0):,.2f}")
        
        return {
            "success": True,
            "data": data
        }
    
    def smart_item_match(self, item_name: str, existing_items: list) -> Optional[Dict]:
        """
        Match extracted item name with existing catalog (DISABLED for quota).
        
        Simple exact matching used instead.
        """
        # Simple exact match
        item_lower = item_name.strip().lower()
        for item in existing_items:
            if item["name"].strip().lower() == item_lower:
                return item
        return None


# Create global instance
extractor = InvoiceExtractor()

if __name__ == "__main__":
    print("InvoiceExtractor initialized successfully!")
