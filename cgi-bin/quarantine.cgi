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
use HTML::Template;



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

#
#  Show a daomin
#
showQuarantine( $domain );
exit;




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
    print "Content-type: text/html\n\n";

    my %all;
    my %spam;

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

    #
    #  Create the loops
    #
    my $all_domains;
    my $spam_domains;

    foreach my $d ( sort keys %all )
    {
        push(@$all_domains,{ domain => $d} );
    }
    foreach my $d ( sort keys %spam)
    {
        push(@$spam_domains,{ domain => $d} );
    }

    #
    #  Load the template, set the values, and exit.
    #
    my $template = HTML::Template->new( filename => "domains.tmpl" );
    $template->param( all_domains => $all_domains ) if ( $all_domains );
    $template->param( spam_domains => $spam_domains ) if ( $spam_domains );
    print $template->output();
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


=begin doc

  Show the quarantine for a single domain.

=end doc

=cut

sub showQuarantine
{
    my( $domain ) = ( @_ );

    #
    #  Show quarantine contents
    #
    print "Content-type: text/html\n\n";

    #
    #  Load the template
    #
    my $template = HTML::Template->new( filename => "quarantine.tmpl",
                                        loop_context_vars => 1 );

    my @entries = readIndexes($domain);
    if ( !@entries )
    {
        print $template->output();
        return;
    }

    my $entries;

    foreach my $line (@entries)
    {
        my ( $from, $to, $file, $subject ) = split( /\|/, $line );

        $to   =~ s/^<|>$//g;
        $to   =~ s/@(.*)$//g;
        $file = basename($file) if ( $file );;

        push(@$entries , {
                          from => $from,
                          to => $to,
                          file => $file,
                          domain => $domain,
                          subject => $subject,
                          } );
    }

    $template->param( entries => $entries ) if ( $entries );
    $template->param( domain => $domain );
    print $template->output();
}
