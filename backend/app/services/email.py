"""
Shared transactional email service using SendGrid.
Call these directly from FastAPI handlers via BackgroundTasks.
"""
from app.core.config import settings

# ── Shared HTML wrapper ────────────────────────────────────────────────────────

_CSS = """
body{margin:0;padding:0;background:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif}
.wrap{max-width:580px;margin:32px auto;border-radius:14px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.08)}
.hdr{background:linear-gradient(135deg,#4c1d95 0%,#7c3aed 100%);padding:32px 40px;text-align:center}
.hdr h1{color:#fff;margin:0;font-size:22px;font-weight:700;letter-spacing:-.5px}
.hdr p{color:rgba(255,255,255,.65);margin:6px 0 0;font-size:13px}
.bdy{background:#fff;padding:40px;border:1px solid #e5e7eb;border-top:none}
.bdy h2{color:#111827;font-size:20px;font-weight:700;margin:0 0 12px}
.bdy p{color:#6b7280;font-size:15px;line-height:1.65;margin:0 0 14px}
.hi{color:#111827;font-weight:600}
.btn{display:inline-block;background:#7c3aed;color:#fff!important;text-decoration:none;padding:13px 30px;border-radius:9px;font-size:15px;font-weight:600;margin:6px 0 24px}
.warn{background:#fffbeb;border:1px solid #fde68a;border-radius:9px;padding:14px 16px;margin:18px 0}
.warn p{color:#92400e;margin:0;font-size:13px;line-height:1.5}
.divider{border:none;border-top:1px solid #f3f4f6;margin:24px 0}
.ftr{background:#f9fafb;padding:20px 40px;border:1px solid #e5e7eb;border-top:none;text-align:center}
.ftr p{color:#9ca3af;font-size:12px;margin:0;line-height:1.6}
"""


def _wrap(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>{_CSS}</style>
</head>
<body>
<div class="wrap">
  <div class="hdr">
    <h1>OakstrattonIMA</h1>
    <p>AI-Powered Influence Marketing</p>
  </div>
  <div class="bdy">{body}</div>
  <div class="ftr">
    <p>© 2025 OakstrattonIMA &nbsp;·&nbsp; This is an automated message, please do not reply.</p>
    <p>You received this email because you have an account on our platform.</p>
  </div>
</div>
</body>
</html>"""


# ── Core send function ─────────────────────────────────────────────────────────

async def send_email(to: str, subject: str, html_body: str) -> None:
    """Send via SendGrid. Silently logs to console when API key is not set."""
    if not settings.SENDGRID_API_KEY:
        print(f"[EMAIL] To={to} | Subject={subject}")
        return

    try:
        import sendgrid
        from sendgrid.helpers.mail import Mail, Email, To, Content

        sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        msg = Mail(
            from_email=Email(settings.EMAIL_FROM, settings.EMAIL_FROM_NAME),
            to_emails=To(to),
            subject=subject,
            html_content=Content("text/html", html_body),
        )
        sg.client.mail.send.post(request_body=msg.get())
    except Exception as exc:
        # Never let email failure break an auth flow
        print(f"[EMAIL ERROR] To={to}: {exc}")


# ── Transactional templates ────────────────────────────────────────────────────

async def send_welcome_email(to: str, full_name: str) -> None:
    body = f"""
<h2>Welcome to OakstrattonIMA! 🎉</h2>
<p>Hi <span class="hi">{full_name}</span>,</p>
<p>Your account is ready. You can now log in and start managing influencer campaigns,
reviewing AI-matched talent, and automating your agency workflows.</p>
<a href="{settings.FRONTEND_URL}/login" class="btn">Go to Dashboard &rarr;</a>
<hr class="divider">
<p style="font-size:13px;color:#9ca3af">If you didn't create this account, please
<a href="mailto:{settings.EMAIL_FROM}" style="color:#7c3aed">contact us</a> immediately.</p>
"""
    await send_email(to, "Welcome to OakstrattonIMA", _wrap("Welcome", body))


async def send_login_alert(to: str, full_name: str) -> None:
    from datetime import datetime
    when = datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")
    body = f"""
<h2>New Sign-In Detected</h2>
<p>Hi <span class="hi">{full_name}</span>,</p>
<p>A successful sign-in to your OakstrattonIMA account was recorded.</p>
<p><strong>When:</strong> {when}</p>
<div class="warn">
  <p>⚠️ &nbsp;If this wasn't you, <a href="{settings.FRONTEND_URL}/forgot-password"
  style="color:#92400e;font-weight:600">reset your password immediately</a>.</p>
</div>
"""
    await send_email(to, "New Sign-In to Your OakstrattonIMA Account", _wrap("Sign-In Alert", body))


async def send_password_changed_alert(to: str, full_name: str) -> None:
    from datetime import datetime
    when = datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")
    body = f"""
<h2>Your Password Was Changed</h2>
<p>Hi <span class="hi">{full_name}</span>,</p>
<p>Your OakstrattonIMA account password was changed on <strong>{when}</strong>.</p>
<div class="warn">
  <p>⚠️ &nbsp;If you did not make this change,
  <a href="{settings.FRONTEND_URL}/forgot-password"
  style="color:#92400e;font-weight:600">reset your password immediately</a>
  and contact us.</p>
</div>
"""
    await send_email(to, "Your Password Has Been Changed", _wrap("Password Changed", body))


async def send_password_reset_email(to: str, full_name: str, reset_token: str) -> None:
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
    body = f"""
<h2>Reset Your Password</h2>
<p>Hi <span class="hi">{full_name}</span>,</p>
<p>We received a request to reset your OakstrattonIMA password.
Click the button below — this link expires in <strong>1 hour</strong>.</p>
<a href="{reset_url}" class="btn">Reset Password &rarr;</a>
<hr class="divider">
<p style="font-size:13px;color:#9ca3af">If you did not request a password reset you can
safely ignore this email. Your password will not change.</p>
<p style="font-size:11px;word-break:break-all;color:#d1d5db">
Or copy this link: {reset_url}</p>
"""
    await send_email(to, "Reset Your OakstrattonIMA Password", _wrap("Password Reset", body))
