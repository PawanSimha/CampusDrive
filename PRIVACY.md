# Privacy Policy — CampusDrive

**Last updated:** May 31, 2026

## 1. Data Controller

CampusDrive (operated by Pawan Simha R)  
Sapthagiri NPS University, Bengaluru, Karnataka, India  
Email: support@campusdrive.edu

## 2. Data We Collect

| Category | Data | Purpose |
|---|---|---|
| Account | Name, email, role (Student/Teacher), password hash | Authentication, RBAC |
| Profile | Branch, semester, bio, avatar | User personalization |
| Content | Uploaded files, reviews, ratings, group messages | Core platform functionality |
| Contact | Name, email, message body | Support inquiries |
| Analytics | Page views, referrer, device type (via Vercel Analytics) | Performance monitoring |

## 3. Legal Basis (GDPR Art. 6)

- **Consent** — Analytics cookies, optional profile fields
- **Contractual necessity** — Account creation, resource sharing
- **Legitimate interest** — Security, fraud prevention, platform improvement

## 4. How We Use Data

- Authenticate users and enforce role-based access
- Enable resource upload, sharing, and review
- Deliver AI assistance via Google Gemini API (no data stored by Gemini)
- Aggregate anonymous usage statistics
- Respond to contact form submissions

## 5. Data Retention

- **Account data:** Retained until account deletion request
- **Uploaded resources:** Retained until user or admin deletion
- **Contact messages:** Retained for 12 months
- **Analytics:** Aggregated, retained for 24 months (Vercel)

## 6. Data Sharing

We do **not** sell personal data. Limited sharing occurs with:

| Third Party | Purpose | Data shared |
|---|---|---|
| MongoDB Atlas | Database hosting | Encrypted user and resource data |
| Vercel Inc. | Hosting, CDN, Web Analytics | IP address, request metadata |
| Google Cloud (Gemini API) | AI assistant (Aradhaya) | User query text (not stored) |

## 7. Your Rights

- **Access:** Request a copy of your data via support@campusdrive.edu
- **Rectification:** Edit profile data in your Dashboard
- **Deletion:** Request account deletion (processed within 30 days)
- **Objection:** Opt out of analytics via the cookie banner
- **Portability:** Export your resources and reviews on request

## 8. Cookies

| Cookie | Type | Duration | Purpose |
|---|---|---|---|
| `session` | Essential | Session | Authentication, CSRF protection |
| `campusdrive_cookie_consent` | Essential | 365 days | Store consent preference |
| `_vercel_analytics` | Analytics | 24 hours | Vercel Web Analytics |

## 9. Security

- Passwords hashed via bcrypt (PBKDF2)
- All traffic over HTTPS (TLS 1.3)
- CSRF protection on all POST endpoints
- HTTP-only, secure, SameSite cookies
- MongoDB Atlas encryption at rest and in transit

## 10. Contact

For privacy inquiries, contact:  
**Email:** support@campusdrive.edu  
**Response time:** Within 72 hours

## 11. Changes to This Policy

Material changes will be announced via the platform dashboard and email notification 14 days in advance.
