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

# ============================================
# SEND WORKSPACE INVITATION EMAIL 📧
# ============================================

def send_workspace_invite_email(

    to_email: str,

    token: str

):

    # Generates link redirect parameter paths using your dynamic FRONTEND_URL environment variable
    invite_url = (
        f"{FRONTEND_URL}/accept-invite?token={token}"
    )

    html = f"""

    <div style="
        font-family:Arial, sans-serif;
        padding:40px;
        background:#f4f7fb;
    ">

      <div style="
          max-width:600px;
          margin:auto;
          background:white;
          border-radius:12px;
          padding:40px;
          box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
      ">

        <h1 style="
            color:#0ea5e9;
            margin-bottom:10px;
            font-size:28px;
            font-weight:900;
        ">
          AgentPulse
        </h1>

        <p style="
            font-size:20px;
            color:#111827;
            font-weight:bold;
            margin-top:20px;
        ">
          You've been invited to join a team workspace!
        </p>

        <p style="
            color:#4b5563;
            line-height:1.6;
            font-size:15px;
        ">
          An administrator has invited you to collaborate on automated runtimes, view real-time agent telemetry, and access mission control dashboards inside their workspace cluster container.
        </p>

        <div style="margin-top:30px; margin-bottom:30px;">
          <a
            href="{invite_url}"
            style="
              display:inline-block;
              padding:14px 28px;
              background:#0ea5e9;
              color:white;
              text-decoration:none;
              border-radius:8px;
              font-weight:bold;
              font-size:15px;
              box-shadow: 0 4px 6px -1px rgba(14,165,233,0.2);
            "
          >
            Accept Workspace Invitation
          </a>
        </div>

        <hr style="border:0; border-top:1px solid #e5e7eb; margin-top:30px;" />

        <p style="
            margin-top:20px;
            color:#9ca3af;
            font-size:13px;
            line-height:1.5;
        ">
          This invitation link is valid for 7 days. If you were not expecting this request, you can safely ignore or delete this email context safely.
        </p>

      </div>

    </div>

    """

    return send_email(

        to_email=to_email,

        subject="You've Been Invited to an AgentPulse Workspace",

        html=html
    )