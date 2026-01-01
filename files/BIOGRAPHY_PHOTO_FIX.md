# FIX: Biography PDF Missing Photos

## The Problem
The biography generator shows "📸 Used 0 unique images" because it can't access the database to load photos.

## The Solution
Two small changes needed:

---

## FIX 1: Update biography_pdf_generator.py

**Location:** `biography_pdf_generator.py` line 848-849

**FIND:**
```python
def generate_biography_pdf(chapters: List[Dict[str, Any]], title: str, subtitle: str, 
                          upload_folder: str, hero_photo: Optional[str] = None) -> BytesIO:
```

**REPLACE WITH:**
```python
def generate_biography_pdf(chapters: List[Dict[str, Any]], title: str, subtitle: str, 
                          upload_folder: str, hero_photo: Optional[str] = None, 
                          db_connection=None) -> BytesIO:
```

**Then UPDATE the database connection logic (lines 852-859):**

**FIND:**
```python
    # Get database connection
    db_connection = None
    try:
        db_path = os.getenv('DATABASE_PATH', 'circle_memories.db')
        if os.path.exists(db_path):
            db_connection = sqlite3.connect(db_path)
    except Exception as e:
        logger.warning(f"Could not connect to database: {e}")
```

**REPLACE WITH:**
```python
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
```

**Then UPDATE the finally block (lines 883-885):**

**FIND:**
```python
    finally:
        if db_connection:
            db_connection.close()
```

**REPLACE WITH:**
```python
    finally:
        # Only close if we created the connection
        if should_close and db_connection:
            db_connection.close()
```

---

## FIX 2: Update app.py biography route

**Location:** `app.py` around line 1350 (in the biography PDF route)

**FIND:**
```python
        # Import the generator functions
        try:
            from biography_pdf_generator import generate_biography_pdf
        except ImportError as e:
            print(f"Import error: {e}")
            return jsonify({
                'status': 'error',
                'message': 'PDF generation module not available'
            }), 500
        
        # Generate PDF
        pdf_buffer = generate_biography_pdf(
            chapters,
            title,
            subtitle,
            UPLOAD_FOLDER,
            hero_photo=None
        )
```

**REPLACE WITH:**
```python
        # Import the generator functions
        try:
            from biography_pdf_generator import generate_biography_pdf
        except ImportError as e:
            print(f"Import error: {e}")
            return jsonify({
                'status': 'error',
                'message': 'PDF generation module not available'
            }), 500
        
        # Get database connection
        db = get_db()
        
        # Generate PDF WITH database connection
        pdf_buffer = generate_biography_pdf(
            chapters,
            title,
            subtitle,
            UPLOAD_FOLDER,
            hero_photo=None,
            db_connection=db
        )
```

---

## What This Does

**Before:**
- Biography generator tries to find database itself
- Fails because it doesn't know the correct path
- No photos load → "Used 0 images"

**After:**
- app.py gets database connection using `get_db()` (which already works)
- Passes connection to biography generator
- Generator can load all 40 photos with years
- Photos match to chapters → Biography has images! 📸

---

## Testing

1. Make both changes above
2. Restart the app:
   ```bash
   python3 app.py
   ```
3. Generate a biography
4. Terminal should show:
   ```
   📸 Used 5 unique images
   ```
   (or however many match your chapters)

---

## Expected Result

Your biography PDF will now include:
- Photos matched to chapters by year
- Photos matched by people names
- Photos matched by keywords
- Cover photo from your collection

With 40 photos that have years, you should get images throughout the biography! 🎉
