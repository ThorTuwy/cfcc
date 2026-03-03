from tomlkit import document

doc = document()
doc.append('foo_sadsad', "asda")
print(doc.as_string())
