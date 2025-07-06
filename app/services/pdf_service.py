from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os
from typing import Dict, Any, List
import base64
import io

class PDFService:
    """Service untuk generate laporan PDF"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles untuk PDF"""
        
        # Style untuk judul utama
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        # Style untuk subjudul
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=18,
            spaceBefore=18,
            textColor=colors.darkblue
        )
        
        # Style untuk teks normal
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=12,
            alignment=TA_JUSTIFY
        )
        
        # Style untuk highlight
        self.highlight_style = ParagraphStyle(
            'CustomHighlight',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=12,
            backColor=colors.lightyellow,
            borderColor=colors.orange,
            borderWidth=1,
            borderPadding=10
        )
        
        # Style untuk warning
        self.warning_style = ParagraphStyle(
            'CustomWarning',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=12,
            backColor=colors.mistyrose,
            borderColor=colors.red,
            borderWidth=1,
            borderPadding=10
        )
    
    def generate_hoax_report(self, analysis_data: Dict[str, Any], output_path: str = None) -> str:
        """Generate laporan analisis hoax dalam format PDF"""
        
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"reports/hoax_analysis_{timestamp}.pdf"
        
        # Pastikan direktori exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Buat dokumen PDF
        doc = SimpleDocTemplate(output_path, pagesize=A4,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Build content
        story = []
        
        # Header
        story.extend(self._build_header())
        
        # Executive Summary
        story.extend(self._build_executive_summary(analysis_data))
        
        # Tweet Analysis
        story.extend(self._build_tweet_analysis(analysis_data))
        
        # Hoax Analysis
        story.extend(self._build_hoax_analysis(analysis_data))
        
        # Bot Detection
        story.extend(self._build_bot_detection(analysis_data))
        
        # Network Analysis
        story.extend(self._build_network_analysis(analysis_data))
        
        # Fact-Check Results
        story.extend(self._build_fact_check_results(analysis_data))
        
        # Recommendations
        story.extend(self._build_recommendations(analysis_data))
        
        # Footer
        story.extend(self._build_footer())
        
        # Build PDF
        doc.build(story)
        
        return output_path
    
    def _build_header(self) -> List:
        """Build header section"""
        content = []
        
        # Title
        title = Paragraph("LAPORAN ANALISIS DETEKSI HOAX", self.title_style)
        content.append(title)
        content.append(Spacer(1, 12))
        
        # Subtitle
        subtitle = Paragraph(f"Tanggal: {datetime.now().strftime('%d %B %Y %H:%M:%S')}", 
                           self.normal_style)
        content.append(subtitle)
        content.append(Spacer(1, 24))
        
        return content
    
    def _build_executive_summary(self, analysis_data: Dict[str, Any]) -> List:
        """Build executive summary section"""
        content = []
        
        content.append(Paragraph("RINGKASAN EKSEKUTIF", self.subtitle_style))
        
        # Ambil data penting
        hoax_analysis = analysis_data.get('hoax_analysis', {})
        bot_detection = analysis_data.get('bot_detection', {})
        network_analysis = analysis_data.get('network_analysis', {})
        
        hoax_prob = hoax_analysis.get('hoax_probability', 0)
        is_hoax = hoax_analysis.get('is_hoax', False)
        bot_prob = bot_detection.get('bot_probability', 0)
        is_bot = bot_detection.get('is_bot', False)
        
        # Summary text
        summary_text = f"""
        Analisis ini mengevaluasi tweet dengan URL: {analysis_data.get('tweet_url', 'N/A')}
        
        <b>Hasil Utama:</b>
        • Probabilitas Hoax: {hoax_prob:.1%}
        • Status Hoax: {'YA' if is_hoax else 'TIDAK'}
        • Probabilitas Bot: {bot_prob:.1%}
        • Status Bot: {'YA' if is_bot else 'TIDAK'}
        • Tingkat Risiko: {self._get_overall_risk_level(hoax_prob, bot_prob)}
        
        <b>Kesimpulan:</b>
        {self._generate_executive_conclusion(hoax_prob, bot_prob, is_hoax, is_bot)}
        """
        
        # Tentukan style berdasarkan risiko
        if is_hoax or hoax_prob > 0.7:
            style = self.warning_style
        elif hoax_prob > 0.5:
            style = self.highlight_style
        else:
            style = self.normal_style
        
        content.append(Paragraph(summary_text, style))
        content.append(Spacer(1, 24))
        
        return content
    
    def _build_tweet_analysis(self, analysis_data: Dict[str, Any]) -> List:
        """Build tweet analysis section"""
        content = []
        
        content.append(Paragraph("ANALISIS TWEET", self.subtitle_style))
        
        tweet_data = analysis_data.get('tweet_data', {})
        user_data = tweet_data.get('user', {})
        
        # Tweet info table
        tweet_info = [
            ['Tweet ID', tweet_data.get('tweet_id', 'N/A')],
            ['Teks Tweet', tweet_data.get('text', 'N/A')[:100] + '...'],
            ['Tanggal Posting', str(tweet_data.get('created_at', 'N/A'))],
            ['Retweet Count', str(tweet_data.get('retweet_count', 0))],
            ['Like Count', str(tweet_data.get('like_count', 0))],
            ['Reply Count', str(tweet_data.get('reply_count', 0))],
        ]
        
        tweet_table = Table(tweet_info, colWidths=[2*inch, 4*inch])
        tweet_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        content.append(tweet_table)
        content.append(Spacer(1, 18))
        
        # User info
        content.append(Paragraph("Informasi Pengguna:", self.normal_style))
        
        user_info = [
            ['Username', '@' + user_data.get('username', 'N/A')],
            ['Display Name', user_data.get('display_name', 'N/A')],
            ['Bio', user_data.get('bio', 'N/A')[:100] + '...'],
            ['Followers', str(user_data.get('followers_count', 0))],
            ['Following', str(user_data.get('following_count', 0))],
            ['Total Tweet', str(user_data.get('tweet_count', 0))],
            ['Verified', 'Ya' if user_data.get('verified', False) else 'Tidak']
        ]
        
        user_table = Table(user_info, colWidths=[2*inch, 4*inch])
        user_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightcyan),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        content.append(user_table)
        content.append(Spacer(1, 24))
        
        return content
    
    def _build_hoax_analysis(self, analysis_data: Dict[str, Any]) -> List:
        """Build hoax analysis section"""
        content = []
        
        content.append(Paragraph("ANALISIS HOAX", self.subtitle_style))
        
        hoax_analysis = analysis_data.get('hoax_analysis', {})
        
        # Hoax probability and status
        hoax_prob = hoax_analysis.get('hoax_probability', 0)
        is_hoax = hoax_analysis.get('is_hoax', False)
        
        status_text = f"""
        <b>Status Hoax:</b> {'TERDETEKSI HOAX' if is_hoax else 'TIDAK TERDETEKSI HOAX'}
        <b>Probabilitas:</b> {hoax_prob:.1%}
        <b>Tingkat Kepercayaan:</b> {hoax_analysis.get('confidence_level', 'N/A').title()}
        """
        
        style = self.warning_style if is_hoax else self.normal_style
        content.append(Paragraph(status_text, style))
        content.append(Spacer(1, 12))
        
        # Analysis summary
        summary = hoax_analysis.get('analysis_summary', 'Tidak ada ringkasan tersedia')
        content.append(Paragraph(f"<b>Ringkasan Analisis:</b><br/>{summary}", self.normal_style))
        content.append(Spacer(1, 12))
        
        # Red flags
        red_flags = hoax_analysis.get('red_flags', [])
        if red_flags:
            content.append(Paragraph("<b>Indikator Bahaya:</b>", self.normal_style))
            for flag in red_flags:
                content.append(Paragraph(f"• {flag}", self.normal_style))
            content.append(Spacer(1, 12))
        
        # Reasons
        reasons = hoax_analysis.get('reasons', [])
        if reasons:
            content.append(Paragraph("<b>Alasan Analisis:</b>", self.normal_style))
            for reason in reasons:
                content.append(Paragraph(f"• {reason}", self.normal_style))
            content.append(Spacer(1, 12))
        
        # Category
        category = hoax_analysis.get('category', 'normal')
        content.append(Paragraph(f"<b>Kategori:</b> {category.title()}", self.normal_style))
        content.append(Spacer(1, 24))
        
        return content
    
    def _build_bot_detection(self, analysis_data: Dict[str, Any]) -> List:
        """Build bot detection section"""
        content = []
        
        content.append(Paragraph("DETEKSI BOT", self.subtitle_style))
        
        bot_detection = analysis_data.get('bot_detection', {})
        
        # Bot probability and status
        bot_prob = bot_detection.get('bot_probability', 0)
        is_bot = bot_detection.get('is_bot', False)
        
        status_text = f"""
        <b>Status Bot:</b> {'TERDETEKSI BOT' if is_bot else 'BUKAN BOT'}
        <b>Probabilitas:</b> {bot_prob:.1%}
        <b>Tingkat Kepercayaan:</b> {bot_detection.get('confidence_level', 'N/A').title()}
        """
        
        style = self.warning_style if is_bot else self.normal_style
        content.append(Paragraph(status_text, style))
        content.append(Spacer(1, 12))
        
        # Explanation
        explanation = bot_detection.get('explanation', 'Tidak ada penjelasan tersedia')
        content.append(Paragraph(f"<b>Penjelasan:</b><br/>{explanation}", self.normal_style))
        content.append(Spacer(1, 12))
        
        # Risk factors
        risk_factors = bot_detection.get('risk_factors', [])
        if risk_factors:
            content.append(Paragraph("<b>Faktor Risiko:</b>", self.normal_style))
            for factor in risk_factors:
                content.append(Paragraph(f"• {factor}", self.normal_style))
            content.append(Spacer(1, 24))
        
        return content
    
    def _build_network_analysis(self, analysis_data: Dict[str, Any]) -> List:
        """Build network analysis section"""
        content = []
        
        content.append(Paragraph("ANALISIS JARINGAN", self.subtitle_style))
        
        network_data = analysis_data.get('network_analysis', {})
        
        if not network_data:
            content.append(Paragraph("Data jaringan tidak tersedia", self.normal_style))
            content.append(Spacer(1, 24))
            return content
        
        # Network metrics
        metrics = network_data.get('network_metrics', {})
        
        metrics_text = f"""
        <b>Metrik Jaringan:</b>
        • Total Node: {metrics.get('num_nodes', 0)}
        • Total Edge: {metrics.get('num_edges', 0)}
        • Densitas: {metrics.get('density', 0):.3f}
        • Komponen Terhubung: {metrics.get('num_components', 0)}
        """
        
        content.append(Paragraph(metrics_text, self.normal_style))
        content.append(Spacer(1, 12))
        
        # Influential nodes
        influential_nodes = network_data.get('influential_nodes', [])
        if influential_nodes:
            content.append(Paragraph("<b>Node Paling Berpengaruh:</b>", self.normal_style))
            for i, node in enumerate(influential_nodes[:5]):  # Top 5
                content.append(Paragraph(
                    f"{i+1}. {node.get('label', 'N/A')} (Skor: {node.get('influence_score', 0):.3f})",
                    self.normal_style
                ))
            content.append(Spacer(1, 12))
        
        # Network report
        network_report = network_data.get('network_report', {})
        if network_report:
            spread_type = network_report.get('spread_type', 'N/A')
            risk_level = network_report.get('risk_level', 'N/A')
            
            report_text = f"""
            <b>Laporan Jaringan:</b>
            • Jenis Penyebaran: {spread_type}
            • Tingkat Risiko: {risk_level}
            • Ringkasan: {network_report.get('summary', 'N/A')}
            """
            
            content.append(Paragraph(report_text, self.normal_style))
        
        content.append(Spacer(1, 24))
        
        return content
    
    def _build_fact_check_results(self, analysis_data: Dict[str, Any]) -> List:
        """Build fact-check results section"""
        content = []
        
        content.append(Paragraph("HASIL FACT-CHECK", self.subtitle_style))
        
        fact_check = analysis_data.get('fact_check_results', {})
        
        if not fact_check:
            content.append(Paragraph("Data fact-check tidak tersedia", self.normal_style))
            content.append(Spacer(1, 24))
            return content
        
        # Search summary
        total_results = fact_check.get('total_results', 0)
        query = fact_check.get('query', 'N/A')
        
        summary_text = f"""
        <b>Ringkasan Pencarian:</b>
        • Query: {query}
        • Total Hasil: {total_results}
        """
        
        content.append(Paragraph(summary_text, self.normal_style))
        content.append(Spacer(1, 12))
        
        # Supporting vs contradicting sources
        supporting = len(fact_check.get('supporting_sources', []))
        contradicting = len(fact_check.get('contradicting_sources', []))
        neutral = len(fact_check.get('neutral_sources', []))
        
        sources_text = f"""
        <b>Distribusi Sumber:</b>
        • Sumber Pendukung: {supporting}
        • Sumber Bertentangan: {contradicting}
        • Sumber Netral: {neutral}
        """
        
        content.append(Paragraph(sources_text, self.normal_style))
        content.append(Spacer(1, 12))
        
        # Key sources
        if contradicting > 0:
            content.append(Paragraph("<b>Sumber yang Bertentangan:</b>", self.normal_style))
            for source in fact_check.get('contradicting_sources', [])[:3]:  # Top 3
                content.append(Paragraph(
                    f"• {source.get('title', 'N/A')} ({source.get('source', 'N/A')})",
                    self.normal_style
                ))
            content.append(Spacer(1, 12))
        
        content.append(Spacer(1, 24))
        
        return content
    
    def _build_recommendations(self, analysis_data: Dict[str, Any]) -> List:
        """Build recommendations section"""
        content = []
        
        content.append(Paragraph("REKOMENDASI", self.subtitle_style))
        
        # Collect recommendations from different analyses
        all_recommendations = []
        
        # Hoax analysis recommendations
        hoax_recs = analysis_data.get('hoax_analysis', {}).get('recommendations', [])
        all_recommendations.extend(hoax_recs)
        
        # Bot detection recommendations
        bot_recs = analysis_data.get('bot_detection', {}).get('recommendations', [])
        all_recommendations.extend(bot_recs)
        
        # Network analysis recommendations
        network_recs = analysis_data.get('network_analysis', {}).get('network_report', {}).get('recommendations', [])
        all_recommendations.extend(network_recs)
        
        # Remove duplicates
        unique_recommendations = list(set(all_recommendations))
        
        if unique_recommendations:
            for i, rec in enumerate(unique_recommendations, 1):
                content.append(Paragraph(f"{i}. {rec}", self.normal_style))
        else:
            content.append(Paragraph("Tidak ada rekomendasi khusus", self.normal_style))
        
        content.append(Spacer(1, 24))
        
        return content
    
    def _build_footer(self) -> List:
        """Build footer section"""
        content = []
        
        content.append(Spacer(1, 24))
        
        footer_text = f"""
        <b>Catatan:</b> Laporan ini dibuat secara otomatis oleh sistem Twitter Hoax Detector.
        Hasil analisis bersifat prediktif dan sebaiknya diverifikasi lebih lanjut dengan sumber-sumber terpercaya.
        
        <b>Tanggal Generate:</b> {datetime.now().strftime('%d %B %Y %H:%M:%S')}
        """
        
        content.append(Paragraph(footer_text, self.normal_style))
        
        return content
    
    def _get_overall_risk_level(self, hoax_prob: float, bot_prob: float) -> str:
        """Dapatkan tingkat risiko keseluruhan"""
        max_prob = max(hoax_prob, bot_prob)
        
        if max_prob > 0.7:
            return "TINGGI"
        elif max_prob > 0.5:
            return "SEDANG"
        else:
            return "RENDAH"
    
    def _generate_executive_conclusion(self, hoax_prob: float, bot_prob: float, is_hoax: bool, is_bot: bool) -> str:
        """Generate kesimpulan eksekutif"""
        
        if is_hoax and is_bot:
            return "Tweet ini berpotensi tinggi sebagai hoax dan kemungkinan disebarkan oleh bot. Perlu tindakan segera."
        elif is_hoax:
            return "Tweet ini berpotensi sebagai hoax. Disarankan untuk tidak mempercayai dan menyebarkan informasi ini."
        elif is_bot:
            return "Tweet ini kemungkinan disebarkan oleh bot. Periksa kredibilitas informasi dengan teliti."
        elif hoax_prob > 0.5 or bot_prob > 0.5:
            return "Tweet ini memiliki indikator yang perlu diwaspadai. Lakukan verifikasi sebelum mempercayai informasi."
        else:
            return "Tweet ini tampak normal, namun tetap disarankan untuk melakukan verifikasi informasi dari sumber terpercaya." 