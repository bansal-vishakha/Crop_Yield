# Project: Professional Crop Yield Prediction & Analysis

## 1. Project Overview

This project provides a professional, structured workflow to build a high-impact crop yield prediction system. It moves beyond a basic academic exercise to reflect a real-world data science approach, emphasizing a robust data foundation, explainable modeling, and interactive reporting.

The project is divided into three core phases:
- **Phase 1: ETL & Database Design:** Building a robust, scalable, and reliable data foundation.
- **Phase 2: Advanced Modeling & Analysis:** Using state-of-the-art techniques to create an accurate and explainable predictive model.
- **Phase 3: Interactive Reporting & Deployment:** Delivering insights through a powerful, interactive dashboard.

---

## Phase 1: Advanced ETL & Database Design (The Professional Foundation)

**Goal:** To build a single source of truth by acquiring diverse datasets, designing a scalable database, and creating an automated ETL pipeline. This is the most critical phase for project success.

---

### **Step 1.1: Project & Environment Setup**

* **The Goal:** Create a clean, organized, and reproducible project structure from the start.

* **The "Why" (Thinking Process):** A messy project is impossible to maintain or share. We establish a standard directory structure to separate data, scripts, and notebooks. A Python virtual environment is non-negotiable; it isolates our project's dependencies, preventing the "it works on my machine" problem by ensuring anyone can replicate the exact environment needed to run the code.

* **Key Commands:**
    ```bash
    # 1. Create the project directory structure
    mkdir crop_yield_project
    cd crop_yield_project
    mkdir data scripts notebooks

    # 2. Create and activate a Python virtual environment
    python3 -m venv venv
    source venv/bin/activate

    # 3. Install initial core libraries
    pip install pandas numpy jupyterlab requests sqlalchemy
    ```

---

### **Step 1.2: Strategic Data Sourcing**

* **The Goal:** To gather a rich, diverse set of features that genuinely influence crop yields.

* **The "Why" (Thinking Process):** The initial report's model was weak because its features were weak. Rainfall alone doesn't determine yield. Factors like soil quality, irrigation (which mitigates poor rainfall), and modern farming inputs (fertilizers) are critical drivers. A professional approach means hypothesizing which factors matter and then actively seeking out that data.

* **Action Plan (No code, just strategy):**
    1.  **Hypothesize Drivers:** Brainstorm factors beyond rainfall (e.g., Soil Type, Soil pH, NPK Fertilizer Use, % Irrigated Area, Min/Max Temperature).
    2.  **Search Government Portals:** Look for data from sources like India's Department of Agriculture, a state's agricultural ministry, or the National Bureau of Soil Survey.
    3.  **Create a Sourcing Script:** In `scripts/data_sourcing.py`, write functions to download these files automatically.

---

### **Step 1.3: Database Schema Design**

* **The Goal:** To design a clean, normalized database schema that prevents errors and is easy to expand.

* **The "Why" (Thinking Process):** Storing everything in one giant CSV file (a "flat file") is a beginner's mistake. It leads to data redundancy (e.g., typing "Maharashtra" 1000 times) and update anomalies. A normalized relational database (even a simple SQLite file) solves this. We separate distinct concepts into their own tables (`districts`, `soil_properties`, `crop_yields`). This ensures that a district's name is stored once, making the data smaller, faster, and more reliable.

* **Key Concepts (To be implemented in the ETL script):**
    * **Primary Keys:** A unique ID for each row in a table (e.g., `district_id`).
    * **Foreign Keys:** A key that links a row in one table to a row in another (e.g., the `district_id` in the `crop_yields` table links back to the `districts` table).

---

### **Step 1.4: Automated ETL Script**

* **The Goal:** To create a single, repeatable script that takes all the messy, raw source data and populates our clean, structured database.

* **The "Why" (Thinking Process):** Data cleaning is never a one-time task. You might get new data, find an error in a source file, or want to add a new data source. An automated script (`scripts/etl.py`) makes this process trivial. You can rerun the script at any time to rebuild the entire database from scratch, ensuring consistency and saving hours of manual work.

* **Key Code Concepts (in `scripts/etl.py`):**
    ```python
    import pandas as pd
    from sqlalchemy import create_engine

    # --- EXTRACT ---
    # Load all raw CSVs into pandas DataFrames
    rainfall_df = pd.read_csv('data/raw_rainfall.csv')
    soil_df = pd.read_csv('data/raw_soil.csv')
    # ... etc.

    # --- TRANSFORM ---
    # The hardest part: standardize column names, handle missing values,
    # and crucially, harmonize district names across different files.
    # Example:
    rainfall_df.rename(columns={'dist': 'district_name'}, inplace=True)
    soil_df['district_name'] = soil_df['district_name'].str.lower().str.strip()
    # ... many more cleaning steps

    # --- LOAD ---
    # Connect to the SQLite database and load the cleaned data
    engine = create_engine('sqlite:///data/agriculture.db')
    districts_table.to_sql('districts', engine, if_exists='replace', index=False)
    crop_yields_table.to_sql('crop_yields', engine, if_exists='replace', index=False)
    # ... etc. for all tables
    ```

---

## Phase 2: Advanced Modeling & Explanatory Analysis

**Goal:** To move beyond basic models to a state-of-the-art approach that is both accurate and, crucially, interpretable.

---

### **Step 2.1: Analytical Base Table (ABT) Creation**

* **The Goal:** To create a single, wide table in memory that joins all our database tables and is ready for modeling.

* **The "Why" (Thinking Process):** Our database is normalized for storage efficiency and integrity. For modeling, however, we need all our features for a given `district-year` in a single row. We write one clean SQL query to join our tables, creating this "Analytical Base Table" (ABT) as a pandas DataFrame. All subsequent feature engineering and modeling will be performed on this ABT.

* **Key Code Concepts (in `notebooks/1-Modeling.ipynb`):**
    ```python
    import pandas as pd
    from sqlalchemy import create_engine

    engine = create_engine('sqlite:///data/agriculture.db')
    query = """
    SELECT
        y.*,
        s.soil_type,
        s.ph_level,
        w.avg_rainfall_mm,
        w.avg_temp_c
    FROM crop_yields y
    LEFT JOIN soil_properties s ON y.district_id = s.district_id
    LEFT JOIN monthly_weather w ON y.district_id = w.district_id AND y.year = w.year
    -- ... more joins
    """
    abt_df = pd.read_sql(query, engine)
    ```

---

### **Step 2.2: Intelligent Feature Engineering**

* **The Goal:** To create new features (signals) from our existing data that make it easier for the model to find patterns.

* **The "Why" (Thinking Process):** Raw data is often not optimal for a model. For example, the absolute rainfall `100mm` is less meaningful than knowing it was `25% below average for that month`. We engineer features that capture these relative changes and interactions.

* **Key Code Concepts (in `notebooks/1-Modeling.ipynb`):**
    ```python
    # Example 1: Rainfall Anomaly (Z-score)
    # df.groupby('district_id')['rainfall_mm'].transform(lambda x: (x - x.mean()) / x.std())

    # Example 2: Growing Season Weather (aggregate weather for specific months)
    # df_growing_season = df[df['month'].isin([6, 7, 8, 9])].groupby(['district_id', 'year'])['rainfall_mm'].sum()

    # Example 3: Interaction Term
    # df['rainfall_x_irrigation'] = df['rainfall_anomaly'] * df['irrigated_area_pct']
    ```

---

### **Step 2.3: Smarter Model Selection**

* **The Goal:** To choose the right tool for the job.

* **The "Why" (Thinking Process):** The original report's use of an LSTM was a classic case of using a complex tool incorrectly. LSTMs are for sequence data, but our problem is a standard tabular prediction task (given these 20 features for a district-year, predict the yield). The industry standard for this is a Gradient Boosting Machine (GBM) like LightGBM or XGBoost. They are highly accurate, fast, and robust. We will use one of these as our primary model.

* **Key Code Concepts (in `notebooks/1-Modeling.ipynb`):**
    ```python
    import lightgbm as lgb
    from sklearn.model_selection import train_test_split
    import joblib

    # X contains all our features, y is the target (e.g., rice_yield)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize and train the LightGBM model
    lgbm = lgb.LGBMRegressor(objective='regression_l1', n_estimators=1000)
    lgbm.fit(X_train, y_train, eval_set=[(X_test, y_test)], callbacks=[lgb.early_stopping(100)])

    # Save the trained model for our dashboard
    joblib.dump(lgbm, 'scripts/yield_model.pkl')
    ```

---

### **Step 2.4: Rigorous Evaluation & Explainability**

* **The Goal:** To understand not just *if* our model is accurate, but *why* it's making the predictions it is.

* **The "Why" (Thinking Process):** A prediction of "2500 kg/ha" is useless without context. A business stakeholder will ask, "Why 2500? What were the key drivers?" We need to move beyond a "black box" model. The SHAP (SHapley Additive exPlanations) library is the industry standard for explaining the output of any machine learning model. It tells us exactly how much each feature contributed to a specific prediction.

* **Key Code Concepts (in `notebooks/1-Modeling.ipynb`):**
    ```python
    import shap

    # Create a SHAP explainer object
    explainer = shap.TreeExplainer(lgbm)
    shap_values = explainer.shap_values(X_test)

    # Visualize the explanation for a single prediction
    shap.force_plot(explainer.expected_value, shap_values[0,:], X_test.iloc[0,:])

    # Visualize overall feature importance
    shap.summary_plot(shap_values, X_test)
    ```

---

## Phase 3: Interactive Reporting & Scenario Analysis

**Goal:** To deliver insights as an interactive tool, not a static report. The dashboard will allow for exploration, prediction, and "what-if" analysis.

---

### **Step 3.1: Tooling Selection**

* **The Goal:** To use the right tools for development and for deployment.

* **The "Why" (Thinking Process):** During development, we need to quickly explore our database. A GUI tool like **DBeaver** is perfect for this—you can write queries and see results instantly without writing Python code. For the final user-facing app, **Streamlit** is the ideal choice. It lets us build a powerful, interactive web app entirely in Python, making it easy to load our saved model and create custom UI elements like sliders and charts.

---

### **Step 3.2: Building the Streamlit Dashboard**

* **The Goal:** To create a multi-faceted dashboard that serves different user needs: exploration, prediction, and planning.

* **The "Why" (Thinking Process):** A good data product does more than just report historical facts. It helps users make future decisions. Our dashboard will have three key functions:
    1.  **Explore:** Let users see historical trends on their own.
    2.  **Predict:** Give users a specific forecast and, crucially, the *reasons* for it (using SHAP).
    3.  **Plan:** Allow users to simulate scenarios ("What would happen to my yield if rainfall was 20% lower?") This turns the dashboard into a strategic tool.

* **Key Code Concepts (in `scripts/dashboard.py`):**
    ```python
    import streamlit as st
    import pandas as pd
    import joblib

    # Load the pre-trained model
    model = joblib.load('yield_model.pkl')

    st.title('Crop Yield Prediction Dashboard')

    # --- UI for user input ---
    state = st.selectbox('Select State:', ['Maharashtra', 'Punjab', ...])
    # ... more selectboxes for district, crop, etc.

    # --- "What-If" Scenario Sliders ---
    st.sidebar.header('Scenario Analysis')
    rainfall_slider = st.sidebar.slider('Adjust Rainfall (%)', -50, 50, 0)
    # ... more sliders for other key features

    # --- Make Prediction ---
    # 1. Get base features for the selected district
    # 2. Adjust features based on slider values
    # 3. Feed the adjusted features to the model
    # prediction = model.predict(input_features)
    # st.metric("Predicted Yield (kg/ha)", f"{prediction[0]:.2f}")

    # --- Display SHAP explanation for the prediction ---
    # (This is more advanced but involves calling the SHAP library)
    ```

---

### **Step 3.3: Deployment with Docker (Advanced)**

* **The Goal:** To package our entire application (code, model, dependencies) into a single, portable container that can run anywhere.

* **The "Why" (Thinking Process):** This is the final step to true reproducibility. A Docker container guarantees that the application will run the same way on a colleague's laptop, a cloud server, or any other machine, eliminating dependency headaches forever.

* **Key Commands:**
    ```bash
    # 1. Create a 'Dockerfile' in the root project directory (a text file with instructions)
    # Example content for Dockerfile:
    # FROM python:3.9-slim
    # WORKDIR /app
    # COPY requirements.txt .
    # RUN pip install -r requirements.txt
    # COPY . .
    # CMD ["streamlit", "run", "scripts/dashboard.py"]

    # 2. Build the Docker image from the Dockerfile
    docker build -t crop-yield-app .

    # 3. Run the application inside a container
    docker run -p 8501:8501 crop-yield-app
    ```

    Of course. Let's walk through the initial project setup phase step-by-step. This guide is designed to be a "follow-along" tutorial, explaining the thinking behind each action and providing the exact commands you'll need.

### **Project Kickstart: Setting Up Your Professional Data Science Environment**

#### **1. The 'Why' - Our Goal for This Phase**

Before we write a single line of analysis code, we need to build a solid foundation. The goal here is **reproducibility and organization**. We want to create a project environment that you or anyone else can set up with a few simple commands. This prevents future headaches like "it works on my machine but not yours" and keeps our project files from becoming a tangled mess.

#### **2. Your Toolkit**

  * **Visual Studio Code (VS Code):** A powerful, free code editor.
  * **A Terminal:** (This is built into VS Code, or you can use your system's default like Terminal on Mac/Linux or PowerShell/WSL on Windows).
  * **Python:** Make sure you have Python 3.8 or newer installed on your system.

-----

### **3. Step-by-Step Setup Guide**

#### **Step 3.1: Create the Project Directory Structure**

First, we'll create the folders that will hold all our project files.

  * **Open your terminal** and navigate to where you want to store your project (e.g., your Desktop or Documents folder).
  * Run the following commands one by one:

<!-- end list -->

```bash
# Create the main project folder and move into it
mkdir crop_yield_project
cd crop_yield_project

# Create the sub-folders for organization
mkdir data scripts notebooks
```

  * **The "Why":**
      * `data/`: Will hold all our data files (raw CSVs, our SQLite database).
      * `scripts/`: For reusable Python scripts, like our ETL pipeline and the final dashboard app.
      * `notebooks/`: For exploratory data analysis (EDA) and model development using Jupyter Notebooks.

#### **Step 3.2: Open the Project in VS Code**

Now, let's open our newly created project folder in VS Code.

  * While still inside the `crop_yield_project` directory in your terminal, run:

<!-- end list -->

```bash
code .
```

  * This command opens the entire current folder (`.`) in VS Code. You should now see your empty `data`, `scripts`, and `notebooks` folders in the Explorer panel on the left.

#### **Step 3.3: Set Up the Python Virtual Environment (`venv`)**

This is the most critical step for managing dependencies. We will create a self-contained Python environment *inside* our project folder.

  * **Open the integrated terminal in VS Code** (View -\> Terminal, or `Ctrl+` \`).
  * Run this command to create the virtual environment. We'll name it `venv`:

<!-- end list -->

```bash
python3 -m venv venv
```

  * You will see a new `venv` folder appear in your VS Code Explorer.
  * **Activate the Environment:**
      * On **Mac/Linux**: `source venv/bin/activate`
      * On **Windows (PowerShell)**: `.\venv\Scripts\Activate.ps1`
  * After activating, you should see `(venv)` appear at the beginning of your terminal prompt. This confirms you are now working inside the virtual environment.
  * **VS Code Integration:** The first time you open a `.py` file, VS Code's Python extension (which you should have installed) will likely detect the `venv` and ask if you want to use it for this workspace. **Click "Yes."** You can always verify or change this by looking at the Python interpreter version in the bottom-right corner of the VS Code window. It should point to your project's `venv`.

#### **Step 3.4: Create Initial Project Files**

Let's create the empty files we'll need, so our project has a clear skeleton.

  * In the VS Code terminal (make sure your `venv` is still active), run these commands:

<!-- end list -->

```bash
# Create a .gitignore file to ignore the venv and other clutter
touch .gitignore

# Create a file to list our dependencies
touch requirements.txt

# Create our main ETL script
touch scripts/etl.py

# Create our main dashboard script
touch scripts/dashboard.py

# Create our first exploratory notebook
touch notebooks/01_Data_Exploration.ipynb
```

  * **The "Why":**
      * `.gitignore`: Tells Git (version control) which files to ignore. We never want to commit our `venv` folder.
      * `requirements.txt`: A list of all Python packages our project needs. This is the key to sharing our project.
      * The other files are placeholders that we will fill in as we build the project.

#### **Step 3.5: Manage Dependencies (Best Practices)**

Now, let's populate our `requirements.txt` and install our starting packages.

  * **Open `requirements.txt`** in VS Code and add the following lines:

<!-- end list -->

```
# Core libraries for data manipulation and database interaction
pandas
sqlalchemy

# For exploratory notebooks
jupyterlab
notebook

# For data acquisition
requests

# Add other libraries as we need them
```

  * **Now, install everything from this file** by running this command in your active `venv` terminal:

<!-- end list -->

```bash
pip install -r requirements.txt
```

  * **Best Practice Workflow:** From now on, whenever you need a new package (e.g., `streamlit`), you should:
    1.  Install it: `pip install streamlit`
    2.  **Immediately update `requirements.txt`** to reflect the change: `pip freeze > requirements.txt`
        This command "freezes" the current state of your environment and saves it to the file.

#### **Step 3.6: Set Up the SQLite Database**

  * **The "Why":** SQLite is a server-less database that is stored in a single file. It's perfect for projects like this. Creating the database is as simple as creating a file.
  * Our `etl.py` script will eventually create and populate this file automatically, but for now, we can create an empty placeholder. In your terminal, run:

<!-- end list -->

```bash
touch data/agriculture.db
```

  * **Viewing the Database in VS Code (Highly Recommended):**
    1.  Go to the **Extensions** tab in VS Code (the icon with four squares).
    2.  Search for and install the extension named **"SQLite"** (Publisher: alexcvzz).
    3.  After installation, go back to your Explorer panel. Right-click on your `data/agriculture.db` file and select **"Open Database"**.
    4.  A new **"SQLITE EXPLORER"** panel will appear on the left, showing your database. For now, it will be empty, but this is how you will visually inspect your tables once the ETL script runs.

-----

### **4. Verification & Debugging - "Is it working?"**

Let's do a quick check to make sure everything is set up correctly.

1.  **Is your `venv` active?** Your terminal prompt should start with `(venv)`. If not, run the activation command again.
2.  **Is VS Code using the right Python?** Look at the bottom-right corner of VS Code. It should say something like "Python 3.x.x ('venv': venv)". If not, click on it and select the interpreter from your project's `venv` folder.
3.  **Are the packages installed?** In your `venv` terminal, type `pip list`. You should see `pandas`, `sqlalchemy`, etc., in the list.
      * **Common Bug:** `ModuleNotFoundError`. If you run a script and get this error, it's almost always because either a) you forgot to install the package, or b) you are running the script with the wrong Python interpreter (your global Python instead of your project's `venv`).
4.  **Can you see the database?** Check that the "SQLITE EXPLORER" panel is visible and shows your `agriculture.db` file.

-----

### **5. What Your Project Looks Like Now**

If you've followed all the steps, your project folder in VS Code should look exactly like this:

```
crop_yield_project/
├── .gitignore
├── data/
│   └── agriculture.db
├── notebooks/
│   └── 01_Data_Exploration.ipynb
├── requirements.txt
├── scripts/
│   ├── dashboard.py
│   └── etl.py
└── venv/
    ├── bin/
    ├── include/
    └── lib/
```

You are now perfectly set up to start the next phase: sourcing data and building the ETL pipeline.

Of course. My last message was a detailed, step-by-step tutorial for this exact starting phase. Let's walk through it together as a "follow-along" guide.

I'll break down the thinking process and the commands from that guide again.

### **Project Kickstart: A Follow-Along Guide to Your Data Science Environment**

#### **1. The Big Picture: Why are we doing this?**

Before we even think about data, our primary goal is to build a clean, organized, and reproducible workspace. Think of it like a chef preparing their kitchen before they start cooking. A clean setup prevents confusion and ensures that if you share your project with someone, they can run it without any issues.

#### **2. Your Tools**

  * **VS Code:** Our code editor, our "kitchen."
  * **Terminal:** The command line, how we give instructions to the computer. We'll use the one built into VS Code.
  * **Python:** The programming language we'll be using.

-----

### **Let's Start: Step-by-Step Setup**

#### **Step 1: Create Your Project's "House"**

We need a dedicated folder for our project.

1.  Open your computer's main terminal (for now, not the one in VS Code).

2.  Navigate to a place you like to store projects, like your `Documents` folder.

3.  Run these commands one by one:

    ```bash
    # This command creates our main project folder
    mkdir crop_yield_project

    # This command moves you inside that new folder
    cd crop_yield_project

    # This creates the "rooms" inside our house for organization
    mkdir data scripts notebooks
    ```

      * **`data/`** is for all data files.
      * **`scripts/`** is for reusable Python code.
      * **`notebooks/`** is for experiments and analysis.

#### **Step 2: Open the Project in VS Code**

Now, let's open our new "house" in our editor.

1.  In the same terminal window (while you're inside `crop_yield_project`), type:

    ```bash
    code .
    ```

2.  This command tells VS Code to open the current folder (`.`). VS Code will launch, and you'll see your folders on the left.

#### **Step 3: Create a "Bubble" for Our Project (The Virtual Environment)**

This is the most important step for avoiding future problems. We'll create a self-contained Python "bubble" (`venv`) that holds all the specific packages for *this project only*.

1.  In VS Code, open the integrated terminal (`View` \> `Terminal` or `Ctrl+` \`).

2.  Run this command to create the environment named `venv`:

    ```bash
    python3 -m venv venv
    ```

3.  You'll see a new `venv` folder appear. Now, we need to "step inside" this bubble to activate it:

      * **On Mac/Linux:** `source venv/bin/activate`
      * **On Windows:** `.\venv\Scripts\Activate.ps1`

4.  Once it's active, your terminal prompt will change to show `(venv)` at the beginning. This is your confirmation that the bubble is active.

5.  **VS Code Helper:** VS Code is smart. It will likely show a pop-up asking if you want to use the Python interpreter from your new `venv`. **Click "Yes"**. This ensures that when you run Python code, it uses the Python inside your bubble, not your computer's main Python.

#### **Step 4: Create the Initial Files**

Let's create the empty files we'll be working with.

1.  In your active `(venv)` terminal in VS Code, run these `touch` commands:

    ```bash
    touch .gitignore
    touch requirements.txt
    touch scripts/etl.py
    touch scripts/dashboard.py
    touch notebooks/01_Data_Exploration.ipynb
    ```

#### **Step 5: Install Our Tools (Dependencies)**

Now we'll install the Python libraries we need. The best practice is to list them in `requirements.txt` first.

1.  Open the `requirements.txt` file in VS Code and paste this in:

    ```
    # Core libraries for data manipulation and database interaction
    pandas
    sqlalchemy

    # For exploratory notebooks
    jupyterlab
    notebook

    # For downloading data
    requests
    ```

2.  Now, in your `(venv)` terminal, run this command to install everything listed in that file:

    ```bash
    pip install -r requirements.txt
    ```

**Best Practice:** Later, if you need a new package (like `streamlit`), you should:

1.  Run `pip install streamlit`.
2.  **Immediately** run `pip freeze > requirements.txt` to update your list with the new package and its version.

#### **Step 6: Set Up the Database**

We'll use SQLite, which is just a single file. Our Python script will create and manage it later, but we can make the empty file now and set up VS Code to view it.

1.  In your terminal, create the empty database file:

    ```bash
    touch data/agriculture.db
    ```

2.  **To see the data inside VS Code:**

      * Go to the **Extensions** tab on the left.
      * Search for and install the **"SQLite"** extension by alexcvzz.
      * Go back to the Explorer, right-click on `data/agriculture.db`, and choose **"Open Database"**.
      * A new **SQLITE EXPLORER** panel will appear. This is where you'll see your data tables later.

-----

### **How to Debug if Things Go Wrong**

  * **Problem: `command not found: python3` or `pip`**

      * **Cause:** Python isn't installed correctly on your system or isn't in your system's PATH.
      * **Fix:** Reinstall Python from the official website, making sure to check the box that says "Add Python to PATH" during installation.

  * **Problem: `ModuleNotFoundError: No module named 'pandas'`**

      * **Cause:** This is the most common error. It means you're running your script with the wrong Python. Your `venv` "bubble" is likely not active, or VS Code is not using it.
      * **Fix:**
        1.  Check your terminal. Does it say `(venv)` at the start? If not, run the activation command again.
        2.  Check the bottom-right corner of VS Code. Does it point to the Python inside your `venv`? If not, click it and select the correct one.
        3.  Run `pip install -r requirements.txt` again just in case.

  * **Problem: `Permission Denied` when activating venv on Windows.**

      * **Cause:** Your system's security policy is blocking scripts from running.
      * **Fix:** Open PowerShell as an Administrator and run `Set-ExecutionPolicy Unrestricted`. Then close it and try again in the regular VS Code terminal.

Your project is now perfectly set up and ready for the next phase: acquiring the data and building the ETL script.