import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    vals = data[1:1+n]
    # Reverse in-place or simply print reversed
    # Since input constraints are moderate, we can print reversed list
    print(' '.join(vals[::-1]))

if __name__ == "__main__":
    main()