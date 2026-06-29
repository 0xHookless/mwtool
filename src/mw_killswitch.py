import os
import sys
import tkinter as tk
import subprocess
import ctypes
import threading
import math

hosts = r"C:\Windows\System32\drivers\etc\hosts"
block_line = "127.0.0.1 www.motivewave.com"
marker = "# MW_BLOCK"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# relaunch as admin if not elevated
if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GhostWave")
        self.geometry("400x260")
        self.configure(bg="#0a0a0a")
        self.resizable(False, False)
        
        self.is_loading = False
        self.angle = 0

        # dark title bar on win10/11
        try:
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(ctypes.c_int(1)), 4)
        except:
            pass

        # custom drag bar
        top = tk.Frame(self, bg="#0a0a0a", height=30)
        top.pack(fill="x")

        title_lbl = tk.Label(top, text="GhostWave", bg="#0a0a0a", fg="#444444", font=("Arial", 8))
        title_lbl.pack(side="left", padx=12, pady=5)

        # status
        self.status_var = tk.StringVar()
        self.status_lbl = tk.Label(self, textvariable=self.status_var, font=("Segoe UI", 16, "bold"), bg="#0a0a0a", fg="#ffffff")
        self.status_lbl.pack(pady=(15, 5))

        # canvas for spinner and glow
        self.canvas = tk.Canvas(self, width=200, height=40, bg="#0a0a0a", bd=0, highlightthickness=0)
        self.canvas.pack()

        # button
        self.btn = tk.Button(self, text="...", font=("Segoe UI", 10, "bold"), 
                        bg="#1a1a1a", fg="#ffffff", activebackground="#2a2a2a", activeforeground="#ffffff", 
                        bd=1, relief="solid", cursor="hand2", width=30, height=2, command=self.start_toggle)
        self.btn.pack(pady=10)

        self.desc_var = tk.StringVar()
        self.desc_lbl = tk.Label(self, textvariable=self.desc_var, font=("Segoe UI", 9), bg="#0a0a0a", fg="#777777")
        self.desc_lbl.pack(pady=5)
        
        self.update_ui()

    def check(self):
        try:
            with open(hosts, 'r') as f:
                for l in f:
                    if block_line in l and marker in l:
                        return True
            return False
        except:
            return False

    def update_ui(self):
        blocked = self.check()
        self.canvas.delete("all")
        if blocked:
            self.status_var.set("STATUS: BLOCKED")
            self.btn.config(text="RESTORE CONNECTION", bg="#1a1a1a", state=tk.NORMAL)
            self.desc_var.set("MotiveWave heartbeat is currently blocked.\nThe license is released for your home PC.")
            self.glow_step = 0
            self.animate_glow()
        else:
            self.status_var.set("STATUS: ACTIVE")
            self.btn.config(text="DROP CONNECTION", bg="#1a1a1a", state=tk.NORMAL)
            self.desc_var.set("MotiveWave heartbeat is active.\nDrop connection to free up the license.")
            
    def animate_glow(self):
        if not self.check() or self.is_loading:
            return
        self.canvas.delete("glow")
        scale = min(1.0, self.glow_step / 15.0)
        if scale >= 1.0:
            pulse = math.sin((self.glow_step - 15) * 0.1) * 0.15 + 0.85
        else:
            pulse = scale
        cx, cy = 60, 20
        colors = ["#1a1a1a", "#222222", "#333333", "#555555", "#aaaaaa", "#ffffff"]
        max_r = 14 * pulse
        for i, color in enumerate(colors):
            r = max_r * (1 - i/len(colors))
            if r > 0:
                self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=color, outline="", tags="glow")
        if scale > 0.3:
            c_val = int(255 * min(1.0, (scale - 0.3) * 1.5))
            hex_c = f"#{c_val:02x}{c_val:02x}{c_val:02x}"
            self.canvas.create_text(110, 20, text="LICENSE FREE", fill=hex_c, font=("Segoe UI", 8, "bold"), tags="glow")
        self.glow_step += 1
        self.after(30, self.animate_glow)
            
    def start_toggle(self):
        if self.is_loading: return
        self.is_loading = True
        self.btn.config(state=tk.DISABLED, text="WORKING...")
        self.canvas.delete("all")
        threading.Thread(target=self.do_toggle, daemon=True).start()
        self.animate_loading()

    def do_toggle(self):
        blocked = self.check()
        try:
            with open(hosts, 'r') as f:
                data = f.readlines()
            
            # clean out old block lines and trailing blank lines
            cleaned = []
            for d in data:
                if marker in d or (block_line in d):
                    continue
                cleaned.append(d)
            
            # strip trailing empty lines
            while cleaned and cleaned[-1].strip() == "":
                cleaned.pop()
            
            with open(hosts, 'w') as f:
                for d in cleaned:
                    f.write(d)
                if not blocked:
                    f.write(f"\n{block_line} {marker}\n")
                else:
                    f.write("\n")
            
            subprocess.run(["ipconfig", "/flushdns"], creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception:
            pass
            
        self.is_loading = False

    def animate_loading(self):
        if not self.is_loading:
            self.update_ui()
            return
        self.canvas.delete("spinner")
        self.angle = (self.angle + 25) % 360
        self.canvas.create_arc(85, 5, 115, 35, start=self.angle, extent=270, outline="#ffffff", width=2, style=tk.ARC, tags="spinner")
        self.after(30, self.animate_loading)

if __name__ == "__main__":
    app = App()
    app.mainloop()
