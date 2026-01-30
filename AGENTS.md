# AGENTS.md - Development Guidelines for Gestion Locative Pro

This file contains development guidelines for agents working on this Qt-based property management application.

## Project Overview

Gestion Locative Pro is a property management application for office rentals with the following tech stack:
- **Frontend**: PySide6 (Qt6)
- **Database**: SQLite with SQLAlchemy ORM
- **Testing**: Custom test runner with subprocess
- **Build**: PyInstaller for Windows executable
- **Language**: Python 3.11+

## Build/Development Commands

### Environment Setup
**IMPORTANT**: Always activate the conda environment before running any code:
```bash
conda activate location
```

### Running the Application
```bash
python main.py
```

### Database Management
```bash
# Create empty database
python app/init_db.py

# Create database with sample data
python app/init_db.py --seed

# On Windows (with cleanup)
Remove-Item data\gestion_locative.db -ErrorAction SilentlyContinue
python app\init_db.py --seed
```

### Testing Commands
```bash
# Run all tests
python run_tests.py

# Run individual test files
python tests/test_crud.py          # CRUD operations
python tests/test_backup.py        # Backup functionality
python tests/test_relation.py      # Relationship tests

# Query database for inspection
python tests/query_db.py
```

### Build Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Build executable (Windows)
pyinstaller --onefile --windowed --clean gestion_locative.spec

# Or with conda
conda run -n location pyinstaller --clean gestion_locative.spec
```

## Code Style Guidelines

### File Organization
```
app/
├── models/          # SQLAlchemy entities
├── repositories/    # Data access layer
├── services/        # Business logic
├── ui/
│   ├── views/       # Main UI components
│   ├── dialogs/     # Modal dialogs
│   └── widgets/     # Reusable UI components
├── database/        # Database connection & migrations
└── utils/           # Utilities (config, etc.)
```

### Import Style
```python
# Standard library imports first
import sys
from pathlib import Path
from datetime import date, datetime

# Third-party imports next
from PySide6.QtWidgets import QWidget, QVBoxLayout
from sqlalchemy import Column, Integer, String
import yaml

# Local imports last
from app.models.entities import Immeuble
from app.repositories.base import BaseRepository
```

### Naming Conventions
- **Classes**: PascalCase (e.g., `ImmeubleRepository`, `MainWindow`)
- **Functions/Methods**: snake_case (e.g., `get_by_id`, `setup_ui`)
- **Variables**: snake_case (e.g., `current_widget`, `session_factory`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `TEST_FILES`, `DEFAULT_CONFIG`)
- **Files**: snake_case for modules (e.g., `immeuble_repository.py`)

### Type Hints
All functions should include proper type hints:
```python
from typing import List, Optional, TypeVar, Generic
from sqlalchemy.orm import Session

T = TypeVar('T', bound=Base)

def get_by_id(self, id: int) -> Optional[T]:
    """Get an entity by its ID"""
    return self.session.query(self.model_class).filter(
        self.model_class.id == id
    ).first()
```

### Error Handling
- Use custom exceptions for validation errors
- Always log errors with context
- Graceful degradation in UI components

```python
class ContratValidationError(Exception):
    """Raised when contract validation fails"""
    pass

try:
    result = self.create_contract(**data)
except ContratValidationError as e:
    QMessageBox.warning(self, "Erreur", str(e))
except Exception as e:
    print(f"Unexpected error: {e}")
    QMessageBox.critical(self, "Erreur", "Erreur système")
```

### Database Patterns
- Use repository pattern for data access
- Session management via context managers
- Proper relationship definitions

```python
# Repository pattern
class ImmeubleRepository(BaseRepository[Immeuble]):
    def __init__(self, session: Session):
        super().__init__(session, Immeuble)
    
    def search_by_name(self, name: str) -> List[Immeuble]:
        return self.session.query(Immeuble).filter(
            Immeuble.nom.contains(name)
        ).all()
```

### UI Patterns
- Inherit from `BaseView` for entity views
- Use Qt signals for communication between components
- Auto-refresh data when changes occur
- Consistent styling with CSS-like stylesheets

```python
class ImmeubleView(BaseView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        # ... UI setup
        
    def load_data(self):
        """Refresh data from repository"""
        self.immeubles = self.repository.get_all()
        self.populate_table()
```

### Configuration Management
- Use singleton `Config` class from `app.utils.config`
- Configuration stored in `config.yaml`
- Default values for all config options

```python
from app.utils.config import Config

config = Config()
db_path = config.database_path
debug = config.is_debug
```

### Documentation
- Use docstrings for all classes and public methods
- Type hints in docstrings
- English comments, French UI text where applicable

### Testing Guidelines
- Test files in `tests/` directory with `test_` prefix
- Each test file is standalone and executable
- Use print statements for test output (test runner captures them)
- Clean up temporary files after tests

```python
def print_section(title: str):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)
```

## Key Integration Points

### Main Application Entry
- Entry point: `main.py`
- Main window class: `MainWindow` in `main.py:30`
- Navigation via sidebar with `QStackedWidget`

### Database Connection
- Connection class: `app.database.connection.get_database()`
- Models in: `app.models.entities`
- Repositories inherit from: `app.repositories.base.BaseRepository`

### UI Architecture
- Base view: `app.ui.views.base_view.BaseView`
- Entity views inherit from `BaseView`
- Use signals for data change notifications

### Configuration
- File: `config.yaml` in project root
- Class: `app.utils.config.Config` (singleton)
- Auto-creates default config if missing

## Development Workflow

1. Run tests: `python run_tests.py`
2. Make changes following code style guidelines
3. Test individual components: `python tests/test_<component>.py`
4. Run full test suite to verify integration
5. Update documentation if API changes
6. Build executable if needed: `pyinstaller --clean gestion_locative.spec`

## Special Considerations

- Windows executable build includes hardcoded paths in `.spec` file
- Database migrations via Alembic (see `app.database.migrations`)
- PDF receipts generation uses ReportLab + Jinja2 templates
- Google Drive backup integration requires OAuth 2.0 setup
- Qt signals must be properly connected for auto-refresh functionality