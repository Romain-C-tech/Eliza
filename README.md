# ⚒️ ForgeBot
 
ForgeBot is an intelligent Discord bot that guides administrators through the complete setup of their server using an interactive
**5-step experience**.
 
---
 
## ⚒️ Features
 
### ⚙️ Guided Setup
- Interactive setup with `/setup`
- Conversational flow + buttons UI
- Full server generation:
  - 📁 Categories  
  - 💬 Channels  
  - 🎭 Roles  
 
---
 
### 🧠 AI-Powered (ML)
- Classifies user input:
  - Server type (gaming, school, community, business)
  - Server size (small, medium, large)
  - Confirmation (yes / no)
- Supports natural language input
 
---
 
### 💳 Built-in Paywall
- Subscription required for:
  - **Medium** and **Large** servers
- PayPal integration (IPN webhook)
- Automatically resumes setup after payment
 
---
 
### 🛡️ Automatic Moderation
- Multi-level toxicity detection
- Automatic sanctions:
  - ⚠️ Warning  
  - 🔇 Mute  
  - 👢 Kick  
  - 🔨 Ban  
- Logs sent to a dedicated channel
 
---
 
### 👋 Welcome System
- Automatic welcome embed
- Auto role assignment
- Modular system via `welcome.py`
 
---
 
### 📖 Interactive Help System
- `/help` command with pagination
- Button-based UI
- Organized by categories
 
---
 
## 🧩 Project Structure
 
 
---
 
## 🔁 Workflow
 
/setup
↓
Step 1 → Server type
Step 2 → Server name
Step 3 → Size (+ paywall if needed)
Step 4 → Special channels
Step 5 → Confirmation
↓
build_server()
 
 
## 📦 Installation
 
### 1. Clone the repository
```bash
git clone https://github.com/your-repo/forgebot.git
cd forgebot
```
### 2. Install dependencies
 
pip install -r requirements.txt
 
### 3. Configure environment variables
 
Create a .env file:
 
DISCORD_TOKEN=your_token_here
 
PAYPAL_EMAIL=your_paypal_email
PAYPAL_WEBHOOK_URL=https://your-domain.com/paypal/webhook
PAYPAL_RETURN_URL=https://your-domain.com/return
 
PAYPAL_PRIX=3.50
PAYPAL_DEVISE=EUR
 
#### ▶️ Run the bot
 
python bot.py
 
#### 🌐 PayPal Webhook
 
The Flask server starts automatically with the bot.
 
Endpoint:
/paypal/webhook
Verifies PayPal payments (IPN)
Unlocks /setup sessions automatically
 
#### Available Commands
 
Command Description
/setup  -> Start server setup
/cancel -> Cancel current setup
/status -> Show session status
/help -> Interactive help menu
/modconfig  -> Show moderation config
 
#### Tech Stack
 
🐍 Python
🤖 discord.py
🧠 Machine Learning (classification)
🌐 Flask (PayPal webhook)
💳 PayPal IPN
 
#### Required Permissions
 
The bot should have:
 
Administrator (recommended)
Manage Roles
Manage Channels
Send Messages
Read Messages
 
#### Author
 
Daniel Fezeu  and Romain Cherhal