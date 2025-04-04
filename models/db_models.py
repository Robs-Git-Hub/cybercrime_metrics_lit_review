import uuid
import re
from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    Date,
    Float,
    ForeignKey,
    Table,
    Enum as SQLEnum,
    create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from config import NotebookConfig

Base = declarative_base()

def generate_short_uuid():
    """Generate a short UUID string (first 8 characters of a UUID4)."""
    return uuid.uuid4().hex[:8]

def generate_cite_key(authors, year, title, postfix=None):
    """
    Generate a citation key in the style:
    
      surname_year_abbr[-postfix]
      
    where:
      - surname: for multiple authors, if a comma is present,
                 use the last word of the first segment (before the comma);
                 otherwise, use the last word of the entire authors string.
      - year: the publication year, or "nd" if missing.
      - abbr: formed by taking the first letter of the first four words of the title.
      
    NOTE: This extraction logic should be reviewed for edge cases.
    """
    # Helper function to remove accented characters.
    def remove_accents(input_str):
        import unicodedata
        return ''.join(c for c in unicodedata.normalize('NFKD', input_str) if not unicodedata.combining(c))
    
    if authors and authors.strip():
        authors_no_accents = remove_accents(authors)
        surname = (authors_no_accents.split(',')[0].split()[-1] if ',' in authors_no_accents
                   else authors_no_accents.split()[-1]).lower()
    else:
        surname = "na"
    year_part = str(year) if year else "nd"
    if title:
        title_no_accents = remove_accents(title)
        title_words = re.findall(r'\w+', title_no_accents.lower())
    else:
        title_words = []
    abbr = "".join(word[0] for word in title_words[:4]) if title_words else "notitle"
    base_key = f"{surname}_{year_part}_{abbr}"
    return f"{base_key}-{postfix}" if postfix else base_key

# Join table for the Many-to-Many relationship between DeepResearchReport and Source.
deep_research_report_source = Table(
    'deep_research_report_source',
    Base.metadata,
    Column('deep_research_report_id', Integer, ForeignKey('deep_research_report.id'), primary_key=True),
    Column('source_id', String, ForeignKey('source.id'), primary_key=True)
)

class Source(Base):
    __tablename__ = 'source'
    
    # Use a short UUID as primary key.
    id = Column(String, primary_key=True, default=generate_short_uuid)
    # A secondary reference string (e.g. "smith2020") now called cite_key.
    cite_key = Column(String, nullable=False, unique=True)
    
    # Additional bibliographic fields.
    title = Column(String, nullable=False)
    year = Column(Integer, nullable=True)
    date = Column(Date, nullable=True)
    authors = Column(Text, nullable=True)
    abstract = Column(Text, nullable=True)
    journal = Column(String, nullable=True)
    volume = Column(Integer, nullable=True)
    booktitle = Column(String, nullable=True)
    pages = Column(String, nullable=True)
    citation_count = Column(Integer, nullable=True)
    citation_velocity = Column(Float, nullable=True)
    doi = Column(String, nullable=True)
    link = Column(String, nullable=True)
    external_ids = Column(Text, nullable=True)
    is_open_access = Column(Boolean, default=False)
    open_access_link = Column(String, nullable=True)
    semantic_scholar_id = Column(String, nullable=True)
    
    # Many-to-Many: a source can be linked to multiple deep research reports.
    deep_research_reports = relationship(
        'DeepResearchReport',
        secondary=deep_research_report_source,
        back_populates='sources'
    )
    
    # One-to-Many: a source can have multiple relevance ratings.
    relevance_ratings = relationship('UnmindSourceRelevanceRating', back_populates='source', cascade='all, delete-orphan')

class DeepResearchReport(Base):
    __tablename__ = 'deep_research_report'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  # e.g. Title or description of the report
    
    # Many-to-Many with Source.
    sources = relationship(
        'Source',
        secondary=deep_research_report_source,
        back_populates='deep_research_reports'
    )
    
    # One-to-Many: a DRR can have several associated research notes.
    research_notes = relationship('ResearchNote', back_populates='deep_research_report', cascade='all, delete-orphan')

# Enum to indicate the route of a research note.
class NoteRouteType(Enum):
    DEEP_RESEARCH_REPORT = "deep_research_report"
    NOTE_TAKING = "note_taking"
    AI_NOTES = "ai_notes"

class ResearchNote(Base):
    __tablename__ = 'research_note'
    
    id = Column(Integer, primary_key=True)
    note_text = Column(Text, nullable=False)
    # Indicates the origin of the note.
    route = Column(SQLEnum(NoteRouteType), nullable=False)
    # Optionally, link to a DeepResearchReport if applicable.
    deep_research_report_id = Column(Integer, ForeignKey('deep_research_report.id'), nullable=True)
    # New: Link to a Source via its cite_key.
    cite_key = Column(String, ForeignKey('source.cite_key'), nullable=False)
    
    deep_research_report = relationship('DeepResearchReport', back_populates='research_notes')
    # Relationship to Source.
    source = relationship('Source')

class UnmindSourceRelevanceRating(Base):
    __tablename__ = 'unmind_source_relevance_rating'
    
    id = Column(Integer, primary_key=True)
    # Use cite_key to connect to the Source table.
    cite_key = Column(String, ForeignKey('source.cite_key'), nullable=False)
    rating = Column(Float, nullable=False)
    topic = Column(String, nullable=True)
    
    # Relationship to the Source.
    source = relationship('Source', back_populates='relevance_ratings')

class FollowUpQuestion(Base):
    __tablename__ = 'follow_up_questions'
    
    id = Column(Integer, primary_key=True)
    toc_id = Column(Integer, nullable=True)
    indicator_id = Column(String, nullable=True)
    question_text = Column(Text, nullable=False)

class SourcesNeededForFollowUps(Base):
    __tablename__ = 'sources_needed_for_follow_ups'
    
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('follow_up_questions.id'), nullable=False)
    cite_key = Column(String, nullable=False)

# Create an engine and initialize the SQLite database.
engine = create_engine(f"sqlite:///{NotebookConfig.DB_FILE}")
Base.metadata.create_all(engine)

