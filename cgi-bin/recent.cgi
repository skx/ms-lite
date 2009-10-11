#!/usr/bin/perl -w
#
#  Shows "recent" spam.
#
# Steve
# --
#


use strict;
use warnings;

use CGI;
use File::Basename;
use HTML::Template;



my @recent = getRecent();
showRecent(@recent);


exit;



=begin doc

 Get recent SPAM.

=end doc

=cut

sub getRecent
{
    #
    #  Values to return
    #
    my @ret;

    #
    #  Get the year day.
    #
    my ( $sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst ) =
      localtime(time);

    #
    #  Find all indexes
    #
    my @files = glob("/spam/$yday/*/index");
    return (@ret ) if ( ! scalar(@files ) );

    #
    #  Sort them by modification date/time.
    #
    my @sorted = sort {( stat($b) )[9] <=> ( stat($a) )[9]} @files;

    #
    #  The most recent.
    #
    my $name = $sorted[0] || undef;
    return( @ret ) if ( !defined($name) );

    #
    #  Open & read
    #
    open( INDEX, "<", $name );
    my @lines = reverse <INDEX>;
    close(INDEX);

    #
    #  Build up no more than ten lines.
    #
    my $count = 10;
    foreach my $line (@lines)
    {
        next if ( !$count );
        push( @ret, $line );
        $count -= 1;
    }

    #
    #  Return
    #
    return (@ret);

}


=begin doc

 Show recent SPAM, via the template.

=end doc

=cut

sub showRecent
{
    my (@recent) = (@_);


    my $entries;

    foreach my $line (@recent)
    {
        my ( $from, $to, $file, $subject ) = split( /\|/, $line );

        my $domain = $to;
        $to =~ s/^<|>$//g;
        $to =~ s/@(.*)$//g;
        if ( $domain =~ /(.*)@(.*)/ )
        {
            $domain = $2;
        }
        $file = basename($file) if ($file);

        push( @$entries,
              {  from    => $from,
                 to      => $to,
                 file    => $file,
                 domain  => $domain,
                 subject => $subject,
              } );
    }

    #
    #  Load the template and set the values in it.
    #
    my $template = HTML::Template->new( filename => "recent.tmpl" );
    $template->param( entries => $entries ) if ( $entries );

    #
    #  Display it
    #
    print "Content-type: text/html\n\n";
    print $template->output();

}
