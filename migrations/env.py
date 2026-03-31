# Migration file example for DATABASE_URL validation
# This file is updated to include validation for the DATABASE_URL.

import os
from sqlalchemy import create_engine
from sqlalchemy.exc import ArgumentError


# Retrieve the DATABASE_URL from environment variable and validate it.
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL is None:
    raise ValueError('DATABASE_URL environment variable is not set.')

try:
    engine = create_engine(DATABASE_URL)
except ArgumentError as e:
    raise ValueError('Invalid DATABASE_URL provided') from e
