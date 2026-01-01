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
