from pexpect import EOF, TIMEOUT


def expected_text(child, text):
    index = child.expect_exact([text, TIMEOUT, EOF], timeout=10)

    return index == 0
