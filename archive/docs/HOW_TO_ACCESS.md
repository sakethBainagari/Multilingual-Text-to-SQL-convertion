# ⚠️ IMPORTANT: How to Access the Application

## ❌ **WRONG WAY** (Will cause errors)

**DO NOT** open the HTML file directly in your browser or VS Code Live Preview:
- ❌ Opening `templates/index.html` directly
- ❌ Using VS Code "Open with Live Server"
- ❌ Double-clicking the HTML file
- ❌ File URLs like `file:///C:/Users/saket/Desktop/text2sqlAgent/templates/index.html`

**Why this fails:**
- The HTML needs the Flask backend server to handle API calls
- Opening the file directly makes API calls to wrong URLs
- You'll see errors like: `File not found: "c:\Users\saket\Desktop\text2sqlAgent\api\similarity-check"`

---

## ✅ **CORRECT WAY** (Always works)

### **Step 1: Start the Flask Server**
```powershell
cd C:\Users\saket\Desktop\text2sqlAgent
python main.py --web
```

You should see:
```
🌐 Starting web interface...
📊 Open your browser and go to: http://localhost:5000
 * Running on http://127.0.0.1:5000
```

### **Step 2: Open in Browser**
**Use one of these URLs (EXACTLY):**
- ✅ **http://localhost:5000**
- ✅ **http://127.0.0.1:5000**

**DO NOT use:**
- ❌ `file:///...` URLs
- ❌ Any other port number
- ❌ VS Code Live Preview

---

## 🔧 **Troubleshooting**

### **Problem: "Failed to check similarity: Server returned non-JSON response"**

**Cause:** You opened the HTML file directly instead of through Flask server

**Solution:**
1. **Close** the HTML file in your browser
2. **Make sure Flask server is running:**
   ```powershell
   python main.py --web
   ```
3. **Open:** http://localhost:5000 in your browser
4. **Test:** Enter a query and click "Check Similarity & Process"

---

### **Problem: "Connection refused" or "Cannot reach server"**

**Cause:** Flask server is not running

**Solution:**
1. Open PowerShell/Terminal
2. Navigate to project folder:
   ```powershell
   cd C:\Users\saket\Desktop\text2sqlAgent
   ```
3. Start server:
   ```powershell
   python main.py --web
   ```
4. Wait for: `Running on http://127.0.0.1:5000`
5. Open: http://localhost:5000

---

### **Problem: "Port 5000 already in use"**

**Cause:** Another Flask server is running

**Solution:**
```powershell
# Stop all Python processes
Get-Process | Where-Object { $_.ProcessName -eq "python" } | Stop-Process -Force

# Start server again
python main.py --web
```

---

## 📋 **Quick Checklist**

Before using the application, verify:

- [ ] Flask server is running (`python main.py --web`)
- [ ] You see: `Running on http://127.0.0.1:5000`
- [ ] You're accessing: **http://localhost:5000** (not file:///)
- [ ] Ollama is running (if using Ollama models): `ollama list`

---

## 🎯 **Full Workflow**

### **Every time you want to use the app:**

1. **Open PowerShell:**
   ```powershell
   cd C:\Users\saket\Desktop\text2sqlAgent
   ```

2. **Start Flask Server:**
   ```powershell
   python main.py --web
   ```

3. **Open Browser:**
   - Go to: **http://localhost:5000**

4. **Use the App:**
   - Enter query (text or voice)
   - Click "Check Similarity & Process"
   - Choose Gemini or Ollama model
   - Generate and execute SQL

5. **When Done:**
   - Press `Ctrl+C` in PowerShell to stop server
   - OR close PowerShell window

---

## 🚀 **Current Status**

**✅ Server Running:** http://localhost:5000
```
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.191.223:5000
```

**✅ To Access:**
1. Open your browser
2. Go to: **http://localhost:5000**
3. Start using the app!

---

## 💡 **Pro Tips**

### **Bookmark This URL:**
Add **http://localhost:5000** to your browser bookmarks for easy access

### **Keep Server Running:**
- The server stays running until you stop it
- You can refresh the browser page without restarting the server
- Only restart if you make code changes

### **Multiple Tabs:**
- You can open multiple browser tabs to http://localhost:5000
- Each tab works independently

### **Access from Phone/Tablet:**
If you're on the same WiFi network:
- Use: **http://192.168.191.223:5000**
- (Replace with your computer's IP if different)

---

## 🎉 **Summary**

**Remember:**
- ✅ **Always start:** `python main.py --web`
- ✅ **Always access:** http://localhost:5000
- ❌ **Never open:** HTML file directly

**That's it!** Follow these steps and everything will work perfectly! 🚀
