@app.route('/api/export/biography/pdf', methods=['POST'])
def generate_biography_pdf_route():
    """Generate magazine-style PDF from approved biography draft."""
    try:
        data = request.json or {}
        chapters = data.get('chapters', [])
        title = data.get('title', 'The Making of a Life')
        subtitle = data.get('subtitle', 'A Family Story')
        include_photos = data.get('include_photos', True)
        
        if not chapters:
            # Try to get from session
            draft = session.get('biography_draft')
            if draft:
                chapters = draft['chapters']
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'No biography chapters found'
                }), 400
        
        # Validate chapters
        if not isinstance(chapters, list) or len(chapters) == 0:
            return jsonify({
                'status': 'error',
                'message': 'Invalid chapters data'
            }), 400
        
        # Import the generator functions
        try:
            from biography_pdf_generator import generate_biography_pdf
        except ImportError as e:
            print(f"Import error: {e}")
            return jsonify({
                'status': 'error',
                'message': 'PDF generation module not available'
            }), 500
        
        # FIXED: Get database connection
        db = get_db()
        
        # Generate PDF WITH database connection
        pdf_buffer = generate_biography_pdf(
            chapters,
            title,
            subtitle,
            UPLOAD_FOLDER,
            hero_photo=None,
            db_connection=db  # ← ADDED THIS!
        )
        
        filename = f'family_biography_{title.replace(" ", "_").lower()}.pdf'
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        print(f"PDF generation error: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'Failed to generate PDF: {str(e)}'
        }), 500
