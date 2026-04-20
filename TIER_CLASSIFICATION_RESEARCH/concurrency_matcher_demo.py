import threading
import time


class Matcher:
    def __init__(self, name: str):
        self.name = name

    def predict(self) -> str:
        time.sleep(0.01)
        return self.name


# Design 1: single mutable global matcher
GLOBAL = None


def prepare_global(name: str) -> None:
    global GLOBAL
    GLOBAL = Matcher(name)


def classify_global() -> str:
    return GLOBAL.predict()


# Design 2: report-keyed dictionary + thread-local current report
DICT = {}
TL = threading.local()
LOCK = threading.Lock()


def prepare_threadlocal(name: str) -> None:
    with LOCK:
        DICT.setdefault(name, Matcher(name))
    TL.id = name


def classify_threadlocal() -> str:
    return DICT[TL.id].predict()


# Design 3: explicit matcher passed through call chain
def prepare_explicit(name: str) -> Matcher:
    return Matcher(name)


def classify_explicit(matcher: Matcher) -> str:
    return matcher.predict()


results = []


def race_global(name: str, delay_before_classify: float) -> None:
    prepare_global(name)
    time.sleep(delay_before_classify)
    results.append(("global", name, classify_global()))


def race_threadlocal(name: str, delay_before_classify: float) -> None:
    prepare_threadlocal(name)
    time.sleep(delay_before_classify)
    results.append(("threadlocal", name, classify_threadlocal()))


def race_explicit(name: str, delay_before_classify: float) -> None:
    matcher = prepare_explicit(name)
    time.sleep(delay_before_classify)
    results.append(("explicit", name, classify_explicit(matcher)))


def run_pair(target):
    threads = [
        threading.Thread(target=target, args=("report_A", 0.03)),
        threading.Thread(target=target, args=("report_B", 0.00)),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


if __name__ == "__main__":
    run_pair(race_global)
    run_pair(race_threadlocal)
    run_pair(race_explicit)

    for kind, expected, got in results:
        status = "OK" if expected == got else "CROSS-CONTAMINATED"
        print(f"{kind}: expected={expected} got={got} {status}")
