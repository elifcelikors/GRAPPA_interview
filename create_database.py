import sqlite3
import pandas as pd

# Code Outline 
## (1) Set up a relational (SQLite) database
## (2) Set up the tables in the SQLite databse
### (a) Create the Visual_Features table
### (b) Create the Ratings table
## (3) Hierarchical tagging 

# Set up SQLite database
conn = sqlite3.connect("grappa_demo.db")
cursor = conn.cursor()

# Load CSV files
visual_features_df = pd.read_csv("/Users/field-admin/Library/CloudStorage/OneDrive-CornellUniversity/Desktop/SID_visualFeatures.csv")
ratings_df = pd.read_csv("/Users/field-admin/Library/CloudStorage/OneDrive-CornellUniversity/Desktop/self.csv")

############ VISUAL FEATURES ############
cursor.execute("DROP TABLE IF EXISTS Visual_Features;")  # Deletes the old table (this becomes necessary when the script is ran multiple times with some changes)
conn.commit()

# Create the Visual_Features Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Visual_Features (
    Image_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    image_name TEXT,
    hue REAL,
    sat REAL,
    bright REAL,
    ED REAL,
    entropy REAL,
    sdHue REAL,
    sdSat REAL,
    sdBright REAL
);
""")

# Insert Data into Visual_Features Table
for _, row in visual_features_df.iterrows():
    cursor.execute("""
        INSERT INTO Visual_Features (image_name, hue, sat, bright, ED, entropy, sdHue, sdSat, sdBright)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (row["image_name"], row["hue"], row["sat"], 
          row["bright"], row["ED"], row["entropy"], 
          row["sdHue"], row["sdSat"], row["sdBright"]))


############ RATINGS TABLE ############
cursor.execute("DROP TABLE IF EXISTS Ratings")  # Deletes the old table
conn.commit()

# Create the Ratings Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Ratings (
    image_name TEXT PRIMARY KEY,
    Avg_Rating REAL
);
""")

# Insert Data from ratings_df into Ratings Table
for _, row in ratings_df.iterrows():
    cursor.execute("""
        INSERT INTO Ratings (image_name, Avg_Rating)
        VALUES (?, ?)
    """, (row["image_name"], row["Avg_Rating"]))

# Commit and close
conn.commit()
conn.close()

print("✅ Database successfully created and populated!")


################################################
############# HIERARCHICAL TAGGING #############
################################################
conn = sqlite3.connect("grappa_demo.db")
cursor = conn.cursor()
################# Define tags with hierarchical structure #################
tags = [
    ("Abstract", None), ("Landscape", None), ("Portrait", None),("Still life", None),  
    ("Surreal", "Abstract"), ("Cubist", "Abstract"), ("Impressionist", "Abstract"),  
    ("Nature", "Landscape"), ("Urban", "Landscape"), 
    ("High Saturation", None),  
    ("Beautiful", None), ("Complex", None), ("Calm", None), ("Exciting", None)
    ]
conn.commit()

################## Create Tags table #################
cursor.execute("DROP TABLE IF EXISTS Tags")  # Deletes the old table
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_name TEXT UNIQUE NOT NULL,
    parent_tag_id INTEGER,
    FOREIGN KEY (parent_tag_id) REFERENCES Tags(tag_id)
);
""")

cursor.execute("DROP TABLE IF EXISTS Image_Tags")  # Deletes the old table
conn.commit()
# Create Image_Tags table (many-to-many relationship)
cursor.execute("""
CREATE TABLE IF NOT EXISTS Image_Tags (
    image_name TEXT,
    tag_id INTEGER,
    PRIMARY KEY (image_name, tag_id),
    FOREIGN KEY (image_name) REFERENCES Images(image_name),
    FOREIGN KEY (tag_id) REFERENCES Tags(tag_id)
);
""")
conn.commit()
print("✅ Tables created successfully!")

##################  Insert tags and maintain hierarchy #################
for tag, parent in tags:
    if parent:
        cursor.execute("SELECT tag_id FROM Tags WHERE tag_name=?", (parent,))
        parent_id = cursor.fetchone()
        parent_id = parent_id[0] if parent_id else None
    else:
        parent_id = None
    cursor.execute("INSERT OR IGNORE INTO Tags (tag_name, parent_tag_id) VALUES (?, ?);", (tag, parent_id))

conn.commit()
print("✅ Tags inserted successfully!")


# assign tags to images
image_tags = [
    ("image1.jpg", "Impressionist"),
    ("image2.jpg", "Surreal"),
    ("image3.jpg", "Abstract"),
]

for image_name, tag_name in image_tags:
    # Get the tag_id for the given tag name
    cursor.execute("SELECT tag_id FROM Tags WHERE tag_name=?", (tag_name,))
    tag_id = cursor.fetchone()

    if tag_id:
        cursor.execute("INSERT INTO Image_Tags (image_name, tag_id) VALUES (?, ?);", (image_name, tag_id[0]))

conn.commit()
print("✅ Image-Tag relationships added successfully!")
conn.close()