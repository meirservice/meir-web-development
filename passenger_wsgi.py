"""Entry point for Namecheap / cPanel "Setup Python App" (Phusion Passenger)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.chdir(HERE)

from app import app as application  # noqa: E402
