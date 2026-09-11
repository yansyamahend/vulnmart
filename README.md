# VulnMart

**VulnMart** is an intentionally vulnerable e-commerce web application designed for learning and practicing **web application security**.

The application simulates an online marketplace with features such as user accounts, products, shopping carts, orders, wallets, transactions, password reset, and administrative functionality.

VulnMart is intentionally built with security weaknesses that can be discovered and analyzed through hands-on security testing.

> **Educational Project:** VulnMart is intended for security research, penetration testing practice, and web security education.

---

## Overview

VulnMart is a vulnerable web application created as a practical environment for understanding how security vulnerabilities can occur in real-world web applications.

Instead of testing isolated vulnerability examples, VulnMart provides a more realistic application workflow where multiple features interact with each other.

This makes it possible to practice the complete vulnerability research process:

```text
Reconnaissance
      ↓
Attack Surface Mapping
      ↓
Vulnerability Identification
      ↓
Exploitation
      ↓
Impact Analysis
      ↓
Root Cause Analysis
      ↓
Remediation
```

The goal is not only to find a vulnerability, but also to understand **why it exists, how it can be exploited, what impact it has, and how it should be fixed**.

---

## Features

VulnMart currently provides several application features commonly found in modern e-commerce applications.

### User Features

* User registration
* User authentication
* User profiles
* Password management
* Password reset
* Product browsing
* Shopping cart
* Checkout
* Order management
* Wallet
* Transaction history
* Currency exchange functionality

### Administrative Features

* User management
* Administrative dashboard
* Account management
* Application management functionality

### Security Training Features

* Multiple application attack surfaces
* Authentication and authorization workflows
* API endpoints
* Financial workflows
* Account management workflows
* Administrative functionality
* Business logic interactions

---

## Security Scope

The application can be used to explore multiple areas of web application security.

### Authentication

Areas related to:

* Login
* Registration
* Session handling
* Password management
* Password reset
* Authentication flows

### Authorization

Areas related to:

* Access control
* Privilege separation
* User-to-user access
* Administrative access
* Resource authorization

### Session Management

Areas related to:

* Session handling
* Authentication state
* Token-based authentication
* Session validation

### Business Logic

Areas related to:

* E-commerce workflows
* Shopping cart operations
* Checkout logic
* Orders
* Wallet operations
* Transactions
* Promotional or financial logic

### User & Account Management

Areas related to:

* User profiles
* Account modification
* Sensitive account operations
* User-related resources

### API Security

The application includes API endpoints that can be investigated for issues involving:

* Input validation
* Authentication
* Authorization
* Object-level access control
* Parameter manipulation
* Business logic

### Administrative Functionality

Administrative functionality provides an additional attack surface for analyzing:

* Privilege boundaries
* Administrative authorization
* User management
* Sensitive operations

> The exact vulnerabilities and exploitation techniques are intentionally not listed in this section so that the application can also be used as a hands-on security testing environment.

---

## Learning Objectives

VulnMart is designed to help security learners develop practical skills in web application testing.

By working with VulnMart, you can practice:

* Understanding web application architecture
* Mapping application attack surfaces
* Analyzing HTTP requests and responses
* Identifying authentication weaknesses
* Testing authorization controls
* Investigating business logic flaws
* Testing API endpoints
* Understanding session and token handling
* Analyzing application behavior
* Building exploitation hypotheses
* Reproducing vulnerabilities
* Assessing security impact
* Identifying root causes
* Developing remediation strategies

The project is intended to encourage a security mindset:

```text
Observe
  ↓
Understand
  ↓
Hypothesize
  ↓
Test
  ↓
Analyze
  ↓
Exploit
  ↓
Explain
  ↓
Remediate
```

---

## Technology Stack

VulnMart is built using a lightweight web application stack.

| Technology     | Purpose                                 |
| -------------- | --------------------------------------- |
| Python         | Backend programming language            |
| FastAPI        | Web application framework               |
| SQLAlchemy     | Database ORM                            |
| Jinja2         | Server-side HTML templating             |
| HTML / CSS     | Frontend                                |
| Docker         | Application containerization            |
| Docker Compose | Local deployment and service management |

---

## Project Structure

```text
vulnmart/
├── app/
│   ├── core/
│   │   ├── dependencies.py
│   │   └── security.py
│   │
│   ├── models/
│   │   ├── cart_item.py
│   │   ├── category.py
│   │   ├── h5_challenge.py
│   │   ├── order.py
│   │   ├── order_item.py
│   │   ├── password_reset.py
│   │   ├── product.py
│   │   ├── user.py
│   │   └── wallet.py
│   │
│   ├── routes/
│   │   ├── accounts.py
│   │   ├── admin.py
│   │   ├── auth.py
│   │   ├── cart.py
│   │   ├── checkout.py
│   │   ├── crew.py
│   │   ├── exchange.py
│   │   ├── h5.py
│   │   ├── orders.py
│   │   ├── pages.py
│   │   ├── password_reset.py
│   │   ├── products.py
│   │   ├── transactions.py
│   │   ├── users.py
│   │   └── wallet.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── crew.py
│   │   ├── password_reset.py
│   │   └── user.py
│   │
│   ├── services/
│   ├── database.py
│   ├── database_seed.py
│   └── main.py
│
├── data/
├── static/
│   └── css/
│       └── style.css
│
├── templates/
│   ├── admin.html
│   ├── admin_user.html
│   ├── base.html
│   ├── cart.html
│   ├── crew_dashboard.html
│   ├── crew_login.html
│   ├── crew_otp.html
│   ├── crew_register.html
│   ├── exchange.html
│   ├── forgot_password.html
│   ├── index.html
│   ├── login.html
│   ├── order.html
│   ├── orders.html
│   ├── product.html
│   ├── profile.html
│   ├── register.html
│   └── reset_password.html
│
├── Dockerfile
├── docker-compose.yml
├── deploy.sh
├── requirements.txt
└── .gitignore
```

---

## Installation

### Prerequisites

Make sure the following tools are installed:

* Git
* Docker
* Docker Compose

Verify your installation:

```bash
git --version
docker --version
docker compose version
```

---

## Running with Docker

Clone the repository:

```bash
git clone https://github.com/yansyamahend/vulnmart.git
```

Move into the project directory:

```bash
cd vulnmart
```

Build and start the application:

```bash
docker compose up --build
```

After the containers are running, access the application through the configured local port.

To stop the application:

```bash
docker compose down
```

To run the application in detached mode:

```bash
docker compose up -d --build
```

To view running containers:

```bash
docker compose ps
```

To view application logs:

```bash
docker compose logs -f
```

---

## Running Without Docker

VulnMart can also be run directly using Python.

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate the virtual environment:

### Linux / WSL

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the application using the appropriate application entry point.

---

## Security Testing

VulnMart can be tested using common web security testing tools.

Examples include:

* Burp Suite
* OWASP ZAP
* Browser Developer Tools
* cURL
* HTTP clients
* Custom scripts

A typical testing workflow can be structured as:

```text
1. Reconnaissance
2. Identify application functionality
3. Map endpoints and parameters
4. Understand authentication
5. Understand authorization
6. Test input handling
7. Test business logic
8. Analyze API behavior
9. Validate vulnerabilities
10. Assess impact
11. Identify root cause
12. Recommend remediation
```

The objective is to understand the application's behavior rather than simply relying on automated scanners.

---

## Reporting Vulnerabilities

When documenting a vulnerability found in VulnMart, a useful report structure is:

```text
## Title

## Severity

## Affected Component

## Description

## Steps to Reproduce

## Proof of Concept

## Impact

## Root Cause

## Remediation
```

For example, a security report should explain not only **what request or payload works**, but also:

* Why the request is accepted
* Which security control is missing
* What an attacker can achieve
* What data or functionality is affected
* How the underlying issue should be remediated

---

## Intended Audience

VulnMart is intended for:

* Cybersecurity beginners
* Web security learners
* Penetration testing students
* CTF players
* Application security enthusiasts
* Security researchers
* Developers learning secure coding

The application can be especially useful for learners who want to move from theoretical vulnerability descriptions toward practical application security testing.

---

## Disclaimer

VulnMart is **intentionally vulnerable** and is created exclusively for educational and security testing purposes.

Do **not** deploy VulnMart in a production environment.

Do **not** expose a vulnerable instance to the public internet unless it has been properly isolated and secured for the intended use.

Only perform security testing against systems and applications that you own or have explicit permission to test.

The author is not responsible for damage, data loss, service disruption, or unauthorized access resulting from misuse of this project.

---

## Contributing

Contributions, improvements, and security research are welcome.

When contributing, please consider:

* Keep the project focused on web application security education.
* Avoid introducing unnecessary dependencies.
* Document significant changes.
* Clearly explain security-relevant behavior.
* Do not expose sensitive information or real credentials.
* Test changes before submitting them.

For vulnerability research, please clearly document the affected functionality and expected security impact.

---

## Roadmap

Potential future improvements include:

* Additional vulnerable application scenarios
* More realistic e-commerce workflows
* Expanded API attack surface
* Additional authentication and authorization scenarios
* Improved documentation
* Structured security challenges
* Official vulnerability writeups
* Difficulty classification for vulnerabilities
* Additional deployment options

---

## Project Status

VulnMart is an educational project under active development.

Features, application behavior, and security scenarios may change over time.

---

## License

This project is intended for educational and security research purposes.

See the repository license for the applicable terms.

---

## Author

Created by **Aryansyah Mahendra**.

GitHub:

https://github.com/yansyamahend

Project:

https://github.com/yansyamahend/vulnmart
