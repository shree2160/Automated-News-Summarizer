from transformers import pipeline

def test():
    try:
        print("Testing sentiment pipeline without task...")
        # This should fail in Transformers 5.x
        pipe = pipeline(model="distilbert-base-uncased-finetuned-sst-2-english")
        print("Success")
    except KeyError as e:
        print(f"Caught expected KeyError: {e}")
    except Exception as e:
        print(f"Caught Exception: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test()
