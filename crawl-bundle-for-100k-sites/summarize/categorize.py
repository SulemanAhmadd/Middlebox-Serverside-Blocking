#! /usr/bin/env python3

"""Categorize error messages and HTML responses"""

import re

def error_name(t_status):
    """Normalize error names"""
    # t_status = 'none'
    if 'IncompleteRead' in t_status:
        t_status = 'IncompleteRead'
    elif 'CertificateError' in t_status:
        t_status = 'CertificateError'
    elif 'certificate verify failed' in t_status:
        t_status = 'certificate verify failed'
    elif 'Connection reset' in t_status:
        t_status = 'Connection reset'
    elif 'timed out' in t_status:
        t_status = 'timed out'
    elif 'handshake failure' in t_status:
        t_status = 'handshake failure'
    elif 'Connection refused' in t_status:
        t_status = 'Connection refused'
    elif 'nodename nor servname provided, or not known' in t_status or 'hostname nor servname provided, or not known' in t_status:
        t_status = 'Unknown nodename nor servname'
    elif 'No route to host' in t_status:
        t_status = 'No route to host'
    elif 'failure in name resolution' in t_status:
        t_status = 'failure in name resolution'
    elif 'Connection refused' in t_status:
        t_status = 'Connection refused'
    elif 'incorrect data check' in t_status:
        t_status = 'incorrect data check'
    elif 'No route to host' in t_status:
        t_status = 'No route to host'
    elif 'failure in name resolution' in t_status:
        t_status = 'failure in name resolution'
    # new entry - for when the internet is down
    elif 'Network is unreachable' in t_status:
        t_status = 'Network is unreachable'
    # new entry - for when the remote end closes connection without response
    elif 'RemoteDisconnected' in t_status:
        t_status = 'Remote disconnection'

    return t_status

def get_geo_block(body):
    geo_errors = [
        "not available in your country",
        "unable to process international online transactions",
        "Not in service area",
        "Site available only for Denmark and Germany.",
        "site is unavailable in your region",
        "not currently in your country",
        "unavailable in your country",
        "isn’t available where you are",
        "you must reside within the fifty states of the United States of America",
    ]

    geo_tag = ''
    if re.search("<span class=\"cf-error-code\">1009</span>", body):
        geo_tag = ":GEO_BLOCKED-1009"
    elif re.search("GEO-IP Filter", body):
        geo_tag = ":GEO_BLOCKED-Filter"
    else:
        for err in geo_errors:
            if re.search(err, body):
                geo_tag = ":GEO_BLOCKED-Other"
                break
    if re.search("prohibited for viewership from within Pakistan", body):
        geo_tag = ":GEO_BLOCKED-SS"

    return geo_tag

def get_abuse_block(body):
    other_errors = [
        "Request forbidden by administrative rules.",
    ]

    ip_errors = [
        "<span class=\"cf-error-code\">1006</span>",
        "<span class=\"cf-error-code\">1007</span>",
        "<span class=\"cf-error-code\">1008</span>"
    ]
    dns_errors = [
        "<span class=\"cf-error-code\">1000</span>",
        "<span class=\"cf-error-code\">1002</span>",
    ]
    abuse_tag = ''
    # IP blocking
    for err in ip_errors:
        if re.search(err, body):
            abuse_tag = ":ABUSE_BLOCKED-IP"
            break
    # DNS to prohibited IP
    for err in dns_errors:
        if re.search(err, body):
            abuse_tag = ":ABUSE_BLOCKED-DNS"
            break
    # Bad browser signature
    if re.search("<span class=\"cf-error-code\">1010</span>", body):
        abuse_tag = ":ABUSE_BLOCKED-1010"
    # Warning for VPN/Tor
    elif re.search("Your request has been blocked by the OctoNet HTTP filter", body):
        abuse_tag = ":ABUSE_BLOCKED-VPN-TOR"
    # Direct IP access
    elif re.search("<span class=\"cf-error-code\">1003</span>", body):
        abuse_tag = ":ABUSE_BLOCKED-1003"
    # Hotlinking denied
    elif re.search("<span class=\"cf-error-code\">1011</span>", body):
        abuse_tag = ":ABUSE_BLOCKED-1011"
    # Access denied
    elif re.search("<span class=\"cf-error-code\">1012</span>", body):
        abuse_tag = ":ABUSE_BLOCKED-1012"
    # JavaScript challenge
    elif re.search("<div class=\"cf-browser-verification cf-im-under-attack\">", body):
        abuse_tag = ":ABUSE_BLOCKED-BV"

    elif re.search("<title>Attention Required! \\| CloudFlare</title>|One more step to access", body):
        abuse_tag = ":ABUSE_BLOCKED-CAPTCHA"
    elif re.search("<noscript id=\"cf-captcha-bookmark\" class=\"cf-captcha-info\">|<button type=\"submit\" class=\"cf-captcha-submit\">", body):
        # A customized captcha page.
        abuse_tag = ":ABUSE_BLOCKED-CAPTCHA"
    elif re.search("<title>Access denied \\| [^ ]* used CloudFlare to restrict access</title>", body):
        # With this one you don't get a captcha. May be controlled by the
        # site operator.
        abuse_tag = ":ABUSE_BLOCKED-AD"

    else:
        # Other errors
        for err in other_errors:
            if re.search(err, body):
                abuse_tag = ":ABUSE_BLOCKED-OTHER"
                break

    return abuse_tag


# Copied from David's error classification for the ooni data
def response(status, headers, body):
    """Categorize an HTML response

    Get the error message from a status code (an int, e.g., 200, 404)
    and the body of the message.  Returns a pair.

    The first component is True if a category has been found, and, in
    this case, the category is returned as the second component.  The
    category is a "blocktype", a string naming previously seen form of
    blocking.  Each string starts with the status code and description
    of what was found in the body, such as the name of the company
    doing the blocking.

    The first component is False if the status and body is
    categorized, and, in this case, the status converted to a string
    is returned for the second component.
    """

    browser_errors = [
        "browser that is not compatible",
        "unsupported__browserItem",
        "browser is not supported",
        "Upgrade Your Browser",
        "Update your browser"
    ]

    geo_tag = get_geo_block(body)
    abuse_tag = get_abuse_block(body)

    blocktype = None
    if status == 200:
        if len(body) == 0:
            blocktype = "200-Empty-page"

        if re.search("Error - site blocked", body):
            blocktype = "200-BRITISHTELECOM"

        # Search for various sorts of unsupported browser messages
        for err in browser_errors:
            if re.search(err, body):
                blocktype = "200-UNSUPPORTED_BROWSER"


        # These are obnoxious search monetization things that ISPs serve when a
        # domain doesn't exit.
        if re.search("<meta http-equiv=\"refresh\" content=\"0;url=http://finder\\.cox\\.net", body):
            blocktype = "200-COX-FINDER"
        if re.search("window\\.open\\('http://www\\.parkingcrew\\.net/privacy\\.html'", body):
            blocktype = "200-PARKINGCREW"
        if re.search("window\\.open\\('http://www\\.parkingcrew\\.net/privacy2\\.html'", body):
            blocktype = "200-PARKINGCREW"
        if re.search("<script src='http://parkingcrew.net/assets/scripts/js3\\.js'", body):
            blocktype = "200-PARKINGCREW"

        if re.search("<title>Scam Blocked</title>\n<meta http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\">", body):
            blocktype = "200-COX-PHISHING"
        if re.search("Your datacenter is blocked\\. Please disable any VPN or proxy\\.", body):
            blocktype =  "200-HACKFORUMS"

        # These are all ISP-specific block pages for URLs blocked by the
        # government of India at the end of 2014.
        # https://securityinabox.org/en/blog/22-02-2015/observations-recent-india-censorship
        if re.search("<!--This is a comment\\. Comments are not displayed in the browser-->", body):
            blocktype =  "200-INDIA"
        # http://chaoslab.in/goiblocks/block_4.png
        if re.search("The requested url is blocked, based on the blocking Instruction order received from the Department of Telecommunications, Ministry of Communications & IT, Government of India\\.", body):
            blocktype =  "200-INDIA"
        # http://chaoslab.in/goiblocks/block_5.png
        # There's also a variation that includes the domain.
        if re.search("HTTP Error 404 - File or Directory not found", body):
            blocktype =  "200-INDIA"
        # This one is not found on the above blog post, however it looks like it
        # is from India and the same bunch of pastebin sites.
        if re.search("The URL you requested has been blocked", body):
            blocktype =  "200-INDIA"

        # This is censorship in Pakistan
        if re.search("The site you are trying\n*to access contains content that is prohibited for viewership from within\n*Pakistan.",
                     body):
            blocktype = "200-Pakistan"

        if re.search("background: url\\(/images/mainBg\\.png\\) top center no-repeat #b9babf;", body):
            blocktype =  "200-TURKEY"
        if re.search("<title>Telekomünikasyon İletişim Başkanlığı</title>.*\\.erisime_engellenmis", body, flags=re.DOTALL):
            blocktype =  "200-TURKEY-TIB"
        if re.search("Not Available in Your Country", body, flags=re.DOTALL):
            blocktype =  "200-Not Available in Your Country"
        if re.search("Access Denied", body, flags=re.DOTALL):
            blocktype =  "200-Access Denied"
        if re.search("We Are Currently Unable to Provide a Shopping Experience", body):
            blocktype =  "200-Not Available in Your Country"
        # if re.search("Gateway GEO-IP Filter Alert", body):
        #     blocktype = "200-Not Available in Your Country: Gateway GEO-IP Filter Alert"

    if status == 403:
        if re.search("Not Available in Your Country", body):
            blocktype = "403-Not-Available-in-Country"
        if re.search("only available inside the US", body):
            blocktype = "403-Only-Available-in-US"
        if re.search("Microsoft-IIS", body):
            blocktype = "403-Microsoft"
        if re.search("You are attempting to access a forbidden site", body):
            blocktype = "403-FORBIDDEN"
        if re.search("\"Server\": \"cloudflare\"", body) or re.search("\"Server\": \"cloudflare\"", headers.get('Server', '')):
            blocktype = "403-CLOUDFLARE"
        if re.search("CloudFront", body):
            blocktype = "403-CLOUDFRONT"
        if re.search("<Error><Code>AccessDenied</Code><Message>Access Denied</Message><RequestId>", body):
            blocktype =  "403-AMAZON-CLOUDFRONT"
        if re.search("<p>You can use this key to <a href=\"http://www\\.ioerror\\.us/bb2-support-key\\?key=[\\w-]+\">fix this problem yourself</a>\\.</p>", body):
            blocktype = "403-BADBEHAVIOR"
        if re.search("Access denied\\.  Your IP address \\[[\\d.]+\\] is blacklisted\\.  If you feel this is in error please contact your hosting providers abuse department", body):
            blocktype ="403-BLUEHOST"
        # if re.search("<title>Attention Required! \\| CloudFlare</title>|One more step to access", body):
        #     blocktype = "403-CLOUDFLARE-CAPTCHA"
        # if  re.search("<noscript id=\"cf-captcha-bookmark\" class=\"cf-captcha-info\">|<button type=\"submit\" class=\"cf-captcha-submit\">", body):
        #     # A customized captcha page.
        #     blocktype = "403-CLOUDFLARE-CAPTCHA"
        # if re.search("<title>Access denied \\| [^ ]* used CloudFlare to restrict access</title>", body):
        #     # With this one you don't get a captcha. May be controlled by the
        #     # site operator.
        #     blocktype = "403-CLOUDFLARE-AD"
        if re.search("This IP has been automatically blocked\\.\n(Questions:|If you have questions, please email:) blocks-\\w+@craigslist\\.org", body):
            blocktype =  "403-CRAIGSLIST"
        if re.search("<h1>We're sorry\\.\\.\\.</h1><p>\\.\\.\\. but your computer or network may be sending automated queries\\.", body):
            blocktype = "403-GOOGLE-SORRY"
        if re.search("<meta http-equiv=\"Content-Type\" content=\"text/html; charset=windows-1256\"><title>M[0-9]-[0-9]\n", body):
            blocktype =  "403-IRAN"
        if re.search("<li>McAfee Global Threat Intelligence has determined</li>", body):
            blocktype = "403-MCAFEE"
        if re.search("<title>Pastebin\\.com - Access Denied Warning</title>\r", body):
            # "Censor Kitty denies access"
            # Pastebin is also on CloudFlare, so you could get a CloudFlare
            # captcha or their own custom block page.
            blocktype = "403-PASTEBIN"
        if re.search("href=\"//help\\.pinterest\\.com/entries/22914692\"", body):
            blocktype = "403-PINTEREST"
        if body == "<h2>Forbidden</h2>\n":
            blocktype = "403-RACKSPACE"
        if re.search("<title>Доступ всё ещё закрыт!</title>", body):
            blocktype = "403-SKYDNS"
        if re.search("<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\"/><meta name=\"id\" content=\"siteBlocked\"/><title>Web Site Blocked</title>", body):
            blocktype = "403-SONICWALL"
        if re.search("<title>Web Site Blocked</title>", body) and re.search("id=\"nsa_banner\" alt=\"SonicWALL Network Security Appliance\"", body):
            blocktype = "403-SONICWALL"
        if re.search("<img alt=\"404 page not found\" title=\"404 page not found\" src=\"data:image/png;base64,iVBOR", body):
            blocktype =  "403-TYPEPAD"
        if re.search("<title>403.6 - Access denied.</title>", body):
            blocktype = "403-WILDAPRICOT"
        if re.search("\\[403 Forbidden Error\\] - You might be blocked by your IP, Country, or ISP\\. You can try to contact us at http://www\\.witza\\.com/contact\\.php", body):
            blocktype = "403-WITZA"
        if re.search("<p>Please retry your request and <a href=\"mailto:feedback\\+forbidden@yelp\\.com", body):
            blocktype = "403-YELP"

    if status == 403 or status == 404:
        if re.search("<H1>Access Denied</H1>\n \nYou don't have permission to access \"[^\"]*\" on this server\\.<P>\nReference&#32;&#35;", body):
            blocktype = "%d-AKAMAI" % status

    if status == 404:
        if re.search("<title>Error 451</title>", body):
            blocktype = "404-LIVEJOURNAL-451"
        if re.search("You are using an <strong>outdated</strong> browser", body):
            blocktype = "404-OUTDATED-BROWSER"

    if status == 406:
        if re.search("This request has been denied for security reasons\\.", body):
            blocktype = "406-SITE5"
        if re.search("<meta http-equiv=\"refresh\" content=\"0;url=http://www\\.ariannelingerie\\.com/shop/\">\n", body):
            blocktype = "406-ARIANNELINGERIE"

    if status == 503:
        if re.search("To discuss automated access to Amazon data please contact api-services-support@amazon\\.com\\.", body):
            blocktype = "503-AMAZON"
        # if re.search("<div class=\"cf-browser-verification cf-im-under-attack\">", body):
        #     blocktype = "503-CLOUDFLARE"
        if re.search("<title>\\s*qos-mission-critical-pan\\s*</title>", body):
            blocktype = "503-DOD"
        if re.search("<p>Please retry your request and <a href=\"mailto:feedback\\+unavailable@yelp.com\\?subject=IP%20Block%20Message%3A%20[\\d.]+\">contact Yelp</a> if you continue experiencing issues\\.</p>", body):
            blocktype = "503-YELP"

    if status in (910, 920):
        if body == "<h1>File not found</h1>":
            blocktype = "%d-VICTORIASSECRET" % status

    if status == 999:
        if re.search("<title>999: request failed</title>", body):
            blocktype = "999-LINKEDIN"
        if re.search("/uas/login\\?trk=sentinel_org_block", body):
            blocktype = "999-LINKEDIN"
        if re.search("Yahoo! - 999 Unable to process request at this time -- error 999", body):
            blocktype = "999-YAHOO"

    if status > 200 and not blocktype:
        blocktype = "%d-OTHER" % status

    if blocktype:
	#print(status)
        if (geo_tag == '' and abuse_tag != ''):
            return True, blocktype+abuse_tag
        elif (geo_tag != '' and abuse_tag == ''):
            return True, blocktype+geo_tag
        elif (geo_tag == '' and abuse_tag == ''):
            return True, blocktype
        else:
            return True, blocktype+"$BOTH$"+geo_tag+abuse_tag
    else:
        if (geo_tag == '' and abuse_tag != ''):
            return True, str(status)+"-UNCAUGHT"+abuse_tag
        elif (geo_tag != '' and abuse_tag == ''):
            return True, str(status)+"-UNCAUGHT"+geo_tag
        elif (geo_tag == '' and abuse_tag == ''):
            return False, str(status)+"-NONBLOCK"
        else:
            return True, str(status)+"-UNCAUGHT"+"$BOTH$"+geo_tag+abuse_tag

        # return False, str(status)+"-NONBLOCK"+geo_tag

    # return False, str(status)+"-NONBLOCK"+geo_tag
    # return False, str(status)+"-NONBLOCK"
