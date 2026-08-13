"""
Desktop Notification & Audio Alert Engine.

Provides non-intrusive notification alerts when NON-SAFE posture persists
for extended periods (>=10s). Uses Windows winsound bell and PowerShell notification,
with a 30-second cooldown timer to prevent user notification fatigue.
"""

import sys
import time
import subprocess
from typing import List, Optional

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False


class PostureNotifier:
    """
    Manages audio chimes and OS desktop notification popups with cooldown throttling.
    """
    def __init__(self, cooldown_sec: float = 30.0, enabled: bool = True):
        self.cooldown_sec = cooldown_sec
        self.enabled = enabled
        self._last_notif_time: Optional[float] = None

    def notify_non_safe(self, duration_sec: float, reasons: List[str], timestamp: Optional[float] = None):
        """
        Trigger alert when NON-SAFE status persists for 10s or more.
        """
        if not self.enabled:
            return

        now = timestamp if timestamp is not None else time.time()

        if self._last_notif_time is not None and (now - self._last_notif_time) < self.cooldown_sec:
            return  # Cooldown active

        self._last_notif_time = now

        reason_str = ", ".join(reasons) if reasons else "Sustained bad posture"
        title = "Ergonomic Alert: Posture Hazard"
        msg = f"Non-Safe posture detected for {duration_sec:.0f}s ({reason_str}). Please adjust your posture!"

        print(f"\n[NOTIF] {title}: {msg}\n")

        # 1. Play subtle audio chime (Windows winsound fallback)
        if HAS_WINSOUND and sys.platform.startswith("win"):
            try:
                winsound.Beep(880, 250)  # A5 pitch for 250ms
            except Exception:
                pass

        # 2. Windows PowerShell Toast Notification (No external pip dependency needed)
        if sys.platform.startswith("win"):
            try:
                ps_script = f'''
                [void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
                $objNotifyIcon = New-Object System.Windows.Forms.NotifyIcon
                $objNotifyIcon.Icon = [System.Drawing.SystemIcons]::Warning
                $objNotifyIcon.BalloonTipIcon = "Warning"
                $objNotifyIcon.BalloonTipTitle = "{title}"
                $objNotifyIcon.BalloonTipText = "{msg}"
                $objNotifyIcon.Visible = $True
                $objNotifyIcon.ShowBalloonTip(4000)
                '''
                subprocess.Popen(
                    ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
                )
            except Exception:
                pass
