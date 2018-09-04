import sys
import reports

def main():
    if len(sys.argv) < 2:
        sys.exit("argv: accno")

    # get argv
    accno = sys.argv[1]

    report, info, err, debug = reports.get_similar_recent_report(accno)
    print(report)
    print(info)
    print(err)
    print(debug)


if __name__ == "__main__":
    main()
