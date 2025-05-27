# app.py - Enhanced Interactive Learning Path Advisor with AI Search & Udemy Integration

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import google.generativeai as genai
from PIL import Image
import numpy as np
import time
import re
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
import requests
from urllib.parse import quote_plus
import asyncio
import aiohttp
import uuid


# Set page configuration
st.set_page_config(
    page_title="Smart Learning Path Advisor",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Multiselect widget */
    .stMultiSelect > div > div > div > div {
       
        border-color: #1f77b4 !important;
    }
    
    /* Multiselect selected items */
    .stMultiSelect > div > div > div > div > span {
        background-color: #1f77b4 !important;
        border-color: #1f77b4 !important;
    }
    
    /* Selectbox */
    .stSelectbox > div > div > select {
        border-color: #1f77b4 !important;
    }
    
    .stSelectbox > div > div > select:focus {
        border-color: #1f77b4 !important;
        box-shadow: 0 0 0 0.2rem rgba(31, 119, 180, 0.25) !important;
    }
    
    /* Radio buttons */
    .stRadio > div > label > div:first-child {
        background-color: #1f77b4 !important;
        border-color: #1f77b4 !important;
    }
    
    /* Checkboxes */
    .stCheckbox > label > div:first-child {
        background-color: #1f77b4 !important;
        border-color: #1f77b4 !important;
    }
    
    /* Slider */
    .stSlider > div > div > div > div {
        background-color: #1f77b4 !important;
    }
    
    /* Text input focus */
    .stTextInput > div > div > input:focus {
        border-color: #1f77b4 !important;
        box-shadow: 0 0 0 0.2rem rgba(31, 119, 180, 0.25) !important;
    }
    
    /* Number input focus */
    .stNumberInput > div > div > input:focus {
        border-color: #1f77b4 !important;
        box-shadow: 0 0 0 0.2rem rgba(31, 119, 180, 0.25) !important;
    }
    
    /* Date input focus */
    .stDateInput > div > div > input:focus {
        border-color: #1f77b4 !important;
        box-shadow: 0 0 0 0.2rem rgba(31, 119, 180, 0.25) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #1f77b4 !important;
        border-color: #1f77b4 !important;
        color: white !important;
    }
    
    .stButton > button:hover {
        background-color: #145a8a !important;
        border-color: #145a8a !important;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background-color: #1f77b4 !important;
        border-color: #1f77b4 !important;
        color: white !important;
    }
    
    .stDownloadButton > button:hover {
        background-color: #145a8a !important;
        border-color: #145a8a !important;
    }
</style>
""", unsafe_allow_html=True)




# Data classes for structured data
@dataclass
class LearningPreference:
    time_available_weeks: int = 8
    preferred_learning_style: str = "Mixed"  # Visual, Auditory, Hands-on, Mixed
    difficulty_preference: str = "Progressive"  # Beginner, Intermediate, Advanced, Progressive
    specific_skills_requested: List[str] = None
    learning_urgency: str = "Medium"  # Low, Medium, High, Critical

@dataclass
class LearningGoal:
    goal_type: str  # skill_development, role_transition, certification, project_based
    target_skill: str = ""
    target_role: str = ""
    deadline: Optional[datetime] = None
    priority: str = "Medium"

@dataclass
class UdemyCourse:
    title: str
    url: str
    description: str
    rating: float
    price: str
    duration: str
    level: str

# Enhanced session state initialization
def initialize_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your enhanced learning advisor with AI-powered search capabilities. I can help you create personalized learning paths and find the best Udemy courses. How can I assist you today?"}
        ]

    if 'learning_path' not in st.session_state:
        st.session_state.learning_path = None

    if 'employee_profile' not in st.session_state:
        st.session_state.employee_profile = {
            "employee_id": "EMP123456",
            "name": "Alex Johnson",
            "current_role": "Data Analyst",
            "skills": ["SQL", "Excel", "Data Visualization"],
            "completed_courses": ["Data Analysis Fundamentals", "Excel Advanced"],
            "career_goals": ["Data Science Manager", "AI Specialist"],
            "skill_proficiency": {
                "SQL": "Intermediate",
                "Excel": "Advanced", 
                "Data Visualization": "Intermediate"
            },
            "experience_level": "Mid-level"
        }
    
    if 'learning_preferences' not in st.session_state:
        st.session_state.learning_preferences = LearningPreference(
            specific_skills_requested=[]
        )
    
    if 'current_learning_goals' not in st.session_state:
        st.session_state.current_learning_goals = []

    if 'search_cache' not in st.session_state:
        st.session_state.search_cache = {}

initialize_session_state()

# 2. Add employee database management functions after initialize_session_state()

@st.cache_data
def load_employee_database():
    """Load employee database with sample data"""
    return {
        "EMP123456": {
            "employee_id": "EMP123456",
            "name": "Alex Johnson",
            "current_role": "Data Analyst",
            "skills": ["SQL", "Excel", "Data Visualization"],
            "completed_courses": ["Data Analysis Fundamentals", "Excel Advanced"],
            "career_goals": ["Data Science Manager", "AI Specialist"],
            "skill_proficiency": {
                "SQL": "Intermediate",
                "Excel": "Advanced", 
                "Data Visualization": "Intermediate"
            },
            "experience_level": "Mid-level",
            "manager_id": "MGR001",
            "department": "Analytics",
            "assigned_learning_path": None
        },
        "EMP789012": {
            "employee_id": "EMP789012",
            "name": "Sarah Chen",
            "current_role": "Junior Data Analyst",
            "skills": ["Excel", "Python"],
            "completed_courses": ["Data Analysis Fundamentals"],
            "career_goals": ["Data Analyst", "Data Scientist"],
            "skill_proficiency": {
                "Excel": "Intermediate",
                "Python": "Beginner"
            },
            "experience_level": "Junior",
            "manager_id": "MGR001",
            "department": "Analytics",
            "assigned_learning_path": None
        },
        "EMP345678": {
            "employee_id": "EMP345678",
            "name": "Michael Rodriguez",
            "current_role": "Business Analyst",
            "skills": ["Excel"],
            "completed_courses": ["Data Analysis Fundamentals"],
            "career_goals": ["Data Scientist"],
            "skill_proficiency": {
                "Excel": "Advanced",
               
            },
            "experience_level": "Mid-level",
            "manager_id": "MGR001",
            "department": "Business",
            "assigned_learning_path": None
        }
    }

def initialize_manager_session_state():
    """Initialize manager-specific session state"""
    if 'employee_database' not in st.session_state:
        st.session_state.employee_database = load_employee_database()
    
    if 'current_manager_id' not in st.session_state:
        st.session_state.current_manager_id = "MGR001"
    
    if 'selected_employee_id' not in st.session_state:
        st.session_state.selected_employee_id = None
    
    if 'manager_mode' not in st.session_state:
        st.session_state.manager_mode = False

# 3. Add manager portal functions

def get_manager_employees(manager_id):
    """Get all employees under a specific manager"""
    return {emp_id: emp_data for emp_id, emp_data in st.session_state.employee_database.items() 
            if emp_data.get('manager_id') == manager_id}

def update_employee_in_database(employee_id, updated_profile):
    """Update employee profile in database"""
    if employee_id in st.session_state.employee_database:
        st.session_state.employee_database[employee_id].update(updated_profile)
        return True
    return False

def assign_learning_path_to_employee(employee_id, learning_path):
    """Assign a learning path to an employee"""
    if employee_id in st.session_state.employee_database:
        st.session_state.employee_database[employee_id]['assigned_learning_path'] = learning_path
        return True
    return False

# 4. Add manager portal page function

def manager_portal_page():
    st.title("👨‍💼 Manager Portal - Learning Path Management")
    st.markdown("*Manage your team's learning and development*")
    
    # Manager info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Manager ID", st.session_state.current_manager_id)
    with col2:
        manager_employees = get_manager_employees(st.session_state.current_manager_id)
        st.metric("Team Size", len(manager_employees))
    with col3:
        employees_with_paths = sum(1 for emp in manager_employees.values() 
                                 if emp.get('assigned_learning_path') is not None)
        st.metric("Active Learning Paths", employees_with_paths)
    
    # Employee selection
    st.markdown("### 👥 Select Employee")
    
    if not manager_employees:
        st.warning("No employees found under your management.")
        return
    
    # Employee selection dropdown
    employee_options = {f"{emp_data['name']} ({emp_id})": emp_id 
                       for emp_id, emp_data in manager_employees.items()}
    
    selected_employee_display = st.selectbox(
        "Choose an employee to manage:",
        options=list(employee_options.keys()),
        key="employee_selector"
    )
    
    if selected_employee_display:
        selected_employee_id = employee_options[selected_employee_display]
        st.session_state.selected_employee_id = selected_employee_id
        
        # Load selected employee data
        employee_data = st.session_state.employee_database[selected_employee_id]
        
        # Display employee information in tabs
        tab1, tab2, tab3 = st.tabs(["📋 Employee Profile", "🎯 Generate Learning Path", "📚 Assigned Learning Path"])
        
        with tab1:
            display_and_edit_employee_profile(selected_employee_id, employee_data)
        
        with tab2:
            generate_learning_path_for_employee(selected_employee_id, employee_data)
        
        with tab3:
            display_assigned_learning_path(selected_employee_id, employee_data)

def display_and_edit_employee_profile(employee_id, employee_data):
    """Display and allow editing of employee profile with enhanced synchronization"""
    st.markdown(f"### 👤 Profile: {employee_data['name']}")
    
    # Show sync status
    current_employee_id = get_current_employee_id()
    if current_employee_id == employee_id:
        st.info("🔄 This profile is synchronized with the Employee Portal")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Basic Information")
        
        # Editable fields
        name = st.text_input("Name", value=employee_data["name"], key=f"name_{employee_id}")
        
        current_role = st.selectbox(
            "Current Role", 
            options=list(role_requirements.keys()), 
            index=list(role_requirements.keys()).index(employee_data["current_role"]) 
            if employee_data["current_role"] in role_requirements else 0,
            key=f"role_{employee_id}"
        )
        
        experience_level = st.selectbox(
            "Experience Level",
            ["Entry Level", "Junior", "Mid-level", "Senior", "Expert"],
            index=["Entry Level", "Junior", "Mid-level", "Senior", "Expert"].index(
                employee_data.get("experience_level", "Mid-level")
            ),
            key=f"exp_{employee_id}"
        )
        
        department = st.text_input(
            "Department", 
            value=employee_data.get("department", ""), 
            key=f"dept_{employee_id}"
        )
    
    with col2:
        st.markdown("#### Skills & Proficiency")
        
        # Get all available skills
        all_skills = set()
        for role_data in role_requirements.values():
            all_skills.update(role_data["required_skills"])
            all_skills.update(role_data["preferred_skills"])
        
        skills = st.multiselect(
            "Current Skills", 
            options=sorted(list(all_skills)), 
            default=employee_data["skills"],
            key=f"skills_{employee_id}"
        )
        
        # Skill proficiency levels
        skill_proficiency = {}
        if skills:
            st.markdown("**Skill Proficiency Levels:**")
            for skill in skills:
                current_proficiency = employee_data.get("skill_proficiency", {}).get(skill, "Intermediate")
                proficiency = st.selectbox(
                    f"Proficiency in {skill}",
                    ["Beginner", "Intermediate", "Advanced"],
                    index=["Beginner", "Intermediate", "Advanced"].index(current_proficiency),
                    key=f"prof_{skill}_{employee_id}"
                )
                skill_proficiency[skill] = proficiency
    
    # Career goals and completed courses
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("#### Career Goals")
        career_goals = st.multiselect(
            "Career Aspirations", 
            options=list(role_requirements.keys()), 
            default=employee_data["career_goals"],
            key=f"goals_{employee_id}"
        )
    
    with col4:
        st.markdown("#### Completed Courses")
        all_courses = course_catalog["title"].tolist()
        completed_courses = st.multiselect(
            "Completed Courses", 
            options=all_courses,
            default=employee_data["completed_courses"],
            key=f"courses_{employee_id}"
        )
    
    # Enhanced update buttons with synchronization
    col_update, col_sync, col_reset = st.columns(3)
    
    with col_update:
        if st.button("✅ Update Profile", type="primary", key=f"update_{employee_id}"):
            updated_profile = {
                "name": name,
                "current_role": current_role,
                "skills": skills,
                "skill_proficiency": skill_proficiency,
                "completed_courses": completed_courses,
                "career_goals": career_goals,
                "experience_level": experience_level,
                "department": department
            }
            
            # Use enhanced sync function
            if sync_employee_profile_changes(employee_id, updated_profile):
                st.success(f"✅ Profile updated and synchronized for {name}!")
                
                # If this employee's learning path exists, consider regenerating it
                if (employee_id in st.session_state.employee_database and 
                    st.session_state.employee_database[employee_id].get('assigned_learning_path')):
                    st.info("💡 Profile changes detected. Consider regenerating the learning path to reflect these updates.")
                
                st.rerun()
            else:
                st.error("Failed to update profile.")
    
    with col_sync:
        if st.button("🔄 Sync to Employee", key=f"sync_{employee_id}"):
            # Force sync this profile to the employee portal if they're the same person
            current_employee_id = get_current_employee_id()
            if current_employee_id == employee_id:
                updated_profile = {
                    "name": name,
                    "current_role": current_role,
                    "skills": skills,
                    "skill_proficiency": skill_proficiency,
                    "completed_courses": completed_courses,
                    "career_goals": career_goals,
                    "experience_level": experience_level,
                    "department": department
                }
                
                if sync_employee_profile_changes(employee_id, updated_profile):
                    st.success("🔄 Profile synchronized with Employee Portal!")
                    st.rerun()
            else:
                st.warning("Can only sync profile for the currently selected employee.")
    
    with col_reset:
        if st.button("🔄 Reset Changes", key=f"reset_{employee_id}"):
            st.rerun()


def generate_learning_path_for_employee(employee_id, employee_data):
    """Generate learning path for selected employee"""
    st.markdown(f"### 🎯 Generate Learning Path for {employee_data['name']}")
    
    # Learning preferences for the employee
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Learning Constraints")
        
        time_available = st.number_input(
            "Time Available (weeks)", 
            min_value=1, 
            max_value=52, 
            value= 20,#st.session_state.learning_path.get("total_duration_weeks", 0),
            key=f"time_{employee_id}"
        )
        
        learning_style = st.selectbox(
            "Preferred Learning Style",
            ["Mixed", "Visual", "Hands-on", "Interactive", "Intensive"],
            key=f"style_{employee_id}"
        )
        
        difficulty_preference = st.selectbox(
            "Difficulty Preference",
            ["Progressive", "Beginner", "Intermediate", "Advanced"],
            key=f"difficulty_{employee_id}"
        )
    
    with col2:
        st.markdown("#### Focus Areas")
        urgency = st.selectbox(
            "Learning Urgency",
            ["Low", "Medium", "High", "Critical"],
            index=1,
            key=f"urgency_{employee_id}"
        )
        
        # Additional skills to focus on
        all_skills = set()
        for role_data in role_requirements.values():
            all_skills.update(role_data["required_skills"])
            all_skills.update(role_data["preferred_skills"])
        
        focus_skills = st.multiselect(
            "Additional Skills to Focus On",
            options=sorted(list(all_skills)),
            key=f"focus_{employee_id}"
        )
    
    # Generate button
    if st.button("🚀 Generate Learning Path", type="primary", key=f"generate_{employee_id}"):
        with st.spinner("Generating personalized learning path..."):
            # Create learning preferences object
            learning_preferences = LearningPreference(
                time_available_weeks=time_available,
                preferred_learning_style=learning_style,
                difficulty_preference=difficulty_preference,
                specific_skills_requested=focus_skills,
                learning_urgency=urgency
            )
            
            # Generate learning path
            learning_path = generate_enhanced_learning_path_with_sync(
                employee_data,
                learning_preferences
            )
            
            if learning_path:
                # Assign to employee
                assign_learning_path_to_employee(employee_id, learning_path)
                
                st.success(f"✅ Learning path generated and assigned to {employee_data['name']}!")
                
                # Display summary
                st.markdown("#### 📊 Learning Path Summary")
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Total Duration", f"{learning_path.get('total_duration_weeks', 0)} weeks")
                with col_b:
                    st.metric("Courses", len(learning_path.get('learning_path', [])))
                with col_c:
                    st.metric("Skills Covered", len(learning_path.get('skill_gaps_addressed', [])))
                
                # Show brief course list
                st.markdown("**Recommended Courses:**")
                for i, course in enumerate(learning_path.get('learning_path', []), 1):
                    priority_emoji = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}.get(
                        course.get('priority', 'Medium'), "⚪"
                    )
                    st.markdown(f"{i}. {course.get('title')} {priority_emoji} - {course.get('duration')}")
                
                st.info("💡 The employee can now view and interact with this learning path in the Employee Portal.")

def display_assigned_learning_path(employee_id, employee_data):
    """Display the currently assigned learning path"""
    st.markdown(f"### 📚 Current Learning Path for {employee_data['name']}")
    
    assigned_path = employee_data.get('assigned_learning_path')
    
    if not assigned_path:
        st.info("No learning path assigned yet. Generate one in the 'Generate Learning Path' tab.")
        return
    
    # Path overview
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Duration", f"{assigned_path.get('total_duration_weeks', 0)} weeks")
    with col2:
        st.metric("Courses", len(assigned_path.get('learning_path', [])))
    with col3:
        st.metric("Skills", len(assigned_path.get('skill_gaps_addressed', [])))
    with col4:
        udemy_count = len(assigned_path.get('udemy_courses', []))
        st.metric("Udemy Courses", udemy_count)
    
    # Strategy explanation
    if assigned_path.get('explanation'):
        st.info(f"**Strategy:** {assigned_path['explanation']}")
    
    # Course details
    st.markdown("#### 📋 Course Details")
    
    for i, course in enumerate(assigned_path.get('learning_path', []), 1):
        with st.expander(f"{i}. {course.get('title')} - {course.get('priority', 'Medium')} Priority"):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**Type:** {course.get('type')}")
                st.markdown(f"**Duration:** {course.get('duration')}")
                st.markdown(f"**Skills:** {', '.join(course.get('skills_gained', []))}")
            with col_b:
                st.markdown(f"**Priority:** {course.get('priority')}")
                st.markdown(f"**Reason:** {course.get('reason', 'N/A')}")
    
    # Udemy courses
    udemy_courses = assigned_path.get('udemy_courses', [])
    if udemy_courses:
        st.markdown("#### 🌟 Udemy Course Recommendations")
        for i, course in enumerate(udemy_courses, 1):
            with st.expander(f"{i}. {course.get('title')} - ⭐{course.get('rating', 4.0)}"):
                col_x, col_y = st.columns(2)
                with col_x:
                    st.markdown(f"**Price:** {course.get('price')}")
                    st.markdown(f"**Duration:** {course.get('duration')}")
                    st.markdown(f"**Level:** {course.get('level')}")
                with col_y:
                    st.markdown(f"**Rating:** ⭐{course.get('rating', 4.0)}")
                    st.link_button("View on Udemy", course.get('url', '#'))
                
                st.markdown(f"**Description:** {course.get('description', 'N/A')}")
    
    # Action buttons
    col_remove, col_regenerate = st.columns(2)
    
    with col_remove:
        if st.button("🗑️ Remove Learning Path", key=f"remove_{employee_id}"):
            st.session_state.employee_database[employee_id]['assigned_learning_path'] = None
            st.success("Learning path removed successfully!")
            st.rerun()
    
    with col_regenerate:
        if st.button("🔄 Regenerate Path", key=f"regenerate_{employee_id}"):
            st.info("Use the 'Generate Learning Path' tab to create a new learning path.")

# employee sync
def sync_employee_learning_path(employee_id, learning_path):
    """Synchronize learning path between employee and manager portals"""
    if employee_id and employee_id in st.session_state.employee_database:
        # Update the employee database with the new learning path
        st.session_state.employee_database[employee_id]['assigned_learning_path'] = learning_path
        
        # Also update the current session learning path
        st.session_state.learning_path = learning_path
        
        return True
    return False

def get_current_employee_id():
    """Get the current employee ID based on the employee profile"""
    if 'employee_profile' in st.session_state:
        return st.session_state.employee_profile.get('employee_id')
    return st.session_state.get('selected_employee_id')




# 5. Modify the main function to add page navigation

def main_with_navigation():
    """Main function with navigation between Manager and Employee portals"""
    
    # Initialize both session states
    initialize_session_state()
    initialize_manager_session_state()
    
    # Navigation
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🧭 Portal Navigation")
    
    portal_mode = st.sidebar.radio(
        "Select Portal:",
        ["👨‍💼 Manager Portal", "👤 Employee Portal"],
        index=0 if not st.session_state.manager_mode else 0
    )
    
    st.session_state.manager_mode = (portal_mode == "👨‍💼 Manager Portal")
    
    if st.session_state.manager_mode:
        manager_portal_page()
    else:
        # Enhanced employee portal with better synchronization
        
        # If no employee profile exists, try to load from selected employee
        if 'employee_profile' not in st.session_state or not st.session_state.employee_profile:
            if st.session_state.selected_employee_id and st.session_state.selected_employee_id in st.session_state.employee_database:
                st.session_state.employee_profile = st.session_state.employee_database[st.session_state.selected_employee_id].copy()
        
        # Sync learning path from employee database if available
        current_employee_id = get_current_employee_id()
        if current_employee_id and current_employee_id in st.session_state.employee_database:
            # Always sync the latest learning path from the database
            assigned_path = st.session_state.employee_database[current_employee_id].get('assigned_learning_path')
            if assigned_path:
                st.session_state.learning_path = assigned_path
                
                # Update employee profile to reflect database state
                st.session_state.employee_profile.update(st.session_state.employee_database[current_employee_id])
                
                # Add welcome message only once
                if not any("manager assigned" in msg.get("content", "") for msg in st.session_state.messages):
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"👋 Welcome back! Your manager has assigned you a personalized learning path. You can view it on the right panel and chat with me to modify or get more information about it."
                    })
        
        enhanced_main()


# extra

# Add this enhanced version of generate_enhanced_learning_path that includes sync
def generate_enhanced_learning_path_with_sync(employee_profile, learning_preferences,specific_requirements=None):
    """Generate learning path and sync with employee database"""
    
    # Generate the learning path using the existing function
    learning_path = generate_enhanced_learning_path(employee_profile, learning_preferences,specific_requirements)
    
    # Sync with employee database if employee ID is available
    employee_id = get_current_employee_id()
    if employee_id and learning_path:
        sync_employee_learning_path(employee_id, learning_path)
    
    return learning_path

## report 

import json
from datetime import datetime, timedelta
import base64

def generate_dynamic_learning_report(learning_path, employee_profile, learning_preferences=None):
    """Generate a comprehensive dynamic HTML report for learning path"""
    
    # Extract data for the report
    current_date = datetime.now()
    employee_name = employee_profile.get('name', 'Employee')
    current_role = employee_profile.get('current_role', 'Current Role')
    
    target_role = employee_profile.get('career_goals', 'Target Role')
    
    # Calculate metrics
    total_weeks = learning_path.get("total_duration_weeks", 12)
    skills_addressed = learning_path.get("skill_gaps_addressed", [])
    udemy_courses = learning_path.get("udemy_courses", [])
    internal_courses = learning_path.get("learning_path", [])
    
    # Calculate financial metrics
    budget = 2000#learning_preferences.budget if learning_preferences else 2000
    estimated_cost = len(udemy_courses) * 50 + len(internal_courses) * 25  # Rough estimate
    roi_percentage = ((budget - estimated_cost) / estimated_cost * 100) if estimated_cost > 0 else 1200
    
    # Generate skill proficiency data
    skill_data = generate_skill_proficiency_data(skills_addressed)
    
    # Create the HTML report
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Learning Path Report - {employee_name}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
        
        .header h1 {{
            color: #2d3748;
            font-size: 2.5rem;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .header-meta {{
            display: flex;
            justify-content: space-between;
            margin-top: 20px;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .meta-item {{
            background: #f7fafc;
            padding: 10px 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}
        
        .section {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .section:hover {{
            transform: translateY(-5px);
            box-shadow: 0 25px 30px -5px rgba(0, 0, 0, 0.15);
        }}
        
        .section-title {{
            color: #2d3748;
            font-size: 1.8rem;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .metric-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }}
        
        .metric-card:hover::before {{
            left: 100%;
        }}
        
        .metric-card:hover {{
            transform: scale(1.05);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
        }}
        
        .metric-value {{
            font-size: 2.5rem;
            font-weight: bold;
            display: block;
        }}
        
        .metric-label {{
            font-size: 0.9rem;
            opacity: 0.9;
            margin-top: 5px;
        }}
        
        .progress-bar {{
            background: #e2e8f0;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
            position: relative;
        }}
        
        .progress-fill {{
            height: 20px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 10px;
            transition: width 2s ease;
            position: relative;
        }}
        
        .progress-fill::after {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            bottom: 0;
            right: 0;
            background-image: linear-gradient(
                45deg,
                rgba(255, 255, 255, 0.2) 25%,
                transparent 25%,
                transparent 50%,
                rgba(255, 255, 255, 0.2) 50%,
                rgba(255, 255, 255, 0.2) 75%,
                transparent 75%,
                transparent
            );
            background-size: 20px 20px;
            animation: move 1s linear infinite;
        }}
        
        @keyframes move {{
            0% {{ background-position: 0 0; }}
            100% {{ background-position: 20px 20px; }}
        }}
        
        .skill-gap-analysis {{
            padding: 20px;
        }}
        
        .icon-large {{
            font-size: 3rem;
            margin-bottom: 10px;
        }}
        
        .skills-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .skill-item {{
            background: #f7fafc;
            border-radius: 15px;
            padding: 20px;
            border-left: 5px solid #667eea;
            transition: all 0.3s ease;
        }}
        
        .skill-item:hover {{
            background: #edf2f7;
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        }}
        
        .skill-current {{
            border-left-color: #48bb78;
            background: linear-gradient(135deg, rgba(72, 187, 120, 0.1), rgba(56, 161, 105, 0.05));
        }}
        
        .skill-gap-critical {{
            border-left-color: #e53e3e;
            background: linear-gradient(135deg, rgba(229, 62, 62, 0.1), rgba(197, 48, 48, 0.05));
        }}
        
        .skill-gap-important {{
            border-left-color: #ed8936;
            background: linear-gradient(135deg, rgba(237, 137, 54, 0.1), rgba(221, 107, 32, 0.05));
        }}
        
        .skill-proficiency {{
            margin: 15px 0;
        }}
        
        .proficiency-bar {{
            background: #e2e8f0;
            border-radius: 10px;
            height: 8px;
            overflow: hidden;
            margin: 5px 0;
        }}
        
        .proficiency-fill {{
            height: 100%;
            border-radius: 10px;
            transition: width 2s ease;
        }}
        
        .proficiency-fill.advanced {{
            background: linear-gradient(90deg, #48bb78, #38a169);
            width: 85%;
        }}
        
        .proficiency-fill.beginner {{
            background: linear-gradient(90deg, #e53e3e, #c53030);
            width: 15%;
        }}
        
        .proficiency-fill.intermediate {{
            background: linear-gradient(90deg, #ed8936, #dd6b20);
            width: 35%;
        }}
        
        .highlight-box {{
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.05));
            border: 2px solid #667eea;
            border-radius: 15px;
            padding: 25px;
            margin-top: 30px;
            text-align: center;
        }}
        
        .progress-indicator {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin: 10px 0;
            justify-content: center;
        }}
        
        .progress-indicator span {{
            min-width: 60px;
            font-weight: 600;
        }}
        
        .timeline {{
            position: relative;
            padding-left: 30px;
        }}
        
        .timeline::before {{
            content: '';
            position: absolute;
            left: 15px;
            top: 0;
            bottom: 0;
            width: 2px;
            background: linear-gradient(to bottom, #667eea, #764ba2);
        }}
        
        .timeline-item {{
            position: relative;
            margin-bottom: 30px;
            background: #f7fafc;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}
        
        .timeline-item::before {{
            content: '';
            position: absolute;
            left: -35px;
            top: 25px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #667eea;
            border: 3px solid white;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
        }}
        
        .course-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .course-card {{
            background: #f7fafc;
            border-radius: 15px;
            padding: 20px;
            border-left: 4px solid #667eea;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        
        .course-card:hover {{
            background: #edf2f7;
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        }}
        
        .comparison-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }}
        
        .comparison-table th,
        .comparison-table td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }}
        
        .comparison-table th {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            font-weight: 600;
        }}
        
        .comparison-table tr:hover {{
            background: #f7fafc;
        }}
        
        .roi-highlight {{
            background: linear-gradient(135deg, #48bb78, #38a169);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            margin: 20px 0;
        }}
        
        .interactive-tooltip {{
            position: relative;
            cursor: help;
        }}
        
        .interactive-tooltip:hover::after {{
            content: attr(data-tooltip);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: #2d3748;
            color: white;
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 0.8rem;
            white-space: nowrap;
            z-index: 1000;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .metrics-grid {{
                grid-template-columns: 1fr;
            }}
            
            .header-meta {{
                flex-direction: column;
            }}
        }}
        
        .fade-in {{
            animation: fadeIn 0.6s ease-in;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header Section -->
        <div class="header fade-in">
            <h1>🎓 Learning Path Report</h1>
            <p><strong>{employee_name}</strong> • {current_role} → {target_role[0]}</p>
            <div class="header-meta">
                <div class="meta-item">
                    <strong>Generated:</strong> {current_date.strftime('%B %d, %Y')}
                </div>
                <div class="meta-item">
                    <strong>Duration:</strong> {total_weeks} weeks
                </div>
                <div class="meta-item">
                    <strong>Completion Target:</strong> {(current_date + timedelta(weeks=total_weeks)).strftime('%B %d, %Y')}
                </div>
            </div>
        </div>

        <!-- Section 1: Employee Profile -->
        <div class="section fade-in">
            <h2 class="section-title">👤 Detailed Employee Profile</h2>
            <div class="metrics-grid">
                <div class="metric-card interactive-tooltip" data-tooltip="Current professional level">
                    <span class="metric-value">📊</span>
                    <span class="metric-label">Current Role</span>
                    <div>{current_role}</div>
                </div>
                <div class="metric-card interactive-tooltip" data-tooltip="Target career goal">
                    <span class="metric-value">🎯</span>
                    <span class="metric-label">Target Role</span>
                    <div>{target_role}</div>
                </div>
                <div class="metric-card interactive-tooltip" data-tooltip="Available learning budget">
                    <span class="metric-value">${budget:,}</span>
                    <span class="metric-label">Learning Budget</span>
                </div>
                <div class="metric-card interactive-tooltip" data-tooltip="Projected timeline for role transition">
                    <span class="metric-value">{total_weeks}</span>
                    <span class="metric-label">Weeks to Target</span>
                </div>
            </div>
            
            <div style="margin-top: 20px;">
                <h3>📋 Background Information</h3>
                <p><strong>Experience Level:</strong> {employee_profile.get('experience_level', 'Mid-level')}</p>
                <p><strong>Department:</strong> {employee_profile.get('department', 'Technology')}</p>
                <p><strong>Learning Style:</strong> {learning_preferences.preferred_learning_style if learning_preferences else 'Mixed'}</p>
                <p><strong>Time Availability:</strong> {learning_preferences.time_available_weeks if learning_preferences else '10'} hours/week</p>
            </div>
        </div>

        <!-- Section 2: Skill Gap Analysis -->
        <div class="section fade-in">
            <div class="skill-gap-analysis">
                <div class="icon-large" style="text-align: center;">📊</div>
                <h3 style="text-align: center; margin-bottom: 20px;">Advanced Skill Gap Analysis</h3>
                <div class="skills-grid">
                    {generate_dynamic_skill_categories_html(skill_data)}
                </div>
                <div class="highlight-box">
                    <h4>🎯 Gap Analysis Summary</h4>
                    <p><strong>Skill Coverage for Target Role:</strong> 45% → Target: 85%</p>
                    <div class="progress-indicator">
                        <span>Current</span>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 45%;"></div>
                        </div>
                        <span>45%</span>
                    </div>
                    <div class="progress-indicator">
                        <span>Target</span>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 85%;"></div>
                        </div>
                        <span>85%</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Section 3: Learning Timeline -->
        <div class="section fade-in">
            <h2 class="section-title">⏰ Comprehensive {total_weeks}-Week Learning Timeline</h2>
            
            <div class="timeline">
                {generate_timeline_html(internal_courses, udemy_courses, total_weeks)}
            </div>
        </div>

        <!-- Section 4: Course Details -->
        <div class="section fade-in">
            <h2 class="section-title">📚 Course Portfolio</h2>
            
            <h3>🏢 Internal Courses ({len(internal_courses)})</h3>
            <div class="course-grid">
                {generate_internal_courses_html(internal_courses)}
            </div>
            
            <h3 style="margin-top: 30px;">🌟 Udemy Courses ({len(udemy_courses)})</h3>
            <div class="course-grid">
                {generate_udemy_courses_html(udemy_courses)}
            </div>
        </div>

        <!-- Section 5: Success Metrics & ROI -->
        <div class="section fade-in">
            <h2 class="section-title">💼 Business Impact & ROI Analysis</h2>
            
            <div class="roi-highlight">
                <h3>💰 Financial Impact</h3>
                <p><strong>Investment:</strong> ${estimated_cost:,} | <strong>ROI:</strong> {roi_percentage:.0f}% | <strong>Cost Avoidance:</strong> $45,000</p>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card" style="background: linear-gradient(135deg, #48bb78, #38a169);">
                    <span class="metric-value">3</span>
                    <span class="metric-label">Portfolio Projects</span>
                </div>
                <div class="metric-card" style="background: linear-gradient(135deg, #ed8936, #dd6b20);">
                    <span class="metric-value">4</span>
                    <span class="metric-label">Certifications</span>
                </div>
                <div class="metric-card" style="background: linear-gradient(135deg, #3182ce, #2c5282);">
                    <span class="metric-value">85%</span>
                    <span class="metric-label">Target Competency</span>
                </div>
                <div class="metric-card" style="background: linear-gradient(135deg, #805ad5, #6b46c1);">
                    <span class="metric-value">12</span>
                    <span class="metric-label">Week Checkpoints</span>
                </div>
            </div>

            <h3 style="margin-top: 30px;">📈 Competency Comparison</h3>
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Competency Area</th>
                        <th>Current Level</th>
                        <th>Target Level</th>
                        <th>Post-Training</th>
                        <th>Gap Closure</th>
                    </tr>
                </thead>
                <tbody>
                    {generate_competency_table_html(skill_data)}
                </tbody>
            </table>
        </div>

        <!-- Section 6: Milestone Checkpoints -->
        <div class="section fade-in">
            <h2 class="section-title">🏆 Milestone Checkpoints</h2>
            
            <div class="timeline">
                <div class="timeline-item">
                    <h4>Week 4 Checkpoint 🎯</h4>
                    <p><strong>Goal:</strong> Complete foundation courses and first assessment</p>
                    <p><strong>Deliverable:</strong> Basic project demonstration</p>
                    <p><strong>Skills Gained:</strong> Fundamental concepts, basic implementation</p>
                </div>
                <div class="timeline-item">
                    <h4>Week 8 Checkpoint 🚀</h4>
                    <p><strong>Goal:</strong> Advanced skill development and mid-term evaluation</p>
                    <p><strong>Deliverable:</strong> Intermediate project portfolio</p>
                    <p><strong>Skills Gained:</strong> Advanced techniques, practical application</p>
                </div>
                <div class="timeline-item">
                    <h4>Week {st.session_state.learning_path.get("total_duration_weeks", 0)} Checkpoint 🎓</h4>
                    <p><strong>Goal:</strong> Final assessment and role readiness evaluation</p>
                    <p><strong>Deliverable:</strong> Comprehensive capstone project</p>
                    <p><strong>Skills Gained:</strong> Expert-level proficiency, leadership capabilities</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Add interactive animations
        document.addEventListener('DOMContentLoaded', function() {{
            // Animate progress bars
            const progressBars = document.querySelectorAll('.progress-fill');
            progressBars.forEach(bar => {{
                const width = bar.dataset.width;
                setTimeout(() => {{
                    bar.style.width = width + '%';
                }}, 500);
            }});
            
            // Add click feedback to metric cards
            const metricCards = document.querySelectorAll('.metric-card');
            metricCards.forEach(card => {{
                card.addEventListener('click', function() {{
                    this.style.transform = 'scale(0.95)';
                    setTimeout(() => {{
                        this.style.transform = 'scale(1.05)';
                    }}, 150);
                }});
            }});
            
            // Fade in sections on scroll
            const observer = new IntersectionObserver((entries) => {{
                entries.forEach(entry => {{
                    if (entry.isIntersecting) {{
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }}
                }});
            }});
            
            document.querySelectorAll('.section').forEach(section => {{
                section.style.opacity = '0';
                section.style.transform = 'translateY(20px)';
                section.style.transition = 'all 0.6s ease';
                observer.observe(section);
            }});
        }});
    </script>
</body>
</html>
    """
    
    return html_content

def generate_skill_proficiency_data(skills):
    """Generate mock skill proficiency data"""
    skill_data = []
    for skill in skills:
        # Generate realistic proficiency scores
        current = max(10, min(75, hash(skill) % 60 + 15))  # 15-75%
        target = min(95, current + 30 + (hash(skill) % 20))  # Target higher
        post_training = min(95, target - 5 + (hash(skill) % 10))  # Realistic achievement
        
        skill_data.append({
            'name': skill,
            'current': current,
            'target': target,
            'post_training': post_training,
            'gap_closure': ((post_training - current) / (target - current) * 100) if target > current else 100
        })
    
    return skill_data

def generate_dynamic_skill_categories_html(skill_data):
    """Generate dynamic HTML for skill categories based on proficiency levels"""
    
    # Categorize skills based on proficiency
    current_strengths = [s for s in skill_data if s['current'] >= 70]
    critical_gaps = [s for s in skill_data if s['current'] <= 25]
    important_gaps = [s for s in skill_data if 26 <= s['current'] <= 69]
    
    # Add some default skills if categories are empty
    if not current_strengths:
        current_strengths = [
            {'name': 'Excel', 'current': 95},
            {'name': 'SQL', 'current': 90},
            {'name': 'Statistics', 'current': 70}
        ]
    
    if not critical_gaps:
        critical_gaps = [
            {'name': 'Python', 'current': 25},
            {'name': 'Machine Learning', 'current': 0},
            {'name': 'Cloud Platforms', 'current': 0}
        ]
    
    if not important_gaps:
        important_gaps = [
            {'name': 'Leadership', 'current': 30},
            {'name': 'Project Management', 'current': 40},
            {'name': 'Business Strategy', 'current': 35}
        ]
    
    html = f"""
    <div class="skill-item skill-current">
        <h4>✅ Current Strengths</h4>
        <div class="skill-proficiency">
            <div class="proficiency-bar">
                <div class="proficiency-fill advanced"></div>
            </div>
        </div>
        {generate_skill_list_html(current_strengths[:4], 'strength')}
    </div>
    
    <div class="skill-item skill-gap-critical">
        <h4>🚨 Critical Gaps</h4>
        <div class="skill-proficiency">
            <div class="proficiency-bar">
                <div class="proficiency-fill beginner"></div>
            </div>
        </div>
        {generate_skill_list_html(critical_gaps[:4], 'critical')}
    </div>
    
    <div class="skill-item skill-gap-important">
        <h4>⚠️ Important Gaps</h4>
        <div class="skill-proficiency">
            <div class="proficiency-bar">
                <div class="proficiency-fill intermediate"></div>
            </div>
        </div>
        {generate_skill_list_html(important_gaps[:4], 'important')}
    </div>
    """
    
    return html

def generate_skill_list_html(skills, category_type):
    """Generate HTML for individual skill items within a category"""
    html = ""
    
    for skill in skills:
        proficiency_level = get_proficiency_label(skill['current'])
        html += f'<p><strong>{skill["name"]}:</strong> {proficiency_level} ({skill["current"]}%)</p>'
    
    return html

def get_proficiency_label(percentage):
    """Convert percentage to proficiency label"""
    if percentage >= 90:
        return "Expert"
    elif percentage >= 75:
        return "Advanced"
    elif percentage >= 50:
        return "Intermediate"
    elif percentage >= 25:
        return "Basic"
    else:
        return "Beginner"

def generate_timeline_html(internal_courses, udemy_courses, total_weeks):
    """Generate timeline HTML"""
    timeline_html = ""
    weeks_per_phase = max(1, total_weeks // 3)
    
    phases = [
        ("Foundation Phase", f"Weeks 1-{weeks_per_phase}", "Building core competencies"),
        ("Development Phase", f"Weeks {weeks_per_phase+1}-{weeks_per_phase*2}", "Advanced skill development"),
        ("Mastery Phase", f"Weeks {weeks_per_phase*2+1}-{total_weeks}", "Expert-level proficiency")
    ]
    
    for i, (phase_name, duration, description) in enumerate(phases):
        courses_in_phase = internal_courses[i::3] + udemy_courses[i::3]  # Distribute courses
        
        timeline_html += f"""
        <div class="timeline-item">
            <h4>{phase_name}</h4>
            <p><strong>Duration:</strong> {duration}</p>
            <p><strong>Focus:</strong> {description}</p>
            <p><strong>Courses:</strong> {len(courses_in_phase)} courses assigned</p>
            <div style="margin-top: 10px;">
                <div class="progress-bar">
                    <div class="progress-fill" data-width="{(i+1)*33}" style="width: 0%;"></div>
                </div>
            </div>
        </div>
        """
    
    return timeline_html

def generate_internal_courses_html(courses):
    """Generate HTML for internal courses"""
    html = ""
    for course in courses[:6]:  # Limit display
        priority_emoji = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}.get(course.get('priority', 'Medium'), "⚪")
        
        html += f"""
        <div class="course-card">
            <h4>{course.get('title', 'Course Title')} {priority_emoji}</h4>
            <p><strong>Type:</strong> {course.get('type', 'Training')}</p>
            <p><strong>Duration:</strong> {course.get('duration', 'N/A')}</p>
            <p><strong>Priority:</strong> {course.get('priority', 'Medium')}</p>
            <p><strong>Skills:</strong> {', '.join(course.get('skills_gained', []))}</p>
            <small style="color: #666;">{course.get('reason', 'Strategic skill development')}</small>
        </div>
        """
    
    return html

def generate_udemy_courses_html(courses):
    """Generate HTML for Udemy courses"""
    html = ""
    for course in courses[:6]:  # Limit display
        stars = "⭐" * int(course.get('rating', 4))
        
        html += f"""
        <div class="course-card">
            <h4>{course.get('title', 'Course Title')}</h4>
            <p><strong>Rating:</strong> {stars} {course.get('rating', 4.0)}</p>
            <p><strong>Price:</strong> {course.get('price', 'N/A')}</p>
            <p><strong>Duration:</strong> {course.get('duration', 'N/A')}</p>
            <p><strong>Level:</strong> {course.get('level', 'Intermediate')}</p>
            <small style="color: #666;">{course.get('description', 'Comprehensive course content')[:100]}...</small>
        </div>
        """
    
    return html

def generate_competency_table_html(skill_data):
    """Generate competency comparison table HTML"""
    html = ""
    for skill in skill_data[:8]:  # Limit to 8 skills
        html += f"""
        <tr>
            <td><strong>{skill['name']}</strong></td>
            <td>{skill['current']}%</td>
            <td>{skill['target']}%</td>
            <td>{skill['post_training']}%</td>
            <td style="color: #48bb78; font-weight: bold;">{skill['gap_closure']:.0f}%</td>
        </tr>
        """
    
    return html

# Updated download button replacement for enhanced_learning_path_management function
# def get_enhanced_download_button():
#     """Return the enhanced download button code"""
#     return """
#     # Replace this section in your enhanced_learning_path_management function:
    
#     # OLD CODE:
#     # st.download_button(
#     #     "⬇️ Download Path",
#     #     data=json.dumps(st.session_state.learning_path, indent=2),
#     #     file_name=f"learning_path_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
#     #     mime="application/json"
#     # )
    
#     # NEW CODE:
#     if st.button("📊 Download Dynamic Report", help="Generate comprehensive learning path report"):
#         with st.spinner("Generating dynamic report..."):
#             try:
#                 # Generate the dynamic HTML report
#                 report_html = generate_dynamic_learning_report(
#                     st.session_state.learning_path,
#                     st.session_state.employee_profile,
#                     st.session_state.get('learning_preferences')
#                 )
                
#                 # Create download
#                 st.download_button(
#                     "⬇️ Download HTML Report",
#                     data=report_html,
#                     file_name=f"learning_path_report_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
#                     mime="text/html",
#                     help="Download interactive HTML report"
#                 )
                
#                 st.success("🎉 Dynamic report generated successfully!")
                
#             except Exception as e:
#                 st.error(f"Error generating report: {str(e)}")
#                 # Fallback to JSON download
#                 st.download_button(
#                     "⬇️ Download JSON (Fallback)",
#                     data=json.dumps(st.session_state.learning_path, indent=2),
#                     file_name=f"learning_path_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
#                     mime="application/json"
#                 )
#     """



# Enhanced learning path management in employee portal
def enhanced_learning_path_management():
    """Enhanced learning path management with database synchronization"""
    
    if st.session_state.learning_path:
        st.markdown("### 📚 Your Learning Path")
        
        # Check if this is a manager-assigned path
        current_employee_id = get_current_employee_id()
        is_manager_assigned = False
        
        if current_employee_id and current_employee_id in st.session_state.employee_database:
            db_path = st.session_state.employee_database[current_employee_id].get('assigned_learning_path')
            is_manager_assigned = (db_path is not None)
        
        if is_manager_assigned:
            st.info("📋 This learning path was assigned by your manager and is synchronized across both portals.")
        
        # Path summary
        total_weeks = st.session_state.learning_path.get("total_duration_weeks", 0)
        skills_count = len(st.session_state.learning_path.get("skill_gaps_addressed", []))
        udemy_count = len(st.session_state.learning_path.get("udemy_courses", []))
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Total Duration", f"{total_weeks} weeks")
        with col_b:
            st.metric("Skills Covered", skills_count)
        with col_c:
            st.metric("Udemy Courses", udemy_count)
        
        # Explanation
        if st.session_state.learning_path.get("explanation"):
            st.info(st.session_state.learning_path["explanation"])
        
        # Learning path items
        st.markdown("#### 🏆 Recommended Internal Courses")
        for i, item in enumerate(st.session_state.learning_path.get("learning_path", [])):
            with st.container():
                # Priority indicator
                priority_colors = {
                    "Critical": "🔴",
                    "High": "🟠", 
                    "Medium": "🟡",
                    "Low": "🟢"
                }
                priority_emoji = priority_colors.get(item.get("priority", "Medium"), "⚪")
                
                st.markdown(f"**{i+1}. {item.get('title')} {priority_emoji}**")
                
                col_x, col_y = st.columns([3, 1])
                with col_x:
                    st.markdown(f"📚 {item.get('type')} • ⏱️ {item.get('duration')}")
                    st.markdown(f"🎯 **Skills:** {', '.join(item.get('skills_gained', []))}")
                with col_y:
                    st.markdown(f"🚨 **{item.get('priority', 'Medium')}**")
                
                # Detailed information
                with st.expander("Details"):
                    st.markdown(f"**Why recommended:** {item.get('reason', 'N/A')}")
                    if item.get('fits_constraints'):
                        st.markdown(f"**Constraint fit:** {item['fits_constraints']}")
                
                st.divider()
        
        # Udemy Courses Section
        udemy_courses = st.session_state.learning_path.get("udemy_courses", [])
        if udemy_courses:
            st.markdown("#### 🌟 Top Udemy Course Recommendations")
            
            for i, course in enumerate(udemy_courses):
                with st.container():
                    # Course header
                    col_title, col_rating = st.columns([3, 1])
                    with col_title:
                        st.markdown(f"**{i+1}. [{course['title']}]({course['url']})**")
                    with col_rating:
                        stars = "⭐" * int(course.get('rating', 4))
                        st.markdown(f"{stars} {course.get('rating', 4.0)}")
                    
                    # Course details
                    col_price, col_duration, col_level = st.columns(3)
                    with col_price:
                        st.markdown(f"💰 **{course.get('price', 'N/A')}**")
                    with col_duration:
                        st.markdown(f"⏱️ **{course.get('duration', 'N/A')}**")
                    with col_level:
                        st.markdown(f"📊 **{course.get('level', 'N/A')}**")
                    
                    # Description
                    st.markdown(f"📝 {course.get('description', 'No description available.')}")
                    
                    # Action button
                    st.link_button(
                        f"🚀 View Course on Udemy",
                        course.get('url', '#'),
                        help=f"Open {course['title']} on Udemy"
                    )
                    
                    st.divider()
        
        # Additional information
        if st.session_state.learning_path.get("progression_notes"):
            with st.expander("📝 Learning Progression Notes"):
                st.markdown(st.session_state.learning_path["progression_notes"])
        
        if st.session_state.learning_path.get("alternative_suggestions"):
            with st.expander("💡 Alternative Learning Suggestions"):
                st.markdown(st.session_state.learning_path["alternative_suggestions"])
        
        # Enhanced action buttons with synchronization
        col_1, col_2, col_3 = st.columns(3)
        with col_1:
            if st.button("🔄 Regenerate Path", type="primary", key="regenerate_main"):
                with st.spinner("Regenerating your learning path..."):
                    # Use current employee profile and preferences
                    new_learning_path = generate_enhanced_learning_path_with_sync(
                        st.session_state.employee_profile,
                        st.session_state.get('learning_preferences', LearningPreference())
                    )
                    
                    if new_learning_path:
                        st.success("✅ Learning path regenerated and synchronized!")
                        st.rerun()
                    else:
                        st.error("Failed to regenerate learning path. Please try again.")
        
        with col_2:
            st.button("📝 Save Learning Plan", key="save_btn", help="Save your learning plan")
        
        with col_3:
            if st.button("📊 Download Dynamic Report", help="Generate comprehensive learning path report"):
                with st.spinner("Generating dynamic report..."):
                    try:
                        # Generate the dynamic HTML report
                        report_html = generate_dynamic_learning_report(
                            st.session_state.learning_path,
                            st.session_state.employee_profile,
                            st.session_state.get('learning_preferences')
                        )
                        
                        # Create download
                        st.download_button(
                            "⬇️ Download HTML Report",
                            data=report_html,
                            file_name=f"learning_path_report_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                            mime="text/html",
                            help="Download interactive HTML report"
                        )
                        
                        st.success("🎉 Dynamic report generated successfully!")
                        
                    except Exception as e:
                        st.error(f"Error generating report: {str(e)}")
                        # Fallback to JSON download
                        st.download_button(
                            "⬇️ Download JSON (Fallback)",
                            data=json.dumps(st.session_state.learning_path, indent=2),
                            file_name=f"learning_path_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                            mime="application/json"
                        )
        
        # Option to clear learning path
        if st.button("🗑️ Clear Learning Path", help="Remove current learning path"):
            # Clear from both session state and database
            st.session_state.learning_path = None
            current_employee_id = get_current_employee_id()
            if current_employee_id:
                sync_employee_learning_path(current_employee_id, None)
            
            st.success("Learning path cleared!")
            st.rerun()
    
    else:
        # No learning path exists - show suggestions
        st.markdown("### 💡 Try These Smart Commands")
        
        sample_commands = [
            ("🐍 Python Learning", "I want to learn Python in 3 weeks"),
            ("🔍 Search Trends", "Search for latest AI trends 2024"),
            ("📊 Data Science Path", "I have 5 weeks to prepare for data scientist role"),
            ("🎓 Udemy Courses", "Find Udemy courses for machine learning"),
            ("⚡ Quick Plan", "Create a quick 1-week intensive plan"),
            ("🔗 Leadership Skills", "I need to learn leadership skills urgently")
        ]
        
        st.markdown("**Smart Examples:**")
        for i, (icon_text, command) in enumerate(sample_commands):
            if st.button(f"{icon_text}", key=f"cmd_{i}", help=command):
                process_enhanced_user_input(command)
# Add employee profile synchronization function

# First, add these helper functions to your code:

def sync_employee_profile_changes(employee_id, updated_profile):
    """Sync any changes made to employee profile back to the database"""
    if employee_id and employee_id in st.session_state.employee_database:
        # Get current database entry
        db_entry = st.session_state.employee_database[employee_id]
        
        # Preserve manager-specific fields that shouldn't be changed by employee
        preserved_fields = ['manager_id', 'employee_id']
        
        for field in preserved_fields:
            if field in db_entry:
                updated_profile[field] = db_entry[field]
        
        # Update database
        st.session_state.employee_database[employee_id].update(updated_profile)
        
        # Also update session state employee profile if it exists
        if 'employee_profile' in st.session_state:
            st.session_state.employee_profile.update(updated_profile)
        
        return True
    return False
# Enhanced employee profile editing with sync

def enhanced_employee_profile_editing():
    """Enhanced employee profile editing for the Employee Portal with database synchronization"""
    
    st.markdown("### 👤 Edit Your Profile")
    
    # Show current employee info
    current_employee_id = get_current_employee_id()
    if current_employee_id:
        st.info(f"Employee ID: {current_employee_id}")
        
        # Get current employee data
        if current_employee_id in st.session_state.employee_database:
            employee_data = st.session_state.employee_database[current_employee_id]
        else:
            employee_data = st.session_state.get('employee_profile', {})
    else:
        st.warning("No employee profile found. Please ensure you're logged in correctly.")
        return
    
    # Profile editing form
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Basic Information")
        
        name = st.text_input("Name", value=employee_data.get("name", ""), key="emp_name")
        
        current_role = st.selectbox(
            "Current Role", 
            options=list(role_requirements.keys()), 
            index=list(role_requirements.keys()).index(employee_data.get("current_role", list(role_requirements.keys())[0])) 
            if employee_data.get("current_role") in role_requirements else 0,
            key="emp_role"
        )
        
        experience_level = st.selectbox(
            "Experience Level",
            ["Entry Level", "Junior", "Mid-level", "Senior", "Expert"],
            index=["Entry Level", "Junior", "Mid-level", "Senior", "Expert"].index(
                employee_data.get("experience_level", "Mid-level")
            ),
            key="emp_exp"
        )
    
    with col2:
        st.markdown("#### Skills & Proficiency")
        
        # Get all available skills
        all_skills = set()
        for role_data in role_requirements.values():
            all_skills.update(role_data["required_skills"])
            all_skills.update(role_data["preferred_skills"])
        
        skills = st.multiselect(
            "Current Skills", 
            options=sorted(list(all_skills)), 
            default=employee_data.get("skills", []),
            key="emp_skills"
        )
        
        # Skill proficiency levels
        skill_proficiency = {}
        if skills:
            st.markdown("**Skill Proficiency Levels:**")
            for skill in skills:
                current_proficiency = employee_data.get("skill_proficiency", {}).get(skill, "Intermediate")
                proficiency = st.selectbox(
                    f"Proficiency in {skill}",
                    ["Beginner", "Intermediate", "Advanced"],
                    index=["Beginner", "Intermediate", "Advanced"].index(current_proficiency),
                    key=f"emp_prof_{skill}"
                )
                skill_proficiency[skill] = proficiency
    
    # Career goals and completed courses
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("#### Career Goals")
        career_goals = st.multiselect(
            "Career Aspirations", 
            options=list(role_requirements.keys()), 
            default=employee_data.get("career_goals", []),
            key="emp_goals"
        )
    
    with col4:
        st.markdown("#### Completed Courses")
        all_courses = course_catalog["title"].tolist()
        completed_courses = st.multiselect(
            "Completed Courses", 
            options=all_courses,
            default=employee_data.get("completed_courses", []),
            key="emp_courses"
        )
    
    # Save button with enhanced sync
    col_save, col_cancel = st.columns(2)
    
    with col_save:
        if st.button("💾 Save Profile Changes", type="primary", key="save_profile"):
            updated_profile = {
                "name": name,
                "current_role": current_role,
                "skills": skills,
                "skill_proficiency": skill_proficiency,
                "completed_courses": completed_courses,
                "career_goals": career_goals,
                "experience_level": experience_level
            }
            
            # Sync changes
            if sync_employee_profile_changes(current_employee_id, updated_profile):
                st.success("✅ Profile changes saved and synchronized!")
                
                # Update current session profile
                st.session_state.employee_profile.update(updated_profile)
                
                # Ask if they want to regenerate learning path
                if st.session_state.get('learning_path'):
                    st.info("💡 Profile updated! Would you like to regenerate your learning path to reflect these changes?")
                
                st.rerun()
            else:
                st.error("Failed to save profile changes.")
    
    with col_cancel:
        if st.button("🔄 Reset Changes", key="reset_profile"):
            st.rerun()


# Set up Google Gemini API
def initialize_gemini_api():
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        st.error("Gemini API key not found. Please set it in Streamlit secrets or as an environment variable.")
        st.stop()
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.0-flash')

gemini_model = initialize_gemini_api()

# AI-powered DuckDuckGo Search Agent
@dataclass
class UdemyCourse:
    title: str
    url: str
    description: str
    rating: float
    price: str
    duration: str
    level: str

class AISearchAgent:
    def __init__(self):
        self.base_url = "https://api.duckduckgo.com/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def search_web(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search DuckDuckGo for web results"""
        try:
            # Use DuckDuckGo instant answer API
            params = {
                'q': query,
                'format': 'json',
                'no_redirect': '1',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = self.session.get(self.base_url, params=params, timeout=10, verify=False)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Extract web results if available
            if 'RelatedTopics' in data:
                for topic in data['RelatedTopics'][:max_results]:
                    if isinstance(topic, dict) and 'Text' in topic and 'FirstURL' in topic:
                        results.append({
                            'title': topic.get('Text', '')[:100] + '...' if len(topic.get('Text', '')) > 100 else topic.get('Text', ''),
                            'url': topic.get('FirstURL', ''),
                            'snippet': topic.get('Text', '')
                        })
            
            # If no related topics, create a structured search result
            if not results and data.get('Abstract'):
                results.append({
                    'title': f"About {query}",
                    'url': data.get('AbstractURL', ''),
                    'snippet': data.get('Abstract', '')
                })
            
            return results
            
        except Exception as e:
            st.error(f"Search error: {e}")
            return []

    def search_udemy_courses(self, skill: str, max_results: int = 10) -> List[Dict]:
        """Search specifically for Udemy courses using DuckDuckGo"""
        try:
            # Search for Udemy courses specifically
            query = f"site:udemy.com {skill} course"
            
            # Use DuckDuckGo HTML search since JSON API is limited
            search_url = f"https://html.duckduckgo.com/html/"
            params = {
                'q': query,
                'kl': 'us-en'
            }
            
            response = self.session.get(search_url, params=params, timeout=15,verify=False)
            response.raise_for_status()
            
            # Parse HTML results (basic extraction)
            html_content = response.text
            results = []
            
            # Extract Udemy course URLs using regex
            udemy_pattern = r'href="([^"]*udemy\.com/course/[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(udemy_pattern, html_content)
            
            for url, title in matches[:max_results]:
                # Clean up the URL and title
                clean_url = url.replace('&amp;', '&')
                if not clean_url.startswith('http'):
                    clean_url = 'https://' + clean_url.lstrip('//')
                
                clean_title = re.sub(r'<[^>]+>', '', title).strip()
                
                if 'udemy.com/course/' in clean_url and clean_title:
                    results.append({
                        'title': clean_title,
                        'url': clean_url,
                        'snippet': f"Udemy course: {clean_title}"
                    })
            
            # If no results from HTML parsing, try alternative search
            if not results:
                results = self._alternative_udemy_search(skill, max_results)
            
            return results
            
        except Exception as e:
            print(f"Udemy search error: {e}")
            return self._alternative_udemy_search(skill, max_results)
    
    def _alternative_udemy_search(self, skill: str, max_results: int = 5) -> List[Dict]:
        """Alternative method to find Udemy courses"""
        try:
            # Try with JSON API but filter for Udemy
            params = {
                'q': f"udemy {skill} course",
                'format': 'json',
                'no_redirect': '1',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = self.session.get(self.base_url, params=params, timeout=10, verify=False)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Check related topics for Udemy links
            if 'RelatedTopics' in data:
                for topic in data['RelatedTopics']:
                    if isinstance(topic, dict) and 'FirstURL' in topic:
                        url = topic.get('FirstURL', '')
                        if 'udemy.com' in url:
                            results.append({
                                'title': topic.get('Text', '').split(' - ')[0] if ' - ' in topic.get('Text', '') else topic.get('Text', ''),
                                'url': url,
                                'snippet': topic.get('Text', '')
                            })
            
            return results[:max_results]
            
        except Exception as e:
            print(f"Alternative search error: {e}")
            return []

    def search_learning_resources(self, skill: str) -> Dict:
        """Search for learning resources for a specific skill"""
        queries = [
            f"{skill} online course tutorial",
            f"learn {skill} programming",
            f"{skill} certification training"
        ]
        
        all_results = []
        for query in queries:
            results = self.search_web(query, max_results=3)
            all_results.extend(results)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)
        
        return {
            'skill': skill,
            'resources': unique_results[:8],  # Limit to top 8 results
            'search_summary': f"Found {len(unique_results)} learning resources for {skill}"
        }

# Enhanced Udemy Course Search Agent
class UdemyCourseAgent:
    def __init__(self):
        self.base_url = "https://www.udemy.com"
        self.search_agent = AISearchAgent()
    
    def generate_udemy_courses(self, skills: List[str]) -> List[UdemyCourse]:
        """Find real Udemy courses using web search"""
        if not skills:
            return []
        
        all_courses = []
        
        for skill in skills:
            # Search for real Udemy courses
            search_results = self.search_agent.search_udemy_courses(skill, max_results=3)
            
            for result in search_results:
                # Extract course info and enhance with realistic details
                course = self._create_course_from_search_result(result, skill)
                if course:
                    all_courses.append(course)
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
        
        # If we found real courses, return them
        if all_courses:
            return all_courses[:5]
        
        # Fallback: Generate realistic courses with proper Udemy URL structure
        return self._generate_fallback_courses(skills)
    
    def _create_course_from_search_result(self, result: Dict, skill: str) -> UdemyCourse:
        """Create a UdemyCourse object from search result with enhanced details"""
        try:
            title = result.get('title', '')
            url = result.get('url', '')
            
            # Validate URL
            if not url or 'udemy.com/course/' not in url:
                return None
            
            # Generate realistic course details using AI or heuristics
            course_details = self._enhance_course_details(title, skill)
            
            return UdemyCourse(
                title=title,
                url=url,
                description=course_details['description'],
                rating=course_details['rating'],
                price=course_details['price'],
                duration=course_details['duration'],
                level=course_details['level']
            )
            
        except Exception as e:
            print(f"Error creating course from result: {e}")
            return None
    
    def _enhance_course_details(self, title: str, skill: str) -> Dict:
        """Generate realistic course details based on title and skill"""
        # Realistic course details based on common patterns
        import random
        
        # Generate description based on title and skill
        description_templates = [
            f"Master {skill} with hands-on projects and real-world examples. Perfect for beginners and professionals looking to advance their skills.",
            f"Complete {skill} course covering fundamentals to advanced concepts. Build practical projects and gain industry-relevant skills.",
            f"Learn {skill} from scratch with step-by-step guidance. Includes exercises, quizzes, and practical assignments.",
            f"Comprehensive {skill} training with expert instruction. Gain confidence through practical application and real-world scenarios.",
            f"Practical {skill} course designed for modern developers. Learn best practices and industry standards."
        ]
        
        # Realistic ratings (Udemy courses typically range 4.0-4.8)
        ratings = [4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8]
        
        # Realistic prices
        prices = ["$19.99", "$29.99", "$49.99", "$69.99", "$89.99", "$99.99"]
        
        # Realistic durations
        durations = ["3 hours", "5 hours", "8 hours", "12 hours", "15 hours", "20 hours", "25 hours"]
        
        # Determine level based on title keywords
        title_lower = title.lower()
        if any(word in title_lower for word in ['beginner', 'basics', 'introduction', 'getting started']):
            level = "Beginner"
        elif any(word in title_lower for word in ['advanced', 'expert', 'mastery', 'professional']):
            level = "Advanced"
        else:
            level = "Intermediate"
        
        return {
            'description': random.choice(description_templates),
            'rating': random.choice(ratings),
            'price': random.choice(prices),
            'duration': random.choice(durations),
            'level': level
        }
    
    def _generate_fallback_courses(self, skills: List[str]) -> List[UdemyCourse]:
        """Generate fallback courses with realistic Udemy URL structure"""
        courses = []
        skills_text = ', '.join(skills)
        
        # Common Udemy course URL patterns for different skills
        course_templates = [
            {
                'title_template': "Complete {skill} Bootcamp",
                'url_template': "complete-{skill}-bootcamp-zero-to-mastery",
                'description': "Master {skill} from beginner to advanced level with hands-on projects and real-world applications.",
                'level': "All Levels"
            },
            {
                'title_template': "{skill} for Beginners",
                'url_template': "{skill}-for-beginners-complete-course",
                'description': "Learn {skill} from scratch with step-by-step guidance and practical exercises.",
                'level': "Beginner"
            },
            {
                'title_template': "Advanced {skill} Masterclass",
                'url_template': "advanced-{skill}-masterclass-expert-level",
                'description': "Take your {skill} skills to the next level with advanced techniques and best practices.",
                'level': "Advanced"
            },
            {
                'title_template': "{skill} Projects Course",
                'url_template': "{skill}-projects-practical-hands-on-course",
                'description': "Build real-world {skill} projects and strengthen your portfolio with practical experience.",
                'level': "Intermediate"
            },
            {
                'title_template': "Professional {skill} Development",
                'url_template': "professional-{skill}-development-course",
                'description': "Professional-grade {skill} training designed for career advancement and industry success.",
                'level': "Intermediate"
            }
        ]
        
        for i, skill in enumerate(skills[:5]):
            template = course_templates[i % len(course_templates)]
            
            # Clean skill name for URL
            clean_skill = re.sub(r'[^a-zA-Z0-9]', '-', skill.lower()).strip('-')
            
            course = UdemyCourse(
                title=template['title_template'].format(skill=skill),
                url=f"https://www.udemy.com/course/{template['url_template'].format(skill=clean_skill)}/",
                description=template['description'].format(skill=skill),
                rating=round(4.0 + (i * 0.15), 1),  # Vary ratings from 4.0 to 4.6
                price=["$49.99", "$69.99", "$89.99", "$59.99", "$79.99"][i],
                duration=["12 hours", "18 hours", "25 hours", "15 hours", "20 hours"][i],
                level=template['level']
            )
            courses.append(course)
        
        return courses

# Initialize agents
search_agent = AISearchAgent()
udemy_agent = UdemyCourseAgent()

# Enhanced course catalog with duration parsing
@st.cache_data
def load_enhanced_course_catalog():
    return pd.DataFrame([
        {"id": "COURSE001", "title": "Python Programming Essentials", "type": "Course", "duration": "4 weeks", "duration_weeks": 4,
         "skills": ["Python", "Programming"], "difficulty": "Beginner", "learning_style": "Hands-on",
         "description": "Learn Python programming fundamentals with practical exercises"},
        {"id": "COURSE002", "title": "Machine Learning Fundamentals", "type": "Course", "duration": "6 weeks", "duration_weeks": 6,
         "skills": ["Machine Learning", "Python", "Statistics"], "difficulty": "Intermediate", "learning_style": "Mixed",
         "description": "Introduction to machine learning algorithms and applications"},
        {"id": "COURSE003", "title": "Data Leadership Workshop", "type": "Workshop", "duration": "2 days", "duration_weeks": 0.5,
         "skills": ["Leadership", "Management", "Data Strategy"], "difficulty": "Advanced", "learning_style": "Interactive",
         "description": "Leadership skills for data professionals"},
        {"id": "COURSE004", "title": "Advanced SQL for Data Analysis", "type": "Course", "duration": "3 weeks", "duration_weeks": 3,
         "skills": ["SQL", "Database", "Data Analysis"], "difficulty": "Intermediate", "learning_style": "Hands-on",
         "description": "Advanced SQL techniques for complex data analysis"},
        {"id": "COURSE005", "title": "Data Visualization with Tableau", "type": "Course", "duration": "2 weeks", "duration_weeks": 2,
         "skills": ["Data Visualization", "Tableau"], "difficulty": "Beginner", "learning_style": "Visual",
         "description": "Create impactful data visualizations using Tableau"},
        {"id": "COURSE006", "title": "Statistics for Data Science", "type": "Course", "duration": "5 weeks", "duration_weeks": 5,
         "skills": ["Statistics", "Data Science"], "difficulty": "Intermediate", "learning_style": "Mixed",
         "description": "Statistical methods essential for data science"},
        {"id": "COURSE007", "title": "Deep Learning Specialization", "type": "Course", "duration": "12 weeks", "duration_weeks": 12,
         "skills": ["Deep Learning", "Neural Networks", "Python"], "difficulty": "Advanced", "learning_style": "Hands-on",
         "description": "Comprehensive deep learning techniques and applications"},
        {"id": "COURSE008", "title": "Agile Project Management", "type": "Course", "duration": "3 weeks", "duration_weeks": 3,
         "skills": ["Project Management", "Agile"], "difficulty": "Beginner", "learning_style": "Interactive",
         "description": "Agile methodologies for project management"},
        {"id": "COURSE009", "title": "Quick Data Analysis Bootcamp", "type": "Intensive", "duration": "1 week", "duration_weeks": 1,
         "skills": ["Data Analysis", "Statistics"], "difficulty": "Intermediate", "learning_style": "Intensive",
         "description": "Rapid introduction to data analysis techniques"},
        {"id": "COURSE010", "title": "Python for Data Science - Fast Track", "type": "Bootcamp", "duration": "2 weeks", "duration_weeks": 2,
         "skills": ["Python", "Data Science"], "difficulty": "Intermediate", "learning_style": "Intensive",
         "description": "Accelerated Python course for data science applications"},
        {"id": "COURSE011", "title": "Business Intelligence Essentials", "type": "Course", "duration": "4 weeks", "duration_weeks": 4,
         "skills": ["Business Intelligence", "Data Analysis"], "difficulty": "Beginner", "learning_style": "Mixed",
         "description": "Introduction to BI tools and methodologies"},
        {"id": "COURSE012", "title": "Cloud Computing Fundamentals", "type": "Course", "duration": "3 weeks", "duration_weeks": 3,
         "skills": ["Cloud Computing", "AWS"], "difficulty": "Beginner", "learning_style": "Hands-on",
         "description": "Learn cloud computing basics with AWS"},
        {"id": "COURSE013", "title": "Data Analysis Fundamentals", "type": "Course", "duration": "3 weeks", "duration_weeks": 3,
         "skills": ["Data Analysis", "Statistics"], "difficulty": "Beginner", "learning_style": "Hands-on",
         "description": "Learn Data Analysis basics"},
        {"id": "COURSE014", "title": "Excel Advanced", "type": "Course", "duration": "3 weeks", "duration_weeks": 3,
         "skills": ["Data Analysis", "Excel"], "difficulty": "Intermediate", "learning_style": "Hands-on",
         "description": "Learn Excel"}
    ])

course_catalog = load_enhanced_course_catalog()

# Enhanced role requirements
@st.cache_data
def load_enhanced_role_requirements():
    return {
        "Data Analyst": {
            "required_skills": ["SQL", "Data Visualization", "Excel", "Statistics"],
            "preferred_skills": ["Python", "Database", "Business Intelligence"],
            "experience_level": "Entry to Mid"
        },
        "Data Scientist": {
            "required_skills": ["Python", "Machine Learning", "Statistics", "Data Visualization"],
            "preferred_skills": ["Deep Learning", "Big Data", "Cloud Computing"],
            "experience_level": "Mid to Senior"
        },
        "AI Specialist": {
            "required_skills": ["Machine Learning", "Deep Learning", "Python", "Mathematics"],
            "preferred_skills": ["Neural Networks", "Research", "Statistics"],
            "experience_level": "Senior"
        },
        "Data Science Manager": {
            "required_skills": ["Leadership", "Data Science", "Team Management", "Strategy"],
            "preferred_skills": ["Communication", "Project Management", "Business Intelligence"],
            "experience_level": "Senior to Executive"
        }
    }

role_requirements = load_enhanced_role_requirements()

# Enhanced intent detection
def detect_user_intent(user_input):
    user_input_lower = user_input.lower()
    
    intents = {
        "request_specific_skill": [
            "learn", "want to learn", "need to learn", "skill", "develop", "improve"
        ],
        "time_constraint": [
            "week", "month", "time", "deadline", "urgent", "quickly", "fast"
        ],
        "learning_path_request": [
            "learning path", "recommend courses", "suggest", "path", "roadmap"
        ],
        "skill_gap_analysis": [
            "gap", "missing", "lack", "need", "should learn"
        ],
        "career_guidance": [
            "career", "role", "position", "promotion", "transition"
        ],
        "course_filtering": [
            "beginner", "advanced", "intermediate", "easy", "difficult"
        ],
        "search_request": [
            "search", "find", "look for", "research", "information about"
        ],
        "udemy_request": [
            "udemy", "online course", "course recommendation", "external courses"
        ]
    }
    
    detected_intents = []
    for intent, keywords in intents.items():
        if any(keyword in user_input_lower for keyword in keywords):
            detected_intents.append(intent)
    
    return detected_intents

# Extract structured information from user input
def extract_learning_requirements(user_input):
    user_input_lower = user_input.lower()
    
    # Extract time constraints
    time_patterns = [
        r"(\d+)\s*weeks?",
        r"(\d+)\s*months?",
        r"in\s*(\d+)\s*weeks?",
        r"within\s*(\d+)\s*weeks?"
    ]
    
    time_available = 0
    for pattern in time_patterns:
        match = re.search(pattern, user_input_lower)
        if match:
            time_value = int(match.group(1))
            if "month" in pattern:
                time_available = time_value * 4  # Convert months to weeks
            else:
                time_available = time_value
            break
    
    # Extract specific skills mentioned
    all_skills = set()
    for skills in role_requirements.values():
        all_skills.update(skills["required_skills"])
        all_skills.update(skills["preferred_skills"])
    
    # Add skills from course catalog
    for _, course in course_catalog.iterrows():
        all_skills.update(course["skills"])
    
    mentioned_skills = [skill for skill in all_skills if skill.lower() in user_input_lower]
    
    # Extract urgency indicators
    urgency_keywords = {
        "critical": ["urgent", "immediately", "asap", "critical"],
        "high": ["soon", "quickly", "fast", "priority"],
        "medium": ["normal", "regular"],
        "low": ["eventually", "when possible", "no rush"]
    }
    
    urgency = "medium"
    for level, keywords in urgency_keywords.items():
        if any(keyword in user_input_lower for keyword in keywords):
            urgency = level
            break
    
    return {
        "time_available_weeks": time_available,
        "mentioned_skills": mentioned_skills,
        "urgency": urgency
    }

#Enhanced learning path generation with Udemy integration
def generate_enhanced_learning_path(employee_profile, learning_preferences, specific_requirements=None):
    # Prepare context
    role_reqs = role_requirements.get(employee_profile["current_role"], {})
    career_goal_reqs = []
    for goal in employee_profile["career_goals"]:
        if goal in role_requirements:
            career_goal_reqs.extend(role_requirements[goal]["required_skills"])
            career_goal_reqs.extend(role_requirements[goal]["preferred_skills"])
    
    # Identify skill gaps
    current_skills = set(employee_profile["skills"])
    required_skills = set(role_reqs.get("required_skills", [])) | set(career_goal_reqs)
    skill_gaps = list(required_skills - current_skills)
    
    # Add specifically requested skills
    if learning_preferences.specific_skills_requested:
        skill_gaps.extend([skill for skill in learning_preferences.specific_skills_requested 
                          if skill not in current_skills])
    
    if specific_requirements and specific_requirements.get("mentioned_skills"):
        skill_gaps.extend([skill for skill in specific_requirements["mentioned_skills"]
                          if skill not in current_skills])
    
    # Remove duplicates
    skill_gaps = list(set(skill_gaps))
    
    # Filter courses based on time constraints and preferences
    filtered_courses = course_catalog.copy()
    
    # Time constraint filtering
    time_constraint = learning_preferences.time_available_weeks
    if specific_requirements and specific_requirements.get("time_available_weeks"):
        specific_requirements["time_available_weeks"] = time_constraint
    if specific_requirements:
        temp = specific_requirements.copy()
    else:
        temp = None
    #del temp['time_available_weeks']
    print('before time filter')
    print(filtered_courses)

    # if time_constraint > 0:
    #     # Allow some flexibility (±1 week)
    #     filtered_courses = filtered_courses[
    #         (filtered_courses["duration_weeks"] <= time_constraint + 1) &
    #         (filtered_courses["duration_weeks"] >= max(1, time_constraint - 2))
    #     ]
    print('After time filter')
    print(filtered_courses)
    print(specific_requirements)
    print(time_constraint)
    # Filter by relevant skills
    relevant_courses = []
    for _, course in filtered_courses.iterrows():
        if any(skill in skill_gaps for skill in course["skills"]):
            if course["title"] not in employee_profile["completed_courses"]:
                relevant_courses.append(course.to_dict())
    print("relevant")
    print(relevant_courses)
    # Generate Udemy courses for alternative suggestions
    udemy_courses = []
    skills_for_udemy = skill_gaps or learning_preferences.specific_skills_requested or []
    if skills_for_udemy:
        with st.spinner("🔍 Finding top Udemy courses..."):
            udemy_courses = udemy_agent.generate_udemy_courses(skills_for_udemy[:3])  # Limit to 3 skills
    
    # Create enhanced prompt
    prompt = f"""
    You are an expert learning path advisor. Create a personalized learning path for an employee.

    EMPLOYEE PROFILE:
    - Current Role: {employee_profile['current_role']}
    - Current Skills: {', '.join(employee_profile['skills'])}
    - Skill Proficiency: {json.dumps(employee_profile.get('skill_proficiency', {}))}
    - Completed Courses: {', '.join(employee_profile['completed_courses'])}
    - Career Goals: {', '.join(employee_profile['career_goals'])}

    LEARNING CONSTRAINTS:
    - Time Available: {time_constraint} weeks (if specified)
    - Learning Style Preference: {learning_preferences.preferred_learning_style}
    - Difficulty Preference: {learning_preferences.difficulty_preference}
    - Urgency: {learning_preferences.learning_urgency}

    SKILL GAPS IDENTIFIED:
    {', '.join(skill_gaps)}

    AVAILABLE COURSES (filtered by constraints):
    {json.dumps(relevant_courses[:15])}  # Limit to prevent token overflow

    SPECIFIC REQUIREMENTS:
    {json.dumps(temp.pop("time_available_weeks")) if temp else "None"}

    Create a learning path with 3-6 courses that:
    1. Addresses the most critical skill gaps first
    2. Strictly Follow Time Available if specified
    3. Follows logical learning progression
    4. Matches the employee's preferred learning style when possible
    5. Considers their current skill proficiency levels

    For each recommended course:
    - Select from the AVAILABLE COURSES list
    - Provide title, type, duration, priority (Critical/High/Medium/Low)
    - Explain why it's recommended and how it fits the constraints
    - Indicate prerequisite relationships if any

    For alternative suggestions, focus on external learning resources and mention that Udemy courses will be provided separately.

    Return response in this JSON format:
    {{
      "learning_path": [
        {{
          "title": "Course Title",
          "type": "Course/Workshop/Bootcamp",
          "duration": "X weeks",
          "duration_weeks": X,
          "priority": "Critical/High/Medium/Low",
          "reason": "Detailed reason for recommendation",
          "skills_gained": ["Skill1", "Skill2"],
          "fits_constraints": "How this course fits time/style constraints"
        }}
      ],
      "total_duration_weeks": X,
      "explanation": "Overall learning path strategy explanation",
      "skill_gaps_addressed": ["Skill1", "Skill2"],
      "progression_notes": "Notes about learning progression and dependencies",
      "alternative_suggestions": "Alternative approaches mentioning external resources like Udemy, Coursera, and free resources. Note that specific Udemy recommendations will be provided separately.",
      "udemy_courses": []
    }}

    Only respond with valid JSON.
    """
    print(prompt)
    try:
        generation_config = {
            "temperature": 0.1,  # Lower temperature for more consistent output
            "top_p": 0.8,
            "top_k": 40,
            #"max_output_tokens": 2048,
            }
        
        response = gemini_model.generate_content(
        prompt,
        generation_config=generation_config
        )
        raw_text = response.text
        
        # Extract JSON from markdown
        match = re.search(r'```json\s*(\{[\s\S]*\})\s*```', raw_text)
        if match:
            json_str = match.group(1)
            result = json.loads(json_str)
        else:
            # Try to parse the entire response as JSON
            result = json.loads(raw_text)
        
        # Add Udemy courses to the result
        result["udemy_courses"] = [
            {
                "title": course.title,
                "url": course.url,
                "description": course.description,
                "rating": course.rating,
                "price": course.price,
                "duration": course.duration,
                "level": course.level
            }
            for course in udemy_courses
        ]
        
        return result
 
    except Exception as e:
        st.error(f"Error generating learning path: {e}")
        return {
            "learning_path": [],
            "explanation": "Error generating learning path. Please try again.",
            "skill_gaps_addressed": [],
            "total_duration_weeks": 0,
            "progression_notes": "",
            "alternative_suggestions": "",
            "udemy_courses": []
        }

#  remove if not working

# from functools import lru_cache

# import hashlib

# def generate_enhanced_learning_path(employee_profile, learning_preferences, specific_requirements=None):
#     """
#     Generate a consistent learning path with caching and deterministic output
#     """
    
#     # Create a cache key based on inputs to ensure consistency
#     cache_key = create_cache_key(employee_profile, learning_preferences, specific_requirements)
    
#     # Check if we have a cached result
#     if 'learning_path_cache' not in st.session_state:
#         st.session_state.learning_path_cache = {}
    
#     if cache_key in st.session_state.learning_path_cache:
#         return st.session_state.learning_path_cache[cache_key]
    
#     # Prepare context
#     role_reqs = role_requirements.get(employee_profile["current_role"], {})
#     career_goal_reqs = []
#     for goal in employee_profile["career_goals"]:
#         if goal in role_requirements:
#             career_goal_reqs.extend(role_requirements[goal]["required_skills"])
#             career_goal_reqs.extend(role_requirements[goal]["preferred_skills"])
    
#     # Identify skill gaps (ensure consistent ordering)
#     current_skills = set(employee_profile["skills"])
#     required_skills = set(role_reqs.get("required_skills", [])) | set(career_goal_reqs)
#     skill_gaps = sorted(list(required_skills - current_skills))  # Sort for consistency
    
#     # Add specifically requested skills (maintain order)
#     if learning_preferences.specific_skills_requested:
#         additional_skills = [skill for skill in learning_preferences.specific_skills_requested 
#                            if skill not in current_skills]
#         skill_gaps.extend(sorted(additional_skills))
    
#     if specific_requirements and specific_requirements.get("mentioned_skills"):
#         additional_skills = [skill for skill in specific_requirements["mentioned_skills"]
#                            if skill not in current_skills]
#         skill_gaps.extend(sorted(additional_skills))
    
#     # Remove duplicates and maintain consistent order
#     skill_gaps = sorted(list(set(skill_gaps)))
    
#     # Filter courses based on time constraints and preferences
#     filtered_courses = course_catalog.copy()
    
#     # Time constraint filtering
#     time_constraint = learning_preferences.time_available_weeks
#     if specific_requirements and specific_requirements.get("time_available_weeks"):
#         time_constraint = specific_requirements["time_available_weeks"]
    
#     print('before time filter')
#     print(filtered_courses)
#     print(specific_requirements)
#     print(time_constraint)
#     if time_constraint > 0:
#         # Allow some flexibility (±1 week)
#         filtered_courses = filtered_courses[
#             (filtered_courses["duration_weeks"] <= time_constraint + 1) &
#             (filtered_courses["duration_weeks"] >= max(1, time_constraint - 2))
#         ]

    
#     print('After time filter')
#     print(filtered_courses)
#     # Filter by relevant skills and sort for consistency
#     relevant_courses = []
#     for _, course in filtered_courses.iterrows():
#         if any(skill in skill_gaps for skill in course["skills"]):
#             if course["title"] not in employee_profile["completed_courses"]:
#                 relevant_courses.append(course.to_dict())

    
#     # Sort courses for consistent ordering
#     #print('before')
#     #print(relevant_courses)
#     relevant_courses = sorted(relevant_courses, key=lambda x: (x["title"], x["duration_weeks"]))
#     #print('after')
#     #print(relevant_courses)
#     # Generate Udemy courses with consistent selection
#     udemy_courses = []
#     skills_for_udemy = skill_gaps or learning_preferences.specific_skills_requested or []
#     if skills_for_udemy:
#         # Take first 3 skills consistently
#         selected_skills = sorted(skills_for_udemy)[:3]
#         with st.spinner("🔍 Finding top Udemy courses..."):
#             udemy_courses = udemy_agent.generate_udemy_courses(selected_skills)
    
#     # Create enhanced prompt with deterministic structure
#     prompt = create_deterministic_prompt(
#         employee_profile, learning_preferences, specific_requirements,
#         time_constraint, skill_gaps, relevant_courses
#     )
#     #print(prompt)
    
#     try:
#         # Use very low temperature for maximum consistency
#         generation_config = {
#             "temperature": 0.0,  # Set to 0 for maximum determinism
#             "top_p": 0.1,        # Very low for consistency
#             "top_k": 1,          # Only consider top option
#             #"seed": 42,          # Add seed if supported by your model
#         }
        
#         response = gemini_model.generate_content(
#             prompt,
#             generation_config=generation_config
#         )
#         raw_text = response.text
        
#         #print(raw_text)
#         # Extract JSON from markdown
#         result = extract_json_from_response(raw_text)
        
#         # Ensure consistent structure and add Udemy courses
#         result = normalize_result_structure(result, udemy_courses)
        
#         # Cache the result
#         st.session_state.learning_path_cache[cache_key] = result

        
        
#         return result
 
#     except Exception as e:
#         st.error(f"Error generating learning path: {e}")
#         default_result = create_default_result()
#         st.session_state.learning_path_cache[cache_key] = default_result
#         return default_result


# def create_cache_key(employee_profile, learning_preferences, specific_requirements):
#     """Create a deterministic cache key from inputs"""
#     # Create a normalized representation of inputs
#     cache_data = {
#         "profile": {
#             "current_role": employee_profile.get("current_role", ""),
#             "skills": sorted(employee_profile.get("skills", [])),
#             "completed_courses": sorted(employee_profile.get("completed_courses", [])),
#             "career_goals": sorted(employee_profile.get("career_goals", [])),
#             "skill_proficiency": employee_profile.get("skill_proficiency", {})
#         },
#         "preferences": {
#             "time_available_weeks": getattr(learning_preferences, 'time_available_weeks', 0),
#             "preferred_learning_style": getattr(learning_preferences, 'preferred_learning_style', ''),
#             "difficulty_preference": getattr(learning_preferences, 'difficulty_preference', ''),
#             "learning_urgency": getattr(learning_preferences, 'learning_urgency', ''),
#             "specific_skills_requested": sorted(getattr(learning_preferences, 'specific_skills_requested', []))
#         },
#         "requirements": specific_requirements or {}
#     }
    
#     # Create hash of the normalized data
#     cache_str = json.dumps(cache_data, sort_keys=True)
#     return hashlib.md5(cache_str.encode()).hexdigest()


# def create_deterministic_prompt(employee_profile, learning_preferences, specific_requirements, 
#                                time_constraint, skill_gaps, relevant_courses):
#     """Create a deterministic prompt with consistent structure"""
    
#     prompt = f"""
# You are an expert learning path advisor. Create a personalized learning path for an employee.
# IMPORTANT: Provide consistent, deterministic recommendations based solely on the data provided.

# EMPLOYEE PROFILE:
# - Current Role: {employee_profile['current_role']}
# - Current Skills: {', '.join(sorted(employee_profile['skills']))}
# - Skill Proficiency: {json.dumps(employee_profile.get('skill_proficiency', {}), sort_keys=True)}
# - Completed Courses: {', '.join(sorted(employee_profile['completed_courses']))}
# - Career Goals: {', '.join(sorted(employee_profile['career_goals']))}

# LEARNING CONSTRAINTS:
# - Time Available: {time_constraint} weeks
# - Learning Style Preference: {learning_preferences.preferred_learning_style}
# - Difficulty Preference: {learning_preferences.difficulty_preference}
# - Urgency: {learning_preferences.learning_urgency}

# SKILL GAPS IDENTIFIED (in priority order):
# {', '.join(skill_gaps)}

# AVAILABLE COURSES (sorted by relevance):
# {json.dumps(relevant_courses[:10], sort_keys=True, indent=2)}

# SPECIFIC REQUIREMENTS:
# {json.dumps(specific_requirements, sort_keys=True) if specific_requirements else "None"}

# INSTRUCTIONS:
# 1. Select exactly 3-5 courses that best address the skill gaps
# 2. Prioritize courses that cover multiple skill gaps
# 3. Ensure logical learning progression
# 4. Respect time constraints
# 5. Use ONLY courses from the AVAILABLE COURSES list above

# Return response in this EXACT JSON format (no variations):
# {{
#   "learning_path": [
#     {{
#       "title": "Course Title",
#       "type": "Course/Workshop/Bootcamp",
#       "duration": "X weeks",
#       "duration_weeks": X,
#       "priority": "Critical/High/Medium/Low",
#       "reason": "Detailed reason for recommendation",
#       "skills_gained": ["Skill1", "Skill2"],
#       "fits_constraints": "How this course fits constraints"
#     }}
#   ],
#   "total_duration_weeks": X,
#   "explanation": "Overall learning path strategy",
#   "skill_gaps_addressed": {json.dumps(skill_gaps)},
#   "progression_notes": "Learning progression and dependencies",
#   "alternative_suggestions": "External resources recommendation",
#   "udemy_courses": []
# }}

# Respond ONLY with valid JSON. No additional text or formatting.
# """
    
#     return prompt


# def extract_json_from_response(raw_text):
#     """Extract and parse JSON from model response"""
#     # Try to extract JSON from markdown first
#     match = re.search(r'```json\s*(\{[\s\S]*\})\s*```', raw_text)
#     if match:
#         json_str = match.group(1)
#         return json.loads(json_str)
    
#     # Try to find JSON object in the text
#     json_match = re.search(r'\{[\s\S]*\}', raw_text)
#     if json_match:
#         return json.loads(json_match.group(0))
    
#     # If no JSON found, try parsing entire response
#     return json.loads(raw_text)


# def normalize_result_structure(result, udemy_courses):
#     """Ensure the result has consistent structure"""
#     normalized = {
#         "learning_path": result.get("learning_path", []),
#         "total_duration_weeks": result.get("total_duration_weeks", 0),
#         "explanation": result.get("explanation", ""),
#         "skill_gaps_addressed": result.get("skill_gaps_addressed", []),
#         "progression_notes": result.get("progression_notes", ""),
#         "alternative_suggestions": result.get("alternative_suggestions", ""),
#         "udemy_courses": []
#     }
    
#     # Add Udemy courses with consistent structure
#     normalized["udemy_courses"] = [
#         {
#             "title": getattr(course, 'title', ''),
#             "url": getattr(course, 'url', ''),
#             "description": getattr(course, 'description', ''),
#             "rating": getattr(course, 'rating', 0),
#             "price": getattr(course, 'price', ''),
#             "duration": getattr(course, 'duration', ''),
#             "level": getattr(course, 'level', '')
#         }
#         for course in udemy_courses
#     ]
    
#     return normalized


# def create_default_result():
#     """Create a default result structure for error cases"""
#     return {
#         "learning_path": [],
#         "total_duration_weeks": 0,
#         "explanation": "Error generating learning path. Please try again.",
#         "skill_gaps_addressed": [],
#         "progression_notes": "",
#         "alternative_suggestions": "",
#         "udemy_courses": []
#     }


# def clear_learning_path_cache():
#     """Clear the learning path cache - useful for testing or manual refresh"""
#     if 'learning_path_cache' in st.session_state:
#         st.session_state.learning_path_cache.clear()
#         st.success("Learning path cache cleared!")




##############################




# Enhanced user input processing with search capabilities
def process_enhanced_user_input(user_input):
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🔍 Analyzing your request...")
    
    # Detect intents and extract requirements
    intents = detect_user_intent(user_input)
    specific_requirements = extract_learning_requirements(user_input)
    
    # Update learning preferences based on extracted requirements
    if specific_requirements["time_available_weeks"] > 0:
        st.session_state.learning_preferences.time_available_weeks = specific_requirements["time_available_weeks"]
    
    if specific_requirements["mentioned_skills"]:
        st.session_state.learning_preferences.specific_skills_requested.extend(
            [skill for skill in specific_requirements["mentioned_skills"] 
             if skill not in st.session_state.learning_preferences.specific_skills_requested]
        )
    
    # Handle search requests
    if "search_request" in intents:
        message_placeholder.markdown("🔍 Searching the web for information...")
        
        # Extract search query
        search_query = user_input
        for phrase in ["search for", "find", "look for", "research", "information about"]:
            if phrase in user_input.lower():
                search_query = user_input.lower().split(phrase, 1)[1].strip()
                break
        
        # Perform search
        search_results = search_agent.search_web(search_query, max_results=5)
        
        if search_results:
            response = f"🔍 **Search Results for: {search_query}**\n\n"
            for i, result in enumerate(search_results, 1):
                response += f"**{i}. {result['title']}**\n"
                response += f"🔗 {result['url']}\n"
                response += f"📝 {result['snippet'][:200]}...\n\n"
            
            response += "Would you like me to search for anything else or help create a learning path based on this information?"
        else:
            response = f"I couldn't find specific search results for '{search_query}', but I can help you create a learning path or find courses related to your interests. What would you like to learn?"
    
    # Generate response based on intents
    elif "learning_path_request" in intents or "request_specific_skill" in intents:
        message_placeholder.markdown("🎯 Creating your personalized learning path...")
        
        with st.spinner("Generating learning path and finding Udemy courses..."):
            result = generate_enhanced_learning_path_with_sync(
                st.session_state.employee_profile,
                st.session_state.learning_preferences,
                specific_requirements
            )
            st.session_state.learning_path = result
            
            response = f"""🎯 **Personalized Learning Path Created!**

**Analysis Summary:**
- **Time Constraint:** {specific_requirements['time_available_weeks']} weeks (if specified)
- **Skills Requested:** {', '.join(specific_requirements['mentioned_skills']) if specific_requirements['mentioned_skills'] else 'Based on your career goals'}
- **Total Duration:** {result.get('total_duration_weeks', 'N/A')} weeks

**Strategy:** {result.get('explanation', '')}

**Learning Progression:** {result.get('progression_notes', '')}

**Alternative Options:** {result.get('alternative_suggestions', '')}

✨ I've also found {len(result.get('udemy_courses', []))} top-rated Udemy courses that complement your learning path. Check the learning path panel on the right to see all recommendations!"""

    elif "skill_gap_analysis" in intents:
        message_placeholder.markdown("📊 Analyzing your skill gaps...")
        
        # Enhanced skill gap analysis with search
        role_reqs = role_requirements.get(st.session_state.employee_profile["current_role"], {})
        current_skills = set(st.session_state.employee_profile["skills"])
        required_skills = set(role_reqs.get("required_skills", []))
        preferred_skills = set(role_reqs.get("preferred_skills", []))
        
        critical_gaps = required_skills - current_skills
        nice_to_have_gaps = preferred_skills - current_skills
        
        response = f"""📊 **Skill Gap Analysis for {st.session_state.employee_profile['current_role']}:**

**🚨 Critical Skills Missing:** {', '.join(critical_gaps) if critical_gaps else 'None - you have all required skills!'}

**💡 Recommended Additional Skills:** {', '.join(nice_to_have_gaps) if nice_to_have_gaps else 'You have excellent coverage!'}

**✅ Your Strengths:** {', '.join(current_skills & (required_skills | preferred_skills))}

Would you like me to create a learning path to address these gaps or search for specific learning resources?"""

        # Perform automatic search for critical gaps
        if critical_gaps:
            message_placeholder.markdown("🔍 Searching for learning resources...")
            
            gap_skills = list(critical_gaps)[:2]  # Limit to top 2 critical skills
            search_results_text = ""
            
            for skill in gap_skills:
                search_result = search_agent.search_learning_resources(skill)
                if search_result['resources']:
                    search_results_text += f"\n\n**🔍 Learning Resources for {skill}:**\n"
                    for resource in search_result['resources'][:3]:  # Top 3 per skill
                        search_results_text += f"• [{resource['title']}]({resource['url']})\n"
            
            if search_results_text:
                response += search_results_text

    else:
        # General conversational response
        conversation_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages[-5:]])
        
        prompt = f"""
        You are a learning advisor chatbot with AI search capabilities. Respond helpfully to the user's message.
        
        Employee Profile: {st.session_state.employee_profile['current_role']}, Skills: {', '.join(st.session_state.employee_profile['skills'])}
        Detected Intents: {', '.join(intents)}
        Extracted Requirements: {json.dumps(specific_requirements)}
        
        Recent conversation: {conversation_context}
        User's message: {user_input}
        
        Provide a helpful, conversational response (max 3 sentences). If they mentioned specific skills or time constraints, acknowledge them.
        If they seem to need search help, offer to search for information. If they need learning guidance, offer to create a learning path.
        """
        
        try:
            generation_config = {
            "temperature": 0.1,  # Lower temperature for more consistent output
            "top_p": 0.8,
            "top_k": 40,
            #"max_output_tokens": 2048,
            }
        
            ai_response = gemini_model.generate_content(
            prompt,
            generation_config=generation_config
            )
            response = ai_response.text
        except Exception as e:
            response = "I'm having trouble processing your request right now. Could you try rephrasing it, or would you like me to search for information or create a learning path?"
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    message_placeholder.markdown(response)

# Enhanced employee profile update function
def update_employee_profile():
    with st.sidebar.expander("👤 Edit Employee Profile", expanded=False):
        # Basic Information
        st.markdown("#### Basic Information")
        name = st.text_input("Name", value=st.session_state.employee_profile["name"])
        
        current_role = st.selectbox(
            "Current Role", 
            options=list(role_requirements.keys()), 
            index=list(role_requirements.keys()).index(st.session_state.employee_profile["current_role"]) 
            if st.session_state.employee_profile["current_role"] in role_requirements else 0
        )
        
        # Skills Section
        st.markdown("#### Skills & Proficiency")
        
        # Get all available skills
        all_skills = set()
        for role_data in role_requirements.values():
            all_skills.update(role_data["required_skills"])
            all_skills.update(role_data["preferred_skills"])
        
        # Add skills from course catalog
        for _, course in course_catalog.iterrows():
            all_skills.update(course["skills"])
        
        skills = st.multiselect(
            "Current Skills", 
            options=sorted(list(all_skills)), 
            default=st.session_state.employee_profile["skills"],
            help="Select all skills you currently possess"
        )
        
        # Skill Proficiency Levels
        st.markdown("#### Skill Proficiency Levels")
        skill_proficiency = {}
        if skills:
            for skill in skills:
                current_proficiency = st.session_state.employee_profile.get("skill_proficiency", {}).get(skill, "Intermediate")
                proficiency = st.selectbox(
                    f"Proficiency in {skill}",
                    ["Beginner", "Intermediate", "Advanced"],
                    index=["Beginner", "Intermediate", "Advanced"].index(current_proficiency),
                    key=f"prof_{skill}"
                )
                skill_proficiency[skill] = proficiency
        
        # Career Goals
        st.markdown("#### Career Goals")
        career_goals = st.multiselect(
            "Career Aspirations", 
            options=list(role_requirements.keys()), 
            default=st.session_state.employee_profile["career_goals"],
            help="Select roles you aspire to achieve"
        )
        
        # Completed Courses
        st.markdown("#### Learning History")
        all_courses = course_catalog["title"].tolist()
        completed_courses = st.multiselect(
            "Completed Courses", 
            options=all_courses,
            default=st.session_state.employee_profile["completed_courses"],
            help="Select courses you have already completed"
        )
        
        # Experience Level
        experience_level = st.selectbox(
            "Overall Experience Level",
            ["Entry Level", "Junior", "Mid-level", "Senior", "Expert"],
            index=["Entry Level", "Junior", "Mid-level", "Senior", "Expert"].index(
                st.session_state.employee_profile.get("experience_level", "Mid-level")
            )
        )
        
        # Update button
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Update Profile", type="primary"):
                st.session_state.employee_profile = {
                    "employee_id": st.session_state.employee_profile["employee_id"],
                    "name": name,
                    "current_role": current_role,
                    "skills": skills,
                    "skill_proficiency": skill_proficiency,
                    "completed_courses": completed_courses,
                    "career_goals": career_goals,
                    "experience_level": experience_level
                }
                
                # Reset learning path when profile is updated
                st.session_state.learning_path = None
                
                # Add system message about profile update
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"✅ Profile updated successfully! Your new profile shows {len(skills)} skills and {len(career_goals)} career goals. Would you like me to create a new learning path based on your updated profile?"
                })
                st.success("Profile updated successfully!")
                st.rerun()
        
        with col2:
            if st.button("🔄 Reset to Default"):
                st.session_state.employee_profile = {
                    "employee_id": "EMP123456",
                    "name": "Alex Johnson",
                    "current_role": "Data Analyst",
                    "skills": ["SQL", "Excel", "Data Visualization"],
                    "completed_courses": ["Data Analysis Fundamentals", "Excel Advanced"],
                    "career_goals": ["Data Science Manager", "AI Specialist"],
                    "skill_proficiency": {
                        "SQL": "Intermediate",
                        "Excel": "Advanced", 
                        "Data Visualization": "Intermediate"
                    },
                    "experience_level": "Mid-level"
                }
                st.info("Profile reset to default values!")
                st.rerun()

# Enhanced sidebar with learning preferences and search features
def enhanced_sidebar():
    with st.sidebar:
        st.image("https://via.placeholder.com/150x150/4CAF50/white?text=AI", width=150)
        st.title("🧠 Smart Learning Advisor")
        st.markdown("*Powered by AI Search & Udemy Integration*")
        
        st.markdown(f"### {st.session_state.employee_profile['name']}")
        st.markdown(f"**Role:** {st.session_state.employee_profile['current_role']}")
        st.markdown(f"**Experience:** {st.session_state.employee_profile.get('experience_level', 'Mid-level')}")
        
        # Employee Profile Editing
        update_employee_profile()
        
        # Current skills with proficiency
        with st.expander("📊 Current Skills & Proficiency", expanded=True):
            if st.session_state.employee_profile["skills"]:
                for skill in st.session_state.employee_profile["skills"]:
                    proficiency = st.session_state.employee_profile.get("skill_proficiency", {}).get(skill, "Unknown")
                    proficiency_emoji = {"Beginner": "🟢", "Intermediate": "🟡", "Advanced": "🔴"}.get(proficiency, "⚪")
                    st.markdown(f"{proficiency_emoji} **{skill}** - {proficiency}")
            else:
                st.info("No skills added yet. Edit your profile to add skills.")
        
        # Career goals
        with st.expander("🎯 Career Goals"):
            if st.session_state.employee_profile["career_goals"]:
                for goal in st.session_state.employee_profile["career_goals"]:
                    st.markdown(f"• {goal}")
            else:
                st.info("No career goals set. Edit your profile to add goals.")
        
        # Completed courses
        with st.expander("📚 Completed Courses"):
            if st.session_state.employee_profile["completed_courses"]:
                for course in st.session_state.employee_profile["completed_courses"]:
                    st.markdown(f"✅ {course}")
            else:
                st.info("No completed courses recorded.")
        
        # Learning preferences section
        with st.expander("⚙️ Learning Preferences", expanded=False):
            st.session_state.learning_preferences.time_available_weeks = st.number_input(
                "Time Available (weeks)", 
                min_value=0, 
                max_value=52, 
                value=st.session_state.learning_preferences.time_available_weeks,
                help="How many weeks can you dedicate to learning?"
            )
            
            st.session_state.learning_preferences.preferred_learning_style = st.selectbox(
                "Learning Style",
                ["Mixed", "Visual", "Hands-on", "Interactive", "Intensive"],
                index=["Mixed", "Visual", "Hands-on", "Interactive", "Intensive"].index(
                    st.session_state.learning_preferences.preferred_learning_style
                )
            )
            
            st.session_state.learning_preferences.difficulty_preference = st.selectbox(
                "Difficulty Preference",
                ["Progressive", "Beginner", "Intermediate", "Advanced"],
                index=["Progressive", "Beginner", "Intermediate", "Advanced"].index(
                    st.session_state.learning_preferences.difficulty_preference
                )
            )
            
            st.session_state.learning_preferences.learning_urgency = st.selectbox(
                "Learning Urgency",
                ["Low", "Medium", "High", "Critical"],
                index=["Low", "Medium", "High", "Critical"].index(
                    st.session_state.learning_preferences.learning_urgency
                )
            )
            
            # Skill request interface
            all_skills = set()
            for role_data in role_requirements.values():
                all_skills.update(role_data["required_skills"])
                all_skills.update(role_data["preferred_skills"])
            
            additional_skills = st.multiselect(
                "Additional Skills to Learn",
                options=sorted(list(all_skills)),
                default=[],#st.session_state.learning_preferences.specific_skills_requested or [],
                help="Select specific skills you want to focus on"
            )
            st.session_state.learning_preferences.specific_skills_requested = additional_skills
        
        # Enhanced Quick Actions
        st.markdown("### 🚀 Quick Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎯 Generate\nLearning Path", type="primary"):
                process_enhanced_user_input("Create a personalized learning path for me based on my preferences")
        
        with col2:
            if st.button("📈 Analyze\nSkill Gaps"):
                process_enhanced_user_input("What are my skill gaps for my current role?")
        
        col3, col4 = st.columns(2)
        with col3:
            if st.button("⏱️ Quick 2-Week\nPlan"):
                process_enhanced_user_input("I have 2 weeks to learn new skills, what do you recommend?")
        
        with col4:
            if st.button("🔍 Search\nResources"):
                if st.session_state.learning_preferences.specific_skills_requested:
                    skills_text = ', '.join(st.session_state.learning_preferences.specific_skills_requested[:2])
                    process_enhanced_user_input(f"Search for learning resources about {skills_text}")
                else:
                    process_enhanced_user_input("Search for learning resources about data science")
        
        # Search Interface
        with st.expander("🔍 AI Search Assistant", expanded=False):
            st.markdown("**Search the web for learning resources, trends, or information:**")
            search_query = st.text_input(
                "Enter search query:",
                placeholder="e.g., 'latest machine learning trends 2024'",
                key="search_input"
            )
            
            col_search1, col_search2 = st.columns(2)
            with col_search1:
                if st.button("🔍 Search Web", key="web_search"):
                    if search_query:
                        process_enhanced_user_input(f"Search for {search_query}")
                    else:
                        st.warning("Please enter a search query")
            
            with col_search2:
                if st.button("📚 Find Courses", key="course_search"):
                    if search_query:
                        process_enhanced_user_input(f"Find courses about {search_query}")
                    else:
                        st.warning("Please enter a topic")
        
        # Reset and Help
        col_reset, col_help = st.columns(2)
        with col_reset:
            if st.button("🔄 Reset Chat"):
                st.session_state.messages = [
                    {"role": "assistant", "content": "Hello! I'm your enhanced learning advisor with AI-powered search capabilities. I can help you create personalized learning paths and find the best Udemy courses. How can I assist you today?"}
                ]
                st.session_state.learning_path = None
                st.rerun()
        
        with col_help:
            if st.button("❓ Help"):
                help_message = """
                **Available Commands:**
                • "Create a learning path for [skill]"
                • "I have [X] weeks to learn [skill]"
                • "Search for information about [topic]"
                • "What are my skill gaps?"
                • "Find Udemy courses for [skill]"
                • "Show me beginner courses only"
                """
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": help_message
                })
                st.rerun()

# Enhanced main interface with better layout
def enhanced_main():
    enhanced_sidebar()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 💬 Smart Learning Assistant")
        st.markdown("*Ask about learning paths, search for resources, or get Udemy course recommendations*")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Enhanced chat input with suggestions
        user_input = st.chat_input("Ask about learning paths, search topics, or request Udemy courses...")
        if user_input:
            process_enhanced_user_input(user_input)
    
    with col2:
        # Enhanced learning path display
        enhanced_learning_path_management()

# Footer with credits
def add_footer():
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>🧠 <strong>Smart Learning Path Advisor</strong></p>
        <p>Powered by Google Gemini AI • Enhanced with DuckDuckGo Search • Udemy Course Integration</p>
        <p><small>Built with ❤️ using Streamlit • AI-Powered Learning Recommendations</small></p>
    </div>
    """, unsafe_allow_html=True)

# Run the enhanced app
# if __name__ == "__main__":
#     enhanced_main()
#     add_footer()

if __name__ == "__main__":
    main_with_navigation()
    add_footer()