#!/usr/bin/env python2.7
#
# Gets the HTTP HEADER from a server // Jonas Thambert
#

import socket, sys

def http_header_grabber(ip, port=80, method="HEAD",
                        timeout=2, http_type="HTTP/1.1"):
    assert method in ['GET', 'HEAD']
    assert http_type in ['HTTP/0.9', "HTTP/1.0", 'HTTP/1.1']
    cr_lf = '\r\n'
    lf_lf = '\n\n'
    crlf_crlf = cr_lf + cr_lf
    res_sep = ''
    # how much read from buffer socket in every read
    rec_chunk = 4096
    s = socket.socket()
    s.settimeout(timeout)
    # Try and connect and throw an exeption if it fails
    try:
    	s.connect((ip, port))
    except socket.gaierror, e:
   	print "Address-related error connecting to server: %s" % e
    	sys.exit(1)
    except socket.error, e:
    	print "Connection error: %s" % e
    	sys.exit(1)
    # the req_data is like 'HEAD HTTP/1.1 \r\n'
    req_data = "{} / {}{}".format(method, http_type, cr_lf)
    # if is a HTTP 1.1 protocol request,
    if http_type == "HTTP/1.1":
        # then we need to send Host header (we send ip instead of host here!)
        # adding host header to req_data like 'Host: google.com:80\r\n'
        req_data += 'Host: {}:{}{}'.format(ip, port, cr_lf)
        # set connection header to close for HTTP 1.1
        # adding connection header to req_data like 'Connection: close\r\n'
        req_data += "Connection: close{}".format(cr_lf)
    # headers join together with `\r\n` and ends with `\r\n\r\n`
    # adding '\r\n' to end of req_data
    req_data += cr_lf
    # the s.send() method may send only partial content. 
    # so we used s.sendall()
    s.sendall(req_data.encode())
    res_data = b''
    # default maximum header response is different in web servers: 4k, 8k, 16k
    # the s.recv(n) method may receive less than n bytes, 
    # so we used it in while.
    while 1:
        try:
            chunk = s.recv(rec_chunk)
            res_data += chunk
        except socket.error:
            break
        if not chunk:
            break
    if res_data:
        # decode `res_data` after reading all content of data buffer
        res_data = res_data.decode()
    else:
        return '', ''
    # detect header and body separated that is '\r\n\r\n' or '\n\n'
    if crlf_crlf in res_data:
        res_sep = crlf_crlf
    elif lf_lf in res_data:
        res_sep = lf_lf
    # for under HTTP/1.0 request type for servers doesn't support it
    #  and servers send just send body without header !
    if res_sep not in [crlf_crlf, lf_lf] or res_data.startswith('<'):
        return '', res_data
    # split header and data section from
    # `HEADER\r\n\r\nBODY` response or `HEADER\n\nBODY` response
    content = res_data.split(res_sep)
    banner, body = "".join(content[:1]), "".join(content[1:])
    return banner, body


def main():
    desc="""Attempts to grab header from a webserver on port 80."""

    # Check that we have 2 args. Name of script and ip or fqdn.
    if len (sys.argv) != 2 :
    	print "\nUsage: ./http_header_grabber.py ip/host\n"
    	sys.exit (1)

    ip = sys.argv[1]
    banner, body = http_header_grabber(ip)
    print('*' * 24)
    print(ip, 'HEAD HTTP/1.1')
    print(banner)


if __name__=='__main__':
	main()
