# Browser Automation

<cite>
**Referenced Files in This Document**   
- [selenium_browser_manager.py](file://tools/selenium_browser_manager.py)
- [supplier_authentication_service.py](file://tools/supplier_authentication_service.py)
- [browser_circuit_breaker.py](file://utils/browser_circuit_breaker.py)
- [system_config.json](file://config/system_config.json)
- [data_store.py](file://utils/data_store.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)

## Introduction
This document provides comprehensive documentation for the browser automation system within the Amazon FBA Agent System, focusing on Chrome management and Playwright integration. The system enables robust, resilient automation for supplier website scraping through advanced browser health monitoring, circuit breaker protection, and automatic restart capabilities. It leverages Chrome DevTools Protocol (CDP) connectivity for deep browser control and integrates tightly with supplier authentication, state management, and diagnostic subsystems. The architecture is designed to handle extended marathon sessions while maintaining stability and performance.

## Project Structure
The browser automation components are organized across multiple directories with clear separation of concerns. Core browser management resides in the `tools/` directory, while circuit breaker logic and utility functions are located in `utils/`. Configuration parameters that govern browser behavior are centralized in `config/system_config.json`.

```mermaid
graph TB
subgraph "Core Automation"
A[selenium_browser_manager.py] --> B[browser_circuit_breaker.py]
A --> C[supplier_authentication_service.py]
end
subgraph "Configuration & State"
D[system_config.json] --> A
E[data_store.py] --> A
end
subgraph "Utilities"
B --> F[logger.py]
C --> F
end
A --> G[OUTPUTS/DIAGNOSTICS]
A --> H[logs/debug/]
```

**Diagram sources**
- [selenium_browser_manager.py](file://tools/selenium_browser_manager.py#L1-L175)
- [browser_circuit_breaker.py](file://utils/browser_circuit_breaker.py#L1-L213)
- [system_config.json](file://config/system_config.json#L1-L300)

**Section sources**
- [selenium_browser_manager.py](file://tools/selenium_browser_manager.py#L1-L175)
- [browser_circuit_breaker.py](file://utils/browser_circuit_breaker.py#L1-L213)
- [system_config.json](file://config/system_config.json#L1-L300)

## Core Components
The browser automation system consists of several key components: the Selenium Browser Manager for Chrome instance control, the Browser Circuit Breaker for failure resilience, the Supplier Authentication Service for login management, and integration with the system configuration and data persistence layers. These components work together to provide a stable, self-healing automation framework capable of handling complex supplier websites over extended periods.

**Section sources**
- [selenium_browser_manager.py](file://tools/selenium_browser_manager.py#L1-L175)
- [browser_circuit_breaker.py](file://utils/browser_circuit_breaker.py#L1-L213)
- [supplier_authentication_service.py](file://tools/supplier_authentication_service.py#L1-L113)

## Architecture Overview
The browser automation architecture follows a layered design with clear separation between browser control, error resilience, authentication, and configuration management. The system uses a singleton pattern for browser instance management, ensuring resource efficiency while providing circuit breaker protection for all operations. Chrome CDP connectivity enables advanced debugging and monitoring capabilities.

```mermaid
graph TD
A[Browser Automation System] --> B[Selenium Browser Manager]
A --> C[Browser Circuit Breaker]
A --> D[Supplier Authentication]
B --> E[Chrome CDP Connectivity]
B --> F[Headless Mode]
B --> G[Stealth Configuration]
C --> H[Failure Threshold Detection]
C --> I[Automatic Recovery]
C --> J[State Management: CLOSED/OPEN/HALF_OPEN]
D --> K[Credentials Management]
D --> L[Login Retry Logic]
D --> M[Session Persistence]
B --> N[System Config]
C --> N
D --> N
N --> O[system_config.json]
B --> P[Diagnostic Logging]
C --> P
D --> P
style A fill:#f9f,stroke:#333
style B fill:#bbf,stroke:#333
style C fill:#bbf,stroke:#333
style D fill:#bbf,stroke:#333
```

**Diagram sources**
- [selenium_browser_manager.py](file://tools/selenium_browser_manager.py#L1-L175)
- [browser_circuit_breaker.py](file://utils/browser_circuit_breaker.py#L1-L213)
- [supplier_authentication_service.py](file://tools/supplier_authentication_service.py#L1-L113)
- [system_config.json](file://config/system_config.json#L1-L300)

## Detailed Component Analysis

### Browser Manager Analysis
The Selenium Browser Manager provides comprehensive Chrome instance management with support for headless operation, stealth mode, and CDP debugging. It uses undetected-chromedriver to bypass anti-bot detection and implements proper resource cleanup.

```mermaid
classDiagram
class SeleniumBrowserManager {
-driver : WebDriver
-headless : bool
-stealth_mode : bool
-log : Logger
+launch_browser(cdp_port) : bool
+get_page(url, timeout) : bool
+navigate_to(url, timeout) : bool
+click(selector, timeout) : bool
+fill(selector, text, timeout) : bool
+text_content(selector, timeout) : str
+get_attribute(selector, attribute, timeout) : str
+wait_for_selector(selector, timeout) : bool
+close() : void
}
class BrowserManager {
-_instance : SeleniumBrowserManager
+get_instance() : SeleniumBrowserManager
}
BrowserManager --> SeleniumBrowserManager : "singleton"
SeleniumBrowserManager --> Options : "configures"
SeleniumBrowserManager --> Service : "uses"
SeleniumBrowserManager --> uc.Chrome : "alternative driver"
```

**Diagram sources**
- [selenium_browser_manager.py](file://tools/selenium_browser_manager.py#L1-L175)

**Section sources**
- [selenium_browser_manager.py](file://tools/selenium_browser_manager.py#L1-L175)

### Circuit Breaker Analysis
The Browser Circuit Breaker implements the circuit breaker pattern to prevent cascading failures during extended automation sessions. It tracks failure counts and automatically blocks operations when thresholds are exceeded, allowing time for recovery.

```mermaid
stateDiagram-v2
[*] --> CLOSED
CLOSED --> OPEN : "failure_count >= threshold"
OPEN --> HALF_OPEN : "timeout_seconds elapsed"
HALF_OPEN --> CLOSED : "success"
HALF_OPEN --> OPEN : "failure"
state OPEN {
[*] --> OpenState
OpenState : Blocked Operations
OpenState : Waiting for timeout
}
state HALF_OPEN {
[*] --> HalfOpenState
HalfOpenState : Limited Operations
HalfOpenState : Testing Recovery
}
state CLOSED {
[*] --> ClosedState
ClosedState : Normal Operations
ClosedState : Failure Count = 0
}
```

**Diagram sources**
- [browser_circuit_breaker.py](file://utils/browser_circuit_breaker.py#L1-L213)

**Section sources**
- [browser_circuit_breaker.py](file://utils/browser_circuit_breaker.py#L1-L213)

### Authentication Service Analysis
The Supplier Authentication Service manages login processes for supplier websites, handling credentials securely and implementing retry logic with backoff for failed login attempts.

```mermaid
sequenceDiagram
participant System
participant AuthService
participant Browser
participant SupplierSite
System->>AuthService : authenticate(supplier)
AuthService->>AuthService : load_credentials(supplier)
AuthService->>Browser : launch_browser()
Browser-->>AuthService : browser_instance
AuthService->>SupplierSite : navigate_to_login()
SupplierSite-->>AuthService : login_page
AuthService->>SupplierSite : fill_credentials()
SupplierSite->>AuthService : response
alt Success
AuthService-->>System : authentication_success
else Failure
AuthService->>AuthService : increment_failure_count
AuthService->>AuthService : check_circuit_breaker
AuthService-->>System : authentication_failed
end
```

**Diagram sources**
- [supplier_authentication_service.py](file://tools/supplier_authentication_service.py#L1-L113)
- [system_config.json](file://config/system_config.json#L1-L300)

**Section sources**
- [supplier_authentication_service.py](file://tools/supplier_authentication_service.py#L1-L113)

## Dependency Analysis
The browser automation system has well-defined dependencies between components, with configuration driving behavior and circuit breaker protection wrapping critical operations.

```mermaid
graph TD
A[selenium_browser_manager.py] --> B[browser_circuit_breaker.py]
A --> C[system_config.json]
A --> D[undetected_chromedriver]
A --> E[Selenium WebDriver]
B --> C
B --> F[logging]
G[supplier_authentication_service.py] --> A
G --> C
G --> H[credentials.json]
I[data_store.py] --> J[pymongo]
I --> C
style A fill:#f96,stroke:#333
style B fill:#f96,stroke:#333
style C fill:#6f9,stroke:#333
style D fill:#69f,stroke:#333
style E fill:#69f,stroke:#333
style F fill:#69f,stroke:#333
style G fill:#f96,stroke:#333
style H fill:#6f9,stroke:#333
style I fill:#f96,stroke:#333
style J fill:#69f,stroke:#333
```

**Diagram sources**
- [selenium_browser_manager.py](file://tools/selenium_browser_manager.py#L1-L175)
- [browser_circuit_breaker.py](file://utils/browser_circuit_breaker.py#L1-L213)
- [supplier_authentication_service.py](file://tools/supplier_authentication_service.py#L1-L113)
- [system_config.json](file://config/system_config.json#L1-L300)
- [data_store.py](file://utils/data_store.py#L1-L22)

**Section sources**
- [selenium_browser_manager.py](file://tools/selenium_browser_manager.py#L1-L175)
- [browser_circuit_breaker.py](file://utils/browser_circuit_breaker.py#L1-L213)
- [supplier_authentication_service.py](file://tools/supplier_authentication_service.py#L1-L113)
- [system_config.json](file://config/system_config.json#L1-L300)
- [data_store.py](file://utils/data_store.py#L1-L22)

## Performance Considerations
The system includes several performance optimizations for browser automation, including headless mode configuration, memory management, and concurrent instance handling. The configuration file specifies key performance parameters such as timeout values, retry strategies, and resource limits.

**Section sources**
- [system_config.json](file://config/system_config.json#L1-L300)
- [selenium_browser_manager.py](file://tools/selenium_browser_manager.py#L1-L175)

## Troubleshooting Guide
Common browser-related issues include debug port conflicts, memory leaks, and WebSocket connection problems. The system addresses these through proper resource cleanup, circuit breaker protection, and health monitoring. For debug port conflicts, ensure no other Chrome instances are using the configured port (default: 9222). Memory leaks are mitigated through the circuit breaker's automatic restart capability and proper browser instance cleanup.

**Section sources**
- [selenium_browser_manager.py](file://tools/selenium_browser_manager.py#L1-L175)
- [browser_circuit_breaker.py](file://utils/browser_circuit_breaker.py#L1-L213)
- [CHROME_CDP_CONNECTIVITY_TROUBLESHOOTING_REPORT.md](file://CHROME_CDP_CONNECTIVITY_TROUBLESHOOTING_REPORT.md)

## Conclusion
The browser automation system provides a robust foundation for supplier website scraping with comprehensive Chrome management and Playwright integration. Its architecture emphasizes resilience through browser health management, circuit breaker protection, and automatic restart capabilities. The integration of Chrome CDP connectivity enables advanced debugging and monitoring, while the authentication system ensures reliable access to supplier websites. This system is designed to handle the challenges of extended automation sessions while maintaining stability and performance.