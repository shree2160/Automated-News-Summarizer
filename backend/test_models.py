from transformers import pipeline

def test():
    try:
        print("Testing summarizer pipeline without task...")
        # This should fail in Transformers 5.x
        pipe = pipeline(model="facebook/bart-large-cnn")
        print("Success")
    except KeyError as e:
        print(f"Caught expected KeyError: {e}")
    except Exception as e:
        print(f"Caught Exception: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test()

