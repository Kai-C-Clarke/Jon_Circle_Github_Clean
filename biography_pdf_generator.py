#!/usr/bin/env python3
"""
Biography PDF Generator - Magazine Style
Creates National Geographic-style PDFs from AI-generated biographies
"""

import os
import re
import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from io import BytesIO
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Track used images to avoid duplicates
used_images_global = set()


class BiographyPDFGenerator:
    """Magazine-style PDF generator for biographies."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the PDF generator."""
        self.config = config or {}
        self.used_images = set()
        self.family_names = self.config.get('family_names', [])
        
    def _create_css(self) -> str:
        """Create magazine-style CSS with spreads and text wrapping."""
        return """
        @page {
            size: A4;
            margin: 20mm;
            
            @top-center {
                content: "The Circle - Family Memory Album";
                font-family: Georgia, serif;
                font-size: 9pt;
                color: #888;
            }
            
            @bottom-center {
                content: counter(page);
                font-family: Georgia, serif;
                font-size: 9pt;
                color: #888;
            }
        }
        
        @page:blank {
            @top-center { content: none; }
            @bottom-center { content: none; }
        }
        
        * {
            box-sizing: border-box;
        }
        
        body {
            font-family: Georgia, serif;
            font-size: 11pt;
            line-height: 1.8;
            color: #333;
            margin: 0;
            padding: 0;
        }
        
        /* Cover Page with Photo */
        .cover {
            position: relative;
            min-height: 280mm;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            align-items: center;
            text-align: center;
            page-break-after: always;
            background: linear-gradient(to bottom, #F5F5DC 0%, #FFF 100%);
            padding: 40px;
        }
        
        .cover-background {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 70%;
            overflow: hidden;
        }
        
        .cover-background img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            opacity: 0.3;
        }
        
        .cover-content {
            position: relative;
            z-index: 10;
            background: rgba(255, 255, 255, 0.95);
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        
        .cover h1 {
            font-size: 52pt;
            color: #8B4513;
            margin: 0 0 20px 0;
            font-weight: normal;
            letter-spacing: 4px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        
        .cover h2 {
            font-size: 20pt;
            color: #D4AF37;
            font-style: italic;
            font-weight: normal;
            margin: 0 0 30px 0;
        }
        
        .cover .date {
            font-size: 11pt;
            color: #666;
        }
        
        .hero-cover-image {
            width: 100%;
            max-width: 600px;
            height: auto;
            margin: 30px auto;
            border: 4px solid #8B4513;
            box-shadow: 0 8px 30px rgba(0,0,0,0.2);
        }
        
        /* Table of Contents */
        .toc {
            page-break-after: always;
            padding: 60px 40px;
            background: linear-gradient(to bottom, #FFF8F0 0%, #FFF 100%);
        }
        
        .toc h2 {
            font-size: 28pt;
            color: #8B4513;
            margin-bottom: 40px;
            text-align: center;
            letter-spacing: 3px;
        }
        
        .toc-entry {
            margin: 20px 0;
            padding: 0;
            display: block;
            overflow: hidden;
            background: white;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .toc-entry-content {
            display: flex;
            align-items: center;
            padding: 15px;
        }
        
        .toc-thumbnail {
            width: 80px;
            height: 80px;
            object-fit: cover;
            margin-right: 20px;
            border-radius: 4px;
            flex-shrink: 0;
        }
        
        .toc-text {
            flex: 1;
        }
        
        .toc-chapter-title {
            font-size: 14pt;
            color: #2c3e50;
            margin: 0;
            font-weight: 600;
            border-left: 4px solid #D4AF37;
            padding-left: 15px;
        }
        
        /* Chapter Styles - Spread Layout */
        .chapter {
            page-break-before: always;
            margin-bottom: 40px;
        }
        
        .chapter-title {
            font-size: 28pt;
            color: #D4AF37;
            margin: 30px 0 40px 0;
            font-weight: bold;
            text-align: center;
            letter-spacing: 3px;
            border-bottom: 2px solid #D4AF37;
            padding-bottom: 15px;
        }
        
        .chapter-narrative {
            text-align: justify;
            margin: 20px 0;
            line-height: 1.9;
            hyphens: auto;
        }
        
        .chapter-narrative p {
            margin: 0 0 18px 0;
            text-indent: 0;
        }
        
        /* Drop caps removed - WeasyPrint doesn't support ::first-letter reliably */
        
        /* Chapter text - ALWAYS two columns for magazine style */
        .chapter-narrative {
            column-count: 2;
            column-gap: 35px;
            column-rule: 1px solid #DDD;
            text-align: justify;
            line-height: 1.8;
            margin: 25px 0;
        }
        
        /* Embedded Images (no floats - WeasyPrint limitation) */
        .image-embed {
            margin: 25px auto;
            max-width: 60%;
            page-break-inside: avoid;
            text-align: center;
        }
        
        .image-embed img {
            width: 100%;
            height: auto;
            border: 3px solid #DDD;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .image-embed .photo-caption {
            margin-top: 10px;
        }
        
        /* Full-page spread layouts */
        .spread-layout {
            page-break-before: always;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0;
            min-height: 250mm;
        }
        
        .spread-image {
            grid-column: 1;
            overflow: hidden;
            background: #F5F5DC;
        }
        
        .spread-image img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .spread-text {
            grid-column: 2;
            padding: 40px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        
        .spread-text h3 {
            font-size: 20pt;
            color: #8B4513;
            margin-bottom: 20px;
        }
        
        .spread-text p {
            text-align: justify;
            line-height: 1.8;
            margin-bottom: 15px;
        }
        
        /* Pull Quotes - Magazine Style */
        .pull-quote {
            background: #F5F5DC;
            padding: 30px 35px;
            margin: 35px 0;
            border-left: 6px solid #D4AF37;
            font-size: 15pt;
            font-style: italic;
            color: #555;
            page-break-inside: avoid;
            line-height: 1.6;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        /* Photo Layouts - Magazine Grid */
        .photo-section {
            margin: 35px 0;
            page-break-inside: avoid;
        }
        
        .photo-grid {
            display: grid;
            gap: 18px;
            margin: 25px 0;
        }
        
        .photo-grid-1 {
            grid-template-columns: 1fr;
        }
        
        .photo-grid-2 {
            grid-template-columns: 1fr 1fr;
        }
        
        .photo-grid-3 {
            grid-template-columns: 2fr 1fr 1fr;
        }
        
        .photo-item {
            break-inside: avoid;
        }
        
        .photo-item img {
            width: 100%;
            height: auto;
            display: block;
            border: 3px solid #DDD;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .photo-caption {
            font-size: 9.5pt;
            font-style: italic;
            color: #666;
            margin: 10px 0 0 0;
            text-align: center;
            line-height: 1.4;
        }
        
        /* Hero Images - Full Page */
        .hero-image {
            width: 100%;
            margin: 35px 0;
            page-break-inside: avoid;
        }
        
        .hero-image img {
            width: 100%;
            height: auto;
            border: 4px solid #8B4513;
            box-shadow: 0 6px 25px rgba(0,0,0,0.15);
        }
        
        .hero-caption {
            font-size: 11pt;
            font-style: italic;
            color: #666;
            text-align: center;
            margin: 12px 0;
            line-height: 1.5;
        }
        
        /* Full-Page Image (occupies entire page) */
        .fullpage-image {
            page-break-before: always;
            page-break-after: always;
            min-height: 250mm;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 0;
        }
        
        .fullpage-image img {
            max-width: 100%;
            max-height: 240mm;
            object-fit: contain;
            border: 5px solid #8B4513;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        
        .fullpage-caption {
            margin-top: 15px;
            font-size: 12pt;
            font-style: italic;
            color: #666;
            text-align: center;
        }
        
        /* Highlighted Names */
        .highlight-name {
            font-weight: bold;
            color: #8B4513;
        }
        """
    
    def _get_safe_photo_path(self, upload_folder: str, filename: str) -> Optional[str]:
        """Get safe photo path preventing directory traversal."""
        try:
            safe_filename = os.path.basename(filename)
            safe_filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', safe_filename)
            
            full_path = os.path.join(upload_folder, safe_filename)
            upload_folder_abs = os.path.abspath(upload_folder)
            full_path_abs = os.path.abspath(full_path)
            
            if not full_path_abs.startswith(upload_folder_abs):
                logger.warning(f"Path traversal attempt detected: {filename}")
                return None
            
            if not os.path.exists(full_path_abs):
                logger.warning(f"Photo file not found: {full_path_abs}")
                return None
            
            return full_path_abs
            
        except Exception as e:
            logger.error(f"Error getting safe photo path for {filename}: {e}")
            return None
    
    def _match_photos_to_chapter(self, chapter_title: str, chapter_text: str, 
                                 available_photos: List[Dict], max_photos: int = 3) -> List[Dict]:
        """Match photos to chapter content using smart algorithms."""
        if not available_photos:
            return []
        
        # Extract year from title (e.g., "1990s" or "1990-1995")
        year_match = re.search(r'(\d{4})', chapter_title)
        chapter_year = int(year_match.group(1)) if year_match else None
        
        scored_photos = []
        
        for photo in available_photos:
            # Skip already used photos
            if photo['filename'] in self.used_images:
                continue
            
            score = 0
            
            # Year matching (highest priority)
            if chapter_year and photo.get('year'):
                year_diff = abs(int(photo['year']) - chapter_year)
                if year_diff == 0:
                    score += 100
                elif year_diff <= 2:
                    score += 50
                elif year_diff <= 5:
                    score += 20
            
            # Family name matching
            photo_text = f"{photo.get('title', '')} {photo.get('description', '')} {photo.get('people', '')}".lower()
            chapter_combined = f"{chapter_title} {chapter_text}".lower()
            
            for name in self.family_names:
                if name.lower() in photo_text and name.lower() in chapter_combined:
                    score += 30
            
            # Keyword matching
            keywords = re.findall(r'\b\w{4,}\b', chapter_combined[:500])  # First 500 chars
            for keyword in set(keywords):
                if keyword in photo_text:
                    score += 5
            
            if score > 0:
                scored_photos.append((score, photo))
        
        # Sort by score and take top matches
        scored_photos.sort(reverse=True, key=lambda x: x[0])
        selected = [photo for score, photo in scored_photos[:max_photos]]
        
        # Mark as used
        for photo in selected:
            self.used_images.add(photo['filename'])
        
        return selected
    
    def _extract_pull_quote(self, text: str, max_length: int = 150) -> Optional[str]:
        """Extract a compelling pull quote from text."""
        sentences = re.split(r'[.!?]+', text)
        
        # Look for sentences with quotes or emotional content
        for sentence in sentences:
            clean = sentence.strip()
            if 30 < len(clean) < max_length:
                if any(char in clean for char in ['"', "'", '!']) or \
                   any(word in clean.lower() for word in ['love', 'remember', 'never', 'always', 'first']):
                    return clean + '.'
        
        # Fallback: interesting length sentence
        for sentence in sentences:
            clean = sentence.strip()
            if 40 < len(clean) < max_length:
                return clean + '.'
        
        return None
    
    def _highlight_names(self, text: str) -> str:
        """Highlight family names in text."""
        for name in self.family_names:
            # Use word boundaries to match full names
            pattern = r'\b(' + re.escape(name) + r')\b'
            text = re.sub(pattern, r'<span class="highlight-name">\1</span>', text, flags=re.IGNORECASE)
        return text
    
    def _create_photo_layout(self, photos: List[Dict], upload_folder: str) -> str:
        """Create dynamic photo grid HTML."""
        if not photos:
            return ""
        
        num_photos = len(photos)
        grid_class = f"photo-grid photo-grid-{num_photos}"
        
        html = f'<div class="photo-section"><div class="{grid_class}">'
        
        for photo in photos:
            photo_path = self._get_safe_photo_path(upload_folder, photo['filename'])
            if not photo_path:
                continue
            
            caption = photo.get('title', '') or photo.get('description', '')
            if photo.get('year'):
                caption = f"{caption} ({photo['year']})" if caption else f"({photo['year']})"
            
            html += f'''
            <div class="photo-item">
                <img src="file://{photo_path}" alt="{caption}">
                {f'<p class="photo-caption">{caption}</p>' if caption else ''}
            </div>
            '''
        
        html += '</div></div>'
        return html
    
    def _create_chapter_html(self, chapter: Dict, photos: List[Dict], upload_folder: str) -> str:
        """Create HTML for a single chapter with magazine-style spread layouts."""
        title = chapter['title']
        narrative = chapter['narrative']
        
        # Highlight family names
        narrative = self._highlight_names(narrative)
        
        # Extract pull quote
        pull_quote = self._extract_pull_quote(narrative)
        
        # Determine layout based on content and photos
        text_length = len(narrative)
        has_photos = len(photos) > 0
        
        html = '<div class="chapter">'
        html += f'<h2 class="chapter-title">{title}</h2>'
        
        # SPREAD LAYOUT: If we have 1 photo and long text, use facing page layout
        if has_photos and len(photos) == 1 and text_length > 800:
            photo_path = self._get_safe_photo_path(upload_folder, photos[0]['filename'])
            if photo_path:
                caption = photos[0].get('title', '') or photos[0].get('description', '')
                if photos[0].get('year'):
                    caption = f"{caption} ({photos[0]['year']})" if caption else f"({photos[0]['year']})"
                
                # Full-page image on one page
                html += f'''
                <div class="fullpage-image">
                    <img src="file://{photo_path}" alt="{caption}">
                    {f'<p class="fullpage-caption">{caption}</p>' if caption else ''}
                </div>
                '''
                
                # Text on facing page with drop cap
                paragraphs = [p.strip() for p in narrative.split('\n\n') if p.strip()]
                html += '<div class="chapter-narrative">'
                
                # Add pull quote in the middle
                halfway = len(paragraphs) // 2
                for i, para in enumerate(paragraphs):
                    html += f'<p>{para}</p>'
                    if i == halfway and pull_quote:
                        html += f'<div class="pull-quote">{pull_quote}</div>'
                
                html += '</div>'
                photos = photos[1:]  # Remove used photo
        
        # SPREAD LAYOUT: If we have 2-3 photos, use grid layout with text
        elif has_photos and len(photos) >= 2:
            # Start with text
            paragraphs = [p.strip() for p in narrative.split('\n\n') if p.strip()]
            
            # First paragraph
            html += '<div class="chapter-narrative">'
            if paragraphs:
                html += f'<p>{paragraphs[0]}</p>'
            html += '</div>'
            
            # Pull quote if we have one
            if pull_quote:
                html += f'<div class="pull-quote">{pull_quote}</div>'
            
            # Photo grid
            html += self._create_photo_layout(photos[:3], upload_folder)
            
            # Remaining text
            if len(paragraphs) > 1:
                use_columns = text_length > 1200
                column_class = 'two-column' if use_columns else ''
                html += f'<div class="chapter-narrative {column_class}">'
                for para in paragraphs[1:]:
                    html += f'<p>{para}</p>'
                html += '</div>'
            
            photos = photos[3:]  # Remove used photos
        
        # SPREAD LAYOUT: Text-heavy chapter with embedded image
        elif has_photos and len(photos) == 1 and text_length > 400:
            paragraphs = [p.strip() for p in narrative.split('\n\n') if p.strip()]
            
            # First paragraph
            html += '<div class="chapter-narrative">'
            if paragraphs:
                html += f'<p>{paragraphs[0]}</p>'
            html += '</div>'
            
            # Embedded image (centered, not floated)
            photo_path = self._get_safe_photo_path(upload_folder, photos[0]['filename'])
            if photo_path:
                caption = photos[0].get('title', '') or photos[0].get('description', '')
                if photos[0].get('year'):
                    caption = f"{caption} ({photos[0]['year']})" if caption else f"({photos[0]['year']})"
                
                html += f'''
                <div class="image-embed">
                    <img src="file://{photo_path}" alt="{caption}">
                    {f'<p class="photo-caption">{caption}</p>' if caption else ''}
                </div>
                '''
            
            # Rest of text continues
            html += '<div class="chapter-narrative">'
            for para in paragraphs[1:]:
                html += f'<p>{para}</p>'
            
            html += '</div>'
            photos = photos[1:]
        
        # SIMPLE LAYOUT: Text only or very short content
        else:
            use_columns = text_length > 1200
            column_class = 'two-column' if use_columns else ''
            
            html += f'<div class="chapter-narrative {column_class}">'
            paragraphs = [p.strip() for p in narrative.split('\n\n') if p.strip()]
            
            for para in paragraphs:
                html += f'<p>{para}</p>'
            
            html += '</div>'
            
            # Pull quote at end if we have one
            if pull_quote:
                html += f'<div class="pull-quote">{pull_quote}</div>'
            
            # Any remaining photos
            if photos:
                html += self._create_photo_layout(photos, upload_folder)
        
        html += '</div>'
        return html
    
    def generate_biography_pdf(self, chapters: List[Dict[str, Any]], title: str, subtitle: str, 
                               upload_folder: str, db_connection: Optional[sqlite3.Connection] = None,
                               hero_photo: Optional[str] = None, family_names: Optional[List[str]] = None) -> BytesIO:
        """Generate complete magazine-style biography PDF."""
        
        # Update family names
        if family_names:
            self.family_names = family_names
        
        # Reset used images
        self.used_images = set()
        
        logger.info(f"Generating magazine-style PDF with {len(chapters)} chapters...")
        
        # Get available photos
        available_photos = []
        if db_connection:
            try:
                cursor = db_connection.execute('''
                    SELECT id, filename, title, description, year, people
                    FROM media
                    WHERE file_type = 'image'
                    ORDER BY year DESC NULLS LAST, created_at DESC
                ''')
                
                for row in cursor.fetchall():
                    available_photos.append({
                        'id': row[0],
                        'filename': row[1] or '',
                        'title': row[2] or '',
                        'description': row[3] or '',
                        'year': row[4],
                        'people': row[5] or ''
                    })
                
                logger.info(f"Loaded {len(available_photos)} photos from database")
                
            except Exception as e:
                logger.error(f"Error loading photos: {e}")
        
        # Build HTML
        html_content = '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>The Circle - Family Memory Album</title>
        </head>
        <body>
        '''
        
        # Cover page with automatic hero image selection
        html_content += '<div class="cover">'
        
        # Select a hero image if not provided
        cover_photo_path = None
        if hero_photo:
            cover_photo_path = self._get_safe_photo_path(upload_folder, hero_photo)
        elif available_photos:
            # Auto-select: prefer photos with people, or earliest dated photo
            for photo in available_photos:
                if photo.get('people') or 'family' in photo.get('title', '').lower():
                    cover_photo_path = self._get_safe_photo_path(upload_folder, photo['filename'])
                    if cover_photo_path:
                        self.used_images.add(photo['filename'])  # Mark as used
                        break
            
            # Fallback: use first available photo
            if not cover_photo_path and available_photos:
                cover_photo_path = self._get_safe_photo_path(upload_folder, available_photos[0]['filename'])
                if cover_photo_path:
                    self.used_images.add(available_photos[0]['filename'])
        
        # Cover with background image
        if cover_photo_path:
            html_content += f'''
            <div class="cover-background">
                <img src="file://{cover_photo_path}" alt="Background">
            </div>
            '''
        
        html_content += '<div class="cover-content">'
        html_content += f'<h1>{title}</h1>'
        html_content += f'<h2>{subtitle}</h2>'
        html_content += f'<p class="date">Created {datetime.now().strftime("%B %d, %Y")}</p>'
        html_content += '</div>'
        html_content += '</div>'
        
        # Table of contents with thumbnails
        html_content += '<div class="toc">'
        html_content += '<h2>Contents</h2>'
        
        # Pre-collect photos for each chapter to get thumbnails
        chapter_thumbnails = {}
        for chapter in chapters:
            chapter_photos = self._match_photos_to_chapter(
                chapter['title'],
                chapter['narrative'],
                available_photos,
                max_photos=1  # Just need first photo for thumbnail
            )
            if chapter_photos:
                photo_path = self._get_safe_photo_path(upload_folder, chapter_photos[0]['filename'])
                if photo_path:
                    chapter_thumbnails[chapter['title']] = photo_path
        
        # Generate TOC entries with thumbnails
        for i, chapter in enumerate(chapters, 1):
            html_content += '<div class="toc-entry">'
            html_content += '<div class="toc-entry-content">'
            
            # Add thumbnail if available
            if chapter['title'] in chapter_thumbnails:
                html_content += f'<img src="file://{chapter_thumbnails[chapter["title"]]}" class="toc-thumbnail" alt="">'
            
            # Chapter title
            html_content += '<div class="toc-text">'
            html_content += f'<div class="toc-chapter-title">{chapter["title"]}</div>'
            html_content += '</div>'
            
            html_content += '</div>'
            html_content += '</div>'
        
        html_content += '</div>'
        
        # Chapters
        for chapter in chapters:
            # Match photos to chapter
            chapter_photos = self._match_photos_to_chapter(
                chapter['title'],
                chapter['narrative'],
                available_photos,
                max_photos=3
            )
            
            if chapter_photos:
                logger.info(f"Matched {len(chapter_photos)} photos to '{chapter['title'][:40]}...'")
            
            html_content += self._create_chapter_html(chapter, chapter_photos, upload_folder)
        
        html_content += '''
        </body>
        </html>
        '''
        
        # Generate PDF
        logger.info("Converting HTML to PDF...")
        font_config = FontConfiguration()
        html_doc = HTML(string=html_content, base_url=upload_folder)
        css_doc = CSS(string=self._create_css(), font_config=font_config)
        
        pdf_bytes = html_doc.write_pdf(stylesheets=[css_doc], font_config=font_config)
        
        buffer = BytesIO(pdf_bytes)
        buffer.seek(0)
        
        logger.info(f"✅ Magazine PDF generated successfully")
        logger.info(f"📸 Used {len(self.used_images)} unique images (no duplicates)")
        
        return buffer


# Legacy function for backward compatibility
def generate_biography_pdf(chapters: List[Dict[str, Any]], title: str, subtitle: str, 
                          upload_folder: str, hero_photo: Optional[str] = None, 
                          db_connection=None) -> BytesIO:
    """Legacy function for backward compatibility."""
    
    # Use provided connection or create new one
    should_close = False
    if db_connection is None:
        try:
            db_path = os.getenv('DATABASE_PATH', 'circle_memories.db')
            if os.path.exists(db_path):
                db_connection = sqlite3.connect(db_path)
                should_close = True
        except Exception as e:
            logger.warning(f"Could not connect to database: {e}")
    
    # Extract family names from chapters
    family_names = []
    for chapter in chapters:
        text = chapter['title'] + ' ' + chapter['narrative']
        name_matches = re.findall(r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b', text)
        family_names.extend(name_matches[:2])
    
    family_names = list(set(family_names))[:5]
    
    # Create generator
    generator = BiographyPDFGenerator()
    
    try:
        return generator.generate_biography_pdf(
            chapters=chapters,
            title=title,
            subtitle=subtitle,
            upload_folder=upload_folder,
            db_connection=db_connection,
            hero_photo=hero_photo,
            family_names=family_names
        )
    finally:
        # Only close if we created the connection
        if should_close and db_connection:
            db_connection.close()


# Example usage
if __name__ == "__main__":
    example_chapters = [
        {
            'title': 'Chapter 1: Early Years (1950-1960)',
            'narrative': '''John was born in a small town in 1950. His early years were marked by simplicity and joy...'''
        },
        {
            'title': 'Chapter 2: College Years (1968-1972)',
            'narrative': '''John attended State University where he met his future wife, Mary...'''
        }
    ]
    
    try:
        pdf_buffer = generate_biography_pdf(
            chapters=example_chapters,
            title="The Life of John",
            subtitle="A Family Memoir",
            upload_folder="./uploads",
            hero_photo=None
        )
        
        with open("test_biography_magazine.pdf", "wb") as f:
            f.write(pdf_buffer.read())
        
        print("✅ Magazine-style PDF generated: test_biography_magazine.pdf")
        
    except Exception as e:
        print(f"❌ Error: {e}")
