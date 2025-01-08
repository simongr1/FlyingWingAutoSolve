import shutil
import os

def empty_directory(directory):
    try:
        shutil.rmtree(directory)  # Remove all contents
        os.makedirs(directory)  # Recreate the empty directory
    except Exception as e:
        print(f"Failed to empty directory. Reason: {e}")

def main():
    # Example usage
    empty_directory('/path/to/your/directory')


if __name__=="__main__":
    main()