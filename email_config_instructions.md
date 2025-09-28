# Email & SMS Configuration for Password Reset

## 📧 Email Setup (Gmail SMTP)

To enable actual email sending for password resets, follow these steps:

### Step 1: Create Email Account
1. Create or use existing Gmail account: `noreply.stenographix@gmail.com`
2. Or use any other Gmail account you prefer

### Step 2: Generate App Password
1. Go to your Gmail account settings
2. Enable 2-Factor Authentication if not already enabled
3. Go to "Security" → "App passwords"
4. Generate a new app password for "Mail"
5. Copy the 16-character password

### Step 3: Update Configuration
In `app.py`, update these lines (around line 142):

```python
sender_email = "your_gmail@gmail.com"  # Replace with your Gmail
sender_password = "your_16_char_app_password"  # Replace with app password
```

### Step 4: Test Email
1. Update the credentials in app.py
2. Restart the application
3. Try the forgot password feature
4. Check the recipient's inbox (and spam folder)

## 📱 SMS Setup (Fast2SMS - Recommended for India)

### Step 1: Register at Fast2SMS
1. Go to https://www.fast2sms.com/
2. Create account and verify mobile number
3. Get free credits or purchase credits

### Step 2: Get API Key
1. Go to API section in Fast2SMS dashboard
2. Copy your API key

### Step 3: Update SMS Code
In `app.py`, find the `send_reset_sms` function and uncomment/update:

```python
# Install required package first:
# pip install requests

import requests

url = "https://www.fast2sms.com/dev/bulkV2"
payload = {
    "authorization": "YOUR_FAST2SMS_API_KEY_HERE",  # Replace with your API key
    "variables_values": otp,
    "route": "otp",
    "numbers": mobile.replace("+91", "")
}

headers = {'cache-control': "no-cache"}
response = requests.post(url, data=payload, headers=headers)
```

### Step 4: Install Dependencies
```bash
pip install requests
```

## 🔧 Alternative SMS Services

### Twilio (International)
```python
from twilio.rest import Client

client = Client("account_sid", "auth_token")
message = client.messages.create(
    body=f"Your admin password reset OTP: {otp}",
    from_="+1234567890",  # Your Twilio number
    to=mobile
)
```

### MSG91 (India)
```python
import requests

url = "https://api.msg91.com/api/v5/otp"
payload = {
    "template_id": "your_template_id",
    "mobile": mobile,
    "authkey": "your_msg91_authkey",
    "otp": otp
}
```

## 🛡️ Security Notes

1. **Never commit credentials to version control**
2. **Use environment variables for production:**
   ```python
   sender_email = os.environ.get('SMTP_EMAIL')
   sender_password = os.environ.get('SMTP_PASSWORD')
   sms_api_key = os.environ.get('SMS_API_KEY')
   ```

3. **Add to .env file:**
   ```
   SMTP_EMAIL=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   SMS_API_KEY=your_sms_api_key
   ```

## 🧪 Current Status

- ✅ Password reset functionality is fully implemented
- ✅ Email structure and HTML template ready
- ✅ SMS structure ready
- ⚠️ Email/SMS currently fall back to console logging
- 🔧 Requires credentials setup for actual sending

## 📝 Testing

1. **Console Mode (Current)**: Check terminal for tokens/OTP
2. **Email Mode**: Update credentials, check inbox
3. **SMS Mode**: Update API key, check mobile

Both email and SMS are designed to work independently - if one fails, the other still works, and console fallback ensures the admin always gets the reset information.