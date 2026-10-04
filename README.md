# Identity Security Lab

> A local security engineering laboratory for studying session-bound request protection, token validation, CSRF protection, and authentication security controls using FastAPI.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API%20Framework-009688)
![Security](https://img.shields.io/badge/Focus-Web%20Security-red)
![Tests](https://img.shields.io/badge/Tests-8%20Passed-brightgreen)
![Status](https://img.shields.io/badge/Status-Active-success)

---

## Overview

**Identity Authentication Lab** is a local security engineering project designed to explore how modern web applications can protect authenticated and state-changing requests.

The project implements a custom **session-bound request protection layer** combined with **CSRF protection**, token validation, User-Agent binding, persistence, expiration, revocation, and automated security testing.

The goal is to study the security mechanisms behind protected web requests in a controlled local environment.

> **Educational / Security Research Project**
>
> This project is intended for educational purposes, defensive security research, and authorized testing in environments owned or controlled by the developer. It is not designed to bypass security controls or access third-party systems without authorization.

---

## Security Architecture

The application uses multiple independent security controls instead of relying on a single token.

```text
                         Client
                           │
                           ▼
                    ┌──────────────┐
                    │   FastAPI    │
                    │ Application  │
                    └──────┬───────┘
                           │
                           ▼
                 Session Identification
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
      Protection Token             CSRF Token
              │                         │
              │                         │
      ┌───────┴────────┐        ┌───────┴────────┐
      │                │        │                │
      ▼                ▼        ▼                ▼
   Token Hash      User-Agent  Session       Header
   Validation       Binding    Binding      Validation
      │                │        │                │
      └────────┬───────┘        └────────┬───────┘
               │                         │
               └────────────┬────────────┘
                            ▼
                     Request Accepted
```

---

## Request Protection Flow

The protected request lifecycle is designed around a session-bound protection token.

```text
Session Initialization
        │
        ▼
Protection Token Generation
        │
        ▼
Token Hash Storage
        │
        ▼
Protection Cookie
        │
        ▼
Protected Request
        │
        ├── Session Validation
        ├── Token Validation
        ├── Expiration Check
        └── User-Agent Binding
        │
        ▼
      Allowed
```

For state-changing operations, an additional CSRF validation layer is required:

```text
Protected Action
      │
      ├── Protection Token
      │
      └── CSRF Token
             │
             ├── Session Binding
             └── Header Validation
                    │
                    ▼
                 Allowed
```

---

## Protection Token

The application generates a high-entropy protection token during session initialization.

The server does **not** need to store the raw protection token. Instead, it stores a SHA-256 hash and validates incoming tokens against the stored hash.

### Protection controls

- Cryptographically secure token generation
- SHA-256 token hashing
- Session binding
- User-Agent binding
- Expiration
- Session revocation
- Tamper detection
- Persistent session storage
- Constant-time comparison using `secrets.compare_digest`

A modified token is rejected by the protection layer.

---

## User-Agent Binding

The protection token is associated with a hash of the User-Agent observed when the session is created.

This provides an additional session-bound validation signal.

Example:

```text
Original Session
      │
      ├── Protection Token
      └── User-Agent A
             │
             ▼
          Request
             │
             ▼
           ALLOWED
```

Changing the User-Agent:

```text
Existing Token
      │
      └── User-Agent B
             │
             ▼
           403
```

This behavior is covered by automated tests.

> IP binding is intentionally optional because strict IP binding can cause legitimate session invalidation when clients change networks, use mobile connections, or use privacy-preserving network configurations.

---

## CSRF Protection

State-changing requests use a separate CSRF token.

The project intentionally keeps the CSRF token conceptually separate from the general protection token.

The CSRF mechanism uses:

```text
CSRF Cookie
     +
X-CSRF-Token Header
     +
Session Binding
```

A valid state-changing request therefore requires both layers:

```text
Protection Token
        +
Valid CSRF Token
        │
        ▼
Protected Action
```

Requests without a CSRF token or with a modified CSRF token are rejected.

---

## Persistent Session Storage

The project uses local JSON-backed persistence for the laboratory environment.

```text
data/
├── sessions.json
└── csrf_tokens.json
```

The files are intentionally excluded from Git through `.gitignore`.

This allows the application to maintain session-related state across application restarts during local testing without committing generated session data to the repository.

---

## Token Lifecycle

```text
              ┌───────────────┐
              │ Session Start │
              └───────┬───────┘
                      │
                      ▼
             Generate Token
                      │
                      ▼
              Store Token Hash
                      │
                      ▼
              Validate Requests
                      │
            ┌─────────┴─────────┐
            │                   │
          Valid               Invalid
            │                   │
            ▼                   ▼
         Allow                403
            │
            ▼
       Expiration / Logout
            │
            ▼
          Revoke
```

---

## Automated Security Testing

The project includes automated tests using `pytest`.

Current test coverage validates:

| Security Control | Expected Result |
|---|---:|
| Valid protection token | `200` |
| Missing protection token | `403` |
| Tampered protection token | `403` |
| Wrong User-Agent | `403` |
| Missing CSRF token | `403` |
| Valid CSRF token | `200` |
| Tampered CSRF token | `403` |
| Logout / session revocation | `403` |

Current result:

```text
8 passed
```

Run the complete test suite with:

```bash
pytest -v
```

---

## Project Structure

```text
Identity-Authentication-Lab/
│
├── app/
│   ├── auth/
│   │   ├── csrf_protection.py
│   │   └── token_protection.py
│   │
│   ├── api/
│   ├── static/
│   ├── templates/
│   ├── __init__.py
│   └── main.py
│
├── data/
│   ├── sessions.json
│   └── csrf_tokens.json
│
├── tests/
│   └── test_security.py
│
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

Generated runtime data inside `data/` is excluded from version control.

---

## Technology Stack

### Backend

- Python
- FastAPI
- Uvicorn

### Security

- Session-bound request protection
- CSRF protection
- Token hashing
- User-Agent binding
- Token expiration
- Session revocation
- Secure random token generation
- Constant-time token comparison

### Testing

- pytest
- FastAPI TestClient

---

## Installation

Clone the repository and enter the project directory:

```bash
git clone https://github.com/dev-nayef/Identity-Authentication-Lab.git
cd Identity-Authentication-Lab
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

---

## Running the Application

Start the development server:

```bash
python -m uvicorn app.main:app --reload
```

The application will be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Running Tests

Execute:

```bash
pytest -v
```

Expected output:

```text
8 passed
```

---

## Security Design Principles

The project follows several defensive security principles:

### 1. Defense in Depth

Multiple independent controls are used instead of trusting a single credential.

### 2. Token Separation

The general request-protection token and CSRF token serve different security purposes.

### 3. Server-Side Validation

Security decisions are made server-side rather than trusting client-controlled values.

### 4. Minimal Token Exposure

The protection token is stored as a server-side hash rather than as plaintext.

### 5. Session Binding

Security tokens are associated with a server-side session.

### 6. Explicit Revocation

Logout removes the server-side session state and invalidates associated protection state.

### 7. Automated Verification

Security assumptions are converted into repeatable automated tests.

---

## Security Testing Scenarios

The project has been manually and automatically tested against scenarios including:

```text
✓ Valid session
✓ Missing protection token
✓ Modified protection token
✓ Changed User-Agent
✓ Missing CSRF token
✓ Modified CSRF token
✓ Valid CSRF token
✓ Session revocation after logout
```

The objective is to verify that security controls fail closed when required security state is missing or invalid.

---

## Scope

This project is intentionally designed as a **local security laboratory**.

It focuses on understanding:

- Authentication state
- Session management
- Request protection
- CSRF defenses
- Token lifecycle management
- Security validation
- Automated security testing

It does not attempt to reproduce or bypass security mechanisms belonging to third-party services.

---

## Future Improvements

Planned areas for future development include:

- Stronger structured session storage
- Configurable token lifetime
- Automated expiration testing
- More comprehensive negative test cases
- Security event logging
- Improved configuration management
- Production-oriented persistent storage
- Additional authentication flows
- Expanded security test coverage
- CI-based automated testing

---

## Author

**Nayef Ashour**

Identity & Authentication Developer focused on:

```text
Identity
Authentication
CIAM
OAuth 2.0
OpenID Connect
Web Security
Python Automation
Security Research
```

---

## License

This project is intended for educational and authorized security research purposes.

Use the techniques demonstrated here only on systems and environments where you have explicit permission to perform testing.