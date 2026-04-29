# 📊 Data Visualization Documentation - text2sqlAgent

## Overview

The visualization system automatically generates interactive charts from SQL query results, helping users understand data patterns without manual chart creation.

---

## Tech Stack

### 1. Plotly (Primary Visualization Library)

**What it does in this project:**

#### Interactive Chart Generation
- Creates charts that users can interact with (hover, zoom, pan)
- Generates JSON specification that renders in browser
- Supports multiple chart types from a single library

#### Chart Types Supported

| Chart Type | When It's Used | Best For |
|------------|----------------|----------|
| **Bar Chart** | One categorical + one numeric column | Comparing categories (department salaries) |
| **Line Chart** | Time-based or sequential data | Trends over time (monthly revenue) |
| **Pie Chart** | Single categorical column with counts | Distribution/composition (department sizes) |
| **Scatter Plot** | Two numeric columns | Correlation analysis (age vs salary) |
| **Histogram** | Single numeric column | Frequency distribution (salary ranges) |

#### Why Plotly
- Works both server-side (Python) and client-side (JavaScript)
- Native JSON output for API responses
- Rich interactivity without extra code
- Professional-looking charts out of the box
- Responsive and mobile-friendly

---

### 2. Matplotlib (Secondary Visualization)

**What it does in this project:**

#### Static Chart Generation
- Creates PNG image files of charts
- Used for export and offline viewing
- Provides fallback if Plotly fails

#### File-Based Output
- Saves charts to `visualizations/` folder
- Named with timestamp for uniqueness
- Can be downloaded or embedded in reports

#### When It's Used
- When user requests image export
- For generating charts in CLI mode
- As backup visualization engine

---

### 3. Seaborn (Statistical Styling)

**What it does in this project:**

#### Visual Styling
- Applies professional statistical plot styling
- Sets consistent color palettes
- Configures default figure aesthetics

#### Integration with Matplotlib
- Works on top of Matplotlib
- Enhances default chart appearance
- Provides statistical visualization patterns

---

## Auto-Detection System

### How Chart Type is Automatically Chosen

The system analyzes query results and automatically selects the most appropriate chart type:

#### Decision Logic

```
IF data is empty:
    → No visualization

IF 2+ numeric columns:
    → Scatter Plot (shows correlation)

IF 1 numeric + 1 categorical column:
    IF categorical has ≤10 unique values:
        → Bar Chart (clear comparison)
    ELSE:
        → Histogram (too many categories)

IF only 1 categorical column:
    → Pie Chart (shows distribution)

IF only 1 numeric column:
    → Histogram (shows frequency)

DEFAULT:
    → Bar Chart (safe fallback)
```

#### Examples

| Query Result | Detected Type | Reason |
|--------------|---------------|--------|
| Department + Avg Salary | Bar Chart | 1 categorical + 1 numeric |
| Age + Salary | Scatter Plot | 2 numeric columns |
| Department counts | Pie Chart | Single categorical with counts |
| All salary values | Histogram | Single numeric column |
| Name + Department + Salary | Bar Chart | Default for mixed data |

---

## Visualization Pipeline

### Step-by-Step Process

```
1. SQL QUERY EXECUTED
   ↓
   Result: DataFrame with rows and columns
   ↓
2. CHECK IF VISUALIZATION REQUESTED
   ├── No → Skip visualization
   └── Yes → Continue
   ↓
3. VALIDATE DATA
   ├── Empty DataFrame → Return null
   └── Has data → Continue
   ↓
4. AUTO-DETECT CHART TYPE
   (unless user specified type)
   ↓
5. PREPARE DATA
   ├── Extract X-axis column (first column)
   ├── Extract Y-axis column (second column)
   └── Handle aggregations if needed
   ↓
6. CREATE PLOTLY FIGURE
   ├── Build data traces (bars, lines, etc.)
   ├── Configure layout (title, axes, colors)
   └── Set interactivity options
   ↓
7. SERIALIZE TO JSON
   ↓
8. SEND TO FRONTEND
   ↓
9. RENDER IN BROWSER
   (Plotly.js handles rendering)
```

---

## Chart Configurations

### Bar Chart
- **X-axis**: Categorical values (names, departments)
- **Y-axis**: Numeric values (counts, averages, sums)
- **Color**: Sky blue gradient
- **Hover**: Shows exact value
- **Best for**: Comparing discrete categories

### Line Chart
- **X-axis**: Sequential or time-based values
- **Y-axis**: Numeric values
- **Markers**: Points at each data value
- **Lines**: Connect consecutive points
- **Best for**: Showing trends and changes

### Pie Chart
- **Slices**: Each category gets a slice
- **Size**: Proportional to value
- **Labels**: Category names on slices
- **Percentages**: Auto-calculated and displayed
- **Best for**: Showing composition/distribution

### Scatter Plot
- **X-axis**: First numeric column
- **Y-axis**: Second numeric column
- **Points**: Each row is a dot
- **Opacity**: Slight transparency for overlapping points
- **Best for**: Finding correlations

### Histogram
- **Bins**: Auto-calculated ranges
- **Height**: Frequency count per bin
- **Bars**: Adjacent (no gaps)
- **Best for**: Understanding data distribution

---

## Interactivity Features

### What Users Can Do with Charts

| Feature | Description |
|---------|-------------|
| **Hover** | See exact data values for any point |
| **Zoom** | Click and drag to zoom into region |
| **Pan** | Drag to move around zoomed view |
| **Reset** | Double-click to reset view |
| **Legend Toggle** | Click legend items to show/hide data series |
| **Download** | Save chart as PNG image |
| **Fullscreen** | Expand chart to fill screen |

### Toolbar Options
- Camera icon: Download as PNG
- Zoom icons: Zoom in/out
- Pan icon: Enable panning mode
- Home icon: Reset to original view
- Autoscale: Fit data to view

---

## Frontend Rendering

### How Charts Appear in Browser

1. **Backend** generates Plotly JSON specification
2. **API Response** includes `visualization_data` field
3. **Frontend JavaScript** receives JSON
4. **Plotly.js** library parses specification
5. **DOM** gets updated with SVG chart
6. **User** sees interactive visualization

### Plotly.js Integration
- Loaded from CDN in HTML head
- `Plotly.newPlot()` creates chart in container
- `Plotly.react()` updates existing chart
- Responsive: adjusts to container size

---

## Visualization Examples by Query Type

### Aggregation Queries
**Query**: "Show average salary by department"
**Result**: Department names + average salaries
**Chart**: Bar chart with departments on X, salaries on Y

### Count Queries
**Query**: "Count employees by department"
**Result**: Department names + counts
**Chart**: Pie chart showing department distribution

### Filtered Queries
**Query**: "Show all employees with salary > 70000"
**Result**: Employee details (name, salary, etc.)
**Chart**: Bar chart of employee names vs salaries

### Comparison Queries
**Query**: "Compare age and salary of employees"
**Result**: Age column + Salary column
**Chart**: Scatter plot showing age vs salary correlation

### Time-Based Queries
**Query**: "Show hiring trends by year"
**Result**: Year + count of hires
**Chart**: Line chart showing trend over time

---

## Export Capabilities

### Chart Export
- **PNG**: Download button in chart toolbar
- **Quality**: High resolution (300 DPI for Matplotlib)

### Data Export
- **CSV**: Comma-separated values for spreadsheets
- **Excel**: Formatted .xlsx file with headers
- **JSON**: Raw data for programmatic use

---

## Performance Considerations

### Large Datasets
- Charts limit to first 1000 rows for performance
- Aggregated data preferred over raw records
- Histograms handle large datasets efficiently

### Browser Performance
- SVG rendering for crisp charts
- WebGL mode available for very large scatter plots
- Lazy loading of chart library

---

## Color Scheme

### Default Palette
- Primary: Sky blue (`#87CEEB`)
- Gradient: Purple theme matching app (`#667eea` to `#764ba2`)
- Background: White with light gray grid
- Text: Dark gray for readability

### Chart-Specific Colors
- Bar: Sky blue with hover highlight
- Line: Blue with markers
- Pie: Auto-generated distinct colors per slice
- Scatter: Blue with transparency

---

## Error Handling

| Scenario | Handling |
|----------|----------|
| Empty data | Skip visualization, show message |
| Single value | Show simple display, not chart |
| All nulls | Skip visualization |
| Invalid data types | Attempt conversion, fallback to bar |
| Too many categories | Switch to histogram |

---

*Visualization transforms raw query results into meaningful visual insights, making data analysis accessible to non-technical users.*
