import os

import resend

from fastapi import HTTPException


# ============================================
# RESEND API KEY
# ============================================

resend.api_key = os.getenv(
    "RESEND_API_KEY"
)


# ============================================
# FRONTEND URL
# ============================================

FRONTEND_URL = os.getenv(
    "FRONTEND_URL"
)


# ============================================
# SEND EMAIL
# ============================================

def send_email(

    to_email: str,

    subject: str,

    html: str

):

    try:

        response = resend.Emails.send({

            "from":
                "AgentPulse <noreply@agentpulseai.dev>",

            "to":
                to_email,

            "subject":
                subject,

            "html":
                html
        })

        return response

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=f"Email send failed: {str(e)}"
        )


# ============================================
# SEND VERIFICATION EMAIL
# ============================================

def send_verification_email(

    to_email: str,

    token: str

):

    verify_url = (
        f"{FRONTEND_URL}/verify-email?token={token}"
    )

    html = f"""

    <div style="
        font-family:Arial;
        padding:40px;
        background:#f4f7fb;
    ">

      <div style="
          max-width:600px;
          margin:auto;
          background:white;
          border-radius:12px;
          padding:40px;
      ">

        <h1 style="
            color:#111827;
            margin-bottom:10px;
        ">
          AgentPulse
        </h1>

        <p style="
            font-size:20px;
            color:#374151;
            font-weight:bold;
        ">
          Verify your email address
        </p>

        <p style="
            color:#6b7280;
            line-height:1.6;
        ">
          Thanks for signing up for AgentPulse.
          Please verify your email to activate
          your account and access the platform.
        </p>

        <a
          href="{verify_url}"
          style="
            display:inline-block;
            margin-top:20px;
            padding:14px 24px;
            background:#2563eb;
            color:white;
            text-decoration:none;
            border-radius:8px;
            font-weight:bold;
          "
        >
          Verify Email
        </a>

        <p style="
            margin-top:30px;
            color:#9ca3af;
            font-size:14px;
        ">
          If you did not create this account,
          you can safely ignore this email.
        </p>

      </div>

    </div>

    """

    return send_email(

        to_email=to_email,

        subject="Verify Your Email",

        html=html
    )


# ============================================
# SEND RESET PASSWORD EMAIL
# ============================================

def send_reset_password_email(

    to_email: str,

    token: str

):

    reset_url = (
        f"{FRONTEND_URL}/reset-password?token={token}"
    )

    html = f"""

    <div style="
        font-family:Arial;
        padding:40px;
        background:#f4f7fb;
    ">

      <div style="
          max-width:600px;
          margin:auto;
          background:white;
          border-radius:12px;
          padding:40px;
      ">

        <h1 style="
            color:#111827;
            margin-bottom:10px;
        ">
          AgentPulse
        </h1>

        <p style="
            font-size:20px;
            color:#374151;
            font-weight:bold;
        ">
          Reset Your Password
        </p>

        <p style="
            color:#6b7280;
            line-height:1.6;
        ">
          We received a request to reset your
          password. Click the button below
          to continue.
        </p>

        <a
          href="{reset_url}"
          style="
            display:inline-block;
            margin-top:20px;
            padding:14px 24px;
            background:#dc2626;
            color:white;
            text-decoration:none;
            border-radius:8px;
            font-weight:bold;
          "
        >
          Reset Password
        </a>

        <p style="
            margin-top:30px;
            color:#9ca3af;
            font-size:14px;
        ">
          If you did not request a password
          reset, you can safely ignore this email.
        </p>

      </div>

    </div>

    """

    return send_email(

        to_email=to_email,

        subject="Reset Your Password",

        html=html
    )