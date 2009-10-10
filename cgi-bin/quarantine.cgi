#!/usr/bin/perl -w
#
# This is a simple viewer for the quarantine which is accessed at
#
#    http://foo.dh/cgi-bin/quarantine.cgi
#
#
# When a mail is rejected for a domain it is stored to:
#
#  /spam/$year-day/$domain/{new cur tmp}
#
# An indexer will be written too:
#
#  /spam/$year-day/$domain/index
#
# This index will contain the following fields:
#
#  1.  From
#  2.  To
#  3.  Filename
#  4.  Subject
#
# Steve
# --
#
#


use strict;
use warnings;

use CGI;
use File::Basename;




#
# Get the domain we're to view.
#
my $cgi = new CGI;
my $domain = $cgi->param("domain") || undef;


#
#  If we've not been given a domain then just show the list.
#
if ( !defined($domain) )
{
    showDomainList();
    exit;
}

#
#  If we've been given a file show it.
#
if ( $cgi->param("file") )
{
    showFile( $domain, $cgi->param("file") );
    exit;
}
else
{

    #
    #  Show quarantine contents
    #
    print "Content-type: text/html\n\n";
    print "<h2>$domain</h2>\n";

    my @entries = readIndexes($domain);

    if ( !@entries )
    {
        print "No mail\n";
        exit;
    }

    print "<table border=1>\n";
    print "<tr><td>From</td><td>TO</td><td>Subject</td></tr>\n";
    foreach my $line (@entries)
    {
        my ( $from, $to, $file, $subject ) = split( /\|/, $line );

        $from =~ s/^<|>$//g;
        $to   =~ s/^<|>$//g;
        $to   =~ s/@(.*)$//g;
        $file = basename($file);
        print
          "<tr><td>$from</td><td>$to</td><td><a href=\"?domain=$domain;file=$file\">$subject</a></td></tr>\n";
    }
    print "</table>\n";


    exit;
}



=begin doc

  Show a single message

=end doc

=cut

sub showFile
{
    my ( $domain, $file ) = (@_);

    my @entries = readIndexes($domain);

    if ( !@entries )
    {
        print "Content-type: text/plain\n\n";
        print "No mail\n";
        exit;
    }

    foreach my $line (@entries)
    {
        my ( $from, $to, $name, $subject ) = split( /\|/, $line );

        my $path = basename($name);

        if ( $path eq $file )
        {
            print "Content-type: text/plain\n\n";

            open( SPAM, "<", "/$name" ) or
              die "Failed to open\n";
            while ( my $line = <SPAM> )
            {
                print $line;
            }
            close(SPAM);
            exit;
        }

    }

    print "Content-type: text/plain\n\n";
    print "File not found\n";
    exit;

}

=begin doc

  Show the domains on this host.

=end doc

=cut


sub showDomainList
{

    #
    #  For each directory beneath /spam/ add it to the list
    # if we found a matching directory beneath /srv
    #
    #
    print "Content-type: text/html\n\n";

    my %all;  
    my %spam ;

    #
    #  Find all domains on the system.
    #
    foreach my $dir ( sort( glob("/srv/*") ) )
    {
        my $domain = basename($dir);
        $all{$domain}=1;
    }

    #
    #  Find all domains which have received spam.
    #
    foreach my $dir ( sort( glob( "/spam/*/*" ) ) )
    {
        my $domain = basename($dir );
        $spam{$domain}=1;
    }

    print <<EOH;
<html>
 <head>
  <title>Mail-Scanning-Lite: Choose a domain</title>
 </head>
 <body>
 <h1>Mail-Scanning-Lite</h1>


 <blockquote>
 <h2>Spammed Domains</h2>
 <ul>
EOH
    foreach my $domain (keys %spam )
    {
        print
          "<li><a href=\"/cgi-bin/quarantine.cgi?domain=$domain\n\">$domain</a></li>\n";
    }

    print <<EOF;
  </ul>
  </blockquote>
  <blockquote>
  <h2>All Domains</h2>
  <ul>
EOF

    foreach my $domain (keys %all )
    {
        print
          "<li><a href=\"/cgi-bin/quarantine.cgi?domain=$domain\n\">$domain</a></li>\n";
    }


  print <<EOF;
 </body>
</html>
EOF
}



sub readIndexes
{
    my ($domain) = (@_);

    my @total;

    foreach my $file ( sort( glob("/spam/*/$domain/index") ) )
    {
        my @entries;

        open( FILE, "<", $file );
        while ( my $line = <FILE> )
        {
            chomp($line);
            push( @entries, $line );
        }
        close(FILE);

        push( @total, reverse(@entries) );
    }

    return @total;
}
