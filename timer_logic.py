class PomodoroLogic:
    def __init__(self):
        self.is_running = False
        self.mode = "work"

    def format_time(self, seconds):
        
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def get_figure_stage(self, elapsed, total, is_break):
        if is_break:
            return "break_form" 
            
        progress = (elapsed / total) * 100
        if progress <= 25: return "form1"
        if progress <= 50: return "form2"
        if progress <= 75: return "form3"
        return "form4"