from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

__author__ = 'Phil Jenkins (Tessella)'

__all__ = ['Base', 'Session']

# Provide a base model implementation
Base = declarative_base()

# Create a session too
Session = sessionmaker()