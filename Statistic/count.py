import ijson
from collections import defaultdict

def main():
    KEYS = ("Speaker", "Description", "Image")

    report_count = 0
    fir_total = 0
    his_total = 0

    # Per-key totals
    fir_dic = defaultdict(int)
    his_dic = defaultdict(int)

    with open("report_dataset.json", "rb") as f:
        for report_id, content in ijson.kvitems(f, ""):
            # keep your ID filter
            try:
                int_id = int(report_id)
            except ValueError:
                continue
            if not (0 <= int_id <= 1000):
                continue

            firsthand = content.get("Firsthand_Information", {}) or {}
            for key in KEYS:
                v = firsthand.get(key, [])
                if isinstance(v, list):
                    n = len(v)
                    fir_dic[key] += n
                    fir_total += n

            historical = content.get("Historical_Information", {}) or {}
            for key in KEYS:
                v = historical.get(key, [])
                if isinstance(v, list):
                    n = len(v)
                    his_dic[key] += n
                    his_total += n

            report_count += 1

    if report_count == 0:
        print("No reports processed.")
        return

    print("fir :", fir_total / report_count)
    print("his :", his_total / report_count)
    print(dict(fir_dic))
    print(dict(his_dic))

if __name__ == "__main__":
    main()
