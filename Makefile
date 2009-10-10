

clean:
	@-find . -name '*~'    -delete
	@-find . -name '*.bak' -delete

tidy:
	perltidy $$(find plugins/ -type f -print) ./cgi-bin/quarantine.cgi
