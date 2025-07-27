import sys

if __name__ == "__main__":
    user_input = sys.argv[1] if len(sys.argv) > 1 else ""
    print(f"[Python] You typed: {user_input}")
