## Tainter
### Taint analysis for Python 3

(Very early) work-in-progress. Here be dragons.

Taint analysis is a type of a static analysis of source code.

It is used to analyse the flow of information in the code, so
we can make sure that there are no unintended leaks.

For example, let's say we store some data about the user, and
we decided to use their insurance number as an ID:

```python
class User:
    insurance_number: str
    date_of_birth: datetime

    @property
    def user_id(self):
        return self.date_of_birth + self.insurance_number
```

Sometime down the line, a well-meaning project manager uses that user ID
in a public report, not knowing that it is generated from personally identifiable
information. Time to lawyer up!

A taint analyser may use an annotation like this:
```python
class User:
    @mark_tainted
    insurance_number: str
    @mark_tainted
    date_of_birth: datetime

    @property
    def user_id(self):
        return self.date_of_birth + self.insurance_number
```

And figure out that user_id is tainted as well, throwing a huge warning whenever
it's used, until we rewrite it to be safe and mark it as such:
```python
class User:
    @mark_tainted
    insurance_number: str
    @mark_tainted
    date_of_birth: datetime

    @mark_safe
    @property
    def user_id(self):
        return hash(self.date_of_birth + self.insurance_number + SALT)
```

## Usage

### Install
```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Use
```
usage: main.py [-h] [-d] [-t TAINTED_ARG [TAINTED_ARG ...]] filename function

Taint analysis is a type of a static analysis of source code.

It is used to analyse the flow of information in the code, so
we can make sure that there are no unintended leaks.

For starters, check out the examples files to see how taint spreads.

Then run the tainter on any of the examples, for example:
python3 main.py --tainted-arg a examples/assignment.py chain
to see how the return value is tainted by input "a" in function chain
in file assingment.py.

positional arguments:
  filename              File to analyse.
  function              Function to analyse.

optional arguments:
  -h, --help            show this help message and exit
  -d, --dump            If selected, dump the AST for the function.
  -t TAINTED_ARG [TAINTED_ARG ...], --tainted-arg TAINTED_ARG [TAINTED_ARG ...]
                        Mark a function argument as tainted.
```

### Test
examples is full of test cases. Run `python -m unittest` to run all of them.