# Security Policy — CleanAir Companion

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Security Guardrails & Defense in Depth

CleanAir Companion implements strict multi-layer security controls designed for AI-native consumer health-adjacent applications:

### 1. Prompt Injection Protection
All user prompts and retrieved RAG document chunks pass through our deterministic sanitizer (`backend/app/utils/sanitizer.py`) before reaching any LLM context. Patterns including instruction overrides, jailbreak attempts, and null byte injections are stripped.

### 2. Hallucination Guardrails
The LLM is strictly prohibited from inventing health statistics or emission metrics. All PM2.5 exposure reductions and CO2e avoidance numbers are computed deterministically by unit-tested Python arithmetic modules backed by peer-reviewed IPCC and ARAI emission factors.

### 3. Medical Safety Escalation
Any query containing acute respiratory symptom indicators (e.g. chest pain, severe dyspnea, blue lips) triggers a deterministic medical escalation directing the user to emergency services.

### 4. Privacy by Design
- GPS coordinates are rounded to 2 decimal places (~1 km precision) before database persistence to prevent exact user location tracking.
- Full user data deletion endpoint (`DELETE /api/v1/auth/me`) ensures compliance with GDPR and DPDP Act.

## Reporting a Vulnerability

If you discover a security vulnerability within CleanAir Companion, please submit an issue or contact `security@cleanair.local`. Vulnerabilities will be addressed within 48 hours.
