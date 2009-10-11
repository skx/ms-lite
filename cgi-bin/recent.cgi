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
    #  Get the year day.
    #
    my ( $sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst ) =
      localtime(time);

    #
    #  Find all indexes
    #
    my @files = glob("/spam/$yday/*/index");
    my @sorted = sort {( stat($a) )[9] <=> ( stat($b) )[9]} @files;

    #
    #  The most recent.
    #
    my $name = $sorted[0];
    open( INDEX, "<", $name );

    my @lines = reverse <INDEX>;

    close(INDEX);

    my @ret;
    my $count = 10;
    foreach my $line (@lines)
    {
        next if ( !$count );
        push( @ret, $line );
        $count -= 1;
    }

    return (@ret);

}


sub showRecent
{
    my (@recent) = (@_);

    my $template = HTML::Template->new( filename => "recent.tmpl" );

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

    $template->param( entries => $entries );

    print $template->output();

}
