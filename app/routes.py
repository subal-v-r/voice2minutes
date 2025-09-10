from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
import os
import json
from datetime import datetime
from typing import Dict, Any

from app.services.asr_service import process_audio_file
from app.services.preprocess import preprocess_transcript
from app.services.summarizer import generate_meeting_summary
from app.services.action_detector import detect_action_items
from app.services.ner_extractor import extract_assignees
from app.services.deadline_parser import extract_deadlines
from app.services.tracker import save_actions_to_db, get_all_actions
from app.utils.pdf_export import generate_pdf_report

router = APIRouter()

@router.post("/upload")
async def upload_meeting_file(file: UploadFile = File(...)):
    """Upload and process meeting audio/video file"""
    
    # Validate file type
    allowed_extensions = {'.mp3', '.wav', '.m4a', '.mp4', '.avi', '.mov'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Unsupported file format")
    
    # Save uploaded file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join("uploads", filename)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    try:
        # Process the file through the pipeline
        result = await process_meeting_pipeline(file_path, filename)
        return JSONResponse(content=result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

async def process_meeting_pipeline(file_path: str, filename: str) -> Dict[str, Any]:
    """Complete processing pipeline for meeting file"""
    
    # Step 1: Speech-to-text with diarization
    transcript_data = await process_audio_file(file_path)
    
    # Step 2: Preprocess transcript
    processed_transcript = preprocess_transcript(transcript_data)
    
    # Step 3: Generate summary
    summary = generate_meeting_summary(processed_transcript)
    
    # Step 4: Detect action items
    action_items = detect_action_items(processed_transcript)
    
    # Step 5: Extract assignees and deadlines
    for action in action_items:
        action['assignees'] = extract_assignees(action['text'], transcript_data.get('speakers', []))
        action['deadline'] = extract_deadlines(action['text'])
    
    # Step 6: Save actions to database
    save_actions_to_db(action_items, filename)
    
    # Prepare result
    result = {
        'filename': filename,
        'transcript': processed_transcript,
        'summary': summary,
        'action_items': action_items,
        'processing_time': datetime.now().isoformat(),
        'speakers': transcript_data.get('speakers', [])
    }
    
    # Save JSON output
    output_path = os.path.join("outputs", f"{filename}_minutes.json")
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    return result

@router.get("/actions")
async def get_actions():
    """Get all tracked actions"""
    actions = get_all_actions()
    return JSONResponse(content={"actions": actions})

@router.post("/actions/{action_id}/complete")
async def mark_action_complete(action_id: int):
    """Mark an action as completed"""
    from app.utils.db import mark_action_completed
    success = mark_action_completed(action_id)
    
    if success:
        return JSONResponse(content={"message": "Action marked as completed"})
    else:
        raise HTTPException(status_code=404, detail="Action not found")

@router.get("/export/{filename}")
async def export_pdf(filename: str):
    """Export meeting minutes as PDF"""
    json_path = os.path.join("outputs", f"{filename}_minutes.json")
    
    if not os.path.exists(json_path):
        raise HTTPException(status_code=404, detail="Meeting minutes not found")
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    pdf_path = generate_pdf_report(data, filename)
    return FileResponse(pdf_path, media_type='application/pdf', filename=f"{filename}_minutes.pdf")
