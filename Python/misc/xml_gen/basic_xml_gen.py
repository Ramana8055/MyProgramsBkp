#!/usr/bin/python -B

from lxml import etree

# create XML 
root = etree.Element('root')
#child without text
root.append(etree.Element('fisrtSubTag'))
# another child with text
child = etree.Element('secondSubTag')
child.text = 'hello world'
root.append(child)
# pretty string ; If true Indentation is done
print etree.tostring(root, pretty_print=True),
