"""
ATS PRO — Entry Point
Run with: python run.py
"""
from app import create_app

app = create_app()

# Register a custom Jinja2 'enumerate' filter
@app.template_filter('enumerate')
def jinja_enumerate(iterable, start=0):
    return enumerate(iterable, start=start)


if __name__ == "__main__":
    print("=" * 50)
    print("  ATS PRO — Starting Server")
    print("  Open: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, host="0.0.0.0", port=5000)
