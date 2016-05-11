#!/usr/local/bin/perl -w

#
# This program walks through HTML pages, extracting all the links to other
# text/html pages and then walking those links. Basically the robot performs
# a breadth first search through an HTML directory structure.
#
# All other functionality must be implemented
#
# Example:
#
#    robot_base.pl mylogfile.log content.txt http://www.cs.jhu.edu/
#
# Note: you must use a command line argument of http://some.web.address
#       or else the program will fail with error code 404 (document not
#       found).

use strict;

use Carp;
use HTML::LinkExtor;
use HTTP::Request;
use HTTP::Response;
use HTTP::Status;
use LWP::RobotUA;
use URI::URL;

URI::URL::strict( 1 );   # insure that we only traverse well formed URL's

$| = 1;

my $log_file = shift (@ARGV);
my $content_file = shift (@ARGV);
my $document_file = shift(@ARGV);

if ((!defined ($log_file)) || (!defined ($content_file)) || (!defined($document_file))) {
	print STDERR "You must specify a log file, a content file, a docments list file and a base_url\n";
	print STDERR "when running the web robot:\n";
	print STDERR "  ./robot_base.pl mylogfile.log content.txt documents.doc base_url\n";
    exit (1);
}

open LOG, ">$log_file";
open CONTENT, ">$content_file";
open DOCUMENT, ">$document_file";

############################################################
##               PLEASE CHANGE THESE DEFAULTS             ##
############################################################

# I don't want to be flamed by web site administrators for
# the lousy behavior of your robots.

my $ROBOT_NAME = 'ggirald1Bot/1.0';
my $ROBOT_MAIL = 'ggirald1@jhu.edu';
my $ROBOT_DELAY_IN_MINUTES = 0.0001;


#
# create an instance of LWP::RobotUA.
#
# Note: you _must_ include a name and email address during construction
#       (web site administrators often times want to know who to bitch at
#       for intrusive bugs).
#
# Note: the LWP::RobotUA delays a set amount of time before contacting a
#       server again. The robot will first contact the base server (www.
#       servername.tag) to retrieve the robots.txt file which tells the
#       robot where it can and can't go. It will then delay. The default
#       delay is 1 minute (which is what I am using). You can change this
#       with a call of
#
#         $robot->delay( $ROBOT_DELAY_IN_MINUTES );
#
#       At any rate, if your program seems to be doing nothing, wait for
#       at least 60 seconds (default delay) before concluding that some-
#       thing is wrong.
#

my $robot = new LWP::RobotUA $ROBOT_NAME, $ROBOT_MAIL;

$robot->delay( $ROBOT_DELAY_IN_MINUTES);

my $base_url    = shift(@ARGV);   # the root URL we will start from

my @search_urls = ();    # current URL's waiting to be trapsed
my @wanted_urls = ();    # URL's which contain info that we are looking for
my %relevance   = ();    # how relevant is a particular URL to our search
my %pushed      = ();    # URL's which have either been visited or are already
                         #  on the @search_urls array

push @search_urls, $base_url;


while (@search_urls) {
    my $url = shift @search_urls;
    # so we know which link we are visiting
	print "\n\n\n**** Current Visiting: $url ****\n";
    #
    # insure that the URL is well-formed, otherwise skip it
    # if not or something other than HTTP
    #

    my $parsed_url = eval { new URI::URL $url; };

    next if $@;
    next if $parsed_url->scheme !~/http/i;
    my $non_www_url = $url;
    $non_www_url =~ s/www\.//i;
    if  ($url =~ /^$base_url/i) {
    	# if url is local URL, do nothing. we can add handle here is needed in future.
    }
    elsif ($non_www_url =~ /^$base_url/i) {
    	# if url is local URL, do nothing. we can add handle here is needed in future.
    }
    else {
    	print " * non-local URL, skipped: $url, base is: $base_url * \n";
    	next;
    }

    #
    # get header information on URL to see it's status (exis-
    # tant, accessible, etc.) and content type. If the status
    # is not okay or the content type is not what we are
    # looking for skip the URL and move on
    #

    print LOG "[HEAD ] $url\n";

    my $request  = new HTTP::Request HEAD => $url;
    my $response = $robot->request( $request );

    next if $response->code != RC_OK;
    next if ! &wanted_content( $response->content_type, $url);

    print LOG "[GET  ] $url\n";

    $request->method( 'GET' );
    $response = $robot->request( $request );

     if ($response->code != RC_OK) {
     	print " XXX Bad URL hit, skipped: $url, base is: $base_url * \n";
     	next;
     }
    next if $response->content_type !~ m@text/html@;

    print LOG "[LINKS] $url\n";

    &extract_content ($response->content, $url);

    my @related_urls  = &grab_urls( $response->content );

    foreach my $link (@related_urls) {

	my $full_url = eval { (new URI::URL $link, $response->base)->abs; };
	delete $relevance{ $link } and next if $@;
	# make sure we only handle the url that is in base URL(cs.jhu.edu) domain
	# my $non_www_furl = $full_url;
	# my $res_base_url = $response->base;
    # $non_www_furl =~ s/www\.//i;

    # remove "or $non_www_furl =~ /^$base_url/i" in the if statement
    # if you don't want to include links with "www" in our search
    if  ($full_url =~ /^$base_url/i) {
    	# print "URL found -> ", $full_url, "\n";
    	$relevance{ $full_url } = $relevance{ $link };
		delete $relevance{ $link } if $full_url ne $link;

		push @search_urls, $full_url and $pushed{ $full_url } = 1
			if ! exists $pushed{ $full_url };
    }
    else {
    	# remove any link that is not within the base url domain
    	delete $relevance{ $link } and next;
	}
    }

    #
    # reorder the urls base upon relevance so that we search
    # areas which seem most relevant to us first.
    # note: in DESC order

    @search_urls =
	sort { $relevance{ $b } <=> $relevance{ $a }; } @search_urls;

}

close LOG;
close CONTENT;
close DOCUMENT;

exit (0);

#
# wanted_content
#
#    UNIMPLEMENTED
#
#  this function should check to see if the current URL content
#  is something which is either
#
#    a) something we are looking for (e.g. postscript, pdf,
#       plain text, or html). In this case we should save the URL in the
#       @wanted_urls array.
#
#    b) something we can traverse and search for links
#       (this can be just text/html).
#

sub wanted_content {
    my $content = shift;
    my $url = $_[1];	# $contect actually contains an array of 2 elements, thus we need to get the 2nd element in the array

    # right now we only accept text/html
    #  and this requires only a *very* simple set of additions
    #

    if ($content =~ m@(text/html|text/plain)@) {
		# print $content, "\n";
		push @wanted_urls, $url;
    }
    # if the content type is what we want, then we write it to the document list output file
    if ($content =~ m@(application/postscript|application/pdf)@) {
		push @wanted_urls, $url;
		print DOCUMENT "DOCUMENT: $content -> $_[0]\n";
		# print "XXX $content, $_[0]\n";
	}
	return $content =~ m@(text/html|text/plain)@;
}

#
# extract_content
#
#    UNIMPLEMENTED
#
#  this function should read through the context of all the text/html
#  documents retrieved by the web robot and extract three types of
#  contact information described in the assignment

sub extract_content {
    my $content = shift;
    my $url = shift;
	# print "XXX, $url\n";

	# We use array to store all the emails and phone in one page :)
	# my @emails = $content =~ /mailto:([a-zA-Z0-9\-\_\+]+\@[a-zA-Z0-9\-]+)/g;
    my @emails = $content =~ m/[a-zA-Z0-9\-\_\+]+\@[a-zA-Z0-9\-]+\.[a-zA-Z0-9\-\.]+/g;
    my @phones = $content =~ m/[0-9]{3}\-[0-9]{3}\-[0-9]{3}|\([0-9]{3}\)\s*[0-9]{3}\-[0-9]{3}/g;
    my @addresses = $content =~ m/\w+\,\s+\w+\s+[0-9]{5}/g;

    # parse out information you want
    # print it in the tuple format to the CONTENT and LOG files, for example:
	foreach my $email (@emails) {
		print CONTENT "($url; EMAIL; $email)\n";
		print LOG "($url; EMAIL; $email)\n";
    }

	foreach my $phone(@phones) {
		print CONTENT "($url; PHONE; $phone)\n";
		print LOG "($url; PHONE; $phone)\n";
	}

	foreach my $address(@addresses) {
		print CONTENT "($url; CITY; $address)\n";
		print LOG "($url; CITY; $address)\n";
	}

    return;
}

#
# grab_urls
#
#    PARTIALLY IMPLEMENTED
#
#   this function parses through the content of a passed HTML page and
#   picks out all links and any immediately related text.
#
#   Example:
#
#     given
#
#       <a href="somepage.html">This is some web page</a>
#
#     the link "somepage.html" and related text "This is some web page"
#     will be parsed out. However, given
#
#       <a href="anotherpage.html"><img src="image.jpg">
#
#       Further text which does not relate to the link . . .
#
#     the link "anotherpage.html" will be parse out but the text "Further
#     text which . . . " will be ignored.
#
#   Relevancy based on both the link itself and the related text should
#   be calculated and stored in the %relevance hash
#
#   Example:
#
#      $relevance{ $link } = &your_relevance_method( $link, $text );
#
#   Currently _no_ relevance calculations are made and each link is
#   given a relevance value of 1.
#

sub grab_urls {
    my $content = shift;
    my %urls    = ();    # NOTE: this is an associative array so that we only
                         #       push the same "href" value once.


  skip:
    while ($content =~ s/<\s*[aA] ([^>]*)>\s*(?:<[^>]*>)*(?:([^<]*)(?:<[^aA>]*>)*<\/\s*[aA]\s*>)?//) {

	my $tag_text = $1;
	my $reg_text = $2;
	my $link = "";
	my $weight = 0;	# The weight of the current link

	if (defined $reg_text) {
	    $reg_text =~ s/[\n\r]/ /;
	    $reg_text =~ s/\s{2,}/ /;
	}

	# make sure we are hitting url and it is not self-reference
	if ($tag_text =~ /href\s*=\s*(?:["']([^"']*)["']|([^\s])*)/i and $tag_text !~ /#/) {
	    $link = $1 || $2;
	    # sometimes we got <a href="">, we simply continue if we have such a link
	    next if !defined($link);
		# print $link, "\n";
	    #
	    # okay, the same link may occur more than once in a
	    # document, but currently I only consider the last
	    # instance of a particular link
	    #

		#
		# Weight the link
		# compute some relevancy function here
		#

		# if the link is to a page, it will likely we can extract some more info there, thus higher rank
		if ($link =~ /(\.htm|\.html|\.shtml|\.php|\.asp|\.jsp)/i) {
			$weight += 300;
		}

		# if the link is to a PDF or PS, we slightly higher the rank (higher than other kind of docs)
		if ($link =~ /(\.pdf\.ps)/i) {
			$weight += 150;
		}

		# if the link is to directory, it will likely we can extract some more info there, thus higher rank
		elsif ($link =~ /\/\w*$/i) {
			$weight += 500;
		}

		# if the link is a document, we lower the rank of the link
		# because we are more interested in text pages that we could extract information from
		#if ($link =~ /(\.ppt|\.jpg|\.gif|\.doc|\.docx|\.zip|\.gz|\.z)$/i) {
		else {
			$weight -= 300;
		}

		# we visit short link first, because it is more likely to be in the same directory within the current page
		# Or it is more likely to contain a more general information for we to extract
		$weight -= length($link);

		# we need to check the link to see if it is an actual link without http, if so we shouldn't add it
		# if ($link =~ /^[a-zA-z0-9]+\.[a-zA-z0-9\-\_]+\.?/ and $link =~ /[(com)(edu)(net)(org)]$/) {
			# we could add other handles for the non-local links
		# }
		# else {
			# print "got link -> $link\n";
			# my $len = length($link);
			# print "length is: $len\n";
			$relevance{ $link } = $weight;
			$urls{ $link }      = 1;
	    # }
	}

	# print $reg_text, "\n" if defined $reg_text;
	# print $link, "\n\n";
    }

    return keys %urls;   # the keys of the associative array hold all the
                         # links we've found (no repeats).
}
