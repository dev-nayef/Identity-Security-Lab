# Identity Security Lab

> A local security engineering laboratory for studying session-bound request protection, CSRF defense, token lifecycle management, and automated security testing with FastAPI.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API%20Framework-009688)
![Security](https://img.shields.io/badge/Focus-Web%20Security-red)
![Tests](https://img.shields.io/badge/Tests-8%20Passed-brightgreen)
![Status](https://img.shields.io/badge/Status-Active-success)

---

## Overview

**Identity Security Lab** is a local security engineering project that demonstrates how a web application can protect authenticated and state-changing requests.

The project implements a custom **session-bound protection layer** combined with **CSRF validation**, User-Agent binding, token expiration, session persistence, revocation, and automated security tests.

The goal is to study defensive identity and request-protection mechanisms in a controlled environment.

> **Educational / Security Research Project**
>
> This project is intended for education, defensive security research, and authorized testing in environments owned or controlled by the developer. It is not designed to bypass security controls or access third-party systems without authorization.

---

## Security Architecture

The application uses separate controls for general request protection and state-changing request protection.

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
      ┌───────┴────────┐        ┌───────┴────────┐
      │                │        │                │
      ▼                ▼        ▼                ▼
 Token Hash       User-Agent  Session       Header
 Validation        Binding    Binding      Validation
      │                │        │                │
      └────────┬───────┘        └────────┬───────┘
               │                         │
               └────────────┬────────────┘
                            ▼
                     Request Accepted
```

---

## Request Protection Flow

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

State-changing operations add a separate CSRF validation layer.

---

## Protection Token

A high-entropy protection token is generated during session initialization.

The server stores a SHA-256 hash of the protection token and validates incoming values using constant-time comparison.

### Controls

- Cryptographically secure token generation
- SHA-256 token hashing
- Session binding
- User-Agent binding
- Token expiration
- Session revocation
- Tamper detection
- Persistent local session storage
- Constant-time comparison with `secrets.compare_digest`

---

## User-Agent Binding

The protection token is associated with a hash of the User-Agent observed when the session is created.

Changing the User-Agent after session creation causes validation to fail.

IP binding is intentionally optional because strict IP binding can invalidate legitimate sessions when clients change networks or use privacy-preserving network configurations.

---

## CSRF Protection

State-changing requests require a separate CSRF token. The CSRF mechanism is kept conceptually separate from the general protection token.

```text
CSRF Cookie
     +
X-CSRF-Token Header
     +
Session Binding
     │
     ▼
CSRF Validation
```

Requests without a CSRF token or with a modified token are rejected.

---

## Session & Token Lifecycle

```text
              ┌───────────────┐
              │ Session Start │
              └───────┬───────┘
                      │
                      ▼
             Generate Tokens
                      │
                      ▼
              Store Session State
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

## Persistent Storage

The local laboratory uses JSON-backed persistence for session-related state:

```text
data/
├── sessions.json
└── csrf_tokens.json
```

Runtime data is excluded from version control through `.gitignore`.

This storage approach is intentionally simple and local; it is not presented as production-grade persistence.

---

## Automated Security Testing

The project includes a pytest suite covering the main protection controls.

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

Run the tests with:

```bash
pytest -v
```

---

## Project Structure

```text
Identity-Security-Lab/
│
├── app/
│   ├── auth/
│   │   ├── csrf_protection.py
│   │   └── session_security.py
│   ├── __init__.py
│   └── main.py
│
├── tests/
│   └── test_security.py
│
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

The `data/` directory is generated at runtime and intentionally excluded from Git.

---

## Technology Stack

- Python
- FastAPI
- Uvicorn
- pytest
- FastAPI TestClient
- Secure random tokens
- SHA-256 hashing
- Session and CSRF controls

---

## Installation

Clone the repository:

```bash
git clone https://github.com/dev-nayef/Identity-Security-Lab.git
cd Identity-Security-Lab
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

---

## Running the Application

```bash
python -m uvicorn app.main:app --reload
```

The application will be available at `http://127.0.0.1:8000`.

FastAPI documentation is available at `http://127.0.0.1:8000/docs`.

---

## Security Design Principles

### 1. Defense in Depth
Multiple independent controls are used instead of trusting a single credential.

### 2. Token Separation
The general protection token and CSRF token serve different security purposes.

### 3. Server-Side Validation
Security decisions are made server-side rather than trusting client-controlled values.

### 4. Minimal Token Exposure
The protection token is stored server-side as a hash rather than plaintext.

### 5. Session Binding
Security tokens are associated with a server-side session.

### 6. Explicit Revocation
Logout removes server-side session state and invalidates associated protection state.

### 7. Automated Verification
Security assumptions are converted into repeatable automated tests.

---

## Security Testing Scenarios

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

It focuses on authentication state, session management, request protection, CSRF defenses, token lifecycle management, security validation, automated security testing, and defensive web security engineering.

It does not attempt to reproduce or bypass security mechanisms belonging to third-party services.

---

## Future Improvements

- Stronger structured session storage
- Configurable token lifetime
- Automated expiration testing
- More comprehensive negative test cases
- Security event logging
- Improved configuration management
- Production-oriented persistent storage
- Expanded security test coverage
- CI-based automated testing
- HTTPS / production cookie configuration

---

## Author

**Nayef Ashour**

Identity & Authentication Developer focused on Identity, Authentication, CIAM, Web Security, Python, Backend Engineering, and Security Research.

---

## License

This project is intended for educational and authorized security research purposes. Use the techniques demonstrated here only on systems and environments where you have explicit permission to perform testing.
