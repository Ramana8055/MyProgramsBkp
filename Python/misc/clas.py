#!/usr/bin/python
import sys
class restaurant():
	bankrupt=False
	def open_branch(self):
		if not self.bankrupt:
			print "Branch is open!!"

print restaurant().bankrupt
restaurant().open_branch()
