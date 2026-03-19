# Security Architecture & Risk Assessment
*Prepared for: Backend Engineering Intern Assessment*

## 1. Executive Summary
This document outlines the current security posture of the Code Evaluation Service MVP and provides a comprehensive risk assessment of evaluating untrusted code. As an MVP constructed to demonstrate backend engineering fundamentals, the service intentionally uses a streamlined execution model to focus on API design, process management, and input validation. 

However, evaluating arbitrary user code is inherently dangerous. This document details the specific vulnerabilities of the current implementation and outlines a formal architectural evolution path to achieve production-level sandboxing (scaling towards architectures like Judge0).

## 2. Risk Assessment of the Current MVP

### Threat Model
Currently, the service evaluates untrusted submissions by spawning a new process on the host system via `subprocess.run(sys.executable)` and leveraging `exec()` and `eval()`. 

While the MVP successfully implements **Time Limits** (a strict 2.0-second timeout to mitigate CPU-bound infinite loops), it is vulnerable to the following vectors:
- **Host Filesystem Access:** Executing code inherits the application user's permissions. Without `chroot` or isolation, malicious submissions can read sensitive environment variables, secrets, or system files (`/etc/passwd`), or attempt to delete critical app files.
- **Server-Side Request Forgery (SSRF) / Network Abuse:** The execution namespace has full network access. A payload could import `urllib` to hit internal AWS metadata endpoints, probe internal local-network services, or execute external DDOS attacks.
- **Resource Exhaustion (Denial of Service):** Timeouts protect against time exhaustion, but they do not prevent Memory Bombing (allocating huge arrays to crash the host via OOM) or Fork Bombs (`os.fork()`) which exhaust PIDs.

### Conclusion on Python Safety
**Can this MVP safely run *any* heavily obfuscated/malicious Python code?**
**No.** The current execution environment acts as an internal tool. For untrusted, public-facing traffic, process-level isolation is insufficient; system-level isolation is mandatory.

## 3. Extensibility & Future Multi-Language Support (e.g., JavaScript)

### Is JavaScript Supported?
Currently, the pipeline is exclusively tightly-coupled to the Python standard library. A naive attempt to support JavaScript would involve installing Node.js and building a parallel execution runner (e.g., a `runner.js` script using Node's `vm` module or `eval`). 

**The architectural takeaway:** Building custom process runners for every language is unscalable and perpetually insecure. This exact problem necessitates the containerized pivot described below.

## 4. Architectural Evolution: Applying Judge0 Sandbox Logic

To elevate this service to the robust standard required for production-scale code execution platforms (like LeetCode or HackerRank), the architecture must adopt the sandboxing paradigms utilized by engines like **Judge0**. 

### Proposed V2 Architecture

1. **Ephemeral Sandboxes (Docker / Kubernetes):**
   Instead of running a python subprocess, the FastAPI backend will utilize the Docker Engine API. Every incoming code submission will spawn a brand-new, sterile, short-lived container (e.g., `docker run --rm python:3.10-slim`).
   
2. **Cgroups & Strict Resource Enforcement:**
   Using Docker (which is essentially a wrapper around Linux kernel namespaces and Control Groups), we can mathematically secure the execution:
   - **Process Limits:** Restrict the maximum number of processes (preventing Fork bombs).
   - **Memory Constraint:** `--memory="128m"` cleanly prevents OOM attacks.
   - **CPU Constraint:** `--cpus="0.5"` handles runaway computation.
   - **Network Warden:** `--network="none"` isolates the container, preventing all external pings, SSRF, and data exfiltration.
   - **Filesystem Lockdown:** `--read-only` disables any rogue modification to the local disk.

3. **Advanced Micro-Sandboxing (isolate / nsjail):**
   For hyper-scale evaluation, Docker's cold-start time (hundreds of milliseconds) may be too slow. The service can ultimately be refactored to use kernel-level jail tools like `isolate` or `nsjail`—the exact technologies powering Judge0. These establish Linux namespaces with sub-millisecond overhead to run code flawlessly with perfect security.

### Summary
The current service successfully demonstrates the required backend engineering competencies—FastAPI service structuring, validation, asynchronous endpoints, and proper unit testing. 

Transitioning the execution engine to leverage kernel-level sandboxing (via Docker SDK or `isolate`) sets a clear roadmap for safely exposing this RCE engine to the public internet, showcasing a deep understanding of infrastructure and system security.
