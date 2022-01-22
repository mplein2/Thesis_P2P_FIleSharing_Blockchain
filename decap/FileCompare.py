def main():
    file1 = "test.jpg"
    file2 = "Received.jpg"
    f1 = open(file1, "rb")
    f2 = open(file2, "rb")
    Status = True
    Counter = 0
    while Status:
        dat1 = f1.read(100)
        dat2 = f2.read(100)
        if dat1 == b'':
            Status = False
        if dat2 == b'':
            Status = False
        if dat1 == dat2:
            print(Counter, " : OK")
            Counter = Counter + 1
        else:
            print(Counter, " : Fault")
            Counter = Counter + 1


if __name__ == '__main__':
    main()
