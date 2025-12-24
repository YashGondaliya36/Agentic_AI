"""AI Invoice Extractor using Gemini Vision"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import json

# Load .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)


class InvoiceExtractor:
    """
    Extract invoice data using Gemini Vision AI.
    
    Handles:
    - Purchase invoices (from suppliers)
    - Sales invoices (for reference)
    - Multi-format (PDF, JPG, PNG)
    """
    
    def __init__(self):
        """Initialize Gemini Vision"""
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        
        genai.configure(api_key=api_key)
        
        # Use Gemini Pro Vision for invoice processing
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={
                "temperature": 0.1,  # Low temp for accurate extraction
                "top_p": 0.8,
                "top_k": 40,
            }
        )
    
    def extract_purchase_invoice(self, image_path: str) -> Dict[str, Any]:
        """
        Extract data from purchase invoice.
        
        Args:
            image_path: Path to invoice image/PDF
            
        Returns:
            Dictionary with extracted invoice data
        """
        print(f"\n📄 Processing invoice: {Path(image_path).name}")
        
        # Check file type
        file_path = Path(image_path)
        file_ext = file_path.suffix.lower()
        
        # Load file based on type
        try:
            if file_ext == '.pdf':
                # For PDFs, we'll use Part with inline_data
                print("   📑 Processing PDF file...")
                with open(file_path, 'rb') as f:
                    pdf_data = f.read()
                
                # Create Part object for PDF
                from google.generativeai.types import content_types
                file_input = {
                    "mime_type": "application/pdf",
                    "data": pdf_data
                }
            else:
                # For images (JPG, PNG), use PIL
                print("   🖼️  Processing image file...")
                image = Image.open(image_path)
                file_input = image
                
        except Exception as e:
            return {"success": False, "error": f"Failed to load file: {e}"}
        
        # Create detailed prompt for hardware distributor invoices
        prompt = """Extract ALL data from this purchase invoice. This is for a HARDWARE DISTRIBUTOR business.

**CRITICAL: Return ONLY valid JSON, no markdown, no explanations.**

Extract the following in this EXACT JSON format:

{
  "supplier_name": "Company name",
  "invoice_number": "Invoice/bill number",
  "invoice_date": "Date (YYYY-MM-DD format)",
  "due_date": "Payment due date (YYYY-MM-DD) or null",
  "supplier_gstin": "GST number if present",
  "supplier_address": "Full address",
  "supplier_contact": "Phone/email if present",
  
  "items": [
    {
      "name": "Item/product name",
      "description": "Additional details if any",
      "hsn_code": "HSN/SAC code if present",
      "quantity": float (just number),
      "unit": "piece/box/kg/etc",
      "unit_price": float (price per unit before GST),
      "gst_rate": float (GST % like 18, 12, 5),
      "gst_amount": float,
      "total": float (final amount for this item)
    }
  ],
  
  "subtotal": float (total before GST),
  "total_gst": float (total GST amount),
  "total_amount": float (grand total),
  "payment_terms": "Net 30 days or similar",
  
  "raw_text": "Any other important information from invoice"
}

IMPORTANT RULES:
- Return ONLY the JSON object, nothing else
- All amounts must be numbers (float), not strings
- If a field is not found, use null
- For items, extract ALL line items
- Be precise with numbers and calculations
- Common hardware items: bolts, screws, tools, nails, wires, pipes, etc.
"""
        
        try:
            # Send to Gemini Vision
            response = self.model.generate_content([prompt, file_input])
            result_text = response.text.strip()
            
            # Clean response (remove markdown if present)
            if result_text.startswith("```json"):
                result_text = result_text.replace("```json", "").replace("```", "").strip()
            elif result_text.startswith("```"):
                result_text = result_text.replace("```", "").strip()
            
            # Parse JSON
            data = json.loads(result_text)
            
            print(f"✅ Extracted: {data.get('supplier_name', 'Unknown')}")
            print(f"   Invoice: {data.get('invoice_number')}")
            print(f"   Items: {len(data.get('items', []))}")
            print(f"   Total: ₹{data.get('total_amount', 0):,.2f}")
            
            return {
                "success": True,
                "data": data
            }
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
            print(f"Raw response: {result_text[:200]}...")
            return {
                "success": False,
                "error": "Failed to parse invoice data",
                "raw_response": result_text
            }
        
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def smart_item_match(self, item_name: str, existing_items: list) -> Optional[Dict]:
        """
        Match extracted item name with existing catalog.
        
        Uses AI to recognize item variations:
        - "M.S. Bolt 10mm" = "Mild Steel Bolt 10mm"
        - "Screwdriver Set 10pc" = "Screwdriver Set (10 pieces)"
        
        Args:
            item_name: Name from invoice
            existing_items: List of {id, name, description} from database
            
        Returns:
            Matched item dict or None
        """
        if not existing_items:
            return None
        
        # Build catalog for AI
        catalog_text = "\n".join([
            f"{item['id']}: {item['name']}" 
            for item in existing_items[:50]  # Limit to prevent token overflow
        ])
        
        prompt = f"""Match this item from an invoice to the most similar item in our catalog.

Invoice Item: "{item_name}"

Our Catalog:
{catalog_text}

If you find a match, respond with ONLY the item ID number.
If NO match, respond with: NONE

Consider variations like:
- M.S. = Mild Steel
- SS = Stainless Steel  
- Different units (box/piece/kg)
- Similar product names

Response (just number or NONE):"""
        
        try:
            response = self.model.generate_content(prompt)
            result = response.text.strip()
            
            if result == "NONE":
                return None
            
            # Extract ID
            item_id = int(result)
            matched_item = next((item for item in existing_items if item['id'] == item_id), None)
            
            if matched_item:
                print(f"   🔗 Matched '{item_name}' → {matched_item['name']}")
            
            return matched_item
            
        except Exception as e:
            print(f"   ⚠️  Match failed: {e}")
            return None


# Global instance
extractor = InvoiceExtractor()


# Test function
if __name__ == "__main__":
    print("🧪 Testing Invoice Extractor...")
    
    # This would test with a sample invoice
    # result = extractor.extract_purchase_invoice("sample_invoice.jpg")
    # print(json.dumps(result, indent=2))
