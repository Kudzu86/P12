import pytest
from unittest.mock import patch
from logger import init_sentry, log_exception


def test_sentry_initialization():
   # Simuler l'initialisation de Sentry et vérifier qu'elle est appelée
   with patch('sentry_sdk.init') as mock_init:
       init_sentry()
       assert mock_init.called  # Vérifie que init() a bien été appelé

def test_exception_logging():
   # Simuler la capture d'exception et vérifier qu'elle est bien loggée
   with patch('logger.capture_exception') as mock_capture:
       error = Exception("Test error")  # Crée une erreur de test
       log_exception(error)  # Tente de logger l'erreur
       mock_capture.assert_called_once_with(error)  # Vérifie que l'erreur a été capturée une seule fois