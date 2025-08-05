# Crop Yield Production & Analysis Project\scripts\etl.py
import pandas as pd # Our master chef for handling data tables 
import sqlite3 as sq # The manager of our SQLite database 
import os # The helpful assistant who knows all the file paths

cwd= os.getcwd()
db_path= os.path.join(cwd, 'data','agriculture.db')
crop_data_path= os.path.join(cwd, 'data', 'csv data', 'raw', 'area_production_yield_data.csv')
normal_rainfall_path= os.path.join(cwd, 'data', 'csv data', 'raw', 'normal_rainfall_data.csv')
monthly_rainfall_path= os.path.join(cwd, 'data', 'csv data', 'raw', 'monthly_rainfall_data.csv')

def clean_data(df):
    # First, let's fix those messy column names
    # 'District Name' becomes 'district_name', much tidier
    df.columns=df.columns.str.lower().str.replace(' ','_')
    # Now, let's hunt for missing values (NaNs), the ghosts in our data machine 
    # A simple strategy: if a number is missing, we'll assume it's 0 
    # If text is missing, we'll label it 'Unknown'
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col]=df[col].fillna(0)
        else:
            # For text columns, we'll also strip any sneaky whitespace from the edges
            df[col]=df[col].astype(str).str.strip()
            df[col]=df[col].fillna('Unknown')
    return df

def main():
    print("--- Starting The Great Data Bake-Off! ---")
    
    #EXTRACT
    print("Step 1: Reading the raw, lumpy ingredients (CSVs)...")
    try:
        crop_df=pd.read_csv(crop_data_path)
        normal_rainfall_df=pd.read_csv(normal_rainfall_path)
        monthly_rainfall_df=pd.read_csv(monthly_rainfall_path)
        print("Successfully loaded CSVs. They smell... raw.")
    except FileNotFoundError as e:
        print(f"🚨HEY! I couldn't find a file. Error: {e}")
        print("Did you rename the CSVs and put them in the 'data/' folder? Go check!")
        return # Stop the script if we can't find the files

    #TRANSFORM
    print("Step 2: Cleaning, chopping, and mixing (Transforming Data)...")
    crop_df_clean=clean_data(crop_df.copy())
    normal_df_clean=clean_data(normal_rainfall_df.copy())
    monthly_rainfall_clean=clean_data(monthly_rainfall_df.copy())
    print("Data is now pretty clean.")
    
    #LOAD
    print("Step 3: Putting the cake in the oven (Loading to Database)...") 
    try:
        # 'with' is a magic word in Python that handles opening and closing things for us
        with sq.connect(db_path) as conn:
            # We're telling pandas to take our clean DataFrame and dump it into an SQL table. 
            # if_exists='replace' is like smashing your old cake to bake a new one. 
            # Great for development, TERRIFYING in production. Use with caution! 
            crop_df_clean.to_sql('crop_production', conn, if_exists = 'replace', index = False)
            normal_df_clean.to_sql('normal_rainfall', conn, if_exists = 'replace', index = False)
            monthly_rainfall_clean.to_sql('monthly_rainfall', conn, if_exists = 'replace', index = False)
            print("Ding! Cake is ready. Data loaded into the database.")
    except Exception as e:
        print(f"🔥Whoops, something went wrong while baking. Error: {e}")
        return
        
    print("--- ETL Pipeline Complete. Bon Appétit! ---")
    # This little piece of magic makes sure main() only runs when you execute this file directly.
    # It's like the 'On' button for our script.
if __name__ == '__main__':
    main()