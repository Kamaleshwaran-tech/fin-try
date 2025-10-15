from extractor import main as process_news
from analyzer import main as analyze_polarity

from sentMail import main as send_email

# Call the main function from send_email

# Run the main function from the polarity analyzer
if __name__ == "__main__":
    process_news()
    analyze_polarity()
    send_email()
    print("Successfuly executed")
