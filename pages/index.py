import os
import streamlit as st

# Get the current directory and list the files in it
dir_path = os.path.dirname(os.path.realpath(__file__))
files = os.listdir(dir_path)

# Check if the requested page exists, default to index if not found
requested_page = st.experimental_get_query_params().get("page", ["index"])[0]
if requested_page + ".py" not in files:
    st.write(f"You have requested page /{requested_page}, but no corresponding file was found in the app's pages/ directory.")
    st.write("Defaulting to app's main page.")
    requested_page = "index"

# Import and run the requested page
if requested_page == "index":
    app_func = st.sidebar.write
else:
    module = __import__("pages." + requested_page, fromlist=["app"])
    app_func = module.app

# Display the app
app_func()



