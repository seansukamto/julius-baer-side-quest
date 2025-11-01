"""
Unit tests for the modernized banking client.

Demonstrates:
- Comprehensive test coverage
- Mock HTTP responses
- Error handling validation
- Input validation testing
"""

import json
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys

# Add parent directory to path for imports
sys.path.insert(0, '.')

from banking_client import (
    BankingClient,
    TransferRequest,
    TransferResponse,
    BankingAPIError,
    AuthenticationError,
    TransferError
)


class TestTransferRequest(unittest.TestCase):
    """Test TransferRequest data class and validation."""

    def test_valid_request(self):
        """Test creation of valid transfer request."""
        request = TransferRequest(
            from_account="ACC1000",
            to_account="ACC1001",
            amount=100.00
        )
        self.assertEqual(request.from_account, "ACC1000")
        self.assertEqual(request.to_account, "ACC1001")
        self.assertEqual(request.amount, 100.00)

    def test_negative_amount(self):
        """Test that negative amounts are rejected."""
        with self.assertRaises(ValueError):
            TransferRequest(
                from_account="ACC1000",
                to_account="ACC1001",
                amount=-100.00
            )

    def test_zero_amount(self):
        """Test that zero amounts are rejected."""
        with self.assertRaises(ValueError):
            TransferRequest(
                from_account="ACC1000",
                to_account="ACC1001",
                amount=0
            )

    def test_same_account(self):
        """Test that same source and destination accounts are rejected."""
        with self.assertRaises(ValueError):
            TransferRequest(
                from_account="ACC1000",
                to_account="ACC1000",
                amount=100.00
            )

    def test_to_dict(self):
        """Test conversion to dictionary."""
        request = TransferRequest(
            from_account="ACC1000",
            to_account="ACC1001",
            amount=100.50
        )
        result = request.to_dict()
        expected = {
            "fromAccount": "ACC1000",
            "toAccount": "ACC1001",
            "amount": 100.50
        }
        self.assertEqual(result, expected)


class TestTransferResponse(unittest.TestCase):
    """Test TransferResponse data class."""

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "transactionId": "test-123",
            "status": "SUCCESS",
            "message": "Transfer completed",
            "fromAccount": "ACC1000",
            "toAccount": "ACC1001",
            "amount": 100.00
        }
        response = TransferResponse.from_dict(data)
        self.assertEqual(response.transaction_id, "test-123")
        self.assertEqual(response.status, "SUCCESS")
        self.assertEqual(response.amount, 100.00)


class TestBankingClient(unittest.TestCase):
    """Test BankingClient methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = BankingClient(base_url="http://localhost:8123")
        self.mock_response = Mock()

    @patch('banking_client.requests.Session')
    def test_authenticate_success(self, mock_session):
        """Test successful authentication."""
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"token": "test-token-123"}
        mock_response.raise_for_status = Mock()
        mock_session_instance.request.return_value = mock_response
        
        client = BankingClient(base_url="http://localhost:8123")
        client.session = mock_session_instance
        
        token = client.authenticate(username="bob", password="secret", claim="transfer")
        self.assertEqual(token, "test-token-123")
        self.assertEqual(client._token, "test-token-123")

    @patch('banking_client.requests.Session')
    def test_transfer_success(self, mock_session):
        """Test successful transfer."""
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "transactionId": "tx-123",
            "status": "SUCCESS",
            "message": "Transfer completed",
            "fromAccount": "ACC1000",
            "toAccount": "ACC1001",
            "amount": 100.00
        }
        mock_response.raise_for_status = Mock()
        mock_session_instance.request.return_value = mock_response
        
        client = BankingClient(base_url="http://localhost:8123")
        client.session = mock_session_instance
        
        result = client.transfer(
            from_account="ACC1000",
            to_account="ACC1001",
            amount=100.00
        )
        
        self.assertEqual(result.status, "SUCCESS")
        self.assertEqual(result.transaction_id, "tx-123")
        self.assertEqual(result.amount, 100.00)

    @patch('banking_client.requests.Session')
    def test_transfer_failure(self, mock_session):
        """Test transfer failure handling."""
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        # Mock response with failure
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "FAILED",
            "message": "Insufficient funds"
        }
        mock_response.raise_for_status = Mock()
        mock_session_instance.request.return_value = mock_response
        
        client = BankingClient(base_url="http://localhost:8123")
        client.session = mock_session_instance
        
        with self.assertRaises(TransferError):
            client.transfer(
                from_account="ACC1000",
                to_account="ACC1001",
                amount=100.00
            )

    @patch('banking_client.requests.Session')
    def test_validate_account(self, mock_session):
        """Test account validation."""
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"valid": True, "accountId": "ACC1000"}
        mock_response.raise_for_status = Mock()
        mock_session_instance.request.return_value = mock_response
        
        client = BankingClient(base_url="http://localhost:8123")
        client.session = mock_session_instance
        
        result = client.validate_account("ACC1000")
        self.assertTrue(result["valid"])

    def test_transfer_invalid_input(self):
        """Test transfer with invalid input."""
        client = BankingClient()
        
        with self.assertRaises(ValueError):
            client.transfer("", "ACC1001", 100.00)
        
        with self.assertRaises(ValueError):
            client.transfer("ACC1000", "ACC1001", -100.00)

    @patch('banking_client.requests.Session')
    def test_connection_error(self, mock_session):
        """Test handling of connection errors."""
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        # Mock connection error
        mock_session_instance.request.side_effect = \
            Exception("Connection refused")
        
        client = BankingClient(base_url="http://localhost:8123")
        client.session = mock_session_instance
        
        with self.assertRaises(BankingAPIError):
            client.transfer("ACC1000", "ACC1001", 100.00)


if __name__ == "__main__":
    unittest.main()
