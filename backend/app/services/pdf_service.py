"""
PDF Generation Service
Handles creation of professional PDF reports using ReportLab
"""

import logging
import io
from datetime import datetime
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

logger = logging.getLogger(__name__)


class PDFService:
    """Service for generating PDF reports"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report"""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1e40af')  # Blue
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=12,
            textColor=colors.HexColor('#1f2937'),  # Dark gray
            borderWidth=1,
            borderColor=colors.HexColor('#e5e7eb'),
            borderPadding=5,
            backColor=colors.HexColor('#f9fafb')  # Light gray background
        ))
        
        # Subsection header style
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=15,
            spaceAfter=8,
            textColor=colors.HexColor('#374151')
        ))
        
        # Key metric style
        self.styles.add(ParagraphStyle(
            name='KeyMetric',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceBefore=8,
            spaceAfter=8,
            leftIndent=20,
            bulletIndent=10,
            bulletFontName='Helvetica-Bold'
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#6b7280')
        ))
    
    def generate_analytics_report(
        self, 
        data: Dict[str, Any], 
        ai_analysis: Optional[str] = None
    ) -> bytes:
        """Generate a comprehensive analytics PDF report"""
        
        buffer = io.BytesIO()
        
        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build content
        story = []
        
        # Title page
        story.extend(self._build_title_page(data))
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self._build_executive_summary(data))
        
        # Key metrics
        story.extend(self._build_key_metrics(data))
        
        # Anomaly analysis
        story.extend(self._build_anomaly_analysis(data))
        
        # Notification summary
        story.extend(self._build_notification_summary(data))
        
        # System performance
        story.extend(self._build_system_performance(data))
        
        # AI Analysis (if available)
        if ai_analysis:
            story.extend(self._build_ai_analysis_section(ai_analysis))
        
        # Footer
        story.extend(self._build_footer())
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        buffer.seek(0)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def _build_title_page(self, data: Dict[str, Any]) -> List:
        """Build the title page"""
        content = []
        
        # Title
        content.append(Paragraph("FINANCEPULSE", self.styles['ReportTitle']))
        content.append(Spacer(1, 0.2 * inch))
        content.append(Paragraph("Anomaly Detection & Security Analytics Report", 
                                 self.styles['Heading1']))
        
        content.append(Spacer(1, 0.5 * inch))
        
        # Report metadata
        timestamp = data.get('timestamp', datetime.utcnow().isoformat())
        try:
            if timestamp.endswith('Z'):
                timestamp = timestamp.replace('Z', '+00:00')
            report_date = datetime.fromisoformat(timestamp).strftime('%B %d, %Y at %I:%M %p UTC')
        except:
            report_date = datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')
        
        metadata_table = Table([
            ['Generated:', report_date],
            ['Report Period:', 'Last 24 Hours'],
            ['System Version:', 'FinancePulse v2.1'],
            ['Classification:', 'CONFIDENTIAL']
        ], colWidths=[2*inch, 4*inch])
        
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
        ]))
        
        content.append(metadata_table)
        content.append(Spacer(1, 1 * inch))
        
        return content
    
    def _build_executive_summary(self, data: Dict[str, Any]) -> List:
        """Build executive summary section"""
        content = []
        
        content.append(Paragraph("EXECUTIVE SUMMARY", self.styles['SectionHeader']))
        
        total_txns = data.get('total_transactions', 0)
        anomalies = data.get('anomalies_detected', 0)
        anomaly_rate = data.get('anomaly_rate', 0) * 100
        confidence = data.get('average_confidence', 0) * 100
        
        summary_text = f"""
        During the reporting period, FinancePulse processed <b>{total_txns:,}</b> transactions 
        and detected <b>{anomalies}</b> anomalous activities, representing a <b>{anomaly_rate:.2f}%</b> 
        anomaly rate. The system maintained an average confidence score of <b>{confidence:.1f}%</b>, 
        demonstrating {'excellent' if anomaly_rate < 2 else 'elevated'} fraud detection capabilities.
        """
        
        content.append(Paragraph(summary_text, self.styles['Normal']))
        content.append(Spacer(1, 0.2 * inch))
        
        return content
    
    def _build_key_metrics(self, data: Dict[str, Any]) -> List:
        """Build key metrics section"""
        content = []
        
        content.append(Paragraph("KEY PERFORMANCE METRICS", self.styles['SectionHeader']))
        
        # Create metrics table
        metrics_data = [
            ['Metric', 'Value', 'Status'],
            ['Total Transactions', f"{data.get('total_transactions', 0):,}", '✓ Normal'],
            ['Anomalies Detected', str(data.get('anomalies_detected', 0)), 
             '⚠ Elevated' if data.get('anomalies_detected', 0) > 50 else '✓ Normal'],
            ['Anomaly Rate', f"{data.get('anomaly_rate', 0) * 100:.2f}%", 
             '⚠ High' if data.get('anomaly_rate', 0) > 0.03 else '✓ Normal'],
            ['System Confidence', f"{data.get('average_confidence', 0) * 100:.1f}%", '✓ Excellent'],
            ['Detection Accuracy', f"{data.get('system_performance', {}).get('detection_accuracy', 0.94) * 100:.1f}%", '✓ Excellent']
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
        ]))
        
        content.append(metrics_table)
        content.append(Spacer(1, 0.3 * inch))
        
        return content
    
    def _build_anomaly_analysis(self, data: Dict[str, Any]) -> List:
        """Build anomaly analysis section"""
        content = []
        
        content.append(Paragraph("ANOMALY BREAKDOWN", self.styles['SectionHeader']))
        
        # Risk level analysis
        content.append(Paragraph("Risk Level Distribution", self.styles['SubsectionHeader']))
        
        risk_levels = data.get('risk_levels', {})
        risk_data = [
            ['Risk Level', 'Count', 'Percentage'],
            ['Critical', str(risk_levels.get('critical', 0)), 
             f"{(risk_levels.get('critical', 0) / max(data.get('anomalies_detected', 1), 1) * 100):.1f}%"],
            ['High', str(risk_levels.get('high', 0)),
             f"{(risk_levels.get('high', 0) / max(data.get('anomalies_detected', 1), 1) * 100):.1f}%"],
            ['Medium', str(risk_levels.get('medium', 0)),
             f"{(risk_levels.get('medium', 0) / max(data.get('anomalies_detected', 1), 1) * 100):.1f}%"],
            ['Low', str(risk_levels.get('low', 0)),
             f"{(risk_levels.get('low', 0) / max(data.get('anomalies_detected', 1), 1) * 100):.1f}%"]
        ]
        
        risk_table = Table(risk_data, colWidths=[2*inch, 1*inch, 1.5*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
        ]))
        
        content.append(risk_table)
        content.append(Spacer(1, 0.2 * inch))
        
        # Anomaly types
        content.append(Paragraph("Anomaly Type Distribution", self.styles['SubsectionHeader']))
        
        anomaly_breakdown = data.get('anomaly_breakdown', {})
        for anomaly_type, count in anomaly_breakdown.items():
            percentage = (count / max(data.get('anomalies_detected', 1), 1)) * 100
            content.append(Paragraph(
                f"• <b>{anomaly_type.replace('_', ' ').title()}:</b> {count} cases ({percentage:.1f}%)",
                self.styles['KeyMetric']
            ))
        
        content.append(Spacer(1, 0.3 * inch))
        
        return content
    
    def _build_notification_summary(self, data: Dict[str, Any]) -> List:
        """Build notification summary section"""
        content = []
        
        content.append(Paragraph("NOTIFICATION SUMMARY", self.styles['SectionHeader']))
        
        notifications = data.get('notifications_sent', {})
        total_notifications = notifications.get('total', 0)
        email_count = notifications.get('email', 0)
        phone_count = notifications.get('phone', 0)
        
        notification_text = f"""
        A total of <b>{total_notifications}</b> notifications were sent during the reporting period:
        """
        content.append(Paragraph(notification_text, self.styles['Normal']))
        content.append(Spacer(1, 0.1 * inch))
        
        content.append(Paragraph(f"• <b>Email Notifications:</b> {email_count}", self.styles['KeyMetric']))
        content.append(Paragraph(f"• <b>Phone Notifications:</b> {phone_count}", self.styles['KeyMetric']))
        
        if data.get('anomalies_detected', 0) > 0:
            notification_rate = (total_notifications / data.get('anomalies_detected', 1)) * 100
            content.append(Paragraph(f"• <b>Notification Coverage:</b> {notification_rate:.1f}%", self.styles['KeyMetric']))
        
        content.append(Spacer(1, 0.3 * inch))
        
        return content
    
    def _build_system_performance(self, data: Dict[str, Any]) -> List:
        """Build system performance section"""
        content = []
        
        content.append(Paragraph("SYSTEM PERFORMANCE", self.styles['SectionHeader']))
        
        performance = data.get('system_performance', {})
        
        perf_data = [
            ['Performance Metric', 'Value', 'Benchmark'],
            ['Detection Accuracy', f"{performance.get('detection_accuracy', 0.94) * 100:.1f}%", '> 90%'],
            ['False Positive Rate', f"{performance.get('false_positive_rate', 0.08) * 100:.1f}%", '< 10%'],
            ['Average Response Time', f"{performance.get('response_time_ms', 45)} ms", '< 100ms']
        ]
        
        perf_table = Table(perf_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        perf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fdf4')])
        ]))
        
        content.append(perf_table)
        content.append(Spacer(1, 0.3 * inch))
        
        return content
    
    def _build_ai_analysis_section(self, ai_analysis: str) -> List:
        """Build AI analysis section"""
        content = []
        
        content.append(PageBreak())
        content.append(Paragraph("AI-POWERED ANALYSIS", self.styles['SectionHeader']))
        
        # Split analysis into paragraphs for better formatting
        analysis_lines = ai_analysis.split('\n')
        current_paragraph = ""
        
        for line in analysis_lines:
            line = line.strip()
            if not line:
                if current_paragraph:
                    content.append(Paragraph(current_paragraph, self.styles['Normal']))
                    content.append(Spacer(1, 0.1 * inch))
                    current_paragraph = ""
            elif line.isupper() or line.endswith('=') or '=' in line:
                # This looks like a header
                if current_paragraph:
                    content.append(Paragraph(current_paragraph, self.styles['Normal']))
                    current_paragraph = ""
                content.append(Paragraph(f"<b>{line.replace('=', '').strip()}</b>", self.styles['SubsectionHeader']))
            else:
                if current_paragraph:
                    current_paragraph += " " + line
                else:
                    current_paragraph = line
        
        # Add any remaining paragraph
        if current_paragraph:
            content.append(Paragraph(current_paragraph, self.styles['Normal']))
        
        content.append(Spacer(1, 0.3 * inch))
        
        return content
    
    def _build_footer(self) -> List:
        """Build report footer"""
        content = []
        
        content.append(Spacer(1, 0.5 * inch))
        content.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.HexColor('#e5e7eb')))
        content.append(Spacer(1, 0.2 * inch))
        
        footer_text = """
        <b>CONFIDENTIAL REPORT</b><br/>
        Generated by FinancePulse AI Intelligence Engine<br/>
        This report contains confidential information and should be handled according to company data security policies.
        """
        
        content.append(Paragraph(footer_text, self.styles['Footer']))
        
        return content


# Global service instance
pdf_service = PDFService()