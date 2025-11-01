# Modern Banking Client - Python 3.x Implementation

## 📋 Overview

This is a **modernized banking client** that demonstrates the transformation from legacy Python 2.7 code to a production-ready Python 3.x implementation using current best practices.

## 🎯 Modernization Highlights

### Before (Legacy Python 2.7)

```python
import urllib2
import json

def transfer_money(from_acc, to_acc, amount):
    url = "http://localhost:8123/transfer"
    data = '{"fromAccount":"' + from_acc + '","toAccount":"' + to_acc + '","amount":' + str(amount) + '}'
    req = urllib2.Request(url, data)
    req.add_header('Content-Type', 'application/json')
    try:
        response = urllib2.urlopen(req)
        result = response.read()
        print "Transfer result: " + result
        return result
    except urllib2.HTTPError, e:
        print "Error: " + str(e.code)
        return None
```

### After (Modern Python 3.x)

- ✅ **Python 3.x syntax**: Type hints, f-strings, dataclasses, context managers
- ✅ **Modern HTTP client**: `requests` library with connection pooling and retries
- ✅ **JWT authentication**: Secure token-based authentication with automatic management
- ✅ **Error handling**: Custom exceptions, structured error messages, proper logging
- ✅ **Input validation**: Dataclasses with validation, type safety
- ✅ **Configuration**: Environment variable support, flexible configuration
- ✅ **Logging**: Structured logging instead of print statements
- ✅ **Code quality**: Clean architecture, separation of concerns, SOLID principles

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Banking API server running on `http://localhost:8123`

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from banking_client import BankingClient

# Initialize client
client = BankingClient(base_url="http://localhost:8123")

# Basic transfer (no authentication)
result = client.transfer(
    from_account="ACC1000",
    to_account="ACC1001",
    amount=100.00
)

print(f"Transfer successful: {result.transaction_id}")
```

### CLI Usage

```bash
# Basic transfer
python banking_client.py --from-account ACC1000 --to-account ACC1001 --amount 100.00

# With JWT authentication (bonus feature)
python banking_client.py --from-account ACC1000 --to-account ACC1001 --amount 100.00 --use-auth

# Validate account
python banking_client.py --validate ACC1000

# List all accounts
python banking_client.py --list-accounts
```

## 📚 Features Implemented

### ✅ Core Features

- [x] Transfer funds between accounts
- [x] Input validation and sanitization
- [x] Comprehensive error handling
- [x] Structured logging
- [x] Modern HTTP client with retry logic

### ✅ Bonus Features

- [x] **JWT Authentication**: Secure token-based authentication
- [x] **Account Validation**: Validate account existence
- [x] **Account Balance**: Get account balance
- [x] **List Accounts**: List all available accounts
- [x] **CLI Interface**: Modern command-line interface
- [x] **Unit Tests**: Comprehensive test coverage

## 🏗️ Architecture

### Design Patterns Applied

- **Data Classes**: Type-safe data structures for requests/responses
- **Dependency Injection**: Configuration via constructor parameters
- **Strategy Pattern**: Retry strategies for HTTP requests
- **Exception Hierarchy**: Custom exceptions for different error types

### Code Structure

```
banking_client.py
├── Data Classes
│   ├── TransferRequest (with validation)
│   └── TransferResponse
├── Exception Classes
│   ├── BankingAPIError (base)
│   ├── AuthenticationError
│   └── TransferError
└── BankingClient Class
    ├── Authentication methods
    ├── Transfer operations
    ├── Account operations
    └── HTTP request handling
```

## 🔧 Configuration

### Environment Variables

```bash
export BANKING_API_URL="http://localhost:8123"
```

### Programmatic Configuration

```python
client = BankingClient(
    base_url="http://localhost:8123",
    timeout=30,
    max_retries=3
)
```

## 🧪 Testing

Run the test suite:

```bash
python -m pytest test_banking_client.py -v
```

Or using unittest:

```bash
python test_banking_client.py
```

## 📊 API Endpoints Used

| Method | Endpoint                   | Purpose             | Auth Required    |
| ------ | -------------------------- | ------------------- | ---------------- |
| `POST` | `/authToken?claim={claim}` | Get JWT token       | No               |
| `POST` | `/transfer`                | Transfer funds      | Optional (bonus) |
| `GET`  | `/accounts/validate/{id}`  | Validate account    | No               |
| `GET`  | `/accounts/balance/{id}`   | Get balance         | No               |
| `GET`  | `/accounts`                | List accounts       | No               |
| `GET`  | `/transactions/history`    | Transaction history | Yes              |

## 🎨 Key Modernizations

### 1. Language Modernization

- **Python 2.7 → Python 3.x**: Complete syntax upgrade
- **Type hints**: Improved code clarity and IDE support
- **Dataclasses**: Structured data with built-in validation
- **F-strings**: Modern string formatting

### 2. HTTP Client Modernization

- **urllib2 → requests**: Modern, user-friendly HTTP library
- **Connection pooling**: Improved performance
- **Retry logic**: Automatic retry on transient failures
- **Structured JSON**: No manual string concatenation

### 3. Error Handling & Logging

- **Print statements → Logging**: Structured, configurable logging
- **None returns → Exceptions**: Proper error propagation
- **Custom exceptions**: Clear error hierarchy
- **Error messages**: Meaningful, actionable error messages

### 4. Security & Authentication

- **JWT tokens**: Secure token-based authentication
- **Token management**: Automatic token handling
- **Input validation**: Prevents injection attacks
- **Secure configuration**: Environment variable support

### 5. Code Architecture

- **Separation of concerns**: Clear module boundaries
- **SOLID principles**: Maintainable, extensible code
- **Type safety**: Reduced runtime errors
- **Documentation**: Comprehensive docstrings

## 📝 Example Usage

### Basic Transfer

```python
from banking_client import BankingClient

client = BankingClient()
result = client.transfer("ACC1000", "ACC1001", 100.00)
print(f"Transaction ID: {result.transaction_id}")
```

### Authenticated Transfer

```python
client = BankingClient()
client.authenticate(username="bob", password="secret", claim="transfer")
result = client.transfer("ACC1000", "ACC1001", 100.00, use_auth=True)
```

### Account Operations

```python
# Validate account
validation = client.validate_account("ACC1000")

# Get balance
balance = client.get_account_balance("ACC1000")

# List all accounts
accounts = client.list_accounts()
```

### Error Handling

```python
from banking_client import TransferError, AuthenticationError

try:
    result = client.transfer("ACC1000", "ACC1001", 100.00)
except TransferError as e:
    print(f"Transfer failed: {e}")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
```

## 🔍 Code Quality

- **Type hints**: Full type coverage
- **Documentation**: Comprehensive docstrings
- **Testing**: Unit tests with mocking
- **Linting**: Follows PEP 8 standards
- **Error handling**: Comprehensive exception handling

## 🎯 Bonus Features Implemented

1. **JWT Authentication** 🏆

   - Token-based authentication
   - Automatic token management
   - Support for different claim scopes

2. **Advanced Account Operations** 🏆

   - Account validation
   - Balance retrieval
   - Account listing

3. **Modern CLI Interface** 🏆

   - Argument parsing
   - Multiple operation modes
   - User-friendly output

4. **Comprehensive Testing** 🏆

   - Unit tests
   - Mock HTTP responses
   - Error scenario coverage

5. **Configuration Management** 🏆
   - Environment variables
   - Flexible configuration
   - Default values

## 📦 Dependencies

- `requests >= 2.31.0`: Modern HTTP client library
- `urllib3 >= 2.0.0`: HTTP library (dependency of requests)

## 🚀 Running the Solution

1. **Start the banking server**:

   ```bash
   cd server
   java -jar core-banking-api.jar
   ```

2. **Run the client**:

   ```bash
   python banking_client.py --from-account ACC1000 --to-account ACC1001 --amount 100.00
   ```

3. **Run tests**:
   ```bash
   python test_banking_client.py
   ```

## 📈 Improvements Summary

| Aspect            | Legacy Code          | Modernized Code                 |
| ----------------- | -------------------- | ------------------------------- |
| Python Version    | 2.7                  | 3.x                             |
| HTTP Library      | urllib2              | requests                        |
| Error Handling    | print + return None  | Custom exceptions               |
| Logging           | print statements     | logging module                  |
| JSON Handling     | String concatenation | json.dumps()                    |
| Type Safety       | None                 | Type hints + dataclasses        |
| Authentication    | None                 | JWT with token management       |
| Testing           | None                 | Comprehensive unit tests        |
| Configuration     | Hardcoded            | Environment variables           |
| Code Organization | Single function      | OOP with separation of concerns |

## 🎉 Conclusion

This modernized banking client demonstrates:

- **Professional code quality** with modern Python practices
- **Production-ready** error handling and logging
- **Secure authentication** with JWT tokens
- **Comprehensive testing** for reliability
- **Clean architecture** following SOLID principles

The code is maintainable, testable, and ready for production use! 🚀
