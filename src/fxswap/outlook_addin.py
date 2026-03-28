import win32com.client
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

def fetch_emails():
    """Fetch emails from the Inbox folder."""
    outlook = win32com.client.Dispatch("Outlook.Application")
    namespace = outlook.GetNamespace("MAPI")
    inbox = namespace.GetDefaultFolder(6)  # 6 refers to the Inbox folder
    emails = []
    for item in inbox.Items:
        if item.Class == 43:  # 43 refers to MailItem
            emails.append({
                "subject": item.Subject,
                "received_time": item.ReceivedTime,
                "entry_id": item.EntryID
            })
    return emails, inbox

def move_email(entry_id, inbox):
    """Move an email to a predefined folder."""
    try:
        # Prompt user for folder name
        folder_name = simpledialog.askstring("Move Email", "Enter the folder name to move the email:")
        if not folder_name:
            messagebox.showinfo("Cancelled", "No folder name provided. Operation cancelled.")
            return

        # Find or create the folder
        target_folder = None
        for folder in inbox.Folders:
            if folder.Name.lower() == folder_name.lower():
                target_folder = folder
                break

        if not target_folder:
            target_folder = inbox.Folders.Add(folder_name)

        # Find the email by EntryID and move it
        mail_item = inbox.Items.Find(f"[EntryID] = '{entry_id}'")
        if mail_item:
            mail_item.Move(target_folder)
            messagebox.showinfo("Success", f"Email moved to '{folder_name}'.")
        else:
            messagebox.showerror("Error", "Email not found.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def create_gui():
    """Create the GUI to display emails and provide move buttons."""
    emails, inbox = fetch_emails()

    root = tk.Tk()
    root.title("Outlook Email Organizer")

    # Create a treeview to display emails
    tree = ttk.Treeview(root, columns=("Subject", "Received Time", "Action"), show="headings")
    tree.heading("Subject", text="Subject")
    tree.heading("Received Time", text="Received Time")
    tree.heading("Action", text="Action")
    tree.column("Subject", width=300)
    tree.column("Received Time", width=150)
    tree.column("Action", width=100)

    # Populate the treeview with emails
    for email in emails:
        tree.insert("", "end", values=(email["subject"], email["received_time"], "Move"))

    tree.pack(fill="both", expand=True)

    # Add a button to move the selected email
    def on_move_button_click():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select an email to move.")
            return

        # Get the EntryID of the selected email
        item_values = tree.item(selected_item[0], "values")
        subject = item_values[0]
        for email in emails:
            if email["subject"] == subject:
                move_email(email["entry_id"], inbox)
                break

    move_button = tk.Button(root, text="Move Selected Email", command=on_move_button_click)
    move_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
