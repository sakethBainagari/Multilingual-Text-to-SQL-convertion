# 🌐 Frontend Documentation - text2sqlAgent

## Overview

The frontend is a single-page web application that provides an intuitive interface for users to interact with the NL-to-SQL system through text or voice input.

---

## Tech Stack

### 1. HTML5

**What it does in this project:**
- Structures the entire web interface including the query input form, results display area, database selector, and visualization container
- Creates the modal popup for database upload functionality
- Defines the workflow steps UI showing the query processing stages (Similarity Check → SQL Generation → Execution → Visualization)
- Provides semantic structure for accessibility and screen readers

**Key UI Components Built:**
- Header with project title and description
- Query input textarea with placeholder examples
- Language selector dropdown (English, Telugu, Hindi)
- Voice input button with recording indicator
- Results table container
- Chart/visualization container
- Database management modal
- Sample queries sidebar
- Export buttons section

---

### 2. CSS3

**What it does in this project:**
- Creates the gradient purple theme (`#667eea` to `#764ba2`) that gives the application its visual identity
- Implements responsive design so the interface works on desktop, tablet, and mobile devices
- Styles the workflow steps with visual indicators (active, completed, error states)
- Adds hover effects and transitions for interactive elements like buttons and cards
- Creates the loading spinner animation during query processing
- Styles the data tables with alternating row colors and hover highlights
- Implements the modal overlay and popup for database upload
- Creates visual feedback for voice recording (pulsing microphone animation)

**Visual States Handled:**
- `.active` - Currently processing step (blue border)
- `.completed` - Successfully finished step (green border)
- `.error` - Failed step (red border)
- `.selected` - User-selected similarity match (highlighted green)

---

### 3. JavaScript (Vanilla)

**What it does in this project:**

#### API Communication
- Sends HTTP POST requests to Flask backend endpoints using `fetch()` API
- Handles JSON responses from the server
- Manages async/await for non-blocking API calls

#### Form Handling
- Captures user query input from textarea
- Validates that query is not empty before submission
- Collects visualization preferences (chart type selection)
- Handles file upload for database files

#### Dynamic UI Updates
- Shows/hides workflow steps based on processing state
- Updates step indicators (active, completed, error)
- Populates results table dynamically from API response
- Displays error messages in styled message boxes
- Updates database selector dropdown when new databases are uploaded

#### Event Listeners
- Query form submission
- Voice input button click
- Sample query click (auto-fills textarea)
- Export button clicks (CSV, Excel, JSON)
- Database selector change
- Modal open/close

#### State Management
- Tracks current processing step
- Stores selected similarity match
- Maintains current database selection
- Manages voice recording state

---

### 4. Web Speech API

**What it does in this project:**

#### Speech Recognition
- Converts spoken words into text that fills the query input field
- Supports three languages:
  - English (en-US)
  - Telugu (te-IN)
  - Hindi (hi-IN)
- Provides real-time transcription as user speaks (interim results)
- Handles browser compatibility (works in Chrome, Edge, Safari)

#### User Experience Flow
1. User clicks microphone button
2. Browser requests microphone permission (first time only)
3. Recording indicator appears (pulsing animation)
4. User speaks their query in selected language
5. Speech is converted to text in real-time
6. Final transcription populates the query textarea
7. User can edit if needed, then submit

#### Error Handling
- Displays message if browser doesn't support speech recognition
- Handles microphone permission denied
- Shows error if no speech detected
- Graceful fallback to text input

---

### 5. Plotly.js (Frontend Charting Library)

**What it does in this project:**

#### Chart Rendering
- Receives chart configuration JSON from Flask backend
- Renders interactive charts in the browser
- Supports multiple chart types:
  - Bar charts (for categorical comparisons)
  - Line charts (for trends over time)
  - Pie charts (for distribution/composition)
  - Scatter plots (for correlation analysis)
  - Histograms (for frequency distribution)

#### Interactivity Features
- Hover tooltips showing exact data values
- Zoom and pan functionality
- Click to select data points
- Legend toggling to show/hide data series
- Download chart as PNG image
- Fullscreen mode

#### Integration with Backend
- Backend sends Plotly JSON specification
- Frontend uses `Plotly.newPlot()` to render
- Chart updates dynamically when new query results arrive

---

## Frontend-Backend Communication

### Request Flow

```
User Action → JavaScript Event Handler → fetch() API Call → Flask Endpoint
                                              ↓
User Sees Result ← DOM Update ← JSON Parse ← HTTP Response
```

### API Calls Made by Frontend

| Action | Endpoint | Method | Data Sent |
|--------|----------|--------|-----------|
| Submit Query | `/api/query` | POST | query, visualize, chart_type |
| Check Similarity | `/api/similarity-check` | POST | query |
| Generate SQL | `/api/generate-sql` | POST | query, model, use_ollama |
| Execute SQL | `/api/execute-sql` | POST | sql_query, visualize |
| Get Schema | `/api/schema` | GET | - |
| Upload Database | `/api/db/upload` | POST | file (multipart) |
| Switch Database | `/api/db/switch` | POST | path |
| Export Data | `/api/export` | POST | data, format, filename |

---

## User Interface Sections

### 1. Header
- Project title and tagline
- Visual branding

### 2. Query Input Area
- Large textarea for natural language query
- Language selector (English/Telugu/Hindi)
- Voice input button with microphone icon
- Submit button

### 3. Workflow Steps Display
- Step 1: Similarity Check - Shows if cached match found
- Step 2: SQL Generation - Shows LLM generating SQL
- Step 3: Execution - Shows query running
- Step 4: Visualization - Shows chart being created

### 4. Results Section
- SQL query display (syntax highlighted)
- Data table with results
- Row count and execution time
- Export buttons (CSV, Excel, JSON)

### 5. Visualization Section
- Interactive Plotly chart
- Chart type indicator
- Download options

### 6. Database Management
- Current database indicator
- Database selector dropdown
- Upload new database button
- Modal for file upload

### 7. Sample Queries Sidebar
- Clickable example queries
- Categorized by complexity
- Multilingual examples

---

## Browser Compatibility

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| Core UI | ✅ | ✅ | ✅ | ✅ |
| Voice Input | ✅ | ❌ | ✅ | ✅ |
| Plotly Charts | ✅ | ✅ | ✅ | ✅ |
| File Upload | ✅ | ✅ | ✅ | ✅ |

---

*Frontend serves as the user-facing layer that collects input, displays results, and provides an intuitive experience for database querying.*
