import csv
import json
import webbrowser
import time
from datetime import datetime, timedelta
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from plyer import notification
import winsound
from PIL import Image, ImageTk
import sv_ttk
import random

# Royal Configuration
CONFIG_FILE = 'princess_config.json'
LOG_FILE = 'royal_decrees.txt'
DEFAULT_CSV = 'royal_schedule.csv'

class RoyalPrincessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("👑✨ Princess Lailan's Royal Meeting Chambers ✨👑")
        self.root.geometry("1000x750")
        self.root.minsize(900, 650)
        
        # Royal-Feminine Color Palette
        self.royal_mauve = "#8B668B"
        self.blush_pink = "#FFB6C1"
        self.gold_leaf = "#D4AF37"
        self.ivory_white = "#FFFFF0"
        self.rose_gold = "#B76E79"
        
        # Load config
        self.config = self.load_config()
        
        # Setup Luxurious UI
        self.setup_royal_chamber()
        
        # Initialize variables
        self.running = False
        self.meetings = []
        self.upcoming_meetings = []
        self.load_meetings()
        
        # Start royal attendant
        self.attendant_thread = None
        
        # Set theme
        sv_ttk.set_theme("light")
        self.apply_royal_glamour()
        
        # Play royal announcement
        self.play_royal_sound("announcement")

    def setup_royal_chamber(self):
        """Create the royal meeting chamber interface"""
        # Create luxurious background
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.draw_royal_pattern()
        
        # Main chamber frame
        self.chamber_frame = ttk.Frame(self.canvas, style='Chamber.TFrame')
        self.canvas.create_window((25, 25), window=self.chamber_frame, anchor="nw")
        
        # Royal header with tiara
        header_frame = ttk.Frame(self.chamber_frame, style='Header.TFrame')
        header_frame.pack(fill=tk.X, pady=(10, 15))
        
        # Tiara icons
        self.tiara_img = self.load_image("tiara.png", (50, 25))
        if self.tiara_img:
            ttk.Label(header_frame, image=self.tiara_img, style='Jewel.TLabel').pack(side=tk.LEFT)
        
        # Glittering title
        title_label = ttk.Label(
            header_frame, 
            text="💎  Princess Lailan's Royal Scheduler  💎", 
            font=('Monotype Corsiva', 24),
            style='Title.TLabel'
        )
        title_label.pack(side=tk.LEFT, padx=15)
        
        if self.tiara_img:
            ttk.Label(header_frame, image=self.tiara_img, style='Jewel.TLabel').pack(side=tk.LEFT)
        
        # Jewel-encrusted control buttons
        control_frame = ttk.Frame(self.chamber_frame, style='Control.TFrame')
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        button_style = 'RoyalButton.TButton'
        self.start_btn = ttk.Button(
            control_frame, 
            text="🌟 Begin Court", 
            command=self.start_service,
            style=button_style
        )
        self.start_btn.pack(side=tk.LEFT, padx=7)
        
        ttk.Button(
            control_frame, 
            text="📜 Issue Invitation", 
            command=self.add_meeting_dialog,
            style=button_style
        ).pack(side=tk.LEFT, padx=7)
        
        ttk.Button(
            control_frame, 
            text="🗂️ Import Scroll", 
            command=self.import_csv,
            style=button_style
        ).pack(side=tk.LEFT, padx=7)
        
        ttk.Button(
            control_frame, 
            text="💍 Settings", 
            command=self.open_settings,
            style=button_style
        ).pack(side=tk.LEFT, padx=7)
        
        # Royal meeting scroll
        self.setup_royal_scroll()
        
        # Status throne
        self.status_var = tk.StringVar(value="Your Royal Highness' court is awaiting commands...")
        status_bar = ttk.Label(
            self.chamber_frame, 
            textvariable=self.status_var,
            style='Throne.TLabel'
        )
        status_bar.pack(fill=tk.X, pady=(15, 0))

    def setup_royal_scroll(self):
        """Create the royal meetings scroll"""
        scroll_frame = ttk.Frame(self.chamber_frame, style='Chamber.TFrame')
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview with scrollbars
        scroll_y = ttk.Scrollbar(scroll_frame, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(scroll_frame, orient=tk.HORIZONTAL)
        
        self.meetings_table = ttk.Treeview(
            scroll_frame,
            columns=('time', 'link', 'status'),
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            selectmode='browse',
            style='Royal.Treeview'
        )
        
        scroll_y.config(command=self.meetings_table.yview)
        scroll_x.config(command=self.meetings_table.xview)
        
        # Configure columns
        self.meetings_table.heading('time', text='Royal Hour', anchor=tk.W)
        self.meetings_table.heading('link', text='Throne Room Link', anchor=tk.W)
        self.meetings_table.heading('status', text='Decree Status', anchor=tk.W)
        
        self.meetings_table.column('time', width=120, stretch=False)
        self.meetings_table.column('link', width=450)
        self.meetings_table.column('status', width=150, stretch=False)
        
        # Pack everything
        self.meetings_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Add royal context menu
        self.setup_royal_menu()

    def setup_royal_menu(self):
        """Setup right-click royal decree menu"""
        self.royal_menu = tk.Menu(self.root, tearoff=0, bg=self.blush_pink, fg='black')
        self.royal_menu.add_command(
            label="🦚 Attend Now", 
            command=self.join_selected_meeting
        )
        self.royal_menu.add_command(
            label="✏️ Edit Decree", 
            command=self.edit_meeting_dialog
        )
        self.royal_menu.add_command(
            label="🗑️ Rescind Invitation", 
            command=self.delete_meeting
        )
        self.royal_menu.add_separator()
        self.royal_menu.add_command(
            label="📋 Copy Scroll", 
            command=self.copy_meeting_link
        )
        
        self.meetings_table.bind(
            "<Button-3>", 
            self.show_royal_menu
        )

    def show_royal_menu(self, event):
        """Show royal context menu"""
        item = self.meetings_table.identify_row(event.y)
        if item:
            self.meetings_table.selection_set(item)
            self.royal_menu.post(event.x_root, event.y_root)

    def apply_royal_glamour(self):
        """Apply luxurious royal-feminine styling"""
        style = ttk.Style()
        
        # Chamber styles
        style.configure('Chamber.TFrame',
                      background=self.ivory_white,
                      bordercolor=self.gold_leaf)
        
        # Header styles
        style.configure('Header.TFrame',
                      background=self.royal_mauve)
        
        style.configure('Title.TLabel',
                      foreground=self.gold_leaf,
                      background=self.royal_mauve,
                      font=('Monotype Corsiva', 24))
        
        style.configure('Jewel.TLabel',
                      foreground=self.gold_leaf,
                      background=self.royal_mauve)
        
        # Button styles
        style.configure('RoyalButton.TButton',
                      foreground="black",
                      background=self.blush_pink,
                      font=('Garamond', 11, 'bold'),
                      bordercolor=self.rose_gold,
                      focusthickness=3,
                      focuscolor=self.gold_leaf)
        
        style.map('RoyalButton.TButton',
                background=[('active', self.rose_gold)],
                foreground=[('active', 'white')])
        
        # Table styles
        style.configure('Royal.Treeview',
                      background=self.ivory_white,
                      foreground="black",
                      fieldbackground="#FDF5E6",
                      bordercolor=self.gold_leaf)
        
        style.configure('Throne.TLabel',
                      foreground=self.gold_leaf,
                      background=self.royal_mauve,
                      font=('Garamond', 10, 'italic'),
                      relief=tk.RIDGE,
                      borderwidth=3)

    def play_royal_sound(self, occasion):
        """Play appropriate royal sounds"""
        if not self.config['play_sound']:
            return
            
        try:
            if occasion == "announcement":
                winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
            elif occasion == "decree":
                for _ in range(3):
                    winsound.Beep(880, 100)
                    winsound.Beep(1046, 100)
            elif occasion == "alert":
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except:
            pass

    def draw_royal_pattern(self):
        """Draw luxurious background pattern"""
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        
        # Create gradient background
        for i in range(0, height, 5):
            r = min(255, int(139 + i/height*50))
            g = min(255, int(102 + i/height*30))
            b = min(255, int(139 + i/height*50))
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_line(0, i, width, i, fill=color)
        
        # Add decorative elements
        self.canvas.create_text(
            width-100, height-50,
            text="👑 Princess Lailan 👑",
            fill=self.gold_leaf,
            font=('Monotype Corsiva', 12)
        )

    def load_config(self):
        """Load or create royal configuration"""
        default_config = {
            'csv_path': DEFAULT_CSV,
            'notifications': True,
            'reminder_before': 5,
            'play_sound': True,
            'theme': 'light'
        }
        
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                return default_config
        else:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(default_config, f, indent=4)
            return default_config

    def save_config(self):
        """Save royal configuration"""
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=4)

    def load_meetings(self):
        """Load royal decrees from scroll"""
        try:
            with open(self.config['csv_path'], mode='r') as file:
                reader = csv.DictReader(file)
                self.meetings = [{
                    'time': row['Time'],
                    'link': row['Link'],
                    'status': 'Pending'
                } for row in reader]
                
            self.update_upcoming_meetings()
            self.update_meetings_table()
        except FileNotFoundError:
            messagebox.showerror(
                "Royal Error",
                f"Could not find royal scroll at {self.config['csv_path']}"
            )
        except Exception as e:
            messagebox.showerror(
                "Royal Error",
                f"Failed to read royal decrees: {str(e)}"
            )

    def update_upcoming_meetings(self):
        """Update list of upcoming royal gatherings"""
        now = datetime.now().strftime('%H:%M')
        today = datetime.now().date()
        
        self.upcoming_meetings = [
            m for m in self.meetings 
            if m['time'] >= now and m['status'] == 'Pending'
        ]
        
        # Sort by royal hour
        self.upcoming_meetings.sort(key=lambda x: x['time'])

    def update_meetings_table(self):
        """Update the royal scroll with current decrees"""
        self.meetings_table.delete(*self.meetings_table.get_children())
        
        for meeting in self.meetings:
            self.meetings_table.insert(
                '', 
                tk.END, 
                values=(
                    meeting['time'],
                    meeting['link'],
                    meeting['status']
                )
            )

    def start_service(self):
        """Begin royal court session"""
        if not self.running:
            self.running = True
            self.start_btn.config(text="🛑 Halt Court")
            self.status_var.set("The royal court is now in session...")
            
            self.attendant_thread = threading.Thread(
                target=self.monitor_royal_schedule,
                daemon=True
            )
            self.attendant_thread.start()
        else:
            self.running = False
            self.start_btn.config(text="🌟 Begin Court")
            self.status_var.set("Court is adjourned")

    def monitor_royal_schedule(self):
        """Monitor for royal gatherings"""
        while self.running:
            now = datetime.now().strftime('%H:%M')
            
            for meeting in self.meetings:
                if meeting['status'] == 'Pending' and meeting['time'] == now:
                    self.attend_royal_gathering(meeting)
                    meeting['status'] = 'Attended'
                    self.log_royal_decree(meeting)
                    self.update_meetings_table()
            
            # Check for royal reminders
            reminder_time = (datetime.now() + timedelta(minutes=5)).strftime('%H:%M')
            for meeting in self.meetings:
                if meeting['status'] == 'Pending' and meeting['time'] == reminder_time:
                    self.send_royal_reminder(meeting)
            
            time.sleep(30)  # Check every 30 seconds

    def attend_royal_gathering(self, meeting):
        """Attend a royal gathering"""
        try:
            webbrowser.open(meeting['link'])
            meeting['status'] = 'Attended'
            
            if self.config['play_sound']:
                self.play_royal_sound("decree")
            
            if self.config['notifications']:
                notification.notify(
                    title="👑 Royal Attendance",
                    message=f"Attended gathering at {meeting['time']}",
                    app_name="Princess Lailan's Scheduler",
                    timeout=10
                )
            
            self.status_var.set(f"Attended royal gathering at {meeting['time']}")
        except Exception as e:
            messagebox.showerror(
                "Royal Error",
                f"Failed to join gathering: {str(e)}"
            )

    def send_royal_reminder(self, meeting):
        """Send royal reminder"""
        if self.config['notifications']:
            notification.notify(
                title="⏰ Royal Reminder",
                message=f"Gathering at {meeting['time']} begins soon",
                app_name="Princess Lailan's Scheduler",
                timeout=10
            )
        
        if self.config['play_sound']:
            self.play_royal_sound("alert")

    def log_royal_decree(self, meeting):
        """Log royal attendance"""
        log_entry = {
            'time': meeting['time'],
            'link': meeting['link'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            # Append to royal log
            log_data = []
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, 'r') as f:
                    try:
                        log_data = json.load(f)
                    except:
                        pass
            
            log_data.append(log_entry)
            
            with open(LOG_FILE, 'w') as f:
                json.dump(log_data, f, indent=4)
            
            # Append to text log
            with open('royal_attendance.txt', 'a') as f:
                f.write(
                    f"{log_entry['timestamp']} - " +
                    f"Attended gathering at {meeting['time']}\n"
                )
        except Exception as e:
            print(f"Failed to log royal decree: {str(e)}")

    def add_meeting_dialog(self):
        """Create royal invitation dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("✉️ Royal Invitation")
        dialog.geometry("500x300")
        dialog.resizable(False, False)
        
        # Decorative frame
        decor_frame = ttk.Frame(dialog, style='Chamber.TFrame')
        decor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(decor_frame, 
                text="Issue New Royal Invitation",
                style='Title.TLabel').pack(pady=10)
        
        # Form with elegant styling
        form_frame = ttk.Frame(decor_frame, style='Chamber.TFrame')
        form_frame.pack(pady=10)
        
        ttk.Label(form_frame, 
                text="When shall we convene? (HH:MM):",
                style='Jewel.TLabel').grid(row=0, column=0, padx=5, pady=5)
        time_entry = ttk.Entry(form_frame, font=('Garamond', 11))
        time_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, 
                text="Throne Room Link:",
                style='Jewel.TLabel').grid(row=1, column=0, padx=5, pady=5)
        link_entry = ttk.Entry(form_frame, width=30, font=('Garamond', 11))
        link_entry.grid(row=1, column=1, padx=5, pady=5)
        
        def issue_invitation():
            time_str = time_entry.get()
            link_str = link_entry.get()
            
            # Validate time format
            try:
                datetime.strptime(time_str, '%H:%M')
            except ValueError:
                messagebox.showerror("Royal Error", "Invalid time format. Use HH:MM")
                return
            
            # Add to royal decrees
            self.meetings.append({
                'time': time_str,
                'link': link_str,
                'status': 'Pending'
            })
            
            # Save to royal scroll
            self.save_meetings_to_csv()
            self.update_meetings_table()
            dialog.destroy()
        
        ttk.Button(
            decor_frame, 
            text="🔮 Issue Invitation", 
            command=issue_invitation,
            style='RoyalButton.TButton'
        ).pack(pady=10)

    def edit_meeting_dialog(self):
        """Edit royal decree dialog"""
        selected = self.meetings_table.selection()
        if not selected:
            messagebox.showwarning("Royal Notice", "No decree selected")
            return
            
        item = self.meetings_table.item(selected[0])
        values = item['values']
        index = self.meetings_table.index(selected[0])
        
        dialog = tk.Toplevel(self.root)
        dialog.title("✏️ Edit Royal Decree")
        dialog.geometry("500x300")
        dialog.resizable(False, False)
        
        # Decorative frame
        decor_frame = ttk.Frame(dialog, style='Chamber.TFrame')
        decor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(decor_frame, 
                text="Amend Royal Decree",
                style='Title.TLabel').pack(pady=10)
        
        # Form with elegant styling
        form_frame = ttk.Frame(decor_frame, style='Chamber.TFrame')
        form_frame.pack(pady=10)
        
        ttk.Label(form_frame, 
                text="Royal Hour (HH:MM):",
                style='Jewel.TLabel').grid(row=0, column=0, padx=5, pady=5)
        time_entry = ttk.Entry(form_frame, font=('Garamond', 11))
        time_entry.insert(0, values[0])
        time_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, 
                text="Throne Room Link:",
                style='Jewel.TLabel').grid(row=1, column=0, padx=5, pady=5)
        link_entry = ttk.Entry(form_frame, width=30, font=('Garamond', 11))
        link_entry.insert(0, values[1])
        link_entry.grid(row=1, column=1, padx=5, pady=5)
        
        def save_changes():
            time_str = time_entry.get()
            link_str = link_entry.get()
            
            # Validate time format
            try:
                datetime.strptime(time_str, '%H:%M')
            except ValueError:
                messagebox.showerror("Royal Error", "Invalid time format. Use HH:MM")
                return
            
            # Update royal decree
            self.meetings[index] = {
                'time': time_str,
                'link': link_str,
                'status': values[2]  # Keep existing status
            }
            
            # Save to royal scroll
            self.save_meetings_to_csv()
            self.update_meetings_table()
            dialog.destroy()
        
        ttk.Button(
            decor_frame, 
            text="💎 Save Changes", 
            command=save_changes,
            style='RoyalButton.TButton'
        ).pack(pady=10)

    def delete_meeting(self):
        """Rescind royal invitation"""
        selected = self.meetings_table.selection()
        if not selected:
            messagebox.showwarning("Royal Notice", "No decree selected")
            return
            
        if not messagebox.askyesno(
            "Royal Confirmation",
            "Rescind this royal invitation?"
        ):
            return
            
        index = self.meetings_table.index(selected[0])
        del self.meetings[index]
        
        self.save_meetings_to_csv()
        self.update_meetings_table()

    def join_selected_meeting(self):
        """Attend selected gathering immediately"""
        selected = self.meetings_table.selection()
        if not selected:
            messagebox.showwarning("Royal Notice", "No gathering selected")
            return
            
        item = self.meetings_table.item(selected[0])
        values = item['values']
        index = self.meetings_table.index(selected[0])
        
        self.attend_royal_gathering({
            'time': values[0],
            'link': values[1],
            'status': values[2]
        })
        
        # Update status if not already attended
        if values[2] != 'Attended':
            self.meetings[index]['status'] = 'Attended'
            self.save_meetings_to_csv()
            self.update_meetings_table()

    def copy_meeting_link(self):
        """Copy throne room link to royal clipboard"""
        selected = self.meetings_table.selection()
        if not selected:
            messagebox.showwarning("Royal Notice", "No gathering selected")
            return
            
        item = self.meetings_table.item(selected[0])
        link = item['values'][1]
        
        self.root.clipboard_clear()
        self.root.clipboard_append(link)
        
        self.status_var.set("Throne room link copied to royal clipboard")

    def import_csv(self):
        """Import royal scroll"""
        file_path = filedialog.askopenfilename(
            title="Select Royal Scroll",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.config['csv_path'] = file_path
            self.save_config()
            self.load_meetings()
            self.status_var.set(f"Royal scroll imported from {file_path}")

    def save_meetings_to_csv(self):
        """Save royal decrees to scroll"""
        try:
            with open(self.config['csv_path'], 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['Time', 'Link'])
                writer.writeheader()
                
                for meeting in self.meetings:
                    writer.writerow({
                        'Time': meeting['time'],
                        'Link': meeting['link']
                    })
        except Exception as e:
            messagebox.showerror(
                "Royal Error",
                f"Failed to save royal scroll: {str(e)}"
            )

    def open_settings(self):
        """Open royal settings"""
        dialog = tk.Toplevel(self.root)
        dialog.title("⚙️ Royal Settings")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        
        # Decorative frame
        decor_frame = ttk.Frame(dialog, style='Chamber.TFrame')
        decor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(decor_frame, 
                text="Royal Court Settings",
                style='Title.TLabel').pack(pady=10)
        
        # Settings frame
        settings_frame = ttk.Frame(decor_frame, style='Chamber.TFrame')
        settings_frame.pack(pady=10)
        
        # Notification settings
        notify_var = tk.BooleanVar(value=self.config['notifications'])
        ttk.Checkbutton(
            settings_frame, 
            variable=notify_var,
            text="Enable Royal Announcements",
            style='Jewel.TCheckbutton'
        ).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        # Sound settings
        sound_var = tk.BooleanVar(value=self.config['play_sound'])
        ttk.Checkbutton(
            settings_frame, 
            variable=sound_var,
            text="Enable Royal Fanfares",
            style='Jewel.TCheckbutton'
        ).grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        # Reminder time
        ttk.Label(settings_frame, 
                text="Royal Reminder Before (minutes):",
                style='Jewel.TLabel').grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        reminder_var = tk.IntVar(value=self.config['reminder_before'])
        ttk.Spinbox(
            settings_frame,
            from_=1,
            to=30,
            textvariable=reminder_var,
            width=5,
            font=('Garamond', 10)
        ).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Theme selection
        ttk.Label(settings_frame, 
                text="Court Appearance:",
                style='Jewel.TLabel').grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        theme_var = tk.StringVar(value=self.config.get('theme', 'light'))
        theme_menu = ttk.Combobox(
            settings_frame,
            textvariable=theme_var,
            values=['light', 'dark'],
            state='readonly',
            width=10,
            font=('Garamond', 10)
        )
        theme_menu.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        def save_settings():
            self.config['notifications'] = notify_var.get()
            self.config['play_sound'] = sound_var.get()
            self.config['reminder_before'] = reminder_var.get()
            self.config['theme'] = theme_var.get()
            
            self.save_config()
            
            # Apply theme
            sv_ttk.set_theme(theme_var.get())
            
            dialog.destroy()
            messagebox.showinfo(
                "Royal Notice", 
                "Court settings have been preserved"
            )
        
        ttk.Button(
            decor_frame, 
            text="💾 Save Settings", 
            command=save_settings,
            style='RoyalButton.TButton'
        ).pack(pady=10)

    def load_image(self, path, size=None):
        """Load and resize an image if it exists"""
        if not os.path.exists(path):
            return None
            
        try:
            img = Image.open(path)
            if size:
                img = img.resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except:
            return None

def main():
    root = tk.Tk()
    app = RoyalPrincessApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()