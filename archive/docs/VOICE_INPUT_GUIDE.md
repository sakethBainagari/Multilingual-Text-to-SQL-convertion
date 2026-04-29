# 🎤 Voice Input Feature Guide

## Overview
Your NL-to-SQL system now supports **voice input in multiple languages**! You can speak your queries in Telugu, Hindi, or English instead of typing them.

## ✨ Features

### Supported Languages
- 🇮🇳 **Telugu (తెలుగు)** - `te-IN`
- 🇮🇳 **Hindi (हिन्दी)** - `hi-IN`
- 🇺🇸 **English** - `en-US`

### Key Capabilities
✅ Real-time speech recognition  
✅ Automatic text conversion  
✅ Visual feedback during recording  
✅ Language switching on-the-fly  
✅ Works completely client-side (no backend changes needed)  
✅ Free to use (Web Speech API)

## 🚀 How to Use

### Step 1: Open the Application
```powershell
python main.py
```
Then select option `2` for Web Interface, or run:
```powershell
python main.py --web
```

### Step 2: Access in Browser
Navigate to: `http://localhost:5000`

### Step 3: Select Your Language
1. Click the language dropdown next to the microphone button
2. Choose your preferred language:
   - తెలుగు (Telugu)
   - हिन्दी (Hindi)
   - English

### Step 4: Start Voice Input
1. **Click the microphone button (🎤)**
2. **Allow microphone permission** when prompted (first time only)
3. The button will turn **red (🔴)** when recording
4. You'll see **"🎙️ Listening... Speak now!"**

### Step 5: Speak Your Query
Speak naturally in your selected language. Examples:

**Telugu:**
```
నాకు డిపార్ట్‌మెంట్ వారీగా సగటు జీతం చూపించు
(Show me average salary by department)

డేటా బేస్ లో ఉద్యోగుల వివరాలు చూపించు
(Show employee details in database)

డిపార్ట్‌మెంట్ పేరు చూపించు
(Show department names)
```

**Hindi:**
```
मुझे विभाग के अनुसार औसत वेतन दिखाएं
(Show me average salary by department)

डेटाबेस में कर्मचारियों का विवरण दिखाएं
(Show employee details in database)

70 हजार से अधिक वेतन वाले कर्मचारियों का डेटा चाहिए
(Get employees with salary greater than 70K)
```

**English:**
```
Show me all employees with salary greater than 70000
Get average salary by department
List all projects with status in progress
```

### Step 6: Stop Recording
Click the microphone button again (now showing 🔴) to stop recording

### Step 7: Review & Process
1. Your spoken text will appear in the query box
2. Review the recognized text
3. Click **"🔍 Check Similarity & Process"** to continue

## 🎯 Tips for Best Results

### For Accurate Recognition:
1. **Speak clearly** and at a moderate pace
2. **Minimize background noise**
3. **Use a good quality microphone**
4. **Speak complete sentences**
5. **Pause briefly** between sentences

### Language-Specific Tips:

**Telugu:**
- Use common database terms in English (e.g., "database", "table", "salary")
- Mix Telugu and English naturally (code-switching is supported)
- Example: "employees table లో data చూపించు"

**Hindi:**
- Similar to Telugu, technical terms can be in English
- Example: "employees की details दिखाओ जिनकी salary 70000 से ज्यादा है"

**English:**
- Standard database query terms work best
- Be specific with column names and conditions

## 🔧 Browser Compatibility

### ✅ Fully Supported:
- Google Chrome (Desktop & Mobile)
- Microsoft Edge
- Opera
- Samsung Internet

### ⚠️ Limited/No Support:
- Firefox (no Web Speech API support)
- Safari (limited speech recognition)
- Internet Explorer (not supported)

**Recommendation:** Use **Google Chrome** or **Microsoft Edge** for best experience.

## 🛠️ Troubleshooting

### "Microphone permission denied"
**Solution:** Allow microphone access in browser settings
1. Click the 🔒 lock icon in address bar
2. Change microphone permission to "Allow"
3. Refresh the page

### "No speech detected"
**Solutions:**
- Check if microphone is connected and working
- Ensure microphone is not muted
- Try speaking louder or closer to the microphone
- Test microphone in system settings

### "Voice input not available"
**Solution:** Your browser doesn't support Web Speech API
- Switch to Google Chrome or Microsoft Edge
- Update your browser to the latest version

### Recognition is inaccurate
**Solutions:**
- Speak more clearly and slowly
- Reduce background noise
- Switch to a better microphone
- Try speaking in simpler sentences
- Use more common words

### Language not recognized correctly
**Solutions:**
- Ensure correct language is selected in dropdown
- Wait for "Listening..." message before speaking
- Try speaking a test phrase first
- Check if your accent matches the selected language variant

## 🌐 Technical Details

### Web Speech API
- **Technology:** Browser-built-in Web Speech API
- **Processing:** Cloud-based (requires internet)
- **Privacy:** Audio sent to Google servers for processing
- **Cost:** Free for all users
- **Latency:** ~500ms-2s depending on network

### How It Works:
1. User clicks microphone button
2. Browser requests microphone permission
3. Audio captured in real-time
4. Audio sent to speech recognition service
5. Text transcript returned
6. Query box auto-populated
7. User can review and process

### Data Flow:
```
User Speech → Browser Mic → Web Speech API → 
Cloud Processing → Text Transcript → Query Box → 
NL-to-SQL Processing → SQL Generation
```

## 📝 Examples by Use Case

### Database Queries (Telugu)
```
టేబుల్ లో ఎంత డేటా ఉంది
employees table చూపించు
salary ఎక్కువ ఉన్న వారు ఎవరు
```

### Database Queries (Hindi)
```
टेबल में कितना डेटा है
employees table दिखाओ
सबसे ज्यादा salary किसकी है
```

### Database Queries (English)
```
How many rows in the table
Show employees table
Who has the highest salary
Create a new table called students
```

### Complex Queries (Mixed Language)
```
Telugu + English:
"employees table లో engineering department వారి average salary ఎంత"

Hindi + English:
"engineering department के employees की average salary क्या है"
```

## 🎉 Enjoy Voice-Powered SQL Queries!

You can now interact with your database naturally by speaking in your preferred language. The system will understand Telugu, Hindi, and English, making data querying more accessible and intuitive!

---

**Need Help?** If you encounter any issues, check the browser console (F12) for detailed error messages.
