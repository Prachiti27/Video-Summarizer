import strip_markdown

class TimestampFormatter:
    
    @staticmethod
    def format(gen_text):
        cp_text: str = strip_markdown.strip_markdown(gen_text)
        return cp_text