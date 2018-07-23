# Explacy

This is a small script to explain spacy parse results.

Here's an example output:
![](https://raw.githubusercontent.com/tylerneylon/explacy/master/img/screenshot.png)

## Installing

This is a single Python module, so the easiest way to use it
is to simply download the main file:

    wget https://raw.githubusercontent.com/tylerneylon/explacy/master/explacy.py

You will also need to have `spacy` installed, along with a
working language model. See [the official installation
instructions for spacy](https://spacy.io/usage/).
If you use `pip` to install Python libraries, then your
`spacy` installation may look like this:

    pip install spacy
    python -m spacy download en

If you use Anaconda, it will be different; see the [spacy
docs](https://spacy.io/usage/).
