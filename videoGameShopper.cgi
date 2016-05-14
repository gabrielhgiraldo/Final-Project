#!"C:\xampp\perl\bin\perl.exe"

use CGI qw(:standard);
use strict;

use Carp;
use HTML::LinkExtor;
use HTTP::Request;
use HTTP::Response;
use HTTP::Status;
use LWP::RobotUA;
#use URI::URL;

#URI::URL::strict( 1 );   # insure that we only traverse well formed URL's

$| = 1;
my $ROBOT_NAME = 'ggirald1Bot/1.0';
my $ROBOT_MAIL = 'ggirald1@jhu.edu';
my $ROBOT_DELAY_IN_MINUTES = 0.0001;

my $robot = new LWP::RobotUA $ROBOT_NAME, $ROBOT_MAIL;

$robot->delay( $ROBOT_DELAY_IN_MINUTES);

my @websites = ("http://www.amazon.com/s/ref=nb_sb_noss_2?url=search-alias%3Dvideogames&field-keywords=
", "http://www.gamestop.com/browse?nav=16k-3-", "Best Buy");
my @product_links;#=(["http://www.google.com","http://www.facebook.com"],["http://www.instagram.com","http://www.noodles.com"]);
my @product_costs;#=(["\$300","\$40"],["\$3","\$2"]);
my @product_names;#=(["womp","boop"],["schloop","schlop"]);
my $game;
print header;
print<<END;
    <h1 align = "center"> Video Game Shopper </h1>
    <form>
        <div align="center">
            <input type="text" name="game">
            <input type="submit" value="Search">
        </div>
    </form>
END

if(param()){
	$game = param('game');
	if(ok()){
		search_websites();
		sort_results();
		print_results();
	}
}

sub ok{
	my $fine = 1;
	if(!$game){
		print "<p align='center'>Your Search is Empty!</p>",br; $fine = 0; 
	}
	return $fine;
}

sub print_results{
	print "printing results",br;
	print "<ul style = 'list-style-type:none;'>\n";
	for(my $i = 0;$i<@websites;$i++){
		my $caption;
		if($websites[$i] =~ /amazon/){
			$caption = "Amazon";
		}
		elsif($websites[$i] =~ /gamestop/){
			$caption = "Game Stop";
		}
		else{
			$caption = "Best Buy";
		}
		print "<li>\n<table>\n<caption><h2 align='left'><u>$caption</u></h2></caption>\n";
		if(!$product_links[$i]){
			print "<tr><td>No Search Results Found </td></tr>\n";
		}
		else{
			print "<tr>\n<th>Rank</th>\n<th>Cost</th>\n<th>Link</th>\n</tr>";
			for(my $j = 0; $j < scalar @{$product_links[$i]};$j++){
				my $place = $j+1;
				print "<tr>\n<td>$place</td>\n<td>\$$product_costs[$i][$j]</td>\n<td><a href='$product_links[$i][$j]'>$product_names[$i][$j]</td>\n</tr>\n";
			}
		}
		print"</table>\n</li>\n";
	}
	print "</ul>"
}
sub sort_results{
	print "sorting results",br;
	for(my $i = 1; $i<2; $i++){
		for(my $j = 0; $j< scalar @{$product_links[$i]};$j++){
			my $min_index = $j;
			for( my $k = $j+1; $k< scalar @{$product_links[$i]};$k++){
				my ($cost_1) = $product_costs[$i][$k] =~ /(\d+)/;
				my ($cost_2) = $product_costs[$i][$min_index] =~ /(\d+)/;
				if($cost_1< $cost_2){
					$min_index = $k;
				}
			}
			my $temp_cost = $product_costs[$i][$j];
			my $temp_link = $product_links[$i][$j];
			my $temp_name = $product_names[$i][$j];
			$product_costs[$i][$j]=$product_costs[$i][$min_index];
			$product_links[$i][$j]=$product_links[$i][$min_index];
			$product_names[$i][$j]=$product_names[$i][$min_index];
			$product_costs[$i][$min_index]=$temp_cost;
			$product_links[$i][$min_index]=$temp_link;
			$product_names[$i][$min_index]=$temp_name;
		}
	}
}
sub search_websites{
#	print "searching websites";
#	my $configurationFile='config.txt';
#	open (my $fh, 'encoding(UTF-8',$configurationFile)
#		or die "Could not open file '$configurationFile' $!";
#	print $configurationFile;
#	while(my $row = <$fh>){
#		print $row;
#		my $i = 0;
#		chomp $row;
#		$websites[$i]=$row;
#		$i++;
#		print $row;
#	}
	#for each of our websites we want to get info from
	for(my $i = 1; $i < 2; $i++){
		#print $websites[$i];
		#append the key words formed from the user's query to the search url
		my @split_search = split / /,$game;
		my $keywords="";
		for(my $j = 0; $j<@split_search;$j++){
			if($j == 0){
				$keywords =$keywords.$split_search[$j];
			}
			else{
				$keywords = $keywords."+".$split_search[$j];
			}
		}
		my $request;
		if($websites[$i] =~/gamestop/){
#			print $websites[$i].$keywords.",28zu0",br;
			$request = new HTTP::Request HEAD => $websites[$i].$keywords.",28zu0";
		}
		my $response = $robot -> request($request);
#		print $response->code;
		next if $response -> code != RC_OK;

		$request->method('GET');
		$response = $robot ->request($request);

		if($response -> code != RC_OK){
			print "url rejected";
			next;
		}
	my $related_urls = &grab_urls($response->content,$i);
	&extract_prices($response->content,$i);
	}
}
sub grab_urls {

    my $content = shift;
    my $i = shift;
#    my %urls    = ();    # NOTE: this is an associative array so that we only
                         #       push the same "href" value once.

     my $index = 0;
  skip:
    while ($content =~ s/<\s*[aA] ([^>]*)>\s*(?:<[^>]*>)*(?:([^<]*)(?:<[^aA>]*>)*<\/\s*[aA]\s*>)?//) {

	my $tag_text = $1;
	my $reg_text = $2;
	my $link = "";

	if (defined $reg_text) {
	    $reg_text =~ s/[\n\r]/ /;
	    $reg_text =~ s/\s{2,}/ /;
	}
#	print $reg_text,br,$tag_text,br;
	# make sure we are hitting url and it is not self-reference
	if ($tag_text =~ /href\s*=\s*(?:["']([^"']*)["']|([^\s])*)/i and $tag_text !~ /#/) {
	    $link = $1 || $2;
#	    print $reg_text,br;
	    if($reg_text =~ /$game/i){
#	    	print "FOUND A MATCH!";
#			print $link,br;
			if($websites[$i] =~ /gamestop/){
				$product_links[$i][$index] = "http://www.gamestop.com".$link;
			}
	    	$product_names[$i][$index] = $reg_text;
	    	$index++;
	    }
	}

	# print $reg_text, "\n" if defined $reg_text;
	# print $link, "\n\n";
    }

#    return keys %urls;   # the keys of the associative array hold all the
                         # links we've found (no repeats).
}
sub extract_prices{
	my $content = shift;
	my $i = shift;
	print "extracting prices",br;
   	#my @costs = $content =~ m/ats-product-price/g;
   	my @costs = $content =~ /<p class="pricing ats-product-price">(.*)<\/p>/g;
   	my $j = 0;
   	for my $cost(@costs) {
   		my @costs = split /\$/, $cost;
   	#	print $cost,br;
   		if($costs[2]){
  	 		$cost = $costs[2];
   		} else {
   			$cost = $costs[1];
   		}
   	#	print $cost,br;
   		$product_costs[$i][$j] =$cost;
		$j++;
   	}
   
}