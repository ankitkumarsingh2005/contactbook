import streamlit as st
import requests
import time
import re

API_URL = "https://contactbook-ide6.onrender.com"


st.title("📒 Contact Management App")

# -------------------------
# Session state management
# -------------------------
if "token" not in st.session_state:
    st.session_state["token"] = None
if "reset_form" not in st.session_state:
    st.session_state["reset_form"] = False

# -------------------------
# Sidebar Login/Register
# -------------------------
st.sidebar.title("🔐 Login")

if st.session_state["token"] is None:
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        res = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
        if res.status_code == 200:
            st.session_state["token"] = res.json()["access_token"]
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.sidebar.error("Login failed.")

    with st.sidebar.expander("🆕 Register"):
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        if st.button("Register"):
            res = requests.post(f"{API_URL}/register", json={"username": new_username, "password": new_password})
            if res.status_code == 200:
                st.success("Registered successfully! Please login.")
            else:
                st.error(res.json().get("detail", "Registration failed."))
else:
    st.sidebar.success("Logged in ✅")
    if st.sidebar.button("Logout"):
        st.session_state["token"] = None
        st.rerun()

# -------------------------
# Auth Header for API calls
# -------------------------
def auth_header():
    return {"Authorization": f"Bearer {st.session_state['token']}"}



if st.session_state["token"]:
    if st.session_state.get("reset_form", False):
        st.session_state["name_input"] = ""
        st.session_state["email_input"] = ""
        st.session_state["contact_input"] = ""
        st.session_state["reset_form"] = False

# Utility to validate email
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Fetch users
def get_contact():
    res = requests.get(f"{API_URL}/contacts/", headers=auth_header())
    if res.status_code == 200:
        return res.json()
    else:
        st.error("Failed to fetch contacts.")
        return []


# Create user
def create_contact(name, email, contact):
    return requests.post(
        f"{API_URL}/contacts/",
        json={"name": name, "email": email, "contact": contact},
        headers=auth_header()
    )


# Update user
def update_contact(contact_id, name, email, contact):
    return requests.put(
        f"{API_URL}/contacts/{contact_id}",
        json={"name": name, "email": email, "contact": contact},
        headers=auth_header()
    )


# Delete user
def delete_contact(contact_id):
    return requests.delete(
        f"{API_URL}/contacts/{contact_id}",
        headers=auth_header()
    )


# Initialize session state for form inputs
if "name" not in st.session_state:
    st.session_state["name"] = ""
if "email" not in st.session_state:
    st.session_state["email"] = ""
if "contact" not in st.session_state:
    st.session_state["contact"] = ""
if "reset_form" not in st.session_state:
    st.session_state["reset_form"] = False


# -------------------
# Add New User Expander
# -------------------
with st.expander("➕ Add New Contact"):
    with st.form("insert_form"):
        name = st.text_input("Name", value=st.session_state["name"], key="name_input")
        email = st.text_input("Email", value=st.session_state["email"], key="email_input")
        contact = st.text_input("Contact", value=st.session_state["contact"], key="contact_input")
        submitted = st.form_submit_button("Add Contact")

        if submitted:
            if not name or not email or not contact:
                st.error("All fields are required.")
                time.sleep(2)
                st.rerun()
            elif not is_valid_email(email):
                st.error("Invalid email format.")
                time.sleep(2)
                st.rerun()
            else:
                response = create_contact(name, email, contact)
                if response.status_code == 200:

                    st.session_state["reset_form"] = True

                    st.success("Contact added successfully!")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(response.json().get("detail", "Error adding user."))
                    time.sleep(2)
                    st.rerun()

# -------------------
# Show User List
# -------------------
st.subheader("📋 Contact List")
users = get_contact()
for user in users:
    if user and 'name' in user:
        with st.expander(f"{user['name']}"):
            st.write(f"**Email**: {user['email']}")
            st.write(f"**Contact**: {user['contact']}")

            # Delete button
            if st.button(f"Delete {user['name']}", key=f"del_{user['id']}"):
                delete_contact(user["id"])
                st.success("Contact deleted.")
                time.sleep(1)
                st.rerun()

            # Update Form inside expander
            st.markdown("✏️ Update Contact")
            with st.form(f"update_form_{user['id']}"):
                new_name = st.text_input("Name", user["name"], key=f"name_{user['id']}")
                new_email = st.text_input("Email", user["email"], key=f"email_{user['id']}")
                new_contact = st.text_input("Contact", user["contact"], key=f"contact_{user['id']}")
                update_btn = st.form_submit_button("Update")

                if update_btn:
                    if not new_name or not new_email or not new_contact:
                        st.error("All fields are required.")
                        time.sleep(2)
                        st.rerun()
                    elif not is_valid_email(new_email):
                        st.error("Invalid email format.")
                        time.sleep(2)
                        st.rerun()
                    else:
                        update_contact(user["id"], new_name, new_email, new_contact)
                        st.success("Contact updated.")
                        time.sleep(2)
                        st.rerun()
    else:
        st.warning("User information is missing or incomplete.")