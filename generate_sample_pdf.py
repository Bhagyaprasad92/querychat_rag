from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def create_sample_pdf(filename="sample_document.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=54, leftMargin=54,
        topMargin=54, bottomMargin=54
    )
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        spaceAfter=14
    )
    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = styles['Normal']
    body_style.fontSize = 10
    body_style.leading = 14

    # Page 1
    story.append(Paragraph("Project Nova: Autonomous Aerial Logistics System", title_style))
    story.append(Paragraph("<b>Author:</b> Advanced Systems Engineering Group | <b>Published:</b> November 15, 2026", body_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("1. Executive Summary", h2_style))
    story.append(Paragraph(
        "Project Nova is a next-generation autonomous drone network designed for rapid, energy-efficient medical supply delivery across remote regions. "
        "The project officially kicked off on January 10, 2026, and entered active flight trials in September 2026. "
        "The primary goal is to reduce critical supply transit times by up to 75% compared to ground transportation, especially in mountainous or flood-prone terrain.",
        body_style
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("2. Key Milestones and Important Dates", h2_style))
    story.append(Paragraph(
        "• <b>January 10, 2026:</b> Project inception and preliminary architectural sign-off.<br/>"
        "• <b>May 4, 2026:</b> First successful indoor tethered flight simulation in Munich.<br/>"
        "• <b>September 18, 2026:</b> Phase 1 outdoor autonomous navigation test over 50 km.<br/>"
        "• <b>December 1, 2026:</b> Scheduled commercial pilot deployment in the Bavarian Alps.<br/>"
        "• <b>March 30, 2027:</b> Target completion date for international regulatory compliance certification.",
        body_style
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("3. Core Technical Advantages", h2_style))
    story.append(Paragraph(
        "Project Nova introduces three key advantages over conventional unmanned aerial vehicles:<br/>"
        "1. <b>Hybrid Solar-Hydrogen Propulsion:</b> Delivers up to 6 hours of continuous flight with zero carbon emissions.<br/>"
        "2. <b>Fault-Tolerant Edge AI:</b> On-board neural navigation enables obstacle avoidance in GPS-denied environments without remote pilot latency.<br/>"
        "3. <b>Hermetic Climate-Controlled Cargo Pod:</b> Maintains vaccines and sensitive medical biologics between 2°C and 8°C throughout transit.",
        body_style
    ))
    story.append(Spacer(1, 14))

    # Page 2 / Section 4
    story.append(Paragraph("4. Operational Budget and Resource Allocation", h2_style))
    story.append(Paragraph(
        "The total approved capital budget for Project Nova is <b>$14.8 million USD</b> spanning FY2026 through FY2028. "
        "Of this budget, $6.2 million is allocated directly to hardware prototyping, $4.5 million to software and autonomous navigation algorithms, "
        "$2.1 million to regulatory safety certifications, and $2.0 million is held in contingency reserve.",
        body_style
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("5. Safety Protocols and Fail-Safes", h2_style))
    story.append(Paragraph(
        "Every drone unit is equipped with triple-redundant avionics and a ballistic recovery parachute system that deploys automatically in the event of total motor failure. "
        "Geofencing boundaries are enforced in hardware, preventing flight into commercial airspace or hazardous weather corridors.",
        body_style
    ))

    doc.build(story)
    print(f"Sample PDF created successfully: {filename}")

if __name__ == "__main__":
    create_sample_pdf()
