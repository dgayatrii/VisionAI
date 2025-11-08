# backend/report_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from datetime import datetime
import os

def _safe_image_flowable(path, max_w, max_h):
    """
    Return an Image flowable restricted to max_w x max_h while preserving aspect ratio,
    or None if path missing or invalid.
    """
    if not path:
        return None
    p = os.path.abspath(path)
    if not os.path.exists(p):
        return None
    try:
        im = Image(p)
        im._restrictSize(max_w, max_h)
        im.hAlign = 'CENTER'
        return im
    except Exception:
        return None

def generate_pdf(patient_info: dict, doctor_info: dict, pdf_path: str):
    """
    Generate a single-page formatted DR screening PDF.
    patient_info keys: name, patient_id, age, gender, diabetes_duration,
                       blood_pressure, medications, other_conditions,
                       left_eye_path, right_eye_path, left_result, right_result, combined_result
    doctor_info keys: full_name, medical_id, hospital_name
    pdf_path: where to write the output PDF file
    """

    # Ensure output directory exists
    out_dir = os.path.dirname(os.path.abspath(pdf_path)) or "."
    os.makedirs(out_dir, exist_ok=True)

    # Document
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=1.8*cm,
        rightMargin=1.8*cm,
        topMargin=1.5*cm,
        bottomMargin=1.2*cm,
    )

    styles = getSampleStyleSheet()
    # Custom styles
    title_style = ParagraphStyle(
        name="Title",
        fontSize=18,
        leading=22,
        alignment=1,  # center
        textColor=colors.HexColor("#1A237E"),  # navy
        fontName="Helvetica-Bold"
    )
    meta_style = ParagraphStyle(name="Meta", fontSize=9.5, leading=12)
    label_bold = ParagraphStyle(name="LabelBold", fontSize=10, fontName="Helvetica-Bold")
    section_title = ParagraphStyle(name="SectionTitle", fontSize=12, fontName="Helvetica-Bold",
                                   textColor=colors.HexColor("#0D47A1"), spaceBefore=6, spaceAfter=4)
    assessment_style = ParagraphStyle(name="Assessment", fontSize=11, fontName="Helvetica-Bold", textColor=colors.red)
    caption_style = ParagraphStyle(name="Caption", fontSize=9, alignment=1)  # center
    footer_style = ParagraphStyle(name="Footer", fontSize=8, alignment=1, textColor=colors.gray)

    story = []

    # Title and date
    story.append(Paragraph("Diabetic Retinopathy Screening Report", title_style))
    story.append(Spacer(1, 0.12*cm))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%d %B %Y, %I:%M %p')}", meta_style))
    story.append(Spacer(1, 0.4*cm))

    # Header: Physician (left) | Patient (right)
    doc_left = []
    doc_left.append(Paragraph("<b>Physician</b>", label_bold))
    doc_left.append(Paragraph(str(doctor_info.get("full_name", "")), meta_style))
    doc_left.append(Spacer(1, 0.12*cm))
    doc_left.append(Paragraph("<b>Medical ID</b>", label_bold))
    doc_left.append(Paragraph(str(doctor_info.get("medical_id", "")), meta_style))
    doc_left.append(Spacer(1, 0.12*cm))
    doc_left.append(Paragraph("<b>Hospital/Clinic</b>", label_bold))
    doc_left.append(Paragraph(str(doctor_info.get("hospital_name", "")), meta_style))

    doc_right = []
    doc_right.append(Paragraph("<b>Patient Details</b>", label_bold))
    doc_right.append(Paragraph(f"<b>Name:</b> {patient_info.get('name','')}", meta_style))
    doc_right.append(Spacer(1, 0.08*cm))
    doc_right.append(Paragraph(f"<b>Patient ID (Email):</b> {patient_info.get('patient_id','')}", meta_style))
    doc_right.append(Spacer(1, 0.08*cm))
    doc_right.append(Paragraph(f"<b>Age:</b> {patient_info.get('age','')}", meta_style))
    doc_right.append(Spacer(1, 0.08*cm))
    doc_right.append(Paragraph(f"<b>Gender:</b> {patient_info.get('gender','')}", meta_style))

    # Put side-by-side: make each column a KeepTogether Table so they don't split awkwardly
    left_col = Table([[doc_left]], colWidths=[doc.width/2.0 - 6])
    right_col = Table([[doc_right]], colWidths=[doc.width/2.0 - 6])
    header_table = Table([[left_col, right_col]], colWidths=[doc.width/2.0, doc.width/2.0])
    header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(header_table)
    story.append(Spacer(1, 0.4*cm))

    # Medical Information
    story.append(Paragraph("Patient Medical Information", section_title))
    med_rows = []
    md = patient_info.get('diabetes_duration', '')
    med_rows.append([Paragraph("<b>Diabetes Duration:</b>", label_bold), Paragraph(str(md), meta_style)])
    bp = patient_info.get('blood_pressure', '') or patient_info.get('blood_sugar_level','')
    med_rows.append([Paragraph("<b>Blood Pressure:</b>", label_bold), Paragraph(str(bp), meta_style)])
    med_rows.append([Paragraph("<b>Medications:</b>", label_bold), Paragraph(str(patient_info.get('medications','')), meta_style)])
    med_rows.append([Paragraph("<b>Other Conditions:</b>", label_bold), Paragraph(str(patient_info.get('other_conditions','')), meta_style)])
    med_table = Table(med_rows, colWidths=[4.5*cm, doc.width - 4.5*cm])
    med_table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
    story.append(med_table)
    story.append(Spacer(1, 0.35*cm))

    # Screening Results
    story.append(Paragraph("Screening Results", section_title))
    res_rows = []
    res_rows.append([Paragraph("<b>Left Eye Diagnosis:</b>", label_bold), Paragraph(str(patient_info.get('left_result','')), meta_style)])
    res_rows.append([Paragraph("<b>Right Eye Diagnosis:</b>", label_bold), Paragraph(str(patient_info.get('right_result','')), meta_style)])
    res_table = Table(res_rows, colWidths=[4.5*cm, doc.width - 4.5*cm])
    res_table.setStyle(TableStyle([('BOTTOMPADDING',(0,0),(-1,-1),4)]))
    story.append(res_table)
    story.append(Spacer(1, 0.12*cm))
    overall = patient_info.get('combined_result','')
    if overall:
        story.append(Paragraph(f"Overall Assessment: <font color='red'><b>{overall}</b></font>", assessment_style))
    story.append(Spacer(1, 0.35*cm))

    # Fundus images (side-by-side) with captions under each image individually
    story.append(Paragraph("Fundus Images", section_title))
    story.append(Spacer(1, 0.2*cm))

    # Calculate max image sizes to fit two images horizontally
    page_half = (doc.width - 1.0*cm) / 2.0
    max_img_w = page_half
    max_img_h = 10 * cm  # cap height

    left_path = patient_info.get('left_eye_path')
    right_path = patient_info.get('right_eye_path')

    left_img = _safe_image_flowable(left_path, max_img_w, max_img_h)
    right_img = _safe_image_flowable(right_path, max_img_w, max_img_h)

    # For each side, create a small nested table: [image], [caption]
    def image_with_caption(img_flowable, caption_text):
        if img_flowable:
            cell = [[img_flowable], [Paragraph(caption_text, caption_style)]]
        else:
            cell = [[Paragraph("<i>Image not available</i>", meta_style)], [Paragraph(caption_text, caption_style)]]
        nested = Table(cell, colWidths=[page_half])
        nested.setStyle(TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'), ('VALIGN',(0,0),(-1,-1),'MIDDLE'), ('BOTTOMPADDING',(0,0),(-1,-1),6)]))
        return nested

    left_cell = image_with_caption(left_img, "Left Eye")
    right_cell = image_with_caption(right_img, "Right Eye")

    images_table = Table([[left_cell, right_cell]], colWidths=[page_half, page_half])
    images_table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('ALIGN',(0,0),(-1,-1),'CENTER')]))
    story.append(images_table)

    # Footer / disclaimer
    story.append(Spacer(1, 0.6*cm))
    story.append(Paragraph("Disclaimer: This AI-generated report is a screening aid and not a substitute for a detailed ophthalmic examination.", footer_style))

    # Build PDF and verify
    try:
        doc.build(story)
    except Exception as e:
        raise RuntimeError(f"Error building PDF: {e}")

    if not os.path.exists(pdf_path):
        raise RuntimeError(f"generate_pdf did not create expected file: {pdf_path}")

    # success
    # print(f"✅ Report created at: {pdf_path}")
