from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import os
from datetime import datetime
from typing import Dict, Any

def generate_pdf_report(data: Dict[str, Any], filename: str) -> str:
    """Generate PDF report from meeting data"""
    
    # Create output directory if it doesn't exist
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate PDF filename
    pdf_filename = f"{filename}_minutes.pdf"
    pdf_path = os.path.join(output_dir, pdf_filename)
    
    # Create PDF document
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1f2937')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.HexColor('#374151')
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor('#4b5563')
    )
    
    # Build document content
    story = []
    
    # Title
    story.append(Paragraph("Meeting Minutes Report", title_style))
    story.append(Spacer(1, 12))
    
    # Meeting metadata
    meeting_info = [
        ['Meeting File:', data.get('filename', 'N/A')],
        ['Processing Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        ['Duration:', f"{len(data.get('speakers', []))} speakers identified"],
        ['Speakers:', ', '.join(data.get('speakers', []))]
    ]
    
    meeting_table = Table(meeting_info, colWidths=[2*inch, 4*inch])
    meeting_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#374151')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(meeting_table)
    story.append(Spacer(1, 20))
    
    # Executive Summary
    summary = data.get('summary', {})
    if summary.get('executive_summary'):
        story.append(Paragraph("Executive Summary", heading_style))
        story.append(Paragraph(summary['executive_summary'], body_style))
        story.append(Spacer(1, 12))
    
    # Agenda Items
    if summary.get('agenda_items'):
        story.append(Paragraph("Agenda Items", heading_style))
        for item in summary['agenda_items']:
            story.append(Paragraph(f"• {item}", body_style))
        story.append(Spacer(1, 12))
    
    # Decisions Made
    if summary.get('decisions'):
        story.append(Paragraph("Decisions Made", heading_style))
        for decision in summary['decisions']:
            story.append(Paragraph(f"✓ {decision}", body_style))
        story.append(Spacer(1, 12))
    
    # Risks Identified
    if summary.get('risks'):
        story.append(Paragraph("Risks Identified", heading_style))
        for risk in summary['risks']:
            story.append(Paragraph(f"⚠ {risk}", body_style))
        story.append(Spacer(1, 12))
    
    # Next Steps
    if summary.get('next_steps'):
        story.append(Paragraph("Next Steps", heading_style))
        for step in summary['next_steps']:
            story.append(Paragraph(f"→ {step}", body_style))
        story.append(Spacer(1, 12))
    
    # Action Items
    action_items = data.get('action_items', [])
    if action_items:
        story.append(Paragraph("Action Items", heading_style))
        
        # Create action items table
        action_data = [['Action', 'Assignee', 'Deadline', 'Priority']]
        
        for action in action_items:
            assignees = ', '.join(action.get('assignees', [])) or 'Unassigned'
            deadline = action.get('deadline', 'No deadline')
            if deadline and deadline != 'No deadline':
                try:
                    deadline_dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                    deadline = deadline_dt.strftime('%Y-%m-%d')
                except:
                    pass
            
            urgency = action.get('deadline_urgency', 'low').title()
            
            action_data.append([
                action.get('text', '')[:60] + ('...' if len(action.get('text', '')) > 60 else ''),
                assignees,
                deadline,
                urgency
            ])
        
        action_table = Table(action_data, colWidths=[3*inch, 1.5*inch, 1*inch, 0.8*inch])
        action_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#374151')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f9fafb'), colors.white]),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(action_table)
    
    # Build PDF
    doc.build(story)
    
    return pdf_path
