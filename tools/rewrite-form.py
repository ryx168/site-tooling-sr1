"""Swap the Contact Form 7 markup for a plain POST form (sausagerolls.biz).

CF7 submits over AJAX to /wp-json/contact-form-7/..., which does not exist on a
static host. Left alone the form looks like it works and drops every enquiry.

Two things matter here beyond swapping the markup:
  * the replacement must NOT carry the class CF7 binds to (wpcf7-form), and the
    plugin script must go, or CF7 hijacks submit and the POST never happens;
  * the field names must match FIELDS in public/_worker.js exactly
    (your-name, company, mail, phone, Help) - these are form 1289 on this site.
"""
import io, re, sys

p = sys.argv[1]
h = io.open(p, encoding="utf-8", errors="replace").read()

m = re.search(r"<form[^>]*wpcf7-form.*?</form>", h, re.S)
if not m:
    print("  no CF7 form found - nothing changed"); sys.exit(1)
old = m.group(0)

# Keep the theme grid (row / col-md-*) so the styling carries over unchanged.
new = """<form action="/contact-send" method="post" class="ps-contact-form" novalidate="novalidate">
<div style="position:absolute;left:-9999px;top:-9999px" aria-hidden="true">
<label>Leave this empty<input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>
<div class="row">
<div class="col-md-6"><span class="wpcf7-form-control-wrap" data-name="your-name">
<input size="40" class="wpcf7-form-control wpcf7-text" autocomplete="name" required="required" placeholder="Name" value="" type="text" name="your-name"></span></div>
<div class="col-md-6"><span class="wpcf7-form-control-wrap" data-name="company">
<input size="40" class="wpcf7-form-control wpcf7-text" autocomplete="organization" placeholder="Company" value="" type="text" name="company"></span></div>
</div>
<div class="row">
<div class="col-md-6"><span class="wpcf7-form-control-wrap" data-name="mail">
<input size="40" class="wpcf7-form-control wpcf7-text" autocomplete="email" required="required" placeholder="E-mail Address" value="" type="email" name="mail"></span></div>
<div class="col-md-6"><span class="wpcf7-form-control-wrap" data-name="phone">
<input size="40" class="wpcf7-form-control wpcf7-text" autocomplete="tel" placeholder="Phone" value="" type="text" name="phone"></span></div>
</div>
<div class="row">
<div class="col-md-12"><span class="wpcf7-form-control-wrap" data-name="Help">
<textarea cols="40" rows="10" class="wpcf7-form-control wpcf7-textarea" placeholder="How can we help?" name="Help"></textarea></span></div>
</div>
<p><input class="wpcf7-form-control wpcf7-submit" type="submit" value="Submit"></p>
</form>"""

h = h.replace(old, new, 1)

# CF7 script would bind to and hijack a form; the config block is dead weight.
n = 0
for pat, fl in [
    (r"<script[^>]*contact-form-7[^>]*>\s*</script>\s*", re.I),
    (r"<script[^>]*contact-form-7-js-extra[^>]*>.*?</script>\s*", re.S | re.I),
    (r"var wpcf7 = \{.*?\};", re.S),
]:
    h, c = re.subn(pat, "", h, flags=fl); n += c

io.open(p, "w", encoding="utf-8", newline=chr(10)).write(h)
print("  form replaced: %d -> %d bytes; cf7 script blocks removed: %d" % (len(old), len(new), n))
print("  fields:", ", ".join(re.findall(r"name=\"([^\"]+)\"", new)))
