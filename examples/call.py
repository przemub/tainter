from utils import mark_safe, mark_output


@mark_safe
def _obfuscate_input(input: str) -> int:
    return hash(input + "sól")


def _poorly_obfuscate_input(input: str) -> str:
    return str(reversed(input))


def safe_call(a):
    return _obfuscate_input(a)


def unsafe_call(a):
    return _poorly_obfuscate_input(a)


def print_test(a):
    print(a)


@mark_output
def _generate_a_report(a):
    # sys.write(a, "report.pdf")
    pass


def mark_output_test(a):
    _generate_a_report(a)
