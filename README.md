

About
-----


  This repository contains the files necessary for a mail-scanning-lite
 service to run upon a single host.

  This system comprises of three distinct parts:

    1.  A collection of plugins for qpsmtpd.

    2.  A standard configuration mechanism, using directories beneath
       /srv.

    3.  A local quarantine of rejected messages, beneath /spam.




Assumptions
-----------

  This system makes several assumptions:

    1. The each mail will read in its entirety and either delivered to
       exim4 running upon the local host, or archived to a rejection location.

       This means incoming mails will always be read in their entirety, even
       if we know very early on that they are spam.  (Without reading them
       we can't store a copy prior to sending the SMTP-time rejection.)

    2. That the configuration for domains is located beneath a common
       prefix.  ("/srv/")

    3. That the rejected quarantine will be located in a fixed location.
       ("/spam/")




Layout
------

  [This step completely ignores the configuration of exim4]

  The domains hosted upon the local machine will be configured beneath
 the directory /srv.  For each domain there will be a sub-directory named
 after the domain.

  The archive of rejected mails will be stored at /spam/





Domain Users Configuration
--------------------------

  The system will configure itself via files in the following directories:

      /srv/example.com/users/valid/
      /srv/example.com/users/invalid/

  If wildcard handling is expected then /users/valid/* will exist.

  e.g. A domain that accepts mail for only the users "foo", and "bar"
 can be constructed via:

     mkdir -p /srv/example.com/users/valid
     touch    /srv/example.com/users/valid/foo
     touch    /srv/example.com/users/valid/bar

  A domain that will accept mail for all recipients will have:

    mkdir -p "/srv/example.com/users/valid"
    touch    "/srv/example.com/users/valid/*"

  (i.e. "/valid/*" is present.)

  A domain that accepts email for all users except "bob" and "fred" will
 have:

    mkdir -p /srv/example.com/users/valid/
    touch   "/srv/example.com/users/valid/*"
    mkdir -p /srv/example.com/users/invalid/
    touch    /srv/example.com/users/invalid/bob
    touch    /srv/example.com/users/invalid/fred


  In terms of precedence an invalid user overrides a valid user.




Per-Domain Configuration
------------------------


  In addition to the handling of user accounts at a given domain you
 can also enable per-domain checks.

  There are two ways to do this:

  1.  Enable all checks on the given domain.

  2.  Enable just some checks for a particular domain.


  To get enable all checks run:

  mkdir -p /srv/example.com/checks
  touch    /srv/example.com/checks/all

  Alternatively you might choose to only run the "helo" and "date" check:

  mkdir -p /srv/example.com/checks/
  touch    /srv/example.com/checks/date
  touch    /srv/example.com/checks/helo


  The name of the file to enable matches the name of the plugin beneath
 ./plugins/checks/ - and you'll need to read the code to see what the checks
 do.

  As this is mail-scanning-lite only some checks are present at the moment,
 more may be ported in the future.



Domain Whitelist Configuration
------------------------------

  Whitelisting follows a similar pattern to the setup of users, with
 three directories:

       /srv/example.com/whitelisted/senders
       /srv/example.com/whitelisted/recipients
       /srv/example.com/whitelisted/ips

  e.g. To never reject mail going to "abuse@example.com" run:

  mkdir -p /srv/example.com/whitelisted/recipients/
  touch    /srv/example.com/whitelisted/recipients/abuse

  e.g. To whitelist the sender "steve@steve.org.uk" :

  mkdir -p /srv/example.com/whitelisted/senders/
  touch    /srv/example.com/whitelisted/senders/steve@steve.org.uk

  "/ips/" match sending ips in the predictable fashion.



Domain Blacklist Configuration
------------------------------

  Note: Blacklisting will occur prior to whitelisting.

  The blacklisting follows the familiar pattern with the following
 directories:

   /srv/example.com/blacklisted/ips/
   /srv/example.com/blacklisted/tld/
   /srv/example.com/blacklisted/senders/
   /srv/example.com/blacklisted/domains/

  For example to reject mail from a particular IP just run:

     mkdir -p /srv/example.com/blacklisted/ips/
     touch    /srv/example.com/blacklisted/ips/1.2.3.4

  Similarly you could reject all mail from @aol.com by running:

     mkdir -p /srv/example.com/blacklisted/domains/
     touch    /srv/example.com/blacklisted/domains/aol.com

  The only blacklisting method which require explaination is the
 blacklisting by TLD.  If you blacklist the TLD ".ph" you are NOT
 actually refusing mail from "foo@bar.ph", or "foo@bar.baz.ph", instead
 you are rejecting incoming connections from hosts which have the
 reverse DNS matching .ph.  If you receive an SMTP connection
 from:
    
    1.2.3.4  -> RDNS == foo.dsl1-2-3.4.co.ph

  Then the connection will default to being spam.


Spam Storage
------------

  Each rejected message will be archived to disk beneath the common
 prefix of /spam/

  The hierarchy is designed to be easy to "empty" or expire, and that
 implies that there will be some overhead.

  Spam rejected on the 212th day of the year, for the domain example.com
 will be located beneath:

      /spam/212/example.com/{ new cur tmp }

  There will be an index created of the sender, recipient, subject, and
 filename the SPAM message was ultimately archived within.

      /spam/212/example.com/index



Steve
--
