# System Architecture Comparison: Before vs After Voice Input

## 📊 Visual Architecture Updates

### **BEFORE: Text-Only System**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  ┌──────────────┐                                                           │
│  │ Input Module │                                                           │
│  │              │                                                           │
│  │ 👤 User      │                                                           │
│  │    Prompt    │                                                           │
│  │    (Text)    │                                                           │
│  └──────┬───────┘                                                           │
│         │                                                                    │
│         └───────────────────────────────────────────────────────────────┐  │
│                                                                          │  │
└──────────────────────────────────────────────────────────────────────────┼──┘
                                                                           │
                                      [Continues to Similarity Module...] ↓
```

### **AFTER: Voice + Text System**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        🆕 NEW VOICE INPUT MODULE                            │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │  🎤 Microphone Handler                                             │    │
│  │  • getUserMedia() API                                              │    │
│  │  • Audio stream capture (16kHz PCM)                                │    │
│  │                           ↓                                         │    │
│  │  🌐 Language Selector                                              │    │
│  │  • Telugu (te-IN)                                                  │    │
│  │  • Hindi (hi-IN)                                                   │    │
│  │  • English (en-US)                                                 │    │
│  │                           ↓                                         │    │
│  │  🗣️ Web Speech API                                                 │    │
│  │  • webkitSpeechRecognition                                         │    │
│  │  • Real-time transcription                                         │    │
│  │  • Google Cloud Speech backend                                     │    │
│  │                           ↓                                         │    │
│  │  📊 Acoustic Analysis                                              │    │
│  │  • MFCC feature extraction                                         │    │
│  │  • Phoneme detection                                               │    │
│  │  • Noise filtering                                                 │    │
│  │                           ↓                                         │    │
│  │  🧠 Language Model                                                 │    │
│  │  • N-gram processing                                               │    │
│  │  • Context-aware prediction                                        │    │
│  │  • Word probability calculation                                    │    │
│  │                           ↓                                         │    │
│  │  ✍️ Text Transcription                                             │    │
│  │  • Final text output                                               │    │
│  │  • Confidence scoring                                              │    │
│  │  • UTF-8 encoding                                                  │    │
│  │                           ↓                                         │    │
│  │  📝 Text Normalization                                             │    │
│  │  • Auto-populate query field                                       │    │
│  │  • Character cleanup                                               │    │
│  │                                                                     │    │
│  └──────────────────────────┬──────────────────────────────────────────┘    │
│                             │                                               │
│                             │ (Voice-generated text)                        │
│                             ↓                                               │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                    Input Module (EXISTING)                         │    │
│  │                                                                     │    │
│  │  👤 User Prompt                                                    │    │
│  │  • Text input (keyboard) ←──────────────────┐                     │    │
│  │  • Voice input (from Voice Module) ←────────┘                     │    │
│  │                                                                     │    │
│  └──────────────────────────┬──────────────────────────────────────────┘    │
│                             │                                               │
└─────────────────────────────┼───────────────────────────────────────────────┘
                              │
                              ↓
         [Continues to Similarity Module and rest of pipeline...]
```

---

## 🔄 Complete Updated Architecture Diagram

### **Full System with Voice Integration**

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  AI-powered Natural Language to SQL Conversion with Voice Input 🎤       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┌─────────────────────┐
│ 🆕 Voice Input      │
│      Module         │
├─────────────────────┤
│ 🎤 Microphone       │
│ 🌐 Language Select  │
│ 🗣️  Speech API      │
│ ✍️  Transcription   │
└──────────┬──────────┘
           │
           ↓ (Text)
┌──────────────────────┐
│   Input Module       │
├──────────────────────┤
│ 👤 User Prompt       │
│  (Text or Voice)     │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────────────────────────────────────────────┐
│              Similarity Index Module                         │
├──────────────────────────────────────────────────────────────┤
│  🧬 Embedding    →  🔎 Search in   →  📊 Similarity  →      │
│  Generator           Database          Computation           │
│  (sentence-          (FAISS)           (L2 Distance)         │
│  transformers)                                               │
│                                             ↓                 │
│                                    ✅ Threshold Checker      │
│                                       (≥70% = Match)         │
└─────────────────────┬──────────────────────┬─────────────────┘
                      │                      │
        ┌─────────────┘                      └─────────────┐
        │ Similarity Found                   No Match      │
        ↓ (≥70%)                              (<70%)       ↓
┌───────────────────────────────────┐    ┌─────────────────────────┐
│ 🆕 Enhanced Entity Swapping       │    │   Select LLM            │
│        Module                     │    ├─────────────────────────┤
├───────────────────────────────────┤    │ 💻 Local LLM            │
│ 🏷️  Named Entity Recognition     │    │   (Ollama Models)       │
│    • Numbers, Strings, Dates      │    │                         │
│                                   │    │         OR              │
│ 🗺️  Entity Mapping                │    │                         │
│    • Original → New               │    │ 🌐 Non-Local LLM        │
│                                   │    │   (Google Gemini)       │
│ 🆕 Column Detection               │    │                         │
│    • Request vs Cached            │    └────────────┬────────────┘
│                                   │                 │
│ 🆕 SQL Structure Adapter          │                 │
│    • SELECT clause modification   │                 │
│                                   │                 │
│ 📝 Rule-Based Slot Filling        │                 │
│    • Regex replacement            │                 │
│                                   │                 │
│ ✓  Validation & Refinement        │                 │
│    • Schema validation            │                 │
│                                   │                 │
└─────────────┬─────────────────────┘                 │
              │                                       │
              │ (Adapted SQL - 0.1s)                 │ (Generated SQL - 2-5s)
              │                                       │
              └──────────────────┬────────────────────┘
                                 │
                                 ↓
              ┌──────────────────────────────────────────┐
              │      💾 Stores & Retrieves               │
              │                                          │
              │  🗄️  SQL Query  ←→  💾 Vector Database  │
              │     Generated         • FAISS Index     │
              │                       • Metadata Store  │
              └──────────────────┬───────────────────────┘
                                 │
                                 ↓
        ┌────────────────────────────────────────────────┐
        │        SQL Execution Module                    │
        ├────────────────────────────────────────────────┤
        │  📋 SQL      →  🔧 Query     →  📊 Result     │
        │  Validator       Executor        Fetcher       │
        │  (Syntax)       (DB Engine)     (Data)         │
        │                                                 │
        │                    ↓                            │
        │                                                 │
        │  💾 Result   →  ⚠️ Error                       │
        │  Formatter      Handler                        │
        │  (JSON)         (Exceptions)                   │
        └────────────┬────────────────────────────────────┘
                     │
                     ↓
        ┌────────────────────────────────────────────────┐
        │       Visualization Module                     │
        ├────────────────────────────────────────────────┤
        │  📥 Input    →  🔄 Data Pre-  →  📊 Visual.   │
        │  Handler         Processor        Generator    │
        │  (Results)      (Transform)      (Charts)      │
        │                                                 │
        │                    ↓                            │
        │                                                 │
        │            🖼️  Output Renderer                 │
        │               (Display)                        │
        └────────────┬────────────────────────────────────┘
                     │
                     ↓
              ┌─────────────┐
              │   🖥️ Result  │
              │   Display    │
              │   (Web UI)   │
              └─────────────┘
```

---

## 🆕 What's New in the Architecture

### **1. Voice Input Module (NEW)**

**Components Added:**
- 🎤 **Microphone Handler** - getUserMedia() API
- 🌐 **Language Selector** - Telugu/Hindi/English
- 🗣️ **Web Speech API** - Browser-based recognition
- 📊 **Acoustic Analysis** - MFCC features
- 🧠 **Language Model** - N-gram processing
- ✍️ **Text Transcription** - Real-time output
- 📝 **Text Normalization** - Auto-populate field

**Location in Flow:**
- **Position:** Before Input Module
- **Input:** User's voice (audio stream)
- **Output:** Normalized text query
- **Processing Time:** 1-2 seconds

### **2. Enhanced Entity Swapping Module (UPGRADED)**

**New Features:**
- 🆕 **Column Detection** - Identifies requested columns
- 🆕 **SQL Structure Adapter** - Modifies SELECT clause
- Handles: `SELECT * → SELECT name, age`

**What Changed:**
- Now handles both literal swapping AND structural changes
- No longer shows warnings for column differences
- Validates columns against schema
- Processing time: Still 0.05s (instant)

### **3. Input Module (MODIFIED)**

**What Changed:**
- Now accepts TWO input types:
  - Manual text (keyboard)
  - Voice-generated text (from Voice Module)
- No backend changes
- Transparent to rest of pipeline

---

## 📋 Architecture Update Checklist

### **For Your Diagram, Add:**

✅ **1. Voice Input Module Box** (Top-left, before Input Module)
   - Position: Above or to the left of current "Input Module"
   - Size: Similar to other module boxes
   - Color: Different color to highlight it's NEW (suggest light blue)

✅ **2. Module Components** (Inside Voice Input box)
   - 🎤 Microphone Handler
   - 🌐 Language Selector (te-IN/hi-IN/en-US)
   - 🗣️ Web Speech API
   - 📊 Acoustic Analysis
   - 🧠 Language Model
   - ✍️ Text Transcription
   - 📝 Text Normalization

✅ **3. Arrows/Flow**
   - From User → Voice Input Module
   - From Voice Input Module → Input Module
   - Label: "Voice-generated text" or "Normalized text query"

✅ **4. Update Input Module**
   - Add note: "Text or Voice input"
   - Show two input paths merging into one

✅ **5. Update Entity Swapping Module**
   - Add labels for NEW components:
     - "Column Detection" (NEW)
     - "SQL Structure Adapter" (NEW)
   - Maybe use different color or icon to show enhancement

✅ **6. Add Legend/Key**
   ```
   🆕 NEW Component
   🔄 Modified Component
   ✓  Existing (unchanged)
   ```

---

## 🎨 Suggested Visual Updates

### **Color Scheme:**
- **Voice Input Module:** Light blue (#E1F5FE)
- **Enhanced Entity Swapping:** Light purple (#F3E5F5)
- **Existing Modules:** Keep current colors
- **Arrows from Voice:** Dashed line (to show optional path)
- **Arrows from Text:** Solid line (traditional path)

### **Icons to Add:**
- 🎤 Microphone (Voice Input)
- 🌐 Globe (Language selection)
- 🗣️ Speech bubble (Speech recognition)
- 🆕 "NEW" badge (on Voice Input box)
- ⭐ "Enhanced" badge (on Entity Swapping box)

### **Labels to Add:**
- "Multilingual Support: Telugu, Hindi, English"
- "Browser-based Processing (Google Cloud)"
- "No Backend Changes Required"
- "1-2s processing time"

---

## 📐 Positioning Suggestions

### **Option A: Vertical Layout** (Recommended)

```
        User Input
            |
    ┌───────┴───────┐
    ↓               ↓
🎤 Voice      OR    📝 Text
Input Module        Input
    ↓               ↓
    └───────┬───────┘
            ↓
    Input Module
            ↓
  Similarity Module
       (rest...)
```

### **Option B: Side-by-Side**

```
🎤 Voice Input Module  ─┐
                        ├──→  Input Module  ──→  Similarity Module
📝 Text Input  ─────────┘              (rest...)
```

---

## 📊 Data Flow Labels to Add

1. **Voice Input → Input Module:**
   - Label: "Transcribed Text (te-IN/hi-IN/en-US)"
   - Time: "1-2 seconds"

2. **Input Module → Similarity Module:**
   - Label: "Natural Language Query"
   - Note: "Same as before"

3. **Enhanced Entity Swapping:**
   - Add label: "Now handles column selection!"
   - Time: "Still 0.05s (instant)"

---

## 🎯 Key Messages to Highlight

Add callout boxes or notes:

1. **"🆕 NEW: Voice Input in 3 Languages"**
   - Telugu, Hindi, English supported
   - Browser-based processing
   - 1-2 second response time

2. **"⚡ Enhanced: Smart Column Adaptation"**
   - Automatically adapts SELECT clauses
   - Validates against schema
   - No AI needed (instant)

3. **"✓ No Backend Changes"**
   - Voice processing is client-side
   - Seamless integration
   - Existing pipeline unchanged

---

## 🖼️ Example: Updated Module Box

```
┌──────────────────────────────────────────┐
│  🆕 Voice Input Module                   │
│  ──────────────────────────────────────  │
│                                          │
│  Multilingual Support (3 Languages)     │
│                                          │
│  🎤 ──→ 🌐 ──→ 🗣️ ──→ 📊 ──→ 🧠 ──→ ✍️  │
│  Mic   Lang  Speech  Acoustic  LM  Text │
│             API     Analysis            │
│                                          │
│  Output: Normalized Text Query          │
│  Time: 1-2 seconds                      │
│  Location: Browser (Client-side)        │
│                                          │
└──────────────────────────────────────────┘
```

---

## 📝 Summary of Changes

| Component | Status | Change Description |
|-----------|--------|-------------------|
| Voice Input Module | 🆕 NEW | Complete new module for multilingual voice input |
| Input Module | 🔄 Modified | Now accepts both text and voice input |
| Entity Swapping | ⭐ Enhanced | Added column detection and SQL structure adaptation |
| Similarity Module | ✓ Unchanged | Works the same way |
| LLM Selection | ✓ Unchanged | No changes |
| SQL Execution | ✓ Unchanged | No changes |
| Visualization | ✓ Unchanged | No changes |
| Vector Database | ✓ Unchanged | No changes |

---

## 🚀 Architecture Evolution

### **Version 1.0 (Original):**
```
Text Input → Similarity → Entity Swap/LLM → SQL → Results
```

### **Version 2.0 (Current with Voice):**
```
Voice Input → Text → Similarity → Enhanced Entity Swap/LLM → SQL → Results
    OR
Text Input → Similarity → Enhanced Entity Swap/LLM → SQL → Results
```

**Key Improvements:**
- ✅ Added voice input in 3 languages
- ✅ Enhanced entity swapping with column adaptation
- ✅ No backend changes required
- ✅ Faster response times (0.1s with cache)
- ✅ Better user experience

---

*Architecture Documentation - Version 2.0*
*Last Updated: October 20, 2025*
