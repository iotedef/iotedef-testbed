def camel_code(name):
    words = []

    for word in name.split("_"):
        words.append(word.capitalize())

    return ''.join(words)

