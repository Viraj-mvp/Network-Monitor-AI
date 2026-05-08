"""
Wizard pages for the setup wizard
"""

from .welcome import WelcomePage
from .monitoring import MonitoringPage
from .email import EmailPage
from .appearance import AppearancePage
from .complete import CompletePage

__all__ = [
    'WelcomePage',
    'MonitoringPage', 
    'EmailPage',
    'AppearancePage',
    'CompletePage'
]
