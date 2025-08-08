"""
OCR Tool - Scene Text Detection and Recognition
Based on: Scene Text Detection and Recognition paper
"""
import cv2
import numpy as np
from typing import List, Dict, Any, Optional
import logging
import re

logger = logging.getLogger(__name__)

class OCRProcessor:
    """
    Scene text detection and recognition for UI screenshots
    Extracts text from UI components for better understanding
    """
    
    def __init__(self):
        self.text_detector = None
        self.text_recognizer = None
        self._initialize_ocr()
    
    def _initialize_ocr(self):
        """Initialize OCR models"""
        try:
            # Try to use PaddleOCR if available
            try:
                from paddleocr import PaddleOCR
                self.ocr_engine = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
                self.ocr_type = "paddle"
                logger.info("PaddleOCR initialized successfully")
            except ImportError:
                # Fallback to Tesseract
                try:
                    import pytesseract
                    self.ocr_engine = pytesseract
                    self.ocr_type = "tesseract"
                    logger.info("Tesseract OCR initialized successfully")
                except ImportError:
                    logger.warning("No OCR engine available, using fallback text detection")
                    self.ocr_type = "fallback"
                    
        except Exception as e:
            logger.error(f"OCR initialization failed: {e}")
            self.ocr_type = "fallback"
    
    async def execute(self, image_path: str, regions: Optional[List[List[int]]] = None, **kwargs) -> Dict[str, Any]:
        """
        Execute OCR on image or specific regions
        
        Args:
            image_path: Path to image
            regions: Optional list of bounding boxes [x, y, w, h] to focus OCR on
            
        Returns:
            Dict with extracted text and locations
        """
        return self.extract_text(image_path, regions)
    
    def extract_text(self, image_path: str, regions: Optional[List[List[int]]] = None) -> Dict[str, Any]:
        """
        Extract text from image using OCR
        
        Returns:
            {
                "text_regions": [
                    {
                        "bbox": [x, y, width, height],
                        "text": "Login",
                        "confidence": 0.95,
                        "text_type": "button_text",
                        "language": "en"
                    }
                ],
                "full_text": "Login Username Password Submit",
                "text_stats": {"total_regions": 4, "avg_confidence": 0.89}
            }
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Extract text based on available OCR engine
            if self.ocr_type == "paddle":
                text_regions = self._extract_with_paddle(image, regions)
            elif self.ocr_type == "tesseract":
                text_regions = self._extract_with_tesseract(image, regions)
            else:
                text_regions = self._extract_with_fallback(image, regions)
            
            # Post-process results
            text_regions = self._post_process_text(text_regions)
            
            # Compile full text
            full_text = " ".join([region["text"] for region in text_regions if region["text"].strip()])
            
            return {
                "text_regions": text_regions,
                "full_text": full_text,
                "text_stats": {
                    "total_regions": len(text_regions),
                    "avg_confidence": np.mean([r["confidence"] for r in text_regions]) if text_regions else 0
                }
            }
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return {
                "text_regions": [],
                "full_text": "",
                "text_stats": {"total_regions": 0, "avg_confidence": 0},
                "error": str(e)
            }
    
    def _extract_with_paddle(self, image: np.ndarray, regions: Optional[List[List[int]]]) -> List[Dict]:
        """Extract text using PaddleOCR"""
        text_regions = []
        
        try:
            if regions:
                # Process specific regions
                for region in regions:
                    x, y, w, h = region
                    roi = image[y:y+h, x:x+w]
                    
                    results = self.ocr_engine.ocr(roi, cls=True)
                    
                    if results and results[0]:
                        for line in results[0]:
                            bbox_rel, (text, confidence) = line
                            
                            # Convert relative bbox to absolute coordinates
                            bbox_abs = self._convert_paddle_bbox(bbox_rel, x, y)
                            
                            text_regions.append({
                                "bbox": bbox_abs,
                                "text": text,
                                "confidence": confidence,
                                "text_type": self._classify_text_type(text),
                                "language": "en"
                            })
            else:
                # Process entire image
                results = self.ocr_engine.ocr(image, cls=True)
                
                if results and results[0]:
                    for line in results[0]:
                        bbox, (text, confidence) = line
                        
                        # Convert PaddleOCR bbox format
                        x = int(min([point[0] for point in bbox]))
                        y = int(min([point[1] for point in bbox]))
                        w = int(max([point[0] for point in bbox]) - x)
                        h = int(max([point[1] for point in bbox]) - y)
                        
                        text_regions.append({
                            "bbox": [x, y, w, h],
                            "text": text,
                            "confidence": confidence,
                            "text_type": self._classify_text_type(text),
                            "language": "en"
                        })
                        
        except Exception as e:
            logger.error(f"PaddleOCR extraction failed: {e}")
        
        return text_regions
    
    def _extract_with_tesseract(self, image: np.ndarray, regions: Optional[List[List[int]]]) -> List[Dict]:
        """Extract text using Tesseract OCR"""
        text_regions = []
        
        try:
            import pytesseract
            
            if regions:
                # Process specific regions
                for region in regions:
                    x, y, w, h = region
                    roi = image[y:y+h, x:x+w]
                    
                    # Get detailed OCR data
                    data = pytesseract.image_to_data(roi, output_type=pytesseract.Output.DICT)
                    
                    for i in range(len(data['text'])):
                        text = data['text'][i].strip()
                        if text and int(data['conf'][i]) > 30:  # Confidence threshold
                            
                            # Adjust coordinates to absolute position
                            abs_x = x + data['left'][i]
                            abs_y = y + data['top'][i]
                            
                            text_regions.append({
                                "bbox": [abs_x, abs_y, data['width'][i], data['height'][i]],
                                "text": text,
                                "confidence": int(data['conf'][i]) / 100.0,
                                "text_type": self._classify_text_type(text),
                                "language": "en"
                            })
            else:
                # Process entire image
                data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                
                for i in range(len(data['text'])):
                    text = data['text'][i].strip()
                    if text and int(data['conf'][i]) > 30:
                        
                        text_regions.append({
                            "bbox": [data['left'][i], data['top'][i], data['width'][i], data['height'][i]],
                            "text": text,
                            "confidence": int(data['conf'][i]) / 100.0,
                            "text_type": self._classify_text_type(text),
                            "language": "en"
                        })
                        
        except Exception as e:
            logger.error(f"Tesseract extraction failed: {e}")
        
        return text_regions
    
    def _extract_with_fallback(self, image: np.ndarray, regions: Optional[List[List[int]]]) -> List[Dict]:
        """
        Fallback text detection using basic computer vision
        This won't actually read text but can detect text-like regions
        """
        text_regions = []
        
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Use MSER (Maximally Stable Extremal Regions) to detect text regions
            mser = cv2.MSER_create()
            regions_mser, _ = mser.detectRegions(gray)
            
            for region in regions_mser:
                # Get bounding box
                x, y, w, h = cv2.boundingRect(region)
                
                # Filter by size (typical text regions)
                if w < 10 or h < 10 or w > 500 or h > 100:
                    continue
                
                # Placeholder text (in real implementation, this would be actual OCR)
                placeholder_text = f"text_{len(text_regions)}"
                
                text_regions.append({
                    "bbox": [x, y, w, h],
                    "text": placeholder_text,
                    "confidence": 0.5,  # Low confidence for fallback
                    "text_type": "unknown",
                    "language": "en"
                })
                
        except Exception as e:
            logger.error(f"Fallback text detection failed: {e}")
        
        return text_regions
    
    def _convert_paddle_bbox(self, bbox_rel: List[List[float]], offset_x: int, offset_y: int) -> List[int]:
        """Convert PaddleOCR relative bbox to absolute coordinates"""
        x_coords = [point[0] for point in bbox_rel]
        y_coords = [point[1] for point in bbox_rel]
        
        x = int(min(x_coords)) + offset_x
        y = int(min(y_coords)) + offset_y
        w = int(max(x_coords) - min(x_coords))
        h = int(max(y_coords) - min(y_coords))
        
        return [x, y, w, h]
    
    def _classify_text_type(self, text: str) -> str:
        """Classify text based on content and context"""
        text_lower = text.lower().strip()
        
        # Button text patterns
        button_patterns = [
            r'^(login|sign in|submit|send|save|cancel|ok|yes|no|continue|next|back|home)$',
            r'^(register|sign up|create account)$',
            r'^(search|find|go)$',
            r'^(add|edit|delete|remove)$'
        ]
        
        for pattern in button_patterns:
            if re.match(pattern, text_lower):
                return "button_text"
        
        # Form labels
        label_patterns = [
            r'^(username|email|password|name|phone|address)$',
            r'^(first name|last name|full name)$',
            r'^(confirm password|repeat password)$'
        ]
        
        for pattern in label_patterns:
            if re.match(pattern, text_lower):
                return "form_label"
        
        # Navigation text
        nav_patterns = [
            r'^(home|about|contact|services|products|blog)$',
            r'^(menu|navigation|nav)$'
        ]
        
        for pattern in nav_patterns:
            if re.match(pattern, text_lower):
                return "navigation_text"
        
        # Placeholder text
        if "placeholder" in text_lower or "enter" in text_lower:
            return "placeholder_text"
        
        # Long text (likely content)
        if len(text.split()) > 5:
            return "content_text"
        
        # Short text (likely labels or titles)
        elif len(text.split()) <= 3:
            return "label_text"
        
        return "general_text"
    
    def _post_process_text(self, text_regions: List[Dict]) -> List[Dict]:
        """Post-process extracted text for better results"""
        
        # Clean up text
        for region in text_regions:
            # Remove extra whitespace
            region["text"] = re.sub(r'\s+', ' ', region["text"]).strip()
            
            # Filter out very short or nonsensical text
            if len(region["text"]) < 1 or region["confidence"] < 0.3:
                continue
            
            # Add semantic information
            region["semantic"] = self._get_text_semantics(region["text"], region["text_type"])
        
        # Remove duplicates and overlaps
        text_regions = self._remove_duplicate_text(text_regions)
        
        # Sort by reading order (top to bottom, left to right)
        text_regions.sort(key=lambda r: (r["bbox"][1], r["bbox"][0]))
        
        return text_regions
    
    def _get_text_semantics(self, text: str, text_type: str) -> Dict[str, Any]:
        """Extract semantic information from text"""
        return {
            "is_interactive": text_type in ["button_text", "form_label"],
            "is_navigation": text_type == "navigation_text",
            "is_form_related": text_type in ["form_label", "placeholder_text"],
            "word_count": len(text.split()),
            "char_count": len(text),
            "contains_numbers": bool(re.search(r'\d', text)),
            "contains_special_chars": bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', text))
        }
    
    def _remove_duplicate_text(self, text_regions: List[Dict]) -> List[Dict]:
        """Remove duplicate or highly overlapping text regions"""
        if not text_regions:
            return text_regions
        
        # Sort by confidence
        text_regions.sort(key=lambda x: x["confidence"], reverse=True)
        
        unique_regions = []
        for region in text_regions:
            is_duplicate = False
            
            for existing in unique_regions:
                # Check text similarity
                if region["text"] == existing["text"]:
                    # Check bbox overlap
                    overlap = self._calculate_bbox_overlap(region["bbox"], existing["bbox"])
                    if overlap > 0.7:  # High overlap threshold for text
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                unique_regions.append(region)
        
        return unique_regions
    
    def _calculate_bbox_overlap(self, bbox1: List[int], bbox2: List[int]) -> float:
        """Calculate overlap ratio between two bounding boxes"""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        
        # Calculate intersection
        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        intersection = (x_right - x_left) * (y_bottom - y_top)
        area1 = w1 * h1
        area2 = w2 * h2
        
        # Return overlap as ratio of smaller area
        smaller_area = min(area1, area2)
        return intersection / smaller_area if smaller_area > 0 else 0.0