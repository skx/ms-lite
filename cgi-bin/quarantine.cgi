#!/usr/bin/perl -w
#
# This is a simple viewer for the quarantine which is accessed at
#
#    http://example.com/cgi-bin/quarantine.cgi
#
# When a mail is rejected for a domain it is stored to:
#
#  /spam/$year-day/$domain/{new cur tmp}
#
# An index of each rejected message for each domain will also be written
# as a flat file:
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
# ("$year-day" is the day number of the current year.)
#
#
# Steve
# --
#
#


use strict;
use warnings;

use CGI;
use File::Basename;
use HTML::Template;



#
# Get the domain we're to view.
#
my $cgi    = new CGI;
my $domain = $cgi->param("domain") || undef;


#
#  If we've not been given a domain then just show the list of available
# domains.
#
if ( !defined($domain) )
{
    showDomainList();
    exit;
}

#
#  If we've been given a mail file to display then show it.
#
if ( $cgi->param("file") )
{
    showFile( $domain, $cgi->param("file") );
    exit;
}

#
#  Otherwise show the quarantine for the given domain.
#
showQuarantine($domain);
exit;




=begin doc

  Show a single email message.

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

        my $path = $name;
        $path = basename($path) if ($path);

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
    print "Content-type: text/html\n\n";

    my %all;
    my %spam;

    #
    #  Find all domains on the system.
    #
    foreach my $dir ( sort( glob("/srv/*") ) )
    {
        my $domain = basename($dir);
        $all{ $domain } = 1;
    }

    #
    #  Find all domains which have received spam.
    #
    foreach my $dir ( sort( glob("/spam/*/*") ) )
    {
        my $domain = basename($dir);
        $spam{ $domain } = 1;
    }

    #
    #  Create the loops
    #
    my $all_domains;
    my $spam_domains;

    foreach my $d ( sort keys %all )
    {
        push( @$all_domains, { domain => $d } );
    }
    foreach my $d ( sort keys %spam )
    {
        push( @$spam_domains, { domain => $d } );
    }

    #
    #  Load the template, set the values, and exit.
    #
    my $template = HTML::Template->new( filename => "domains.tmpl" );
    $template->param( all_domains  => $all_domains )  if ($all_domains);
    $template->param( spam_domains => $spam_domains ) if ($spam_domains);
    print $template->output();
}



=begin doc

  Return the index of rejected messages for the given domain.

  NOTE: We only bother with the previous five days.

=end doc

=cut
sub readIndexes
{
    my ($domain) = (@_);

    my @total;

    #
    #  Get the year day.
    #
    my ( $sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst ) =
      localtime(time);

    my $count = 5;

    while( $count > 0 )
    {
        if ( -e "/spam/$yday/$domain/index")
        {
            my @entries;

            open( FILE, "<", "/spam/$yday/$domain/index" );
            while ( my $line = <FILE> )
            {
                chomp($line);
                push( @entries, $line );
            }
            close(FILE);

            push( @total, reverse(@entries) );
        }

        $count -= 1;
        $yday  -= 1;
        if ( $yday < 0 ) { $yday = 365; }
    }
    return @total;
}


=begin doc

  Show the quarantine for a single domain.

=end doc

=cut

sub showQuarantine
{
    my ($domain) = (@_);

    #
    #  Show quarantine contents
    #
    print "Content-type: text/html\n\n";

    #
    #  Load the template
    #
    my $template = HTML::Template->new( filename          => "quarantine.tmpl",
                                        loop_context_vars => 1 );

    #
    #  Find all the details of the rejected mails.
    #
    my @avail = readIndexes($domain);
    my $count = scalar( @avail );

    #
    #  No messages?
    #
    if ( $count <= 0 )
    {
        print $template->output();
        return;
    }

    #
    #  The start & end to show.
    #
    my $start = $cgi->param("start") || 0;
    my $end   = $start + 1000;

    #
    #  The values we'll display
    #
    my $entries;

    my $cur = 0;
    foreach my $line (@avail)
    {
        next unless ( ( $cur >= $start ) &&  ( $cur <= $end ) );

        my ( $from, $to, $file, $subject ) = split( /\|/, $line );

        $to =~ s/^<|>$//g;
        $to =~ s/@(.*)$//g;
        $file = basename($file) if ($file);

        push( @$entries,
              {  from    => $from,
                 to      => $to,
                 file    => $file,
                 domain  => $domain,
                 subject => $subject,
              } );

        $cur +=1;
    }

    #
    #  Paging.
    #
    my $page ;
    my $pages = int ( $count / 1000 );
    my $i = 0;
    while( $i < $pages )
    {
        push( @$page, { start => 1000 *( $i + 1), page =>( $i + 1 ) } );
        $i += 1;
    }

    $template->param( entries => $entries ) if ($entries);
    $template->param( count   => $count );
    $template->param( domain  => $domain );
    $template->param( pages => $pages ) if ( $pages );
    print $template->output();
}
