"""
RAG Memory System - Context management and knowledge retrieval
"""
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import pickle
import hashlib
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)

class RAGMemory:
    """
    Retrieval-Augmented Generation memory system for AutoDevFlow
    Manages context, knowledge base, and execution history
    """
    
    def __init__(self, memory_dir: str = "memory"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        
        # Memory components
        self.knowledge_base = self._load_knowledge_base()
        self.execution_history = self._load_execution_history()
        self.context_cache = {}
        self.paper_knowledge = self._load_paper_knowledge()
        
        # Configuration
        self.max_context_size = 10000  # tokens
        self.max_history_entries = 1000
        self.similarity_threshold = 0.7
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load persistent knowledge base"""
        kb_path = self.memory_dir / "knowledge_base.json"
        
        if kb_path.exists():
            try:
                with open(kb_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load knowledge base: {e}")
        
        # Initialize with default knowledge
        return {
            "ui_patterns": self._get_default_ui_patterns(),
            "api_patterns": self._get_default_api_patterns(),
            "code_templates": self._get_default_code_templates(),
            "best_practices": self._get_default_best_practices()
        }
    
    def _load_execution_history(self) -> List[Dict[str, Any]]:
        """Load execution history"""
        history_path = self.memory_dir / "execution_history.json"
        
        if history_path.exists():
            try:
                with open(history_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load execution history: {e}")
        
        return []
    
    def _load_paper_knowledge(self) -> Dict[str, Any]:
        """Load knowledge extracted from research papers"""
        paper_kb_path = self.memory_dir / "paper_knowledge.json"
        
        if paper_kb_path.exists():
            try:
                with open(paper_kb_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load paper knowledge: {e}")
        
        # Initialize with paper-based knowledge
        return {
            "pix2code": {
                "description": "Generating Code from a Graphical User Interface Screenshot",
                "key_concepts": [
                    "CNN encoder for visual features",
                    "LSTM decoder for code generation",
                    "Domain-specific language (DSL)",
                    "Attention mechanism for spatial alignment"
                ],
                "applications": ["UI to code conversion", "Automated GUI development"]
            },
            "mask_rcnn": {
                "description": "Instance segmentation and object detection",
                "key_concepts": [
                    "Region Proposal Network (RPN)",
                    "Feature Pyramid Network (FPN)",
                    "ROI Align for precise feature extraction",
                    "Multi-task loss function"
                ],
                "applications": ["UI component detection", "Object localization"]
            },
            "codet5": {
                "description": "Code understanding and generation with T5",
                "key_concepts": [
                    "Text-to-text transfer transformer",
                    "Code-aware pre-training",
                    "Multi-task learning",
                    "Identifier-aware tokenization"
                ],
                "applications": ["Code generation", "Code summarization", "API generation"]
            },
            "codebert": {
                "description": "Pre-trained model for programming and natural languages",
                "key_concepts": [
                    "Bimodal pre-training",
                    "Masked language modeling",
                    "Replaced token detection",
                    "Code-text alignment"
                ],
                "applications": ["Code quality assessment", "Bug detection", "Code search"]
            }
        }
    
    def store_execution_context(self, execution_id: str, context: Dict[str, Any]) -> None:
        """Store execution context for future reference"""
        try:
            context_entry = {
                "execution_id": execution_id,
                "timestamp": datetime.now().isoformat(),
                "context": context,
                "context_hash": self._hash_context(context)
            }
            
            self.execution_history.append(context_entry)
            
            # Limit history size
            if len(self.execution_history) > self.max_history_entries:
                self.execution_history = self.execution_history[-self.max_history_entries:]
            
            # Cache recent context
            self.context_cache[execution_id] = context_entry
            
            # Persist to disk
            self._save_execution_history()
            
        except Exception as e:
            logger.error(f"Failed to store execution context: {e}")
    
    def retrieve_similar_contexts(self, current_context: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve similar execution contexts from history"""
        try:
            current_hash = self._hash_context(current_context)
            similar_contexts = []
            
            for entry in reversed(self.execution_history):  # Most recent first
                similarity = self._calculate_context_similarity(current_context, entry["context"])
                
                if similarity >= self.similarity_threshold:
                    similar_contexts.append({
                        "entry": entry,
                        "similarity": similarity
                    })
                
                if len(similar_contexts) >= limit:
                    break
            
            # Sort by similarity
            similar_contexts.sort(key=lambda x: x["similarity"], reverse=True)
            
            return [ctx["entry"] for ctx in similar_contexts]
            
        except Exception as e:
            logger.error(f"Failed to retrieve similar contexts: {e}")
            return []
    
    def get_relevant_knowledge(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Retrieve relevant knowledge for a query"""
        try:
            relevant_knowledge = {
                "ui_patterns": [],
                "api_patterns": [],
                "code_templates": [],
                "best_practices": [],
                "paper_insights": [],
                "historical_solutions": []
            }
            
            query_lower = query.lower()
            
            # Search UI patterns
            for pattern_name, pattern_data in self.knowledge_base.get("ui_patterns", {}).items():
                if self._is_relevant(query_lower, pattern_data):
                    relevant_knowledge["ui_patterns"].append({
                        "name": pattern_name,
                        "data": pattern_data
                    })
            
            # Search API patterns
            for pattern_name, pattern_data in self.knowledge_base.get("api_patterns", {}).items():
                if self._is_relevant(query_lower, pattern_data):
                    relevant_knowledge["api_patterns"].append({
                        "name": pattern_name,
                        "data": pattern_data
                    })
            
            # Search code templates
            for template_name, template_data in self.knowledge_base.get("code_templates", {}).items():
                if self._is_relevant(query_lower, template_data):
                    relevant_knowledge["code_templates"].append({
                        "name": template_name,
                        "data": template_data
                    })
            
            # Search paper knowledge
            for paper_name, paper_data in self.paper_knowledge.items():
                if self._is_relevant(query_lower, paper_data):
                    relevant_knowledge["paper_insights"].append({
                        "paper": paper_name,
                        "data": paper_data
                    })
            
            # Search historical solutions
            if context:
                similar_contexts = self.retrieve_similar_contexts(context, limit=3)
                relevant_knowledge["historical_solutions"] = similar_contexts
            
            return relevant_knowledge
            
        except Exception as e:
            logger.error(f"Failed to retrieve relevant knowledge: {e}")
            return {}
    
    def update_knowledge_base(self, category: str, key: str, data: Dict[str, Any]) -> None:
        """Update knowledge base with new information"""
        try:
            if category not in self.knowledge_base:
                self.knowledge_base[category] = {}
            
            self.knowledge_base[category][key] = {
                **data,
                "updated_at": datetime.now().isoformat(),
                "usage_count": self.knowledge_base[category].get(key, {}).get("usage_count", 0) + 1
            }
            
            self._save_knowledge_base()
            
        except Exception as e:
            logger.error(f"Failed to update knowledge base: {e}")
    
    def learn_from_execution(self, execution_result: Dict[str, Any]) -> None:
        """Learn from execution results and update knowledge base"""
        try:
            # Extract patterns from successful executions
            if execution_result.get("status") == "success":
                self._extract_success_patterns(execution_result)
            
            # Learn from failures
            elif execution_result.get("status") == "failed":
                self._extract_failure_patterns(execution_result)
            
            # Update usage statistics
            self._update_usage_statistics(execution_result)
            
        except Exception as e:
            logger.error(f"Failed to learn from execution: {e}")
    
    def get_context_summary(self, context: Dict[str, Any]) -> str:
        """Generate a summary of the current context"""
        try:
            summary_parts = []
            
            # Input types
            if "image_path" in context:
                summary_parts.append("UI screenshot provided")
            
            if "nl_spec" in context:
                summary_parts.append("Natural language specification provided")
            
            # Generated components
            if "components" in context:
                comp_count = len(context["components"])
                summary_parts.append(f"{comp_count} UI components detected")
            
            if "endpoints" in context:
                endpoint_count = len(context["endpoints"])
                summary_parts.append(f"{endpoint_count} API endpoints generated")
            
            # Quality metrics
            if "quality_score" in context:
                score = context["quality_score"]
                summary_parts.append(f"Quality score: {score:.2f}")
            
            return "; ".join(summary_parts) if summary_parts else "No context available"
            
        except Exception as e:
            logger.error(f"Failed to generate context summary: {e}")
            return "Context summary unavailable"
    
    def get_recommendations(self, current_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get recommendations based on current context and historical data"""
        try:
            recommendations = []
            
            # Get similar historical contexts
            similar_contexts = self.retrieve_similar_contexts(current_context, limit=3)
            
            for ctx in similar_contexts:
                if ctx["context"].get("status") == "success":
                    recommendations.append({
                        "type": "historical_success",
                        "description": f"Similar successful execution: {ctx['context'].get('summary', 'N/A')}",
                        "confidence": 0.8,
                        "details": ctx["context"]
                    })
            
            # Get relevant best practices
            relevant_knowledge = self.get_relevant_knowledge(
                self.get_context_summary(current_context), 
                current_context
            )
            
            for practice in relevant_knowledge.get("best_practices", []):
                recommendations.append({
                    "type": "best_practice",
                    "description": practice["data"].get("description", ""),
                    "confidence": 0.7,
                    "details": practice["data"]
                })
            
            # Get paper-based insights
            for insight in relevant_knowledge.get("paper_insights", []):
                recommendations.append({
                    "type": "research_insight",
                    "description": f"From {insight['paper']}: {insight['data'].get('description', '')}",
                    "confidence": 0.6,
                    "details": insight["data"]
                })
            
            return sorted(recommendations, key=lambda x: x["confidence"], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return []
    
    def _hash_context(self, context: Dict[str, Any]) -> str:
        """Generate hash for context"""
        # Create a simplified version for hashing
        hashable_context = {
            "has_image": "image_path" in context,
            "has_spec": "nl_spec" in context,
            "component_count": len(context.get("components", [])),
            "endpoint_count": len(context.get("endpoints", []))
        }
        
        context_str = json.dumps(hashable_context, sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()
    
    def _calculate_context_similarity(self, ctx1: Dict[str, Any], ctx2: Dict[str, Any]) -> float:
        """Calculate similarity between two contexts"""
        try:
            # Feature extraction
            features1 = self._extract_context_features(ctx1)
            features2 = self._extract_context_features(ctx2)
            
            # Calculate similarity
            common_features = set(features1.keys()) & set(features2.keys())
            
            if not common_features:
                return 0.0
            
            similarity_sum = 0.0
            for feature in common_features:
                if isinstance(features1[feature], (int, float)) and isinstance(features2[feature], (int, float)):
                    # Numerical similarity
                    max_val = max(features1[feature], features2[feature])
                    if max_val > 0:
                        similarity_sum += 1 - abs(features1[feature] - features2[feature]) / max_val
                    else:
                        similarity_sum += 1.0
                elif features1[feature] == features2[feature]:
                    # Exact match
                    similarity_sum += 1.0
            
            return similarity_sum / len(common_features)
            
        except Exception as e:
            logger.error(f"Failed to calculate context similarity: {e}")
            return 0.0
    
    def _extract_context_features(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from context for similarity calculation"""
        features = {
            "has_image": "image_path" in context,
            "has_spec": "nl_spec" in context,
            "component_count": len(context.get("components", [])),
            "endpoint_count": len(context.get("endpoints", [])),
            "has_auth": any("auth" in str(item).lower() for item in context.get("endpoints", [])),
            "has_crud": any(method in str(context.get("endpoints", [])).lower() 
                          for method in ["post", "put", "delete"]),
            "quality_score": context.get("quality_score", 0.0)
        }
        
        return features
    
    def _is_relevant(self, query: str, data: Dict[str, Any]) -> bool:
        """Check if data is relevant to query"""
        try:
            # Convert data to searchable text
            searchable_text = json.dumps(data).lower()
            
            # Simple keyword matching
            query_words = query.split()
            matches = sum(1 for word in query_words if word in searchable_text)
            
            return matches / len(query_words) >= 0.3  # At least 30% of words match
            
        except Exception:
            return False
    
    def _extract_success_patterns(self, execution_result: Dict[str, Any]) -> None:
        """Extract patterns from successful executions"""
        try:
            # Extract UI patterns
            if "ui_components" in execution_result:
                components = execution_result["ui_components"]
                for component in components:
                    pattern_key = f"{component.get('class_label', 'unknown')}_pattern"
                    self.update_knowledge_base("ui_patterns", pattern_key, {
                        "description": f"Successful {component.get('class_label')} detection",
                        "properties": component.get("properties", {}),
                        "success_rate": 1.0
                    })
            
            # Extract API patterns
            if "api_endpoints" in execution_result:
                endpoints = execution_result["api_endpoints"]
                for endpoint in endpoints:
                    pattern_key = f"{endpoint.get('method', 'GET')}_{endpoint.get('path', '').replace('/', '_')}"
                    self.update_knowledge_base("api_patterns", pattern_key, {
                        "description": f"Successful API endpoint generation",
                        "method": endpoint.get("method"),
                        "path": endpoint.get("path"),
                        "success_rate": 1.0
                    })
            
        except Exception as e:
            logger.error(f"Failed to extract success patterns: {e}")
    
    def _extract_failure_patterns(self, execution_result: Dict[str, Any]) -> None:
        """Extract patterns from failed executions"""
        try:
            error_info = execution_result.get("error", "")
            
            # Store common failure patterns
            failure_key = f"failure_{hashlib.md5(error_info.encode()).hexdigest()[:8]}"
            self.update_knowledge_base("failure_patterns", failure_key, {
                "error": error_info,
                "context": execution_result.get("context", {}),
                "timestamp": datetime.now().isoformat(),
                "occurrence_count": 1
            })
            
        except Exception as e:
            logger.error(f"Failed to extract failure patterns: {e}")
    
    def _update_usage_statistics(self, execution_result: Dict[str, Any]) -> None:
        """Update usage statistics for knowledge base entries"""
        try:
            # Update tool usage statistics
            tools_used = execution_result.get("tools_used", [])
            for tool in tools_used:
                self.update_knowledge_base("tool_usage", tool, {
                    "usage_count": 1,
                    "last_used": datetime.now().isoformat(),
                    "success_rate": 1.0 if execution_result.get("status") == "success" else 0.0
                })
            
        except Exception as e:
            logger.error(f"Failed to update usage statistics: {e}")
    
    def _save_knowledge_base(self) -> None:
        """Save knowledge base to disk"""
        try:
            kb_path = self.memory_dir / "knowledge_base.json"
            with open(kb_path, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save knowledge base: {e}")
    
    def _save_execution_history(self) -> None:
        """Save execution history to disk"""
        try:
            history_path = self.memory_dir / "execution_history.json"
            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(self.execution_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save execution history: {e}")
    
    def _get_default_ui_patterns(self) -> Dict[str, Any]:
        """Get default UI patterns"""
        return {
            "login_form": {
                "description": "Standard login form pattern",
                "components": ["email_input", "password_input", "submit_button"],
                "layout": "vertical",
                "success_rate": 0.9
            },
            "navigation_bar": {
                "description": "Horizontal navigation bar",
                "components": ["logo", "nav_links", "user_menu"],
                "layout": "horizontal",
                "success_rate": 0.95
            },
            "card_layout": {
                "description": "Card-based content layout",
                "components": ["image", "title", "description", "action_button"],
                "layout": "grid",
                "success_rate": 0.85
            }
        }
    
    def _get_default_api_patterns(self) -> Dict[str, Any]:
        """Get default API patterns"""
        return {
            "rest_crud": {
                "description": "RESTful CRUD operations",
                "endpoints": ["GET /items", "POST /items", "PUT /items/{id}", "DELETE /items/{id}"],
                "success_rate": 0.9
            },
            "auth_endpoints": {
                "description": "Authentication endpoints",
                "endpoints": ["POST /auth/login", "POST /auth/register", "POST /auth/logout"],
                "success_rate": 0.95
            },
            "file_upload": {
                "description": "File upload endpoint",
                "endpoints": ["POST /upload"],
                "content_type": "multipart/form-data",
                "success_rate": 0.8
            }
        }
    
    def _get_default_code_templates(self) -> Dict[str, Any]:
        """Get default code templates"""
        return {
            "react_component": {
                "description": "Basic React functional component",
                "template": "const {ComponentName} = () => { return (<div>{content}</div>); };",
                "success_rate": 0.9
            },
            "fastapi_endpoint": {
                "description": "Basic FastAPI endpoint",
                "template": "@app.{method}('/{path}') async def {function_name}(): return {'message': 'success'}",
                "success_rate": 0.9
            }
        }
    
    def _get_default_best_practices(self) -> Dict[str, Any]:
        """Get default best practices"""
        return {
            "ui_accessibility": {
                "description": "Ensure UI components are accessible",
                "guidelines": ["Use semantic HTML", "Add ARIA labels", "Ensure keyboard navigation"],
                "importance": "high"
            },
            "api_security": {
                "description": "Implement proper API security",
                "guidelines": ["Use HTTPS", "Implement authentication", "Validate inputs"],
                "importance": "critical"
            },
            "code_quality": {
                "description": "Maintain high code quality",
                "guidelines": ["Use linting", "Write tests", "Document code"],
                "importance": "high"
            }
        }