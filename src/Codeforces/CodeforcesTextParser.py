""""
This file parses the codeforces texts (Statement, input, output and notes)
Codeforces text is a little weird structure, that is way this is divided into 3 parts:
First we parsed the Tags containing each tag a paragraph,
Then we divide paragraphs into text segments (As some segments contain special tags for things like bold)
and then we parse the text to interpret the latex tags.
"""
from bs4 import Tag,NavigableString
from pylatexenc.latex2text import LatexNodes2Text
from rich.text import Text
from utils.lower_upper_index_translator import to_superscript,to_subscript
"""
Codeforces use $$$...$$$ for his latex rendering, but differs from the default latex rendering
in that this are not intended to break line, so we add this exception using this modfy class.
"""
class NoNewlineLatexNodes2Text(LatexNodes2Text):
    def math_node_to_text(self, node):
        is_display = getattr(node, 'displaytype', None) == 'display'
        if is_display:
            node.displaytype = 'inline'
        text = super().math_node_to_text(node)
        if is_display:
            node.displaytype = 'display'
        return text

def _parse_text(text: str) -> str:
    latex_to_text = NoNewlineLatexNodes2Text().latex_to_text
    text = latex_to_text(text)
    return text

def _parse_tex_span(tex_span: Tag) -> Text:
    result = Text()
    for child in tex_span.children:
        if isinstance(child, NavigableString):
            result += _parse_text(child)
            continue

        if child.name == "i":
            result += Text(_parse_text(child.text), style="italic")
            continue


        child_class = child.get('class',[None])[0]
        if child_class is None:
            result += _parse_text(child)
            continue

        if child_class == "upper-index":
            result += Text(to_superscript(_parse_text(child.text)))
        elif child_class == "lower-index":
            result += Text(to_subscript(_parse_text(child.text)))
        else:
            result += Text(_parse_text(child.text))

    return result


def _parse_paragraph(paragraph: Tag) -> Text:
    result_paragraph = Text()
    for child in paragraph.children:
        if isinstance(child, NavigableString):
            result_paragraph += _parse_text(child)
        elif child.name == 'span':
            child_class = child.get('class')[0]
            if child_class == "tex-font-style-bf":
                result_paragraph += Text(_parse_text(child.text), style="bold")
            elif child_class == "tex-font-style-it":
                result_paragraph += Text(_parse_text(child.text), style="italic")
            elif child_class == "tex-span":
                result_paragraph += _parse_tex_span(child)
            else:
                result_paragraph += Text(_parse_text(child.text))

    return result_paragraph

def get_text_in_div(div: Tag) -> Text:
    result = Text()
    li_position = 1

    for child in div.findChildren(recursive=True):
        if child.name == 'li':
            result += (Text(f"{li_position}. ") + _parse_paragraph(child))
            result += '\n'
            li_position += 1
            continue
        if child.name == 'p':
            if li_position != 1:
                result += '\n'
            li_position = 1
            result += _parse_paragraph(child)
            result += '\n\n'
            continue


    return result