def word_counts(text):
    import string

    punctuation = '.,;:!?"\'()[]{}'
    return {
        token: text.split().count(token)
        for token in {
            word.lower().strip(punctuation)
            for word in text.split()
            if word.lower().strip(punctuation)
        }
    }
