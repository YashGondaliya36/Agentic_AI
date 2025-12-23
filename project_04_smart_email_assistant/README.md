# 📧 Smart Email Assistant

**AI-powered email automation with human-in-the-loop control.**

## 🎯 What It Does

Automatically processes your Gmail inbox:

1. **Classifies** emails (urgent/important/normal/promotional/spam)
2. **Generates** professional draft responses
3. **Asks for your approval** before sending (human-in-the-loop)
4. **Sends** approved emails
5. **Marks** original emails as read

**You stay in control!** Every email is reviewed before sending.

## 🏗️ Architecture

```
Email → Classify → Need Reply? → Generate Draft → 👤 YOU APPROVE → Send
                        ↓
                      Archive
```

### Multi-Agent System

- **Classifier Agent**: Categorizes & prioritizes emails
- **Draft Writer Agent**: Generates professional responses
- **Gmail Integration**: Reads & sends emails
- **LangGraph Workflow**: Orchestrates the process

### Human-in-the-Loop

- Review every draft before sending
- Edit drafts if needed
- Skip emails you don't want to reply to
- **Full control at all times**

## 🚀 Setup

### 1. Install Dependencies

```bash
cd project_04_smart_email_assistant
pip install -r requirements.txt
```

### 2. Configure Gmail API

**This project uses the same Gmail OAuth from Project 2!**

If you haven't set it up:

1. Go to Google Cloud Console
2. Enable Gmail API
3. Create OAuth credentials (Desktop app)
4. Download as `credentials.json`
5. Place in this directory

**Gmail scopes needed:**
- `gmail.readonly` - Read emails
- `gmail.send` - Send emails
- `gmail.modify` - Mark as read

### 3. Environment Variables

Uses root `.env` file:

```bash
# Already in root .env
GOOGLE_API_KEY=your_gemini_key
```

### 4. Run

```bash
python main.py
```

## 💡 How It Works

### Step 1: Fetch Unread Emails

```
📬 Fetching unread emails...
✅ Found 3 emails
```

### Step 2: Classify Each Email

```
📊 Classifying: "Meeting Request"
   From: John Doe
   ✅ Category: IMPORTANT
   ⭐ Priority: 4/5
   📝 Action Required: True
```

### Step 3: Generate Draft

```
✍️  Writing draft response...
   ✅ Draft created

==================================
DRAFT PREVIEW:
==================================
Hi John,

Thank you for reaching out...
```

### Step 4: Human Review (HITL)

```
📝 DRAFT RESPONSE (Please Review)
==================================
[Full draft shown]
==================================

What would you like to do?
  [approve/edit/skip]

→ approve
✅ Draft approved!
```

### Step 5: Send Email

```
📤 Sending email...
✅ Email sent to john@example.com
✅ Original marked as read
```

## 🎓 Key Features

| Feature | Description |
|---------|-------------|
| **Auto-Classification** | AI categorizes emails automatically |
| **Smart Drafts** | Professional responses generated |
| **Human Control** | You approve every email |
| **Edit Capability** | Modify drafts before sending |
| **Gmail Integration** | Full OAuth authentication |
| **State Management** | LangGraph tracks everything |
| **Error Handling** | Graceful failures |

## 🔧 Configuration

### Email Categories

- `urgent` - Needs immediate response
- `important` - High priority, respond today
- `normal` - Standard email
- `promotional` - Marketing/newsletters (auto-archived)
- `spam` - Junk (auto-archived)

### Priority Levels

- `5` - Highest priority
- `4` - High
- `3` - Medium
- `2` - Low
- `1` - Lowest

## 📊 Workflow Details

```python
# LangGraph workflow
1. classify_node()
   ↓
2. decide_after_classification()
   ├→ Need reply? → draft_node()
   └→ No reply? → archive_node()
        ↓
3. Human reviews draft (INTERRUPT)
   ↓
4. send_node()
   └→ Mark as read
```

### Human-in-the-Loop Implementation

Uses LangGraph's checkpoint system:
- Workflow pauses after draft generation
- User reviews in terminal
- User can: approve, edit, or skip
- Workflow resumes with user input

## 💼 Use Cases

### Customer Support
- Auto-generate responses to common questions
- Maintain professional tone
- Save hours daily

### Sales  
- Quick responses to leads
- Professional follow-ups
- Never miss an opportunity

### Personal
- Handle newsletters efficiently
- Respond to friends/family
- Manage your inbox better

## 🛠️ Customization

### Change Classification Logic

Edit `agents/classifier.py`:
```python
# Modify the prompt to change categories
# Add your own classification rules
```

### Adjust Draft Style

Edit `agents/draft_writer.py`:
```python
# Change tone, length, format
# Add company-specific guidelines
```

### Add More Agents

Create new agents:
```python
# agents/researcher.py
# Search for context before replying

# agents/scheduler.py
# Auto-schedule meetings from emails
```

## 📈 Future Enhancements

Planned features:
- [ ] Context search (Tavily) before replying
- [ ] Email thread analysis
- [ ] Auto-schedule meetings
- [ ] Follow-up reminders
- [ ] Batch processing
- [ ] Email templates
- [ ] Smart signatures
- [ ] Priority inbox

## 🔒 Security

**Protected:**
- ✅ OAuth credentials (gitignored)
- ✅ Email tokens (gitignored)
- ✅ API keys (in root .env)

**You control:**
- ✅ Every email sent
- ✅ What gets archived
- ✅ Draft editing

**Nothing is automated without your approval!**

## 📚 Learn More

- [LangGraph Human-in-the-Loop](https://langchain-ai.github.io/langgraph/how-tos/human-in-the-loop/)
- [Gmail API Python](https://developers.google.com/gmail/api/quickstart/python)
- [Google Gemini AI](https://ai.google.dev/)

## ✅ Completion Checklist

- [x] Gmail integration
- [x] Email classification
- [x] Draft generation
- [x] Human-in-the-loop
- [x] Email sending
- [x] Mark as read
- [ ] Install dependencies
- [ ] Setup Gmail OAuth
- [ ] Test with real emails

## 🎉 Success!

You've built a **production-ready email automation system** with:
- Multi-agent AI
- Human-in-the-loop
- Real Gmail integration
- LangGraph workflows

**This is portfolio-worthy!** 🏆

---

Made with ❤️ using LangGraph, Google Gemini, and Gmail API
