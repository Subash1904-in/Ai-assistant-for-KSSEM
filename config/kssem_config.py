"""
KSSEM College Configuration File
Personalized settings for the Virtual AI Assistant system
"""

import os
from typing import Dict, List, Tuple

# KSSEM College Information
COLLEGE_INFO = {
    "name": "KSSEM College",
    "full_name": "KSSEM College of Engineering and Management",
    "location": "Bangalore, Karnataka, India",
    "established": "2001",
    "accreditation": "AICTE Approved, NBA Accredited",
    "website": "https://kssem.edu.in",
    "contact": {
        "phone": "+91-80-2848-1234",
        "email": "info@kssem.edu.in",
        "address": "KSSEM Campus, Electronic City, Bangalore - 560100"
    }
}

# Campus Buildings and Locations
CAMPUS_BUILDINGS = {
    "main_block": {
        "name": "Main Academic Block",
        "floors": 4,
        "departments": ["CSE", "ECE", "ME", "Civil", "AI&ML"],
        "coordinates": (0, 0),
        "description": "Primary academic building housing lecture halls and labs"
    },
    "library": {
        "name": "Central Library",
        "floors": 2,
        "coordinates": (50, 30),
        "description": "Digital and physical resource center with study spaces",
        "hours": "8:00 AM - 8:00 PM",
        "capacity": "200 students"
    },
    "cafeteria": {
        "name": "Student Cafeteria",
        "coordinates": (30, 60),
        "description": "Multi-cuisine food court with seating for 150",
        "hours": "7:00 AM - 9:00 PM"
    },
    "auditorium": {
        "name": "KSSEM Auditorium",
        "coordinates": (80, 20),
        "description": "500-seat auditorium for events and conferences",
        "facilities": ["Stage", "Sound System", "Projector", "Green Rooms"]
    },
    "sports_complex": {
        "name": "Sports Complex",
        "coordinates": (100, 80),
        "description": "Indoor and outdoor sports facilities",
        "facilities": ["Basketball Court", "Volleyball Court", "Gym", "Indoor Games"]
    },
    "hostels": {
        "name": "Student Hostels",
        "coordinates": (120, 40),
        "description": "Separate blocks for boys and girls",
        "capacity": "400 students",
        "facilities": ["WiFi", "24/7 Security", "Dining Hall"]
    }
}

# Department Information
DEPARTMENTS = {
    "CSE": {
        "full_name": "Computer Science and Engineering",
        "head": "Dr. Rajesh Kumar",
        "location": "Main Block, 2nd Floor",
        "labs": ["Programming Lab", "Database Lab", "Networks Lab", "AI Lab"],
        "courses": ["B.Tech CSE", "M.Tech CSE", "Ph.D CSE"]
    },
    "ECE": {
        "full_name": "Electronics and Communication Engineering",
        "head": "Dr. Priya Sharma",
        "location": "Main Block, 3rd Floor",
        "labs": ["Electronics Lab", "Communication Lab", "VLSI Lab"],
        "courses": ["B.Tech ECE", "M.Tech ECE"]
    },
    "ME": {
        "full_name": "Mechanical Engineering",
        "head": "Dr. Arun Singh",
        "location": "Main Block, 1st Floor",
        "labs": ["Machine Shop", "CAD Lab", "Thermal Lab"],
        "courses": ["B.Tech ME", "M.Tech ME"]
    },
    "AI&ML": {
        "full_name": "Artificial Intelligence and Machine Learning",
        "head": "Dr. Suresh Reddy",
        "location": "Main Block, 4th Floor",
        "labs": ["AI Lab", "ML Lab", "Robotics Lab"],
        "courses": ["B.Tech AI&ML", "M.Tech AI&ML"]
    }
}

# Campus Map Configuration
CAMPUS_MAP_CONFIG = {
    "dimensions": (200, 150),  # Width x Height in meters
    "scale": "1 pixel = 1 meter",
    "landmarks": [
        {"name": "Main Gate", "coordinates": (0, 75), "type": "entrance"},
        {"name": "Parking Area", "coordinates": (20, 70), "type": "facility"},
        {"name": "Garden", "coordinates": (40, 90), "type": "recreation"},
        {"name": "ATM", "coordinates": (25, 45), "type": "service"},
        {"name": "Medical Room", "coordinates": (35, 35), "type": "health"},
        {"name": "WiFi Hotspots", "coordinates": [(10, 10), (50, 50), (100, 100)], "type": "technology"}
    ],
    "walking_paths": [
        # Main pathways connecting buildings
        [(0, 75), (25, 75), (50, 75), (80, 75), (100, 75), (120, 75)],  # East-West path
        [(50, 0), (50, 30), (50, 60), (50, 90), (50, 120), (50, 150)],  # North-South path
        [(25, 45), (35, 35), (50, 30)],  # Library to Medical Room
        [(80, 20), (100, 80), (120, 40)]  # Auditorium to Sports to Hostels
    ]
}

# Academic Calendar and Events
ACADEMIC_CALENDAR = {
    "semester_start": "August 1, 2024",
    "semester_end": "December 15, 2024",
    "holidays": [
        "Independence Day - August 15",
        "Ganesh Chaturthi - September 7",
        "Gandhi Jayanti - October 2",
        "Diwali - November 1-3",
        "Christmas - December 25"
    ],
    "exam_periods": [
        "Mid-Semester: September 15-20",
        "End-Semester: December 1-10"
    ],
    "events": [
        "Tech Fest - October 15-17",
        "Cultural Day - November 20",
        "Alumni Meet - December 10"
    ]
}

# Library Resources
LIBRARY_RESOURCES = {
    "books": {
        "total": "25,000+",
        "categories": ["Engineering", "Management", "Literature", "Reference"],
        "digital_books": "5,000+",
        "journals": "100+ subscriptions"
    },
    "databases": [
        "IEEE Xplore",
        "Springer Link",
        "Science Direct",
        "JSTOR",
        "Google Scholar"
    ],
    "special_collections": [
        "Rare Books Section",
        "Thesis Repository",
        "Project Reports Archive",
        "Competitive Exam Materials"
    ]
}

# Student Services
STUDENT_SERVICES = {
    "academic": [
        "Course Registration",
        "Grade Reports",
        "Transcript Requests",
        "Academic Counseling"
    ],
    "administrative": [
        "ID Card Services",
        "Fee Payment",
        "Transportation",
        "Hostel Management"
    ],
    "career": [
        "Placement Cell",
        "Internship Support",
        "Career Counseling",
        "Industry Connect"
    ]
}

# Faculty Information
FACULTY_INFO = {
    "total_faculty": 85,
    "qualifications": {
        "Ph.D": "45%",
        "M.Tech": "40%",
        "B.Tech": "15%"
    },
    "research_areas": [
        "Artificial Intelligence",
        "Machine Learning",
        "IoT and Embedded Systems",
        "Renewable Energy",
        "Data Science",
        "Cybersecurity"
    ]
}

# Infrastructure Details
INFRASTRUCTURE = {
    "classrooms": {
        "lecture_halls": 25,
        "seminar_halls": 8,
        "capacity": "1500 students"
    },
    "laboratories": {
        "computer_labs": 12,
        "engineering_labs": 18,
        "research_labs": 6
    },
    "technology": {
        "wifi_coverage": "100% campus",
        "smart_classrooms": 15,
        "digital_library": "24/7 access",
        "cctv_surveillance": "Complete coverage"
    }
}

# Emergency Contacts
EMERGENCY_CONTACTS = {
    "campus_security": "+91-80-2848-1235",
    "medical_room": "+91-80-2848-1236",
    "fire_safety": "+91-80-2848-1237",
    "police_station": "100",
    "ambulance": "108"
}

# API Endpoints for College Systems
API_ENDPOINTS = {
    "moodle": "https://moodle.kssem.edu.in/api",
    "library": "https://library.kssem.edu.in/api",
    "student_portal": "https://portal.kssem.edu.in/api",
    "faculty_portal": "https://faculty.kssem.edu.in/api",
    "events": "https://events.kssem.edu.in/api"
}

# Localization Settings
LOCALIZATION = {
    "primary_language": "English",
    "supported_languages": ["English", "Kannada", "Hindi", "Telugu"],
    "timezone": "Asia/Kolkata",
    "currency": "INR",
    "date_format": "DD/MM/YYYY"
}

# Security and Privacy Settings
SECURITY_CONFIG = {
    "encryption": "AES-256",
    "gdpr_compliance": True,
    "data_retention_days": 90,
    "anonymization": True,
    "access_logging": True,
    "session_timeout_minutes": 30
}

# Performance Targets
PERFORMANCE_TARGETS = {
    "response_time_ms": 2000,  # <2 seconds
    "uptime_percentage": 99.0,
    "nlp_accuracy": 90.0,
    "navigation_precision": 90.0,
    "accessibility_compliance": 86.0
}

# Environment Variables
ENV_VARS = {
    "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
    "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
    "AWS_REGION": os.getenv("AWS_REGION", "ap-south-1"),
    "GOOGLE_CLOUD_CREDENTIALS": os.getenv("GOOGLE_CLOUD_CREDENTIALS"),
    "DATABASE_URL": os.getenv("DATABASE_URL"),
    "REDIS_URL": os.getenv("REDIS_URL", "redis://localhost:6379"),
    "API_SECRET_KEY": os.getenv("API_SECRET_KEY"),
    "ENVIRONMENT": os.getenv("ENVIRONMENT", "development")
}

# SLAM Configuration for Campus Mapping
SLAM_CONFIG = {
    "algorithm": "ORB-SLAM3",
    "sensor_type": "LiDAR + Camera",
    "mapping_frequency": "5 Hz",
    "localization_accuracy": "±0.1 meters",
    "map_update_interval": "24 hours",
    "offline_mode": True,
    "pre_mapped_areas": [
        "Main Block (100%)",
        "Library (100%)",
        "Cafeteria (100%)",
        "Auditorium (100%)",
        "Sports Complex (90%)",
        "Hostels (95%)"
    ]
}

# NLP Training Data Sources
NLP_TRAINING_DATA = {
    "faq_database": "data/kssem_faqs.json",
    "course_catalog": "data/courses.json",
    "faculty_directory": "data/faculty.json",
    "event_schedule": "data/events.json",
    "campus_services": "data/services.json"
}

# Accessibility Features
ACCESSIBILITY_FEATURES = {
    "voice_navigation": True,
    "screen_reader_support": True,
    "high_contrast_mode": True,
    "large_text_option": True,
    "multilingual_support": True,
    "gesture_control": True,
    "audio_descriptions": True
}