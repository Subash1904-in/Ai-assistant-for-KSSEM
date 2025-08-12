"""
FastAPI Backend for KSSEM Virtual AI Assistant
Provides REST API endpoints for query processing, navigation, and resource access
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import json
import asyncio
from datetime import datetime
import logging

# Internal imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from src.ai_processing_layer.nlp_engine.intent_recognition import KSSEMIntentRecognizer
from src.ai_processing_layer.slam_engine.mapping import KSSEMSLAMEngine, Point3D
from src.utils.encryption import PrivacyManager
from src.utils.logging import setup_logger

# Pydantic models for API requests/responses
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="User query text")
    user_id: Optional[str] = Field(None, description="Anonymous user identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    location: Optional[Dict[str, float]] = Field(None, description="User's current location")
    use_voice: bool = Field(False, description="Whether query came from voice input")

class NavigationRequest(BaseModel):
    destination: str = Field(..., description="Destination name or building")
    start_location: Optional[Dict[str, float]] = Field(None, description="Starting coordinates")
    preferences: Optional[Dict[str, Any]] = Field(None, description="Navigation preferences")

class QueryResponse(BaseModel):
    response: str
    intent: str
    confidence: float
    entities: Dict[str, str]
    navigation_data: Optional[Dict] = None
    additional_info: Optional[Dict] = None
    timestamp: datetime
    session_id: Optional[str] = None

class NavigationResponse(BaseModel):
    route: Dict[str, Any]
    instructions: List[str]
    distance: float
    estimated_time: float
    waypoints: List[Dict[str, float]]

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    services: Dict[str, bool]
    version: str = "1.0.0"

# Initialize FastAPI app
app = FastAPI(
    title="KSSEM Virtual AI Assistant API",
    description="RESTful API for KS School of Engineering and Management Virtual Assistant",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core components
intent_recognizer = None
slam_engine = None
privacy_manager = None
logger = None

# Initialize components at startup
@app.on_event("startup")
async def startup_event():
    """Initialize all AI components and services"""
    global intent_recognizer, slam_engine, privacy_manager, logger
    
    try:
        # Setup logging
        logger = setup_logger("kssem_api")
        logger.info("Starting KSSEM Virtual AI Assistant API")
        
        # Initialize NLP engine
        logger.info("Initializing NLP Intent Recognition Engine...")
        intent_recognizer = KSSEMIntentRecognizer()
        
        # Initialize SLAM engine
        logger.info("Initializing SLAM Navigation Engine...")
        slam_engine = KSSEMSLAMEngine()
        
        # Initialize privacy manager
        logger.info("Initializing Privacy Management...")
        privacy_manager = PrivacyManager()
        
        logger.info("✓ All components initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown"""
    if logger:
        logger.info("Shutting down KSSEM Virtual AI Assistant API")

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check the health status of all services"""
    services_status = {
        "nlp_engine": intent_recognizer is not None,
        "slam_engine": slam_engine is not None,
        "privacy_manager": privacy_manager is not None,
        "database": True,  # Add actual database check
        "api": True
    }
    
    overall_status = "healthy" if all(services_status.values()) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now(),
        services=services_status
    )

# Main query processing endpoint
@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest, background_tasks: BackgroundTasks):
    """
    Process user queries and return comprehensive responses
    """
    try:
        if not intent_recognizer:
            raise HTTPException(status_code=503, detail="NLP service not available")
        
        # Log query (anonymized)
        if logger and privacy_manager:
            anonymized_query = privacy_manager.anonymize_text(request.query)
            logger.info(f"Processing query: {anonymized_query}")
        
        # Recognize intent
        intent_result = intent_recognizer.recognize_intent(request.query)
        
        # Process based on intent
        response_text = intent_result.response_template
        navigation_data = None
        additional_info = None
        
        # Handle navigation intents
        if intent_result.intent == "navigation" and "location" in intent_result.entities:
            location = intent_result.entities["location"]
            navigation_data = await get_navigation_data(location, request.location)
            response_text = f"I'll guide you to {location}. " + response_text
        
        # Handle facility information
        elif intent_result.intent == "facility_info":
            additional_info = await get_facility_information(intent_result.entities)
        
        # Handle department information
        elif intent_result.intent == "department_info":
            additional_info = await get_department_information(intent_result.entities)
        
        # Handle faculty information
        elif intent_result.intent == "faculty_info":
            additional_info = await get_faculty_information(intent_result.entities)
        
        # Handle admission information
        elif intent_result.intent == "admission_info":
            additional_info = await get_admission_information()
        
        # Handle placement information
        elif intent_result.intent == "placement_info":
            additional_info = await get_placement_information()
        
        # Handle emergency
        elif intent_result.intent == "emergency":
            additional_info = await get_emergency_contacts()
            response_text = "🚨 " + response_text
        
        # Store query for analytics (in background)
        if privacy_manager:
            background_tasks.add_task(
                store_query_analytics,
                request.query,
                intent_result.intent,
                intent_result.confidence,
                request.session_id
            )
        
        return QueryResponse(
            response=response_text,
            intent=intent_result.intent,
            confidence=intent_result.confidence,
            entities=intent_result.entities,
            navigation_data=navigation_data,
            additional_info=additional_info,
            timestamp=datetime.now(),
            session_id=request.session_id
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Navigation endpoint
@app.post("/navigation", response_model=NavigationResponse)
async def get_navigation(request: NavigationRequest):
    """
    Calculate navigation route to destination
    """
    try:
        if not slam_engine:
            raise HTTPException(status_code=503, detail="Navigation service not available")
        
        # Convert start location to Point3D if provided
        start_point = None
        if request.start_location:
            start_point = Point3D(
                request.start_location.get("x", 200),
                request.start_location.get("y", 150),
                request.start_location.get("z", 0)
            )
        
        # Calculate route
        route = slam_engine.calculate_route(request.destination, start_point)
        
        if not route:
            raise HTTPException(status_code=404, detail=f"Destination '{request.destination}' not found")
        
        # Convert waypoints to dict format
        waypoints = [
            {"x": wp.x, "y": wp.y, "z": wp.z}
            for wp in route.waypoints
        ]
        
        return NavigationResponse(
            route={
                "start": {"x": route.start.x, "y": route.start.y, "z": route.start.z},
                "end": {"x": route.end.x, "y": route.end.y, "z": route.end.z}
            },
            instructions=route.instructions,
            distance=route.distance,
            estimated_time=route.estimated_time,
            waypoints=waypoints
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating navigation: {e}")
        raise HTTPException(status_code=500, detail="Navigation calculation failed")

# Campus information endpoints
@app.get("/campus/buildings")
async def get_buildings():
    """Get all campus buildings information"""
    try:
        if not slam_engine:
            raise HTTPException(status_code=503, detail="Campus data not available")
        
        buildings = slam_engine.campus_map.get("buildings", [])
        return {"buildings": buildings, "count": len(buildings)}
        
    except Exception as e:
        logger.error(f"Error fetching buildings: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch buildings data")

@app.get("/campus/facilities")
async def get_facilities():
    """Get all campus facilities information"""
    try:
        # Load facilities from knowledge base
        facilities_file = "/workspace/data/knowledge_base/faq.json"
        with open(facilities_file, 'r') as f:
            faq_data = json.load(f)
        
        # Extract facility-related information
        facilities = []
        for qa in faq_data.get("frequently_asked_questions", []):
            if qa["category"] == "facilities":
                facilities.append({
                    "question": qa["question"],
                    "answer": qa["answer"],
                    "keywords": qa["keywords"]
                })
        
        return {"facilities": facilities, "count": len(facilities)}
        
    except Exception as e:
        logger.error(f"Error fetching facilities: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch facilities data")

@app.get("/campus/departments")
async def get_departments():
    """Get all departments information"""
    try:
        departments_file = "/workspace/data/knowledge_base/departments.json"
        with open(departments_file, 'r') as f:
            departments_data = json.load(f)
        
        return departments_data
        
    except Exception as e:
        logger.error(f"Error fetching departments: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch departments data")

@app.get("/campus/map")
async def get_campus_map():
    """Get complete campus map data"""
    try:
        if not slam_engine:
            raise HTTPException(status_code=503, detail="Map data not available")
        
        return slam_engine.campus_map
        
    except Exception as e:
        logger.error(f"Error fetching campus map: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch map data")

# Utility functions
async def get_navigation_data(location: str, user_location: Optional[Dict]) -> Dict:
    """Get navigation data for a specific location"""
    if not slam_engine:
        return None
    
    start_point = None
    if user_location:
        start_point = Point3D(
            user_location.get("x", 200),
            user_location.get("y", 150),
            user_location.get("z", 0)
        )
    
    route = slam_engine.calculate_route(location, start_point)
    
    if route:
        return {
            "distance": route.distance,
            "estimated_time": route.estimated_time,
            "instructions": route.instructions[:3],  # First 3 instructions
            "has_full_route": True
        }
    
    return {"has_full_route": False}

async def get_facility_information(entities: Dict[str, str]) -> Dict:
    """Get detailed facility information"""
    try:
        # Load FAQ data
        faq_file = "/workspace/data/knowledge_base/faq.json"
        with open(faq_file, 'r') as f:
            faq_data = json.load(f)
        
        facility = entities.get("facility", "").lower()
        
        # Find relevant FAQ
        for qa in faq_data.get("frequently_asked_questions", []):
            if facility in qa["answer"].lower() or any(facility in keyword for keyword in qa["keywords"]):
                return {
                    "type": "facility_info",
                    "question": qa["question"],
                    "answer": qa["answer"],
                    "category": qa["category"]
                }
        
        return {"type": "facility_info", "message": "Facility information not found"}
        
    except Exception as e:
        logger.error(f"Error getting facility info: {e}")
        return {"error": "Failed to fetch facility information"}

async def get_department_information(entities: Dict[str, str]) -> Dict:
    """Get detailed department information"""
    try:
        departments_file = "/workspace/data/knowledge_base/departments.json"
        with open(departments_file, 'r') as f:
            departments_data = json.load(f)
        
        department = entities.get("department", "").lower()
        
        # Find matching department
        for dept in departments_data.get("departments", []):
            if (department in dept["name"].lower() or 
                department == dept["id"] or
                any(department in spec.lower() for spec in dept.get("specializations", []))):
                return {
                    "type": "department_info",
                    "department": dept
                }
        
        return {"type": "department_info", "message": "Department information not found"}
        
    except Exception as e:
        logger.error(f"Error getting department info: {e}")
        return {"error": "Failed to fetch department information"}

async def get_faculty_information(entities: Dict[str, str]) -> Dict:
    """Get faculty information"""
    try:
        departments_file = "/workspace/data/knowledge_base/departments.json"
        with open(departments_file, 'r') as f:
            departments_data = json.load(f)
        
        faculty_name = entities.get("faculty", "").lower()
        
        # Search through departments for faculty
        for dept in departments_data.get("departments", []):
            if "head" in dept and faculty_name in dept["head"]["name"].lower():
                return {
                    "type": "faculty_info",
                    "faculty": dept["head"],
                    "department": dept["name"],
                    "role": "Department Head"
                }
        
        return {"type": "faculty_info", "message": "Faculty information not found"}
        
    except Exception as e:
        logger.error(f"Error getting faculty info: {e}")
        return {"error": "Failed to fetch faculty information"}

async def get_admission_information() -> Dict:
    """Get admission information"""
    try:
        faq_file = "/workspace/data/knowledge_base/faq.json"
        with open(faq_file, 'r') as f:
            faq_data = json.load(f)
        
        admission_info = []
        for qa in faq_data.get("frequently_asked_questions", []):
            if qa["category"] == "admissions":
                admission_info.append({
                    "question": qa["question"],
                    "answer": qa["answer"]
                })
        
        return {"type": "admission_info", "information": admission_info}
        
    except Exception as e:
        logger.error(f"Error getting admission info: {e}")
        return {"error": "Failed to fetch admission information"}

async def get_placement_information() -> Dict:
    """Get placement information"""
    try:
        faq_file = "/workspace/data/knowledge_base/faq.json"
        with open(faq_file, 'r') as f:
            faq_data = json.load(f)
        
        for qa in faq_data.get("frequently_asked_questions", []):
            if qa["category"] == "placements":
                return {
                    "type": "placement_info",
                    "question": qa["question"],
                    "answer": qa["answer"]
                }
        
        return {"type": "placement_info", "message": "Placement information not found"}
        
    except Exception as e:
        logger.error(f"Error getting placement info: {e}")
        return {"error": "Failed to fetch placement information"}

async def get_emergency_contacts() -> Dict:
    """Get emergency contact information"""
    try:
        faq_file = "/workspace/data/knowledge_base/faq.json"
        with open(faq_file, 'r') as f:
            faq_data = json.load(f)
        
        emergency_contacts = faq_data.get("emergency_contacts", {})
        
        return {
            "type": "emergency_contacts",
            "contacts": emergency_contacts,
            "message": "🚨 Emergency contacts - Please call immediately if needed"
        }
        
    except Exception as e:
        logger.error(f"Error getting emergency contacts: {e}")
        return {"error": "Failed to fetch emergency contacts"}

async def store_query_analytics(query: str, intent: str, confidence: float, session_id: Optional[str]):
    """Store query analytics for system improvement (anonymized)"""
    try:
        if privacy_manager:
            anonymized_query = privacy_manager.anonymize_text(query)
            # Store in database or analytics system
            analytics_data = {
                "timestamp": datetime.now().isoformat(),
                "query_hash": privacy_manager.hash_text(query),
                "intent": intent,
                "confidence": confidence,
                "session_id": session_id
            }
            # In production, store in actual database
            logger.info(f"Analytics stored for intent: {intent}")
    except Exception as e:
        logger.error(f"Error storing analytics: {e}")

# Development/testing endpoints
@app.get("/test/intents")
async def test_intents():
    """Test endpoint for intent recognition"""
    if not intent_recognizer:
        raise HTTPException(status_code=503, detail="NLP service not available")
    
    test_queries = [
        "Where is the library?",
        "How do I get to CSE department?",
        "What are the library timings?",
        "Tell me about placement statistics"
    ]
    
    results = []
    for query in test_queries:
        result = intent_recognizer.recognize_intent(query)
        results.append({
            "query": query,
            "intent": result.intent,
            "confidence": result.confidence,
            "entities": result.entities
        })
    
    return {"test_results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")