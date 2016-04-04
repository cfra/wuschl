# wuschl

This is a small python script that aims at making it possible to conveniently
build (regression) tests based on a corpus found by
[afl](http://lcamtuf.coredump.cx/afl/).

## Design

On creation of a new test, wuschl will create a c file and a header file.
The c file initially contains one function `test` that takes an input and
an output stream and returns an `int`.

This function should be edited by the user so that it uses the data from
the input stream in the operation that should be verified. The result of
that operation should be put into the output stream and/or the return
value.

After compiling the source with afl-gcc, it can be fuzzed with afl. The
fuzzing can find paths that lead to crashes/hangs on one hand, but on the
other hand, it can also be used to build a corpus of test inputs that
trigger usage of different paths in the operation.

Wuschl supports to collect this corpus into the header file that is included
into the c file for the test. Along with this corpus of input data, it collects
the current output and return value.

This can then be used, e.g. after refactoring the implementation of the
operation, to verify that it still behaves as before. It should be noted that
once the header with the test corpus has been generated, afl is not required
to run the test anymore, only to fuzz again and to add more testcases.

## Usage

Create a testcase:

    wuschl create foo

Edit foo.c so that the `test` function calls the operation that should be tested.
Compile foo.c with afl annotations:

    afl-gcc -o foo foo.c

Now you can initialize the fuzzing process:

    wuschl fuzz foo

Wuschl will complain that there is no starting point for fuzzing. To remediate this,
put some test input into the `foo_afl/input` directory that was created. Now,
running the fuzz command again will actually start the fuzzer.

Once you are happy with the fuzzing done, you can abort afl with Ctrl+C and review
its result.

If you are happy with the results, you can collect those as testcases with

    wuschl update foo

If you now recompile foo - possibly with regular gcc - you can just run it like
this:

    ./foo

And it will verify whether the operation performs as it did when the test corpus
was created. If it doesn't this is treated as a failure. To look into a failure
in more detail, you can call

    ./foo <id>

And will receive more output about why the test failed. Also, you can manually put
data into the `test` function and see its output by calling

    ./foo -r

Incidentally, this is also the mode in which afl calls foo.
