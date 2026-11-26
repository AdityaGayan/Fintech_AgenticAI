import re
from io import BytesIO
from typing import List, Optional
from xml.sax.saxutils import escape

from pydantic import BaseModel, Field
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from src.agents.base_agent import invoke_gemini_safely

class SRSDocument(BaseModel):
    title: str
    version: str
    purpose: str
    scope: str
    definitions_and_acronyms: List[str]
    references: List[str]
    overview: str
    product_perspective: str
    product_functions: List[str]
    user_characteristics: List[str]
    constraints: List[str]
    assumptions_and_dependencies: List[str]
    user_interfaces: List[str]
    hardware_interfaces: List[str]
    software_interfaces: List[str]
    communication_interfaces: List[str]
    functions: List[str]
    performance_requirements: List[str]
    logical_database_requirements: List[str]
    design_constraints: List[str]
    software_quality_attributes: List[str]
    object_oriented_models: List[str]
    appendices: List[str]
    index: List[str]

    def to_ieee_markdown(self) -> str:
        """Render the structured requirements into an IEEE-style SRS outline."""
        def bullets(items: List[str]) -> str:
            return "\n".join(f"- {item}" for item in items) or "- None identified"

        def requirement_bullets(items: List[str], prefix: str) -> str:
            if not items:
                return "- None identified"
            return "\n".join(
                f"- **{prefix}{index:03d}:** {item}"
                for index, item in enumerate(items, start=1)
            )

        return f"""# Software Requirements Specification

## Title Page

- **Title:** {self.title}
- **Version:** {self.version}

## Table of Contents

1. Introduction
2. Overall Description
3. Specific Requirements
4. Appendices
5. Index

## 1. Introduction

### 1.1 Purpose
{self.purpose}

### 1.2 Scope
{self.scope}

### 1.3 Definitions, Acronyms, and Abbreviations
{bullets(self.definitions_and_acronyms)}

### 1.4 References
{bullets(self.references)}

### 1.5 Overview
{self.overview}

## 2. Overall Description

### 2.1 Product Perspective
{self.product_perspective}

### 2.2 Product Functions
{bullets(self.product_functions)}

### 2.3 User Characteristics
{bullets(self.user_characteristics)}

### 2.4 Constraints
{bullets(self.constraints)}

### 2.5 Assumptions and Dependencies
{bullets(self.assumptions_and_dependencies)}

## 3. Specific Requirements

### 3.1 External Interfaces

#### 3.1.1 User Interfaces
{requirement_bullets(self.user_interfaces, "UI")}

#### 3.1.2 Hardware Interfaces
{requirement_bullets(self.hardware_interfaces, "HW")}

#### 3.1.3 Software Interfaces
{requirement_bullets(self.software_interfaces, "SW")}

#### 3.1.4 Communication Interfaces
{requirement_bullets(self.communication_interfaces, "COM")}

### 3.2 Functions
{requirement_bullets(self.functions, "FUN")}

### 3.3 Performance Requirements
{requirement_bullets(self.performance_requirements, "PERF")}

### 3.4 Logical Database Requirements
{requirement_bullets(self.logical_database_requirements, "DB")}

### 3.5 Design Constraints
{requirement_bullets(self.design_constraints, "DC")}

### 3.6 Software System Quality Attributes
{requirement_bullets(self.software_quality_attributes, "QA")}

### 3.7 Object-Oriented Models
{requirement_bullets(self.object_oriented_models, "OO")}

## 4. Appendices
{bullets(self.appendices)}

## 5. Index
{bullets(self.index)}
"""

    def to_pdf(self) -> bytes:
        """Render the detailed SRS as a styled, paginated PDF document."""
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name="SRSTitle", parent=styles["Title"], alignment=TA_CENTER,
            fontName="Helvetica-Bold", fontSize=22, leading=28, textColor=colors.HexColor("#10233f"),
            spaceAfter=18,
        ))
        styles.add(ParagraphStyle(
            name="SRSHeading", parent=styles["Heading1"], fontName="Helvetica-Bold",
            fontSize=15, leading=20, textColor=colors.HexColor("#163e69"), spaceBefore=14, spaceAfter=8,
        ))
        styles.add(ParagraphStyle(
            name="SRSSubheading", parent=styles["Heading2"], fontName="Helvetica-Bold",
            fontSize=11, leading=15, textColor=colors.HexColor("#245c8d"), spaceBefore=9, spaceAfter=4,
        ))
        styles.add(ParagraphStyle(
            name="SRSBody", parent=styles["BodyText"], fontName="Helvetica",
            fontSize=9.5, leading=14, textColor=colors.HexColor("#25364d"), spaceAfter=6,
        ))
        styles.add(ParagraphStyle(
            name="SRSBullet", parent=styles["BodyText"], fontName="Helvetica",
            fontSize=9.5, leading=14, leftIndent=14, firstLineIndent=-8,
            textColor=colors.HexColor("#25364d"), spaceAfter=4,
        ))

        def inline_markup(value: str) -> str:
            safe = escape(value)
            return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", safe)

        story = []
        for line in self.to_ieee_markdown().splitlines():
            stripped = line.strip()
            if not stripped:
                story.append(Spacer(1, 4))
            elif stripped.startswith("# "):
                story.append(Paragraph(inline_markup(stripped[2:]), styles["SRSTitle"]))
            elif stripped.startswith("## "):
                story.append(Paragraph(inline_markup(stripped[3:]), styles["SRSHeading"]))
            elif stripped.startswith("### ") or stripped.startswith("#### "):
                offset = 4 if stripped.startswith("#### ") else 3
                story.append(Paragraph(inline_markup(stripped[offset:]), styles["SRSSubheading"]))
            elif stripped.startswith("- "):
                story.append(Paragraph(f"- {inline_markup(stripped[2:])}", styles["SRSBullet"]))
            else:
                story.append(Paragraph(inline_markup(stripped), styles["SRSBody"]))

        output = BytesIO()

        def add_page_number(canvas, document):
            canvas.saveState()
            canvas.setStrokeColor(colors.HexColor("#d7e1ec"))
            canvas.line(18 * mm, 14 * mm, 192 * mm, 14 * mm)
            canvas.setFont("Helvetica", 8)
            canvas.setFillColor(colors.HexColor("#718096"))
            canvas.drawString(18 * mm, 9 * mm, "Software Requirements Specification")
            canvas.drawRightString(192 * mm, 9 * mm, f"Page {document.page}")
            canvas.restoreState()

        document = SimpleDocTemplate(
            output, pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
            topMargin=18 * mm, bottomMargin=20 * mm,
            title=self.title, author="FinTech Requirements Studio",
        )
        document.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
        return output.getvalue()


def generate_srs_document(
    stakeholder_context: str = "",
    retrieved_policies: str = "",
    requirements: Optional[List[dict]] = None,
) -> dict:
    """Generate a detailed IEEE-style SRS directly from stakeholder input."""
    legacy_requirements = ""
    if requirements:
        legacy_requirements = "\n".join(
            f"{req['id']}: {req['statement']} | Category: {req['category']} | "
            f"Priority: {req['priority']} | Compliance: {req['compliance_mapping']}"
            for req in requirements
        )
    prompt = (
        "You are a senior Requirements Engineer. Generate a complete Software "
        "Requirements Specification following the IEEE 830/29148-style structure. "
        "Use only the supplied stakeholder context and retrieved policies. Do not "
        "invent business capabilities. Generate every section in the requested "
        "format, including all four external-interface subsections. Translate the "
        "stakeholder statements into precise, testable requirements. Make the SRS "
        "detailed: explain the business context, actors, system boundaries, normal "
        "and exception flows, validation rules, measurable performance targets, "
        "data entities, security controls, operational constraints, quality goals, "
        "and verification criteria. Provide multiple concrete items in each "
        "applicable Specific Requirements subsection.\n\n"
        f"Stakeholder context:\n{stakeholder_context}\n\n"
        f"Previously structured requirements, if present:\n{legacy_requirements or 'None'}\n\n"
        f"Retrieved policies:\n{retrieved_policies or 'None'}"
    )
    result = invoke_gemini_safely(SRSDocument, prompt)
    if result is None:
        raise RuntimeError("The SRS agent could not generate the SRS document.")
    return {
        "structured_document": result.model_dump(),
        "markdown": result.to_ieee_markdown(),
        "pdf_bytes": result.to_pdf(),
        "pdf_filename": "software_requirements_specification.pdf",
        "source": "SRS Agent",
    }


