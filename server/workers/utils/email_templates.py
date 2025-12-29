def signup_template(base_url: str, name: str, token: str) -> str:
    verification_link = f"{base_url}/verify?token={token}"

    return f"""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <title>Verify your email</title>
  </head>
  <body style="font-family: Arial, Helvetica, sans-serif; background-color: #f6f6f6; padding: 20px;">
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr>
        <td align="center">
          <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; padding: 24px; border-radius: 6px;">
            <tr>
              <td>
                <h2 style="margin-top: 0;">Hi {name},</h2>

                <p>
                  Thanks for signing up. Please confirm your email address by clicking the button below.
                </p>

                <p style="text-align: center; margin: 30px 0;">
                  <a href="{verification_link}"
                     style="background-color: #2563eb; color: #ffffff; padding: 12px 20px;
                            text-decoration: none; border-radius: 4px; font-weight: bold;">
                    Verify Email
                  </a>
                </p>

                <p>
                  This verification link is valid for <strong>30 minutes</strong>.
                  If it expires, you can request a new one from the signup page.
                </p>

                <p>
                  If you did not create an account, you can safely ignore this email.
                </p>

                <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;" />

                <p style="font-size: 12px; color: #6b7280;">
                  This is an automated message. Please do not reply.
                </p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
""".strip()
