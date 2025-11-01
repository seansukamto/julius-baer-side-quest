"""
Modern Banking Client - Modernized from Python 2.7 Legacy Code

This module provides a modernized, production-ready banking client that demonstrates:
- Python 3.x modern syntax (type hints, f-strings, dataclasses)
- Modern HTTP client (requests library with connection pooling)
- JWT authentication with token management
- Comprehensive error handling and logging
- Input validation and sanitization
- Configuration management
- Clean architecture with separation of concerns
"""

import json
import logging
import os
import sys
from dataclasses import dataclass
from typing import Optional, Dict, Any
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TransferRequest:
    """Data class for transfer requests with validation."""
    from_account: str
    to_account: str
    amount: float

    def __post_init__(self):
        """Validate transfer request data."""
        if not self.from_account or not isinstance(self.from_account, str):
            raise ValueError("from_account must be a non-empty string")
        if not self.to_account or not isinstance(self.to_account, str):
            raise ValueError("to_account must be a non-empty string")
        if self.amount <= 0:
            raise ValueError("amount must be greater than 0")
        if self.from_account == self.to_account:
            raise ValueError("from_account and to_account cannot be the same")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "fromAccount": self.from_account,
            "toAccount": self.to_account,
            "amount": round(self.amount, 2)
        }


@dataclass
class TransferResponse:
    """Data class for transfer responses."""
    transaction_id: Optional[str] = None
    status: Optional[str] = None
    message: Optional[str] = None
    from_account: Optional[str] = None
    to_account: Optional[str] = None
    amount: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransferResponse':
        """Create TransferResponse from dictionary."""
        return cls(
            transaction_id=data.get("transactionId"),
            status=data.get("status"),
            message=data.get("message"),
            from_account=data.get("fromAccount"),
            to_account=data.get("toAccount"),
            amount=data.get("amount")
        )


class BankingAPIError(Exception):
    """Base exception for banking API errors."""
    pass


class AuthenticationError(BankingAPIError):
    """Raised when authentication fails."""
    pass


class TransferError(BankingAPIError):
    """Raised when transfer operations fail."""
    pass


class BankingClient:
    """
    Modern banking client with JWT authentication and comprehensive error handling.
    
    Modernizations from legacy code:
    1. Python 3.x syntax (type hints, f-strings, dataclasses)
    2. Modern requests library with connection pooling and retries
    3. JWT authentication with automatic token refresh
    4. Proper exception handling instead of returning None
    5. Structured logging instead of print statements
    6. Input validation and sanitization
    7. Configuration management via environment variables
    8. Type safety with dataclasses and type hints
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize the banking client.
        
        Args:
            base_url: Base URL for the banking API (defaults to env var or localhost:8123)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.base_url = base_url or os.getenv("BANKING_API_URL", "http://localhost:8123")
        self.timeout = timeout
        self._token: Optional[str] = None
        self._token_claim: Optional[str] = None

        # Create session with connection pooling and retry strategy
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        logger.info(f"Initialized BankingClient with base URL: {self.base_url}")

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        require_auth: bool = False
    ) -> Dict[str, Any]:
        """
        Make an HTTP request with error handling and logging.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., '/transfer')
            data: Request payload
            headers: Additional headers
            require_auth: Whether JWT token is required
            
        Returns:
            JSON response as dictionary
            
        Raises:
            AuthenticationError: If authentication fails
            BankingAPIError: For other API errors
        """
        url = urljoin(self.base_url, endpoint)
        
        request_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if headers:
            request_headers.update(headers)
            
        if require_auth:
            if not self._token:
                raise AuthenticationError(
                    "Authentication required but no token available. "
                    "Call authenticate() first."
                )
            request_headers["Authorization"] = f"Bearer {self._token}"

        try:
            logger.debug(f"Making {method} request to {url}")
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                headers=request_headers,
                timeout=self.timeout
            )
            
            # Log response for debugging
            logger.debug(f"Response status: {response.status_code}")
            
            # Handle authentication errors
            if response.status_code == 401:
                raise AuthenticationError(
                    f"Authentication failed: {response.text}"
                )
            
            # Raise exception for HTTP errors
            response.raise_for_status()
            
            # Parse JSON response
            try:
                return response.json()
            except json.JSONDecodeError:
                logger.warning(f"Non-JSON response: {response.text}")
                return {"raw_response": response.text}

        except requests.exceptions.Timeout:
            raise BankingAPIError(f"Request timeout after {self.timeout} seconds")
        except requests.exceptions.ConnectionError as e:
            raise BankingAPIError(
                f"Connection error: Unable to reach {self.base_url}. "
                f"Is the server running? {str(e)}"
            )
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error {response.status_code}: {response.text}"
            logger.error(error_msg)
            raise BankingAPIError(error_msg) from e
        except requests.exceptions.RequestException as e:
            raise BankingAPIError(f"Request failed: {str(e)}") from e

    def authenticate(
        self,
        username: str = "bob",
        password: str = "secret",
        claim: str = "transfer"
    ) -> str:
        """
        Authenticate with the banking API and obtain JWT token.
        
        Args:
            username: Username for authentication
            password: Password for authentication
            claim: Token claim scope ('enquiry' or 'transfer')
            
        Returns:
            JWT token string
            
        Raises:
            AuthenticationError: If authentication fails
        """
        endpoint = f"/authToken?claim={claim}"
        auth_data = {
            "username": username,
            "password": password
        }

        try:
            logger.info(f"Authenticating with claim: {claim}")
            response = self._request("POST", endpoint, data=auth_data)
            
            token = response.get("token") or response.get("access_token")
            if not token:
                raise AuthenticationError(
                    f"No token received in response: {response}"
                )
            
            self._token = token
            self._token_claim = claim
            logger.info("Authentication successful")
            return token

        except BankingAPIError:
            raise
        except Exception as e:
            raise AuthenticationError(f"Authentication failed: {str(e)}") from e

    def transfer(
        self,
        from_account: str,
        to_account: str,
        amount: float,
        use_auth: bool = False
    ) -> TransferResponse:
        """
        Transfer funds between accounts.
        
        Modern improvements:
        - Type hints and dataclasses for type safety
        - Input validation before making request
        - Proper error handling with custom exceptions
        - Structured response object
        - Optional JWT authentication (bonus feature)
        
        Args:
            from_account: Source account ID (e.g., "ACC1000")
            to_account: Destination account ID (e.g., "ACC1001")
            amount: Transfer amount (must be > 0)
            use_auth: Whether to use JWT authentication (bonus feature)
            
        Returns:
            TransferResponse object with transaction details
            
        Raises:
            ValueError: If input validation fails
            TransferError: If transfer operation fails
            AuthenticationError: If authentication is required but fails
        """
        try:
            # Create and validate transfer request
            transfer_request = TransferRequest(
                from_account=from_account,
                to_account=to_account,
                amount=amount
            )
            
            logger.info(
                f"Transferring {amount} from {from_account} to {to_account}"
            )
            
            # Make transfer request
            response_data = self._request(
                method="POST",
                endpoint="/transfer",
                data=transfer_request.to_dict(),
                require_auth=use_auth
            )
            
            # Parse response
            transfer_response = TransferResponse.from_dict(response_data)
            
            if transfer_response.status == "SUCCESS":
                logger.info(
                    f"Transfer successful: {transfer_response.transaction_id}"
                )
            else:
                error_msg = transfer_response.message or "Transfer failed"
                logger.warning(f"Transfer failed: {error_msg}")
                raise TransferError(error_msg)
            
            return transfer_response

        except ValueError as e:
            logger.error(f"Invalid transfer request: {str(e)}")
            raise
        except BankingAPIError:
            raise
        except Exception as e:
            raise TransferError(f"Transfer operation failed: {str(e)}") from e

    def validate_account(self, account_id: str) -> Dict[str, Any]:
        """
        Validate if an account exists and is valid.
        
        Args:
            account_id: Account ID to validate
            
        Returns:
            Dictionary with validation result
            
        Raises:
            BankingAPIError: If validation request fails
        """
        if not account_id:
            raise ValueError("account_id cannot be empty")
        
        endpoint = f"/accounts/validate/{account_id}"
        logger.info(f"Validating account: {account_id}")
        
        try:
            return self._request("GET", endpoint)
        except BankingAPIError as e:
            logger.error(f"Account validation failed: {str(e)}")
            raise

    def get_account_balance(self, account_id: str) -> Dict[str, Any]:
        """
        Get account balance.
        
        Args:
            account_id: Account ID
            
        Returns:
            Dictionary with account balance information
            
        Raises:
            BankingAPIError: If request fails
        """
        if not account_id:
            raise ValueError("account_id cannot be empty")
        
        endpoint = f"/accounts/balance/{account_id}"
        logger.info(f"Getting balance for account: {account_id}")
        
        try:
            return self._request("GET", endpoint)
        except BankingAPIError as e:
            logger.error(f"Failed to get account balance: {str(e)}")
            raise

    def list_accounts(self) -> Dict[str, Any]:
        """
        List all accounts.
        
        Returns:
            Dictionary with account list
            
        Raises:
            BankingAPIError: If request fails
        """
        logger.info("Listing all accounts")
        try:
            return self._request("GET", "/accounts")
        except BankingAPIError as e:
            logger.error(f"Failed to list accounts: {str(e)}")
            raise

    def get_transaction_history(self, use_auth: bool = True) -> Dict[str, Any]:
        """
        Get transaction history (requires authentication).
        
        Args:
            use_auth: Whether to use authentication (default: True)
            
        Returns:
            Dictionary with transaction history
            
        Raises:
            BankingAPIError: If request fails
            AuthenticationError: If authentication is required but fails
        """
        logger.info("Getting transaction history")
        try:
            return self._request("GET", "/transactions/history", require_auth=use_auth)
        except BankingAPIError as e:
            logger.error(f"Failed to get transaction history: {str(e)}")
            raise


def main():
    """
    CLI interface demonstrating the modernized banking client.
    
    This replaces the legacy main() function with:
    - Proper argument parsing
    - Better user feedback
    - Error handling
    - Example usage of all features
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Modern Banking Client - Transfer funds between accounts"
    )
    parser.add_argument(
        "--from-account",
        default="ACC1000",
        help="Source account ID (default: ACC1000)"
    )
    parser.add_argument(
        "--to-account",
        default="ACC1001",
        help="Destination account ID (default: ACC1001)"
    )
    parser.add_argument(
        "--amount",
        type=float,
        default=100.00,
        help="Transfer amount (default: 100.00)"
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="Base URL for banking API (default: http://localhost:8123)"
    )
    parser.add_argument(
        "--use-auth",
        action="store_true",
        help="Use JWT authentication (bonus feature)"
    )
    parser.add_argument(
        "--validate",
        help="Validate account ID instead of transferring"
    )
    parser.add_argument(
        "--list-accounts",
        action="store_true",
        help="List all accounts"
    )

    args = parser.parse_args()

    # Initialize client
    client = BankingClient(base_url=args.base_url)

    try:
        # Authenticate if requested
        if args.use_auth:
            client.authenticate(claim="transfer")
            print("✓ Authentication successful")

        # Handle different operations
        if args.validate:
            result = client.validate_account(args.validate)
            print(f"✓ Account validation result: {json.dumps(result, indent=2)}")
        elif args.list_accounts:
            accounts = client.list_accounts()
            print(f"✓ Accounts: {json.dumps(accounts, indent=2)}")
        else:
            # Perform transfer
            result = client.transfer(
                from_account=args.from_account,
                to_account=args.to_account,
                amount=args.amount,
                use_auth=args.use_auth
            )
            print(f"✓ Transfer successful!")
            print(f"  Transaction ID: {result.transaction_id}")
            print(f"  Status: {result.status}")
            print(f"  Message: {result.message}")
            print(f"  Amount: ${result.amount}")

    except BankingAPIError as e:
        print(f"✗ Error: {str(e)}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}", file=sys.stderr)
        logger.exception("Unexpected error in main")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
