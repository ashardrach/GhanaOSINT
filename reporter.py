import json
from datetime import datetime
from colorama import Fore, init

init(autoreset=True)

def generate_html_report(query, query_type, results, output_file):
    phone_section = ""
    if results.get("phone_info"):
        p = results["phone_info"]
        phone_section = f"""
        <div class="section">
            <h2>📱 Phone Intelligence</h2>
            <table>
                <tr><td>Number</td><td>{p.get('cleaned','')}</td></tr>
                <tr><td>International</td>
                    <td>{p.get('international','')}</td></tr>
                <tr><td>Network</td><td>{p.get('network','')}</td></tr>
                <tr><td>Valid</td>
                    <td>{'✅ Yes' if p.get('valid') else '❌ No'}</td></tr>
                <tr><td>MoMo Capable</td>
                    <td>{'✅ Yes' if p.get('momo_capable') else '❌ No'}</td></tr>
            </table>
        </div>"""

    email_section = ""
    if results.get("email_info"):
        e = results["email_info"]
        domain = e.get("domain_info", {})
        breach = e.get("breach_info", {})
        email_section = f"""
        <div class="section">
            <h2>📧 Email Intelligence</h2>
            <table>
                <tr><td>Email</td><td>{e.get('email','')}</td></tr>
                <tr><td>Username</td><td>{e.get('username','')}</td></tr>
                <tr><td>Provider</td>
                    <td>{domain.get('provider','Unknown')}</td></tr>
                <tr><td>Disposable</td>
                    <td>{'🚨 YES' if domain.get('disposable')
                         else '✅ No'}</td></tr>
                <tr><td>Data Breaches</td>
                    <td>{'🚨 ' + str(breach.get('breach_count',0))
                         + ' breaches found'
                         if breach.get('breached')
                         else '✅ No breaches found'}</td></tr>
            </table>
        </div>"""

    fraud_section = ""
    if results.get("fraud_check"):
        f = results["fraud_check"]
        color = "#ff4444" if f.get("found") else "#00cc44"
        fraud_section = f"""
        <div class="section">
            <h2>🚨 Fraud Database Check</h2>
            <table>
                <tr><td>In Database</td>
                    <td style="color:{color}">
                        {'⚠️ YES — REPORTED' if f.get('found')
                         else '✅ Not reported'}</td></tr>
                <tr><td>Risk Score</td>
                    <td style="color:{color}">
                        {f.get('risk_score',0)}/100</td></tr>
                <tr><td>Reports</td>
                    <td>{f.get('report_count',0)}</td></tr>
                <tr><td>Verdict</td>
                    <td style="color:{color}">
                        {f.get('verdict','Clean')}</td></tr>
            </table>
        </div>"""

    profiles_section = ""
    profiles = results.get("social_profiles", [])
    if profiles:
        rows = ""
        for p in profiles:
            rows += f"""
            <tr>
                <td>{p['platform']}</td>
                <td><a href="{p['url']}" target="_blank"
                       style="color:#89b4fa">{p['url']}</a></td>
            </tr>"""
        profiles_section = f"""
        <div class="section">
            <h2>🌐 Social Media Profiles Found
                ({len(profiles)} accounts)</h2>
            <table>
                <tr>
                    <th style="text-align:left;padding:8px">Platform</th>
                    <th style="text-align:left;padding:8px">URL</th>
                </tr>
                {rows}
            </table>
        </div>"""

    dorks_section = ""
    if results.get("google_dorks"):
        rows = ""
        for d in results["google_dorks"]:
            rows += f"""
            <tr>
                <td style="color:#cdd6f4">{d['description']}</td>
                <td><a href="{d['url']}" target="_blank"
                   style="color:#89b4fa">🔎 Search Google</a></td>
            </tr>"""
        dorks_section = f"""
        <div class="section">
            <h2>🔎 Manual Search Links</h2>
            <p style="color:#a0a0a0; margin-bottom:10px; font-size:13px">
                Click each link to search Google for this person
                on specific platforms. Opens in a new tab.</p>
            <table>
                <tr>
                    <th style="text-align:left;padding:8px">Search Type</th>
                    <th style="text-align:left;padding:8px">Link</th>
                </tr>
                {rows}
            </table>
        </div>"""

    risk_score = results.get("overall_risk_score", 0)
    if risk_score >= 70:
        risk_color = "#ff0000"
        risk_verdict = "HIGH RISK"
    elif risk_score >= 40:
        risk_color = "#ff8800"
        risk_verdict = "MEDIUM RISK"
    else:
        risk_color = "#00cc44"
        risk_verdict = "LOW RISK"

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>GhanaOSINT Report — {query}</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
    font-family: 'Segoe UI', Arial, sans-serif;
    background:#0f0f1a; color:#e0e0e0; padding:20px;
}}
.header {{
    background:linear-gradient(135deg,#1a1a2e,#16213e);
    padding:30px; border-radius:10px;
    border:1px solid #333; margin-bottom:20px;
}}
.header h1 {{ color:#89b4fa; font-size:26px; }}
.header p {{ color:#a0a0a0; margin-top:5px; }}
.risk-badge {{
    display:inline-block;
    background:{risk_color};
    color:white; padding:8px 20px;
    border-radius:20px; font-size:18px;
    font-weight:bold; margin-top:10px;
}}
.section {{
    background:#1a1a2e; padding:20px;
    border-radius:10px; margin-bottom:15px;
    border:1px solid #333;
}}
.section h2 {{
    color:#89b4fa; margin-bottom:15px;
    font-size:16px;
}}
table {{ width:100%; border-collapse:collapse; }}
td, th {{
    padding:8px 12px;
    border-bottom:1px solid #2a2a3e;
    vertical-align:top;
}}
td:first-child {{ color:#a0a0a0; width:200px; }}
.footer {{
    text-align:center; margin-top:20px;
    color:#555; font-size:12px;
}}
.warning {{
    background:#2a1a1a; border:1px solid #ff4444;
    padding:15px; border-radius:8px;
    margin-bottom:15px; color:#ff8888;
}}
a:hover {{ text-decoration:underline; }}
</style>
</head>
<body>
<div class="header">
    <h1>🔍 GhanaOSINT Intelligence Report</h1>
    <p>Query: <strong>{query}</strong> ({query_type})</p>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <div class="risk-badge">{risk_verdict} — {risk_score}/100</div>
</div>

<div class="warning">
    ⚠️ <strong>Legal Notice:</strong> This report contains publicly
    available information only. Use responsibly and in accordance
    with Ghana's Data Protection Act 2020 and Cybersecurity Act 2020.
</div>

{phone_section}
{email_section}
{fraud_section}
{profiles_section}
{dorks_section}

<div class="footer">
    <p>Generated by GhanaOSINT — For authorized use only</p>
    <p>Built by ashardrach | Report ID:
       {datetime.now().strftime('%Y%m%d%H%M%S')}</p>
</div>
</body>
</html>"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(Fore.GREEN + "\n[+] HTML report saved: " + output_file)
    return output_file